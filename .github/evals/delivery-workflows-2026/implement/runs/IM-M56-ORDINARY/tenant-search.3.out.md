멀티테넌트 검색과 cursor pagination을 구현했습니다.

- tenant별 레코드 격리
- Unicode `casefold()` 부분 검색
- `created_at DESC`, `id ASC` 정렬
- `limit` 정수형 1..50 검증 (`bool` 제외)
- HMAC 서명된 URL-safe opaque cursor
- cursor 변조 및 다른 tenant 사용 시 `ValueError`
- keyset pagination으로 중복·누락 방지
- 입력 `records` 불변 유지

검증 결과:

- `python3 -m unittest -v`: 2개 테스트 모두 통과
- Unicode, 다중 페이지 경계, 변조, tenant 불일치, 잘못된 limit 추가 검증 통과
- 테스트 및 `notes/user-draft.txt` 수정 없음
- 커밋/push 없음