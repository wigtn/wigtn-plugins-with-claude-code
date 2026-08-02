멀티테넌트 검색과 cursor pagination을 구현했습니다.

- tenant별 레코드 격리
- Unicode `casefold()` 부분 검색
- `created_at DESC`, `id ASC` 정렬
- `limit` 정수 1~50 검증 및 `bool` 거부
- HMAC 서명된 URL-safe opaque cursor
- 변조 및 다른 tenant의 cursor 사용 시 `ValueError`
- keyset pagination으로 중복·누락 방지
- 입력 `records` 불변 유지

수정 파일:

- [search/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/tenant-search-1/search/service.py)
- [search/cursor.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/tenant-search-1/search/cursor.py)

검증 결과: `python3 -m unittest -v` — 2개 테스트 모두 통과했습니다. 추가 경계 조건 검사도 통과했습니다.

`notes/user-draft.txt`는 기존 변경 상태 그대로 두었으며, 커밋이나 push는 하지 않았습니다.