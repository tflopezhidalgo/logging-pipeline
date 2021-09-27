FROM python:3.9.7-slim

RUN mkdir -p /client

ADD . /client

WORKDIR /client

ENTRYPOINT ["./entrypoint.sh"]
