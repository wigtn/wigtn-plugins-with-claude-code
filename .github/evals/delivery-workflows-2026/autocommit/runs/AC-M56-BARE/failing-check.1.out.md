검사가 실패하여 커밋하지 않았습니다.

- 실행: `python3 -m unittest -v`
- 실패: `test_app.TestValue.test_value`
- 원인: 기대값은 `1`이지만 `app.py`가 `2`를 반환함
- 변경은 우회하거나 수정하지 않았으며 작업 트리에 그대로 남아 있습니다.