웹훅 수신·재시도 기능을 구현했습니다.

- [signing.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-3/webhook/signing.py:5): HMAC-SHA256 검증, malformed header 처리, `hmac.compare_digest` 적용
- [delivery.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/webhook-delivery-3/webhook/delivery.py:1): 이벤트 중복·충돌 처리 및 재시도 지연 구현
- 입력 `bytes`는 변경하지 않으며 표준 라이브러리만 사용

검증 결과:

- `python3 -m unittest -v` → 공개 테스트 3개 통과
- 인라인 요구사항 경계 테스트 → 4개 통과
- `git diff --check` → 통과
- `notes/user-draft.txt` → 기존 사용자 수정 그대로 보존
- 커밋·push·의존성 설치·외부 접근 없음

미검증 요구사항이나 알려진 잔여 위험은 없습니다.