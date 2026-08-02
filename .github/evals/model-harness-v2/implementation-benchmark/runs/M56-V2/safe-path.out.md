Fixed [implementation.py](/private/tmp/wigtn-implementation-bench-v1/work/M56-V2/safe-path/implementation.py) while preserving `safe_join(root, user_path)`.

It now rejects:

- Absolute paths
- `..` traversal outside the root
- Existing symlinks pointing outside the root

Verification:

```text
test_escape ... ok
test_inside ... ok

Ran 2 tests in 0.001s
OK
```

Additional traversal and symlink edge checks also passed. Tests were not edited.