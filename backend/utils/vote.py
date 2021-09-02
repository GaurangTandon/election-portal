from datetime import datetime

from flask import g
from backend.models.orm import db
from backend.models.models import Election, ElectionMethods, Votes


def vote(election_id, args):

    user = g.user
    assert user

    election = Election.query.filter_by(id=election_id).first()
    if not election:
        return "Election not found", 404

    current_datetime = datetime.now()
    voting_start_date = election.voting_start_date
    voting_end_date = election.voting_end_date

    if not (voting_start_date <= current_datetime <= voting_end_date):
        return "Voting is currently closed", 400

    vote = Votes.query.filter_by(election_id=election_id, user_id=user.id).first()
    if vote:
        return "You have already voted in this election", 400

    constituency = election.get_constituency(user)
    if not constituency:
        return "You are not eligible to vote in this election", 400

    votes = args.get("votes")
    if not votes:
        return "Please provide a list of candidates", 400

    if len(set(votes)) != len(votes):
        return "Please provide a list of unique candidates", 400

    if len(votes) > constituency.preferences:
        return "You need to vote for %d candidates" % constituency.preferences, 400

    if election.election_method == ElectionMethods.IRV:

        for candidate_id in votes:
            candidate = election.get_candidate(candidate_id, approval_status=True)
            if not candidate:
                return "Candidate not found", 400
            if len(candidate.votes) == 0:
                candidate.votes = [1]
            else:
                candidate_votes = list(candidate.votes)
                candidate_votes[0] += 1
                candidate.votes = candidate_votes

    elif election.election_method == ElectionMethods.STV:
        for i, candidate_id in enumerate(votes):
            candidate = election.get_candidate(candidate_id, approval_status=True)
            if not candidate:
                return "Candidate not found", 400
            if not constituency.is_candidate_eligible(candidate.user):
                return "This candidate is from another constituency", 400
            if len(candidate.votes) == 0:
                candidate.votes = [0 for _ in range(constituency.preferences)]
            candidate_votes = list(candidate.votes)
            candidate_votes[i] += 1
            candidate.votes = candidate_votes

    vote = Votes(election_id=election_id, user_id=user.id, vote_time=datetime.now())
    db.session.add(vote)
    db.session.commit()
    return "Success", 200
