#!/usr/bin/env bash
# Reproduce: fresh Erigon on the scenario genesis, then replay the recorded Engine API calls.
# usage: repro.sh <path to erigon binary>
set -euo pipefail
ERIGON=$1
cd "$(dirname "$0")"
W=$(mktemp -d)
openssl rand -hex 32 > "$W/jwt.hex"
"$ERIGON" init --datadir "$W/data" genesis.json > "$W/init.log" 2>&1
"$ERIGON" --datadir "$W/data" --networkid 1 --externalcl --authrpc.jwtsecret "$W/jwt.hex" --authrpc.port 8651 \
	--nodiscover --no-downloader --nat none --port 30391 --torrent.port 42191 --private.api.addr 127.0.0.1:19191 \
	--http=false > "$W/erigon.log" 2>&1 &
PID=$!
trap 'kill $PID 2>/dev/null; wait $PID 2>/dev/null; rm -rf "$W"' EXIT
until curl -s -o /dev/null http://127.0.0.1:8651; do sleep 1; done
python3 replay.py scenario.jsonl.gz http://127.0.0.1:8651 "$W/jwt.hex"
