Updated [implementation.py](/tmp/wigtn-implementation-bench-v1/work/M56-V2/authorization/implementation.py:1) to:

- Enforce matching organization/tenant first.
- Allow same-organization admins.
- Allow same-organization document owners.
- Fail closed for missing organization or user identity.

Verification:

```text
$ python3 -m unittest -v
test_owner_same_org ... ok
test_tenant_boundary ... ok

Ran 2 tests in 0.000s

OK
```

Tests were not modified.