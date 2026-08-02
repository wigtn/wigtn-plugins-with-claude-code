구현 완료했습니다. 커밋/푸시/의존성 설치/외부 서비스 접근은 하지 않았고, `notes/user-draft.txt`는 수정하지 않았습니다. 작업 전부터 해당 파일은 modified 상태였습니다.

변경 파일:
- [webhook/signing.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-3/webhook/signing.py:5): `sha256=<hex>` HMAC-SHA256 검증, malformed header `False`, `hmac.compare_digest` 사용
- [webhook/delivery.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-3/webhook/delivery.py:5): 최초 이벤트 저장, 동일 ID+payload 중복 `False`, 동일 ID 다른 payload `ValueError`
- [webhook/delivery.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/webhook-delivery-3/webhook/delivery.py:14): retry delay 정책 구현

검증:
- `python3 -m unittest -v` 통과: 3 tests OK
- 추가 로컬 assertions로 malformed signature, payload conflict, retry attempt 경계조건 확인 완료

현재 git 상태는 `notes/user-draft.txt`, `webhook/delivery.py`, `webhook/signing.py`가 modified입니다.