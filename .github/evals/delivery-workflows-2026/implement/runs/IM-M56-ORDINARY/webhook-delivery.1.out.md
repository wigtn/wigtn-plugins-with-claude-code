웹훅 기능을 구현했습니다.

- `sha256=<64자리 hex>` 형식 검증 및 `hmac.compare_digest` constant-time 비교
- 이벤트 중복 저장 방지 및 payload 충돌 시 `ValueError`
- 실패 횟수별 재시도 지연 `0/60/300초`
- 2xx 응답 및 4회 이후 재시도 중단
- 입력 bytes를 변경하지 않고 표준 라이브러리만 사용

변경 파일:

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/webhook-delivery-1/webhook/signing.py)
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/webhook-delivery-1/webhook/delivery.py)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. `notes/user-draft.txt`의 기존 변경은 건드리지 않았으며 커밋·push도 하지 않았습니다.