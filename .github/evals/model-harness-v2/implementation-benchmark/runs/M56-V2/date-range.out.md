Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-V2/date-range/implementation.py:4):

- Counts both endpoints with `+ 1`.
- Raises `ValueError` for reversed ranges.
- Preserves `inclusive_days(start, end)` signature.
- Tests unchanged.

Verification:

```text
Ran 2 tests in 0.000s

OK
```