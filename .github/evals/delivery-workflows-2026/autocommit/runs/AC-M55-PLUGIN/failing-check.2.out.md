검증 실패로 커밋하지 않았습니다.

실행한 검사:

```bash
python3 -m unittest -v
```

결과: 실패

```text
FAIL: test_value (test_app.TestValue.test_value)
AssertionError: 2 != 1
```

현재 변경은 `app.py`만 남아 있으며, `value()`가 `1` 대신 `2`를 반환하도록 바뀐 상태입니다. 테스트 부산물 `__pycache__/`는 제거했습니다.