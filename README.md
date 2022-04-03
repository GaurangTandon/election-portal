# election-portal
minimalistic election portal for universities

**Status:** Stable release on master

## Installation

Setup a virtual environment, then run `pip install -r requirements.txt`. If you face issues related to `pg_config` executable not found, follow this [SO link](https://stackoverflow.com/questions/11618898). If you face issues related to `python-ldap`, follow this [SO link](https://stackoverflow.com/questions/4768446).

To setup the postgres database, you'll need to setup a postgres user following the instructions here (https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e) \[scroll to bottom for psql exclusive instructions\]. Note that creating a password less user is easier to test with. If you want to use a password-enabled user, follow the URI as given [here](https://stackoverflow.com/a/42371542/2181238). The name of the user and database is given in the docker-compose yaml file.

Then we create the `.env` file. First, do `cp .env.template .env`, then edit `.env` with correct values.

## Setup

Command to create the docker volume: `docker volume create -o device=/root/election-portal/app/static -o type=bind -o o=bind election_static`. If you're debugging locally (not on root server), you should use `device=$PWD/data`.

Create a file `docker-compose.override.yaml` with these contents. The `SECRET_KEY` is used to create authentication tokens, so it is important to override it in production. In debug mode, the `REDIRECT_HOST` ensures that CAS will redirect you to localhost instead of election.iiit.ac.in. 

```yaml
services:
    app:
        environment:
            REDIRECT_HOST: http://127.0.0.1:5000
            SECRET_KEY: top_secret_key
```

### Polling booth setup

For a polling booth setup, you would intend to restrict the "cast vote" endpoint to a select group of devices. The devices are uniquely identifier using their IP address and their client browser fingerprints. You can specify these values in a comma-separated list as in the docker compose override yaml file:

```yaml
services:
    app:
        environment:
            RESTRICTED_FINGERPINTS: <fingerprintvalues>
            RESTRICTED_IP_ADDRS: 172.18.0.1
```

Note: The [browser fingerprints](https://www.npmjs.com/package/@fingerprintjs/fingerprintjs) are **not** always unique fingerprints across different client devices. It is advisable to have a unique configuration of browser, window size, resolution, etc. that is different from stock default values.

## Backups and Restore

Backups are taken and rotated regularly. All backups are mounted at `/var/opt/pgbackups` (mounted in `docker-compose.yaml`) in the host machine. The setup for backups is given in the [linked docker hub image frontpage](https://hub.docker.com/r/prodrigestivill/postgres-backup-local). The `chown` command should be run in the host machine.

### Restore locally

You first need to drop existing tables. Steps are:
 
- `docker exec -it <container> bash` to land into the postgres container.
- You'll land in the container as `root`. Switch to postgres user via `su postgres`.
- Then launch `psql` using correcct username and dbname, for example, `psql --user=sqluser --dbname=election`
- drop all tables in the existing database, for that, refer to [this SO answer](https://stackoverflow.com/a/3327326/2181238)

Once this is done run the command given on that docker hub frontpage. Note that:

- You'll probably find the file to `zcat` in `/var/opt/pgbackups/daily`
- `docker exec` needs to be done into the `postgres` container and not the `pgbackups` container

Once this is done the database should successfully restore.

### User management

If you want to create a new user with read only roles, 

- Run `createuser --interactive` in the postgres shell (`su postgres`)
- Enter the psql shell with the superuser user (`su postgres` and then `psql --user=sqluser --dbname=election`).
- `alter user <username> with password 'password';` is the next command
- `grant connect on database election to <username>;` and `grant select on all tables in schema public to <username>;` will set the correct permissions
