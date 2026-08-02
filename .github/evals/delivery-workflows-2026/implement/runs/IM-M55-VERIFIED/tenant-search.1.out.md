구현 완료했습니다.

변경 파일:
- [search/service.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/tenant-search-1/search/service.py:3): tenant 범위 필터, Unicode `casefold()` 부분 일치, `created_at desc/id asc` 정렬, limit 검증, cursor 기반 페이지 이동 구현
- [search/cursor.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/tenant-search-1/search/cursor.py:19): URL-safe opaque cursor 인코딩과 HMAC 서명 검증, tenant mismatch/변조 시 `ValueError`

검증:
- `python3 -m unittest -v` 통과: 2 tests OK
- 추가 로컬 체크 통과: Unicode casefold, bool limit 거부, tenant mismatch cursor 거부, cursor 변조 거부, records 불변성

참고:
- `notes/user-draft.txt`는 수정하지 않았습니다. 작업 전부터 modified 상태였습니다.
- 커밋/push/install/external access는 하지 않았습니다.