from datetime import datetime
from operator import itemgetter
import os
import sys

from flask import g, send_from_directory, session

from app.models.orm import db
from app.models.models import (
    Candidates,
    CumulativeHashes,
    Election,
    ElectionMethods,
    Hashes,
    VoteCamp,
    Votes,
)
from .crypto import generate_nonce, get_nonce_and_hash, hash256

VOTEID_SESSION_KEY = "voteid"


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

    # method to print in docker compose
    # print("hello2", file=sys.stdout, flush=True)
    # sys.stdout.flush()

    # casting empty vote is allowed
    # if not votes:
    #     return "Please provide a list of candidates", 400

    # remove trailing list of empty votes
    while len(votes) > 0 and votes[-1] == '':
        votes.pop()

    # it is allowed to not vote for any candidate
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
        # possible when number of candidates is less than the number of seats
        if candidate_id == "":
            continue
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

    vcamp = VoteCamp(
        cumulative_hash=1, has_cast=False, has_audited=False, election_id=election.id
    )

    hash_objects = []
    hashes = []
    for idx, candidate in enumerate(candidates):
        key = candidate.get_key()
        nonce, hsh = get_nonce_and_hash(key)
        hash_obj = Hashes(
            key=key,
            nonce=nonce,
            vote_camp=vcamp.id,
            vote_camp_order=idx,
            user_id=candidate.user.id,
        )
        hash_objects.append(hash_obj)
        hashes.append(hsh)

    hash_concat = "".join(hashes)
    nonce_f, hash_f = get_nonce_and_hash(hash_concat)
    cum_hash = CumulativeHashes(nonce=nonce_f, hash_str=hash_concat)

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

    session[VOTEID_SESSION_KEY] = vcamp.id
    return {"id": vcamp.id, "hash": hash_f}, 200


def cast(votecamp_id):
    """
    Take the votes given by votecamp id and actually perform them
    """
    votecamp = VoteCamp.query.get_or_404(votecamp_id)
    election = Election.query.get_or_404(votecamp.election_id)

    # votes given by votecamp are guaranteed to be correct as
    # validation has already taken place when putting them into db previously

    if votecamp.has_cast or votecamp.has_audited:
        return "This vote has already been cast or audited", 400

    if votecamp_id != session[VOTEID_SESSION_KEY]:
        return "Can only cast vote with the same votecamp id as in the session", 400

    votecamp.has_cast = True
    votes = Hashes.query.filter_by(vote_camp=votecamp_id).all()

    for vote_hash in votes:
        vote_pref_order = vote_hash.vote_camp_order
        user_id = vote_hash.user_id
        el2 = votecamp.election_id
        candidate = Candidates.query.filter_by(user_id=user_id, election_id=el2).first()
        if election.election_method == ElectionMethods.IRV:
            if not candidate.votes or len(candidate.votes) == 0:
                candidate.votes = [1]
            else:
                candidate_votes = list(candidate.votes)
                candidate_votes[0] += 1
                candidate.votes = candidate_votes
        elif election.election_method == ElectionMethods.STV:
            consti = election.get_candidate_constituency(candidate)
            if not candidate.votes or len(candidate.votes) == 0:
                candidate.votes = [0 for _ in range(consti.preferences)]
            candidate_votes = list(candidate.votes)
            candidate_votes[vote_pref_order] += 1
            candidate.votes = candidate_votes
        else:
            assert False
        db.session.add(candidate)

    vote = Votes(
        election_id=votecamp.election_id, user_id=g.user.id, vote_time=datetime.now()
    )

    db.session.add(vote)
    db.session.add(votecamp)
    db.session.commit()
    return "Success", 200


def audit(votecamp_id, return_file=True):
    votecamp = VoteCamp.query.get_or_404(votecamp_id)

    if votecamp.has_cast:
        return "Votes that have been finalized cannot be audited", 401

    votecamp.has_audited = True
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
                    "hash": hash256(combined_str),
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
    combined = key_f + "," + nonce
    final_hash = hash256(combined)

    token_details = {
        "voted_keys": voted_keys,
        "final_key_str": key_f,
        "final_nonce": nonce,
        "final_combined_key": combined,
        "final_hash": final_hash,
    }
    diagnostic_str = build_diagnostic_for_token(token_details)

    # no file paths here are user-crafted strings
    # even then, send_from_directory ensures that files _outside_ the supplied DIR
    # will not be sent in any way
    filename = f"{final_hash[:15]}.md"  # probability of collision is 2^60
    INTER_DIR = "votedata"
    DIR = f"static/{INTER_DIR}"
    if 'static' not in os.listdir("."):
        DIR = "app/" + DIR
    with open(f"{DIR}/{filename}", "w") as f:
        f.write(diagnostic_str)

    if return_file:
        return send_from_directory(DIR, filename)
    else:
        rel_to_static_path = INTER_DIR + "/" + filename
        return rel_to_static_path, filename


def build_diagnostic_for_token(token_details):
    """
    Generates a plain text string explaining in natural language how to audit
    a token
    token_details is a dictionary containing all the metadata required to generate
    this plain text
    """

    token = token_details["final_hash"]
    message = ""

    def output(s: str):
        nonlocal message
        message += s

    output(
        f"# Audit of `token`\n\nThe given token proof is: `{token}`. This file contains information on how to audit this token. Through this auditing, you will be guaranteed that this token proof is a genuine representation of the original vote choices.\n"
    )

    voted_keys = token_details["voted_keys"]
    message += (
        "We used the SHA256 hashing algorithm. You can run it on Linux"
        + ' as `echo -n "<string>" | sha256sum`\n'
        + "We added nonces to the strings (before hashing them) to make it impossible to reverse-engineer the string to match the hash. Each nonce is a 16 byte random integer.\n"
        + "You can find more details about our cryptographic methodology on the page https://election.iiit.ac.in/security"
        + f"\n\nThe given token encodes {len(voted_keys)} preferences\n"
    )
    for order, pref in voted_keys:
        key, nonce = pref["key"], pref["nonce"]
        output(f"\n## Preference {order + 1}\n\n")
        output(
            f"The unique key of the candidate is: `{key}`"
            + f", and the nonce attached to it is: `{nonce}`"
            + f". This yields the combined string: `{pref['combined']}`\n"
        )
        output(f"The hash of the above combined string is: `{pref['hash']}`\n")

    output("\n## Combining all hashes\n\n")
    output(
        f"The combined string of all hashes is: `{token_details['final_key_str']}`\n"
        + f"Using the nonce: `{token_details['final_nonce']}`,"
        + f" the final string of all hashes obtained is: `{token_details['final_combined_key']}`\n"
    )
    output(
        f"\nHashing the above final string gives the final hash: `{token_details['final_hash']}`. This final hash is the same as the token proof that was assigned to you.\n"
    )

    output(
        "\n## Conclusion\n\nWe have successfully audited the internal representation of the given token proof."
    )
    return message
