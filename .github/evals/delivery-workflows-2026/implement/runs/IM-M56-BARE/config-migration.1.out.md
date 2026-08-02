구현 완료했습니다.

- v1/v2 설정을 `CanonicalConfig`로 변환
- HTTPS endpoint 검증
- timeout 범위 `100..30000ms` 및 bool/type 검증
- 혼합 스키마, 누락·알 수 없는 필드 검증
- 입력 mapping 불변 유지
- v1 `enabled=True` 기본값 적용

변경 파일: [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/config-migration-1/config/migrate.py:1)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.

`notes/user-draft.txt`의 기존 변경사항은 수정하지 않았으며 커밋·push도 하지 않았습니다.