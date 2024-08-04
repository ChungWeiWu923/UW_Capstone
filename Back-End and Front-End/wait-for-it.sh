#!/bin/bash
# wait-for-it.sh

set -e

HOST="$1"
PORT="$2"
TIMEOUT="${3:-30}"
DELAY="${4:-2}"

if [ "$HOST" == "" ] || [ "$PORT" == "" ]; then
  echo "Usage: $0 host port [timeout] [delay]"
  exit 1
fi

echo "Waiting for $HOST:$PORT to be available..."

start_time=$(date +%s)

while ! nc -z $HOST $PORT >/dev/null 2>&1; do
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    if [ $elapsed_time -ge $TIMEOUT ]; then
        echo "Operation timed out after $TIMEOUT seconds"
        exit 1
    fi

    echo "Waiting for $HOST:$PORT... retrying in $DELAY seconds."
    sleep $DELAY
done

echo "$HOST:$PORT is available."

shift 4
exec "$@"
