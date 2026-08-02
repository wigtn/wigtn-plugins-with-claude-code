Fixed [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/event-dedupe/implementation.py):

- Rejects empty event IDs with `ValueError`.
- Returns `False` for duplicate events.
- Adds and returns `True` for new events.
- Preserved the public signature and did not edit tests.

Verification:

```text
Ran 2 tests in 0.000s

OK
```