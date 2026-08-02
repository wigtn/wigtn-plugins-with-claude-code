구현 완료했습니다. 변경 파일은 [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/expense-approval-2/expense/service.py:8) 하나입니다.

반영 내용:
- `submit` 양수 금액 검증, `PENDING` 생성, owner 범위 idempotency 처리
- 같은 owner/key에서 payload 불일치 시 `ValueError`
- idempotent 재호출 시 같은 expense 반환 및 audit 미증가
- `decide`에서 같은 팀 manager만 허용, 본인 경비 처리 금지
- `PENDING -> APPROVED/REJECTED` 단일 전이만 허용
- 재결정은 같은 action이어도 `ValueError`, audit 미증가
- reject reason 필수
- submit/decide audit에 `actor/action/before/after` 기록

검증:
- `python3 -m unittest -v` 통과
- 추가 acceptance 스니펫 통과: 양수 검증, idempotency mismatch, cross-team/self/reject reason/redecision/audit 불변성 확인

참고:
- `notes/user-draft.txt`는 작업 전부터 수정 상태였고 건드리지 않았습니다.
- 커밋, push, 외부 작업은 하지 않았습니다.