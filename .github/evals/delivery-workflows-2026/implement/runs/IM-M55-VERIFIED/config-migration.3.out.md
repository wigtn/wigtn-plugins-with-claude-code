구현 완료했습니다. 변경은 [config/migrate.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/config-migration-3/config/migrate.py:15)에만 했고, `notes/user-draft.txt`는 수정하지 않았습니다. 해당 파일은 작업 전부터 modified 상태였습니다.

반영 내용:
- v1 `{endpoint, timeout_seconds}`를 `CanonicalConfig(endpoint, timeout_ms, enabled=True)`로 변환
- v2 `{version: 2, delivery: {endpoint, timeout_ms, enabled}}` 변환
- `https` endpoint 검증
- timeout `100..30000ms` 검증
- mixed v1/v2 필드, 알 수 없는 최상위 필드, 입력 타입 오류, bool timeout을 `ValueError` 처리
- 입력 mapping 비변경 유지

검증:
- `python3 -m unittest -v` 통과: 3 tests OK
- 추가 focused checks 통과: mixed fields, unknown fields, bool timeout, input type error, mapping immutability, v1 enabled 기본값

커밋/push/외부 서비스 접근은 하지 않았습니다.