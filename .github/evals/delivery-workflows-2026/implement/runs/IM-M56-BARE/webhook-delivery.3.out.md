웹훅 기능을 구현했습니다.

- `verify_signature`: 엄격한 `sha256=<64자리 hex>` 검증 및 `hmac.compare_digest` 사용
- `WebhookStore.accept`: 중복 감지 및 payload 충돌 시 `ValueError`
- `retry_delay`: 2xx 처리와 `0/60/300초` 재시도 정책 적용
- 표준 라이브러리만 사용
- 기존 `notes/user-draft.txt` 변경 내용 보존
- 커밋·push 없음

수정 파일:

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-3/webhook/signing.py)
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-3/webhook/delivery.py)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.