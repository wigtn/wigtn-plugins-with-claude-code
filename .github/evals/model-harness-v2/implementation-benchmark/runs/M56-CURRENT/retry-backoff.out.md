Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/retry-backoff/implementation.py) to:

- Cap exponential delays at `cap`.
- Raise `ValueError` for negative attempts or non-positive base/cap.
- Preserve the public signature.
- Leave tests unchanged.

Verification:

```text
$ python3 -m unittest -v
test_cap ... ok
test_invalid ... ok

Ran 2 tests in 0.000s
OK
```

Exit code: `0`.