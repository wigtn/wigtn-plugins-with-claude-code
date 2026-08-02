Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-CURRENT/state-transition/implementation.py) to:

- Allow transitions only from `PENDING`.
- Support `approve`, `reject`, and `cancel`.
- Raise `ValueError` for terminal states and invalid actions.
- Preserve `transition(state, action)`.

Verification:

```text
Ran 3 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`