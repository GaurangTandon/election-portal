# election-portal
minimalistic election portal for universities

**Status:** Work in Progress, expected launch date: 10th September

## Installation

Setup a virtual environment, then run `pip install -r requirements.txt`. If you face issues related to `pg_config` executable not found, follow this [SO link](https://stackoverflow.com/questions/11618898). If you face issues related to `python-ldap`, follow this [SO link](https://stackoverflow.com/questions/4768446).

To setup the postgres database, you'll need to setup a postgres user following the instructions here (https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e) \[scroll to bottom for psql exclusive instructions\]. Note that creating a password less user is easier to test with. If you want to use a password-enabled user, follow the URI as given [here](https://stackoverflow.com/a/42371542/2181238) 

Then we create the `.env` file. First, do `cp .env.template .env`, then edit `.env` with correct values.

## Setup

Command to create the docker volume: `docker volume create -o device=/root/election-portal/app/static -o type=bind -o o=bind election_static`
