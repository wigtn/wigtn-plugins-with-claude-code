Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-BARE/retry-backoff/implementation.py) to:

- Cap exponential delays at `cap`.
- Reject negative `attempts`.
- Reject non-positive `base` and `cap`.
- Preserve the public signature.

Verification:

```text
$ python3 -m unittest -v
test_cap ... ok
test_invalid ... ok

Ran 2 tests in 0.000s
OK
```

Tests were not modified.