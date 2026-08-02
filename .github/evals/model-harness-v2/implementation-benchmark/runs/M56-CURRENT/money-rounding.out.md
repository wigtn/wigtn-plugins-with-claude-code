Fixed [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/money-rounding/implementation.py:5) using exact largest-remainder allocation with deterministic tie-breaking and input validation.

Verification:

```text
test_invalid ... ok
test_sum_and_deterministic_remainder ... ok

Ran 2 tests in 0.000s
OK
```

Additional allocation invariants across multiple totals and weight sets also passed.