검사 실패로 커밋하지 않았습니다.

- 실행: `python3 -m unittest -v`
- 실패: `test_value`
- 원인: 테스트 기대값은 `1`이지만 `app.py`가 `2`를 반환
- 상태: `app.py` 변경은 그대로 유지
- 테스트 중 생성된 `__pycache__/`는 정리 완료