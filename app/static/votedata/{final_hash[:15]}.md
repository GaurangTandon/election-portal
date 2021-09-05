# Audit of `token`

The given token proof is: `c9d2fe881087d62861d1c5fd1551ae67254add55dbc89b6659eeaa7d114285b5`. This file contains information on how to audit this token. Through this auditing, you will be guaranteed that this token proof is a genuine representation of the original vote choices.
We used the SHA256 hashing algorithm. You can run it on Linux as `echo -n "<string>" | sha256sum`
We added nonces to the strings (before hashing them) to make it impossible to reverse-engineer the string to match the hash. Each nonce is a 16 byte random integer.
You can find more details about our cryptographic methodology on the page https://election.iiit.ac.in/security

The given token encodes 3 preferences

## Preference 1

The unique key of the candidate is: `3`, and the nonce attached to it is: `8b0e35aa9ab8af35`. This yields the combined string: `3,8b0e35aa9ab8af35`
The hash of the above combined string is: `1ae4954be3ef06f6cdbbdcb1ca34ae3d18318c93670e82dc2aa57b6ffe36b613`

## Preference 2

The unique key of the candidate is: `4`, and the nonce attached to it is: `e9346cb44ea94910`. This yields the combined string: `4,e9346cb44ea94910`
The hash of the above combined string is: `e1b9b81c651f8c85c1299dbdd9dabe3193a07b4495887c5a3377727d10ed87cc`

## Preference 3

The unique key of the candidate is: `5`, and the nonce attached to it is: `c0e0c16dd292dde9`. This yields the combined string: `5,c0e0c16dd292dde9`
The hash of the above combined string is: `f247821c7e420d83e4c91ad07ea1f3c8e2bf12759ce178e56a341d5e76ce0869`

## Combining all hashes

The combined string of all hashes is: `1ae4954be3ef06f6cdbbdcb1ca34ae3d18318c93670e82dc2aa57b6ffe36b613e1b9b81c651f8c85c1299dbdd9dabe3193a07b4495887c5a3377727d10ed87ccf247821c7e420d83e4c91ad07ea1f3c8e2bf12759ce178e56a341d5e76ce0869,f4de88d3426b27a9`
Using the nonce: `f4de88d3426b27a9`, the final string of all hashes obtained is: `1ae4954be3ef06f6cdbbdcb1ca34ae3d18318c93670e82dc2aa57b6ffe36b613e1b9b81c651f8c85c1299dbdd9dabe3193a07b4495887c5a3377727d10ed87ccf247821c7e420d83e4c91ad07ea1f3c8e2bf12759ce178e56a341d5e76ce0869,f4de88d3426b27a9`
Hashing the above final string gives the final hash: `c9d2fe881087d62861d1c5fd1551ae67254add55dbc89b6659eeaa7d114285b5`. This final hash is the same as the token proof that was assigned to you.

## Conclusion

We have successfully audited the internal representation of the given token proof.