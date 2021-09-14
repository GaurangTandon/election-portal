-- batchwise/programme wise count of voters

SELECT batch, COUNT(*) FROM
    ((SELECT user_id, election_id FROM votes WHERE election_id = 2) A 
        JOIN "user" u 
        ON A.user_id = u.id)
    GROUP BY batch
    ORDER by batch;

SELECT batch, programme, COUNT(*) FROM
    ((SELECT user_id, election_id FROM votes WHERE election_id = 2) A 
        JOIN "user" u 
        ON A.user_id = u.id)
    GROUP BY batch, programme
    ORDER by batch, programme;
    
    
-- Count votes in IRV

SELECT u.name, B.count FROM
    (SELECT key, COUNT(*) FROM 
        (SELECT id from votecamp WHERE election_id = 2 AND has_cast=true) AS A JOIN hashes
            ON hashes.vote_camp = A.id

        GROUP BY hashes.key
        ORDER BY hashes.key) B JOIN "user" u
    ON u.roll_number::varchar(64) = B.key;

-- Count all distinct voters

SELECT COUNT(*) from votes where election_id = 2;

-- Code to count the votes

SELECT key, vote_camp_order, COUNT(*) FROM 
    (SELECT id from votecamp WHERE election_id = 2 AND has_cast=true) AS A JOIN hashes
        ON hashes.vote_camp = A.id

    GROUP BY hashes.key, hashes.vote_camp_order
    ORDER BY hashes.key, vote_camp_order;
