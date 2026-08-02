구현 완료했습니다. 변경 파일은 [expense/service.py](/private/tmp/wigtn-delivery-implement-v4/IM-M55-VERIFIED-work/expense-approval-1/expense/service.py:10) 하나입니다.

반영 내용:
- `submit` 양수 금액 검증, `PENDING` 생성, owner 범위 idempotency 처리
- 같은 idempotency key와 다른 payload 재사용 시 `ValueError`
- 멱등 재호출 시 같은 ID 반환 및 audit 미증가
- `decide`의 manager/team/self-decision/PENDING-only/reason 검증
- 결정 후 재결정은 같은 action이어도 `ValueError`, audit 미증가
- 생성/결정 audit에 `actor/action/before/after` 기록

검증:
- `python3 -m unittest -v` 통과: 3 tests OK
- 추가 인메모리 요구사항 체크 통과

참고: `notes/user-draft.txt`는 기존에 dirty 상태였고 수정하지 않았습니다. 커밋, push, 외부 작업도 하지 않았습니다.