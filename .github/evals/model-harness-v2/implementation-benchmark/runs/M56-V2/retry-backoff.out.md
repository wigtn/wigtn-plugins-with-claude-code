Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-V2/retry-backoff/implementation.py) to:

- Apply the configured delay cap.
- Validate negative attempts and non-positive `base`/`cap`.
- Preserve `retry_delays(attempts, base=1, cap=30)`.

Verification:

```text
test_cap ... ok
test_invalid ... ok

Ran 2 tests in 0.000s
OK
```