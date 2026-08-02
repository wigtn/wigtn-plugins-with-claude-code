구현 완료했습니다. 변경은 [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/expense-approval-3/expense/service.py:8)만 했고, `notes/user-draft.txt`는 건드리지 않았습니다.

반영 내용:
- `submit()` 양수 금액 검증, `PENDING` 생성, owner 범위 idempotency 처리
- 같은 owner의 같은 key+payload 재호출은 기존 expense 반환 및 audit 미증가
- 같은 owner의 같은 key+다른 payload는 `ValueError`
- `decide()`는 manager로 보이는 actor(`actor_id`가 `m`으로 시작), 같은 팀, 본인 아님 조건을 검증
- `PENDING -> APPROVED/REJECTED` 단일 전이만 허용
- 이미 결정된 expense 재처리는 `ValueError`, audit 미증가
- `REJECTED`에는 non-empty reason 요구
- submit/decide audit에 `actor/action/expense_id/before/after` 기록

검증:
- `python3 -m unittest -v` 성공
  - 3 tests, OK
- 추가 직접 probe로 idempotency conflict, non-manager/self decision, reject reason, 재결정 audit 미증가 확인 완료

현재 worktree에는 제가 수정한 `expense/service.py`와, 작업 전부터 있던 `notes/user-draft.txt` 수정 상태가 남아 있습니다. 커밋, push, 외부 작업은 하지 않았습니다.