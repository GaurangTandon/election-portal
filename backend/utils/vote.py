from datetime import datetime
from operator import itemgetter

from flask import g

from backend.models.orm import db
from backend.models.models import (
    Candidates,
    CumulativeHashes,
    Election,
    ElectionMethods,
    Hashes,
    VoteCamp,
    Votes,
)
from .crypto import generate_nonce, get_nonce_and_hash


def vote(election_id, votes):
    user = g.user
    assert user

    election = Election.query.filter_by(id=election_id).first()
    if not election:
        return "Election not found", 404

    current_datetime = datetime.now()
    voting_start_date = election.voting_start_date
    voting_end_date = election.voting_end_date

    # trivial checks first
    if not (voting_start_date <= current_datetime <= voting_end_date):
        return "Voting is currently closed", 400

    if not votes:
        return "Please provide a list of candidates", 400

    if len(set(votes)) != len(votes):
        return "Please provide a list of unique candidates", 400

    # db checks next
    constituency = election.get_constituency(user)
    if not constituency:
        return "You are not eligible to vote in this election", 400

    vote = Votes.query.filter_by(election_id=election_id, user_id=user.id).first()
    if vote:
        return "You have already voted in this election", 400

    if len(votes) > constituency.preferences:
        return (
            "You can vote for atmost %d candidates" % constituency.preferences,
            400,
        )

    candidates = []
    for candidate_id in votes:
        candidate = election.get_candidate(candidate_id, approval_status=True)
        err = f"Candidate with id {candidate_id}"
        if not candidate:
            return f"{err} not found", 404
        if not constituency.is_candidate_eligible(candidate.user):
            return (
                f"{err} is from another constituency (required: {constituency.id})",
                401,
            )
        candidates.append(candidate)

    vcamp = VoteCamp(cumulative_hash=1, used=False)

    hash_objects = []
    hashes = []
    for idx, candidate in enumerate(candidates):
        key = candidate.get_key()
        nonce, hsh = get_nonce_and_hash(key)
        hash_obj = Hashes(
            key=key,
            nonce=nonce,
            hash=hsh,
            vote_camp=vcamp.id,
            vote_camp_order=idx,
            election_id=election_id,
            user_id=candidate.user.id,
        )
        hash_objects.append(hash_obj)
        hashes.append(hsh)

    hash_concat = "".join(hashes)
    nonce_f, hash_f = get_nonce_and_hash(hash_concat)
    cum_hash = CumulativeHashes(nonce=nonce_f, hash=hash_f, hash_str=hash_concat)

    db.session.add(cum_hash)
    db.session.commit()

    # IDs are only correct after committing into db
    vcamp.id = generate_nonce(length=VoteCamp.ID_LEN)
    vcamp.cumulative_hash = cum_hash.id
    db.session.add(vcamp)
    db.session.commit()

    for hobj in hash_objects:
        hobj.vote_camp = vcamp.id
        db.session.add(hobj)
    db.session.commit()

    return {"id": vcamp.id, "hash": hash_f}, 200


def cast(election_id, votecamp_id):
    """
    Take the votes given by votecamp id and actually perform them
    """
    election = Election.query.get_or_404(election_id)
    votecamp = VoteCamp.query.get_or_404(votecamp_id)

    # votes given by votecamp are guaranteed to be correct as
    # validation has already taken place when putting them into db previously

    if votecamp.used:
        return "This vote has already been cast. Please recheck the id", 400

    votecamp.used = True
    votes = Hashes.query.filter_by(vote_camp=votecamp_id).all()

    for vote_hash in votes:
        vote_pref_order = vote_hash.vote_camp_order
        user_id = vote_hash.user_id
        el2 = vote_hash.election_id
        assert el2 == election_id
        candidate = Candidates.query.filter_by(
            user_id=user_id, election_id=election_id
        ).first()
        if election.election_method == ElectionMethods.IRV:
            if len(candidate.votes) == 0:
                candidate.votes = [1]
            else:
                candidate_votes = list(candidate.votes)
                candidate_votes[0] += 1
                candidate.votes = candidate_votes
        elif election.election_method == ElectionMethods.STV:
            consti = election.get_candidate_constituency(candidate)
            if len(candidate.votes) == 0:
                candidate.votes = [0 for _ in range(consti.preferences)]
            candidate_votes = list(candidate.votes)
            candidate_votes[vote_pref_order] += 1
            candidate.votes = candidate_votes
        else:
            assert False
        db.session.add(candidate)

    db.session.add(votecamp)
    db.session.commit()
    return "Success", 200


def audit(votecamp_id):
    votecamp = VoteCamp.query.get_or_404(votecamp_id)

    if votecamp.used:
        # ideally auditing should be allowed multiple times, but hard to integrate in the UI anyway
        return "This vote has already been cast/audited. Please recheck the id", 401

    votecamp.used = True
    votes = Hashes.query.filter_by(vote_camp=votecamp_id).all()

    voted_keys = []
    for vote_hash in votes:
        vote_pref_order = vote_hash.vote_camp_order
        key = vote_hash.key
        nonce = vote_hash.nonce
        combined_str = key + "," + nonce

        voted_keys.append(
            (
                vote_pref_order,
                {
                    "key": key,
                    "nonce": nonce,
                    "combined": combined_str,
                    "hash": vote_hash.hash,
                },
            )
        )
    voted_keys.sort(key=itemgetter(0))

    db.session.add(votecamp)
    db.session.commit()

    combined_hash_obj = CumulativeHashes.query.filter_by(
        id=votecamp.cumulative_hash
    ).first()
    key_f = combined_hash_obj.hash_str
    nonce = combined_hash_obj.nonce

    return {
        "voted_keys": voted_keys,
        "final_key_str": key_f,
        "final_nonce": nonce,
        "final_combined_key": key_f + "," + nonce,
        "final_hash": combined_hash_obj.hash,
    }
