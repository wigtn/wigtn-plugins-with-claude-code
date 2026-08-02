구현을 완료했습니다: [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/config-migration-3/config/migrate.py)

- v1/v2를 `CanonicalConfig`로 변환
- HTTPS endpoint 및 100~30000ms 범위 검증
- 혼합/알 수 없는 필드, bool timeout, 타입 오류를 `ValueError`로 처리
- v1 `enabled=True` 기본값 적용
- 입력 mapping 불변성 유지
- `notes/user-draft.txt`는 수정하지 않았으며 커밋/push하지 않음

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.