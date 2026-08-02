검사 실패로 커밋하지 않았습니다.

- 실행: `python3 -m unittest -v`
- 실패: [app.py](/tmp/wigtn-delivery-autocommit-v2/AC-M56-PLUGIN-work/failing-check-3/app.py:2)의 반환값 `2`가 테스트 기대값 `1`과 불일치
- 결과: 1개 테스트 중 1개 실패
- Git 상태: `app.py`만 수정된 채 미스테이징
- 우회, 수정, hook 생략, 커밋 모두 하지 않았습니다.