Implemented v1/v2 config migration in [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/config-migration-1/config/migrate.py:44).

What changed:
- v1 `{endpoint, timeout_seconds}` migrates to `CanonicalConfig(endpoint, timeout_ms, enabled=True)`.
- v2 `{version: 2, delivery: {endpoint, timeout_ms, enabled}}` migrates to canonical form.
- Validates HTTPS endpoint, timeout range `100..30000ms`, bool timeout rejection, mapping type errors, unknown/mixed fields, and v2 delivery shape.
- Does not mutate the input mapping.

Verification:
- `python3 -m unittest -v` exited 0, all 3 public tests passed.
- Ran additional ad hoc migration checks for mixed fields, unknown fields, bool timeout, bounds, invalid types, and immutability; passed.

Notes:
- `notes/user-draft.txt` was already modified before my changes and was left untouched.
- No tests were edited. No commit/push or dependency install was performed.