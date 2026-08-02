구현 완료했습니다. 커밋/push/의존성 설치/외부 접속은 하지 않았습니다.

변경 파일:
- [webhook/signing.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-2/webhook/signing.py:5): `sha256=<hex>` 형식 검증, malformed header `False`, HMAC-SHA256 계산, `hmac.compare_digest` constant-time 비교.
- [webhook/delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-2/webhook/delivery.py:5): 최초 이벤트 저장, 동일 ID+payload 중복 `False`, 동일 ID 다른 payload `ValueError`.
- [webhook/delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-2/webhook/delivery.py:15): retry delay 정책 구현. `attempt < 1`은 `ValueError`, 2xx는 `None`, 실패 attempt 1/2/3은 `0/60/300`, 이후 `None`.

검증:
- `python3 -m unittest -v` 실행: 3 tests OK
- 추가 스니펫으로 malformed signature, payload conflict, retry 경계값 확인: `supplemental checks passed`

`notes/user-draft.txt`는 수정하지 않았습니다. 작업 전후 해시가 동일했습니다:
`2e6bf3de2c8584b9037e30287e3b0f6e00ac65b004c7ae0ec7ef6abf3e2a3083`

현재 `git status --short`에는 기존의 `notes/user-draft.txt` 수정 상태와 이번 변경 파일 2개만 남아 있습니다.