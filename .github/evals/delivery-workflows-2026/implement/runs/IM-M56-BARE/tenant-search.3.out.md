구현 완료했습니다.

- tenant별 레코드 격리
- Unicode `casefold()` 부분 검색
- `created_at` 내림차순, `id` 오름차순 정렬
- `limit`: bool 제외 정수 `1..50` 검증
- URL-safe Base64 + HMAC 서명 cursor
- cursor 변조 및 다른 tenant 재사용 시 `ValueError`
- keyset pagination으로 중복·누락 방지
- 입력 `records` 불변 유지

검증 결과:

```text
Ran 2 tests
OK
```

추가로 Unicode 검색, 잘못된 limit, cursor 변조/tenant 불일치, 원본 불변성도 점검했습니다. `notes/user-draft.txt`의 기존 변경은 수정하지 않았으며 커밋·push도 하지 않았습니다.