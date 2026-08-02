검사 실패로 커밋하지 않았습니다.

- 실행: `python3 -m unittest -v`
- 결과: 1개 테스트 실패
- 원인: [app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M56-PLUGIN-work/failing-check-2/app.py:2)는 `2`를 반환하지만 [test_app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M56-PLUGIN-work/failing-check-2/test_app.py:5)는 `1`을 기대합니다.
- 스테이징된 파일 없음
- HEAD 유지: `a4bb9f6`
- 검사 중 생성된 `__pycache__/`는 제거했습니다.

테스트나 훅을 우회하지 않았고, `app.py` 변경도 그대로 보존했습니다.