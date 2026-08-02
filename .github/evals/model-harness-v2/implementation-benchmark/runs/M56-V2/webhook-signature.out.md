Fixed [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-V2/webhook-signature/implementation.py:1) to:

- Compute HMAC-SHA256 correctly.
- Use constant-time `hmac.compare_digest`.
- Return `False` for malformed signatures.
- Use only the Python standard library.

Verification:

```text
Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`  
Tests were not modified.