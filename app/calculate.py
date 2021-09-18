"""
This script takes as input all the votes that were recorded
And generates the hash value for them
In theory, this hash value should match the one you were given when voting.
If it does not match, it means the vote values have been modified in the database
or there is an error in this script (latter is more likely)
"""

from collections import defaultdict
from hashlib import sha256
import sys

votes = defaultdict(list)
last_nonces = {}
c = 50
i = 0

# the exported data csv is passed here
# the query to generated the exported data dump is given here
# https://github.com/GaurangTandon/election-portal/blob/master/sqlcommands.sql#L57
with open(sys.argv[1], encoding="utf-8-sig") as f:
    for line in f:
        i += 1
        # if i > c:
        #     break
        vc, order, key, nonce, cnonce, _, hash_str = line.strip().replace('"', '').split(",")
        # avoid empty string key, for example, when empty vote
        votes[vc].append((key, nonce))
        assign = (cnonce, hash_str)
        if vc in last_nonces:
            assert last_nonces[vc] == assign
        else:
            last_nonces[vc] = assign

# print(votes)
# print(last_nonces)
tokens = []
for key, values in votes.items():
    s = ""
    for k, n in values:
        if k:
            s += sha256((k + "," + n).encode()).hexdigest()
    cn, hash_str = last_nonces[key]
    final_str = s + "," + cn
    hash_str += "," + cn
    assert final_str == hash_str
    tokens.append(sha256(final_str.encode()).hexdigest())

print("\n".join(tokens))
