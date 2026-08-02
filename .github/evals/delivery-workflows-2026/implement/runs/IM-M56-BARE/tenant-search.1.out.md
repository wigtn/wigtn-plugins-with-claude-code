구현을 완료했습니다.

- 테넌트 격리 및 Unicode `casefold` 부분 검색
- `created_at` 내림차순, `id` 오름차순 정렬
- `limit` 정수 `1..50` 검증 및 `bool` 거부
- URL-safe Base64 + HMAC 서명 커서
- 커서 변조 및 다른 테넌트 사용 시 `ValueError`
- 정렬 키 기반 pagination으로 중복·누락 방지
- 입력 `records` 불변 유지

변경 파일:

- [search/service.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/tenant-search-1/search/service.py:4)
- [search/cursor.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/tenant-search-1/search/cursor.py:29)

검증 결과: `python3 -m unittest -v` — 2개 테스트 모두 통과했습니다. 추가 경계 조건 검사도 통과했습니다.

기존에 변경돼 있던 `notes/user-draft.txt`는 수정하지 않았으며 커밋이나 push도 하지 않았습니다.