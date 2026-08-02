Updated `implementation.py` to:

- Use stable ID-based cursors, unaffected by inserted rows.
- Validate that `limit` is a positive integer.
- Reject cursors that no longer identify a row.
- Preserve `page(rows, cursor=None, limit=2)`.

Verification:

```text
Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`