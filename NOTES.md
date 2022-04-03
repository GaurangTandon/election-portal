# Implementation notes


This is where we discuss about the implementation of the whole page.

## Polling booth setup

The polling booth setup completes one main objective: students should be forced to come out of their rooms and cast their vote in a designated room noted as a "polling booth". This room is designated by the EC. The reason for this objective is to prevent vote coercion, wherein friends of a student force that student to vote for a particular candidate. (We assume that booth capturing does not happen in a small college.)

The current implementation uses client side IP address and browser fingerprint as a means to detect if machine that is attempting to cast a vote is a polling booth machine or not.

### Browser fingerprinting

We should attempt to emulate a trustless system as far as possible. Unfortunately, the browser fingerprinting approach is not completely trustless.

It is not a safe way to prevent unauthorized machines from accessing the election page. This is because, I can inspect the network request in the authorized machine to see what fingerprint value it is sending to the server, and then copy over that same fingerprint over to my unauthorized machine.

One way to improve this system towards a trustless setup is to have the server send a time-based unique code to the client. The resultant fingerprint is calculated using some combination of the real browser fingerprint and this unique code. This unique code can only be used once.