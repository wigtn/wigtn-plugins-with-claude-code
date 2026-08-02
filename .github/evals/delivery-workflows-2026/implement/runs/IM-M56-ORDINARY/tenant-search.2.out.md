멀티테넌트 검색과 cursor pagination을 구현했습니다.

- tenant별 레코드 격리
- Unicode `casefold()` 부분 검색
- `created_at DESC`, `id ASC` 정렬
- `limit` 정수 검증 (`bool` 제외, 1~50)
- HMAC 서명 URL-safe opaque cursor
- 커서 변조 및 다른 tenant 재사용 시 `ValueError`
- keyset pagination으로 중복·누락 방지
- 입력 `records` 불변 유지

변경 파일:

- [service.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/tenant-search-2/search/service.py)
- [cursor.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/tenant-search-2/search/cursor.py)

검증 결과: `python3 -m unittest -v` — 2개 테스트 모두 통과했습니다. 추가 경계 조건 검사도 통과했습니다.

`notes/user-draft.txt`의 기존 변경은 보존했으며 커밋/push하지 않았습니다.