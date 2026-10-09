# Erigon BranchCache reorg repro

Reproduces an Erigon `main` bug where, after an unwind, the commitment trie warmup caches branches of the unwound fork in `BranchCache`, and a valid block is rejected with `wrong trie root`.

```
./repro.sh /path/to/erigon
```

`repro.sh` runs `erigon init` on `genesis.json`, starts the node with `--externalcl`, and `replay.py` (Python stdlib) replays the 16,876 recorded Engine API calls in `scenario.jsonl.gz`. The last call is `engine_newPayloadV4` for block 1 `0xd964d8b6db25f953e0bbc20d715ca82d0aa634566eb93686a7805fa88c4e7d3c`, which must be VALID.

The scenario is 4,714 tests of EEST `tests@v21.0.0` `blockchain_tests_engine_x`, pre-alloc group `0x234bacfeb83d6b61` (Prague), on one node, with `engine_forkchoiceUpdated` back to genesis before each test.

Needs `python3`, `curl` and `openssl`. Takes about 6 minutes.
