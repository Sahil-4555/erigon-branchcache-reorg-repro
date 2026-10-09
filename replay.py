#!/usr/bin/env python3
"""Replay a recorded Engine API scenario against a node and report the final block's status.

The recording holds every engine_newPayload / engine_forkchoiceUpdated call (with the answer Erigon main gave) from
running 4,714 EEST v21 blockchain_tests_engine_x tests of pre-alloc group 0x234bacfeb83d6b61 (Prague) on one node,
with a forkchoiceUpdated back to genesis before each test. The last call is the newPayload that must be VALID.

usage: replay.py <scenario.jsonl[.gz]> <authrpc url> <jwt secret file>
Python 3 standard library only.
"""
import base64, gzip, hashlib, hmac, json, sys, time, urllib.request


def jwt(secret):
    enc = lambda b: base64.urlsafe_b64encode(b).rstrip(b"=")
    head, body = enc(b'{"alg":"HS256","typ":"JWT"}'), enc(json.dumps({"iat": int(time.time())}).encode())
    return (head + b"." + body + b"." + enc(hmac.new(secret, head + b"." + body, hashlib.sha256).digest())).decode()


def main():
    path, url, secret_file = sys.argv[1:4]
    secret = bytes.fromhex(open(secret_file).read().strip().removeprefix("0x"))
    opener = gzip.open if path.endswith(".gz") else open
    calls = [c for c in map(json.loads, opener(path, "rt")) if "method" in c]
    differ = 0
    for i, c in enumerate(calls):
        body = json.dumps({"jsonrpc": "2.0", "id": i, "method": c["method"], "params": c["params"]}).encode()
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json",
                                                              "Authorization": "Bearer " + jwt(secret)})
        resp = json.load(urllib.request.urlopen(req, timeout=120))
        got = resp.get("result") or {"error": resp.get("error")}
        status = (got.get("payloadStatus") or got).get("status")
        recorded = c["result"][1] if c["result"][0] == "ok" else {}
        want = (recorded.get("payloadStatus") or recorded).get("status") if isinstance(recorded, dict) else None
        # A busy node may answer SYNCING and be asked again; that is timing, not a different verdict.
        if i < len(calls) - 1 and status != want and "SYNCING" not in (status, want):
            differ += 1
            print(f"call {i} {c['method']}: got {status}, recording has {want}")
        if (i + 1) % 2000 == 0:
            print(f"{i + 1}/{len(calls)} calls", flush=True)
    last = calls[-1]["params"][0]
    print(f"\n{differ} earlier calls differ from the recording")
    print(f"final {calls[-1]['method']} block {int(last['blockNumber'], 16)} {last['blockHash']}: {json.dumps(got)}")
    print("expected: VALID (EEST fixture; geth, Nethermind and reth return VALID)")


if __name__ == "__main__":
    main()
