FROM python:3.8-slim

WORKDIR /opt

# Server time must be India timezone
# as elections have to start and end at correct times
ENV TZ=Asia/Kolkata
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Prevents Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Prevents Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED 1

RUN apt update && \
    # pg_config is required to build psycopg2 from source
    # which is required for interfacing with a postgresdb 
    apt install -y libpq-dev && \
    # for python ldap
    apt install -y libsasl2-dev python3-dev libldap2-dev libssl-dev && \
    apt install -y gcc && \
    rm -rf /var/lib/apt/lists

COPY requirements.txt /opt
RUN pip install --no-cache-dir -r /opt/requirements.txt

COPY . /opt

ENV PYTHONPATH /opt

CMD ["gunicorn", "--threads", "24", "-b", "0.0.0.0:5000", "app.app:app"]
