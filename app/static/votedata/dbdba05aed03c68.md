# Audit of `token`

The given token proof is: `dbdba05aed03c68d7f303ac56993317a9e7c00f6a37637d3a57c63fd03f83b79`. This file contains information on how to audit this token. Through this auditing, you will be guaranteed that this token proof is a genuine representation of the original vote choices.
We used the SHA256 hashing algorithm. You can run it on Linux as `echo -n "<string>" | sha256sum`
We added nonces to the strings (before hashing them) to make it impossible to reverse-engineer the string to match the hash. Each nonce is a 16 byte random integer.
You can find more details about our cryptographic methodology on the page https://election.iiit.ac.in/security

The given token encodes 1 preferences

## Preference 1

The unique key of the candidate is: `2018`, and the nonce attached to it is: `e2dfe41b438a5d5c`. This yields the combined string: `2018,e2dfe41b438a5d5c`
The hash of the above combined string is: `71e17683daf6aa7b50405754246a7091e245dd3f2ce3f990955b8a2b82e74cf2`

## Combining all hashes

The combined string of all hashes is: `71e17683daf6aa7b50405754246a7091e245dd3f2ce3f990955b8a2b82e74cf2,8e38c62ccf43dd28`
Using the nonce: `8e38c62ccf43dd28`, the final string of all hashes obtained is: `71e17683daf6aa7b50405754246a7091e245dd3f2ce3f990955b8a2b82e74cf2,8e38c62ccf43dd28`

Hashing the above final string gives the final hash: `dbdba05aed03c68d7f303ac56993317a9e7c00f6a37637d3a57c63fd03f83b79`. This final hash is the same as the token proof that was assigned to you.

## Conclusion

We have successfully audited the internal representation of the given token proof.