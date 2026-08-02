구현 완료했습니다: [config/migrate.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/config-migration-1/config/migrate.py)

- v1/v2를 `CanonicalConfig`로 변환
- HTTPS endpoint 및 timeout 범위 검증
- 혼합/알 수 없는 필드, bool timeout, 타입 오류를 `ValueError` 처리
- 입력 mapping 불변성 유지
- v1 `enabled=True` 기본 적용
- `notes/user-draft.txt` 및 테스트 미수정
- 커밋/push 없음

검증: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.