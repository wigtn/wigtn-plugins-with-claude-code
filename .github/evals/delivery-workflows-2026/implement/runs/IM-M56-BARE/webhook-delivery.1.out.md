웹훅 기능을 구현했습니다.

- `verify_signature`: 엄격한 `sha256=<64자리 hex>` 검증 및 constant-time 비교
- `WebhookStore.accept`: 최초 저장, 동일 payload 중복 거부, 다른 payload는 `ValueError`
- `retry_delay`: 2xx 및 재시도 횟수별 정책 적용
- 입력 bytes 원본 유지, 표준 라이브러리만 사용
- `notes/user-draft.txt`와 테스트 파일 보존
- 커밋·push 없음

수정 파일:

- [webhook/signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-1/webhook/signing.py)
- [webhook/delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-1/webhook/delivery.py)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. 추가 경계 조건 검사와 `git diff --check`도 통과했습니다.