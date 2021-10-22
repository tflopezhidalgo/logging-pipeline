#!/bin/bash

_term() {
  echo "Caught SIGTERM signal!"
  kill -TERM "$child" 2>/dev/null
}

trap _term SIGTERM

# Make sure /logs exists
mkdir -p /logs

python3 -m src.server.main &

child=$!
wait "$child"
