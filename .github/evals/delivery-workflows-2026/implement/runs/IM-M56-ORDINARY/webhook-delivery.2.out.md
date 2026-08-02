구현 완료했습니다.

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/webhook-delivery-2/webhook/signing.py): 엄격한 헤더 검증과 constant-time HMAC-SHA256 비교
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/webhook-delivery-2/webhook/delivery.py): 이벤트 중복·충돌 처리 및 재시도 지연 구현
- `python3 -m unittest -v`: 3개 테스트 모두 통과
- 추가 경계 조건 검사 통과
- `notes/user-draft.txt`의 기존 수정 상태 보존
- 테스트, 의존성, 커밋 및 push 변경 없음