Fixed [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/date-range/implementation.py):

- Counts both endpoints with `+ 1`.
- Raises `ValueError` for reversed ranges.
- Preserved `inclusive_days(start, end)` signature.
- Tests were not edited.

Verification:

```text
Ran 2 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`