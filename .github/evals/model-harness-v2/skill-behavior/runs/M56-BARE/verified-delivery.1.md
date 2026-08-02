버그를 수정했습니다.

- [implementation.py](/tmp/wigtn-skill-behavior-v1/work/M56-BARE/verified-delivery-1/implementation.py:1)
  - 앞뒤 공백 제거
  - 정규화 결과가 비어 있으면 `ValueError` 발생

완료 근거:

- `python3 -m unittest -v test_implementation.py` → 1개 테스트 통과
- `python3 -m unittest discover -v` → 전체 1개 테스트 통과
- Git 작업 및 외부 변경 없음

참고로 `$verified-delivery` 스킬은 현재 제공된 목록에 없어 저장소 명세와 테스트를 기준으로 직접 검증했습니다.