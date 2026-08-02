Implemented webhook signing, dedupe storage, and retry delay behavior.

Changed files:
- [webhook/signing.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-1/webhook/signing.py:1): HMAC-SHA256 `sha256=<hex>` verification, malformed headers return `False`, constant-time digest comparison.
- [webhook/delivery.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-1/webhook/delivery.py:1): first-event accept, duplicate same payload returns `False`, conflicting payload raises `ValueError`, retry schedule implemented.

Verification:
- `python3 -m unittest -v` passed: 3 tests OK.
- Additional local smoke check passed for malformed signatures, uppercase hex, duplicate/conflicting payloads, retry edge cases, and byte input preservation.

I did not edit tests or `notes/user-draft.txt`. That file already had a pre-existing modification and remains preserved. No commit, push, dependency install, or external service access was performed.