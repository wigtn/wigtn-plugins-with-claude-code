검사 실패로 커밋하지 않았습니다.

- 실행: `python3 -m unittest -v`
- 실패: `test_app.TestValue.test_value`
- 원인: 예상값 `1`, 실제값 `2`
- `app.py` 변경은 그대로 유지되어 있습니다.
- 테스트가 생성한 `__pycache__`만 정리했습니다.