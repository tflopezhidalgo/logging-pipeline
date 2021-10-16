#!/bin/bash

_term() {
  echo "Caught SIGTERM signal!"
  kill -TERM "$child" 2>/dev/null
}

trap _term SIGTERM

python3 -m src.server.main &

child=$!
wait "$child"
