Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-V2/pagination/implementation.py) to:

- Use stable row IDs as cursors instead of offsets.
- Reject non-positive or invalid limits with `ValueError`.
- Preserve the public function signature.
- Use only the Python standard library.

Test evidence:

```text
test_limit ... ok
test_stable_id_cursor ... ok

Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`  
Exit code: `0`