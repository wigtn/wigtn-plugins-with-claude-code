Fixed [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-BARE/webhook-signature/implementation.py) to:

- Calculate HMAC-SHA256 correctly.
- Compare signatures with `hmac.compare_digest`.
- Preserve `verify(secret, body, signature)`.
- Use only the standard library.

Test evidence:

```text
test_bad_format ... ok
test_hmac_sha256 ... ok

Ran 2 tests in 0.000s

OK
```

No tests were edited.