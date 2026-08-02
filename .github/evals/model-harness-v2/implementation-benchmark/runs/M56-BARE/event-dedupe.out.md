Fixed [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-BARE/event-dedupe/implementation.py) to:

- Reject empty event IDs with `ValueError`.
- Return `False` for duplicates without modifying `seen`.
- Accept and record new event IDs.

Verification:

```text
Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`