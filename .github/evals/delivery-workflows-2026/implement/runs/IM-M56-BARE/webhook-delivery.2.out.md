구현 완료했습니다.

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-2/webhook/signing.py:1): 엄격한 `sha256=<64자리 hex>` 검증 및 `hmac.compare_digest` 적용
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/webhook-delivery-2/webhook/delivery.py:1): 이벤트 중복·충돌 처리와 재시도 지연 구현
- 입력 payload는 바이트 스냅샷으로 저장
- malformed 헤더 및 모든 요구 경계 조건 확인
- `python3 -m unittest -v`: 3개 테스트 모두 통과
- 기존에 수정되어 있던 `notes/user-draft.txt`는 건드리지 않음
- 커밋·push·의존성 설치 없음