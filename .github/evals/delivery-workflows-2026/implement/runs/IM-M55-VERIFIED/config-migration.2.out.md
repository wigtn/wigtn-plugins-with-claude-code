Implemented `migrate_config` in [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/config-migration-2/config/migrate.py:55).

What changed:
- Supports v1 `endpoint` + `timeout_seconds` to `CanonicalConfig(..., timeout_ms, enabled=True)`.
- Supports v2 `version=2` + `delivery.endpoint/timeout_ms/enabled`.
- Validates HTTPS endpoints, timeout range `100..30000ms`, bool timeout rejection, input mapping type, mixed v1/v2 fields, and unknown fields.
- Does not mutate the input mapping.

Verification:
- `python3 -m unittest -v` passed: 3 tests.
- Added inline focused checks for non-mutation, bounds, bool timeout, mixed fields, unknown top-level fields, and input type errors: passed.

Worktree note:
- Changed: `config/migrate.py`
- Pre-existing and untouched: `notes/user-draft.txt`
- No commit/push/dependency install/external access performed.