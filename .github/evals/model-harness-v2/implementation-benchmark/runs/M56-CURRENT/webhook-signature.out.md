Fixed [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/webhook-signature/implementation.py) to:

- Compute HMAC-SHA256 correctly.
- Use constant-time `hmac.compare_digest`.
- Return `False` for invalid signature types.
- Preserve `verify(secret, body, signature)`.

Verification:

```text
Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`