FROM python:3.9.7-slim

RUN mkdir -p /server

ADD . /server

WORKDIR /server

ENTRYPOINT ["./entrypoint.sh"]
