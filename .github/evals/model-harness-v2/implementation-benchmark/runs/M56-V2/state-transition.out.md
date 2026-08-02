Fixed [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-V2/state-transition/implementation.py):

- Allows transitions only from `PENDING`.
- Maps `approve`, `reject`, and `cancel`.
- Raises `ValueError` for terminal states and unknown actions.
- Preserved `transition(state, action)` signature.
- Tests unchanged.

Verification:

```text
Ran 3 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`