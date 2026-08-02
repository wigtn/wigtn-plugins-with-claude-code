구현 완료했습니다. 변경은 [expense/service.py](/private/tmp/wigtn-delivery-implement-v1/IM-M55-VERIFIED-work/expense-approval-1/expense/service.py)에만 들어갔습니다.

반영 내용:
- 양수 금액만 `PENDING` 경비 생성
- owner 범위 idempotency 처리 및 payload 충돌 시 `ValueError`
- 같은 팀 manager만 승인/거절 가능
- 본인 경비 처리 금지
- `PENDING -> APPROVED/REJECTED` 단회 전이
- `REJECTED` 사유 필수
- 생성/결정 audit 기록, 중복 submit/동일 결정 재호출은 audit 미증가

검증:
- `python3 -m unittest -v` 통과
- 추가 스모크 확인 통과

`notes/user-draft.txt`는 기존에 수정된 상태였고 건드리지 않았습니다.