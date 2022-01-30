# syntax=docker/dockerfile:1

FROM python:3-alpine

WORKDIR /app

RUN pip3 install lnetatmo
RUN pip3 install influxdb_client

RUN echo '*/5 * * * * /usr/local/bin/python /app/netatmo_influxdb.py' > /etc/crontabs/root

COPY netatmo_influxdb.py netatmo_influxdb.py

ENTRYPOINT [ "crond", "-l", "2", "-f" ]
