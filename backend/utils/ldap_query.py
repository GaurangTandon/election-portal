import ldap
import re


def get_ldap_data(email):

    # Init connection with iiit's LDAP
    l = ldap.initialize("ldaps://ldap.iiit.ac.in")

    # Query database
    results = l.search_s(
        "ou=Users,dc=iiit,dc=ac,dc=in",
        ldap.SCOPE_SUBTREE,
        filterstr="(mail={})".format(email),
    )

    ret = {}  # Return dictionary

    # Handle errors here
    if len(results) != 1:
        raise ValueError("Unique match for given rollnumber not found in LDAP")

    else:
        res = results[0][1]
        # Add any other details if required to below dict
        required = {
            "name": "cn",
            "email": "mail",
            "rollno": "uidNumber",
            "gender": "gender",
        }
        for req in required:
            ret[req] = res[required[req]][0]
        # Retrieve programme and course specially from the other string
        infostr = results[0][0]
        batch_details = list(re.split("uid=|,ou=|,dc=", infostr)[2:4])
        ret["programme"] = batch_details[0]
        ret["batch"] = batch_details[1]

    purify = lambda b: b.decode() if isinstance(b, bytes) else b
    
    return {a: purify(b) for a, b in ret.items()}
