Updated [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-BARE/state-transition/implementation.py) to:

- Allow transitions only from `PENDING`.
- Raise `ValueError` for terminal/invalid states.
- Raise `ValueError` for unknown actions.
- Preserve `transition(state, action)`.

Verification:

```text
Ran 3 tests in 0.000s

OK
```

Command: `python3 -m unittest -v`