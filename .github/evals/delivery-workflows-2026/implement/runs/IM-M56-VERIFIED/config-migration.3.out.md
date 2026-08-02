v1/v2 배달 설정을 `CanonicalConfig`로 변환하는 기능을 구현했습니다.

- [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/config-migration-3/config/migrate.py:34): v1/v2 스키마 판별 및 변환
- [입력 검증](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/config-migration-3/config/migrate.py:12): HTTPS URL, 100–30000ms 범위, bool·타입 오류 검증
- 혼합 필드와 알 수 없는 필드 거부
- v1 `enabled=True` 기본 적용
- 입력 mapping을 변경하지 않음

검증 결과:

- `python3 -m unittest -v` — 3개 테스트 모두 통과
- 추가 검증 — 유효 4개 및 오류 15개 사례 통과
- `git diff --check` — 통과

`notes/user-draft.txt`의 기존 변경은 건드리지 않았으며, 커밋·푸시·외부 접근·의존성 설치도 하지 않았습니다.