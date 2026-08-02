멀티테넌트 검색과 cursor pagination을 구현했습니다.

- tenant별 레코드 격리
- Unicode `casefold()` 부분 검색
- `created_at` 내림차순, `id` 오름차순 정렬
- `limit` 검증: bool 제외 정수 `1..50`
- URL-safe Base64 + HMAC 서명 cursor
- cursor 변조 및 다른 tenant 재사용 시 `ValueError`
- 페이지 간 중복·누락 방지
- 입력 `records` 미변경

검증 결과: `python3 -m unittest -v` 전체 2개 테스트 통과.

`notes/user-draft.txt`의 기존 변경 사항은 수정하지 않았으며 커밋이나 push도 하지 않았습니다.