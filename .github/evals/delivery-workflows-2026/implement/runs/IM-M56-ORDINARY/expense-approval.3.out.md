경비 승인 기능을 [expense/service.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/expense-approval-3/expense/service.py)에 구현했습니다.

- 양수 정수 금액만 `PENDING` 생성
- owner 범위 idempotency 보장
- 팀 일치 및 본인 승인 방지
- `APPROVE`/`REJECT` 단일 상태 전이
- 반려 사유 검증
- 생성·결정 audit 기록 및 재호출 시 audit 불변
- UUID 기반 경비 ID 생성

검증 결과:

```text
Ran 3 tests in 0.000s

OK
```

추가 경계 조건 점검도 통과했습니다. 기존 변경 상태였던 `notes/user-draft.txt`는 수정하지 않았으며 커밋·push·외부 작업도 수행하지 않았습니다.