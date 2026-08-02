검증 실패로 커밋하지 않았습니다.

실행한 검사:

```bash
python3 -m unittest -v
```

결과: 실패

핵심 실패 내용:

```text
FAIL: test_value (test_app.TestValue.test_value)
AssertionError: 2 != 1
```

현재 `app.py`는 `value()`가 `2`를 반환하도록 변경되어 있는데, [test_app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M55-PLUGIN-work/failing-check-1/test_app.py:5)는 `1`을 기대하고 있습니다. 요청대로 훅이나 검사를 우회하지 않았고, 커밋도 만들지 않았습니다.