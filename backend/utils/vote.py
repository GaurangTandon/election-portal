from datetime import datetime

from flask import g

from backend.models.orm import db
from backend.models.models import (
    CumulativeHashes,
    Election,
    ElectionMethods,
    Hashes,
    VoteCamp,
    Votes,
)
from .crypto import get_nonce_and_hash


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

    vcamp = VoteCamp(cumulative_hash=1)

    hash_objects = []
    hashes = []
    for idx, candidate in enumerate(candidates):
        key = candidate.get_key()
        nonce, hsh = get_nonce_and_hash(key)
        hash_obj = Hashes(
            key=key, nonce=nonce, hash=hsh, vote_camp=vcamp.id, vote_camp_order=idx
        )
        hash_objects.append(hash_obj)
        hashes.append(hsh)

    hash_concat = "".join(hashes)
    nonce_f, hash_f = get_nonce_and_hash(hash_concat)
    cum_hash = CumulativeHashes(nonce=nonce_f, hash=hash_f, hash_str=hash_concat)

    db.session.add(cum_hash)
    db.session.commit()

    # IDs are only correct after committing into db
    vcamp.cumulative_hash = cum_hash.id
    db.session.add(vcamp)
    db.session.commit()

    for hobj in hash_objects:
        hobj.vote_camp = vcamp.id
        db.session.add(hobj)
    db.session.commit()

    return {"id": cum_hash.id, "hash": hash_f}, 200
