구현과 검증을 완료했습니다.

- [webhook/signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-2/webhook/signing.py:6): 엄격한 `sha256=<64 hex>` 검증 및 `hmac.compare_digest` constant-time 비교
- [webhook/delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-2/webhook/delivery.py:1): 중복 이벤트 저장 및 payload 충돌 처리
- [webhook/delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-2/webhook/delivery.py:17): 2xx와 attempt별 재시도 정책 구현
- 표준 라이브러리만 사용하고 입력 bytes를 변형하지 않음

검증 결과:

- `python3 -m unittest -v` — 3개 테스트 통과
- 인라인 경계조건 검사 — malformed 헤더, 충돌 payload, 전체 retry 스케줄 통과
- `git diff --check` — 통과
- 미검증 요구사항 없음

`notes/user-draft.txt`의 기존 수정은 보존했습니다. 커밋·push·외부 접근은 수행하지 않았습니다.