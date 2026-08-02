경비 승인 기능을 [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/expense-approval-3/expense/service.py)에 구현했습니다.

- 양수 금액 제출 및 `PENDING` 생성
- owner 범위 멱등성 및 payload 충돌 검증
- 같은 팀 관리자, 본인 처리 금지
- 단일 승인/거절 상태 전이
- 거절 사유 필수 검증
- 생성/결정 audit 기록 및 재호출 시 audit 불변
- UUID 기반 경비 ID 생성

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.

`notes/user-draft.txt`와 테스트는 수정하지 않았으며 커밋이나 외부 작업도 수행하지 않았습니다.