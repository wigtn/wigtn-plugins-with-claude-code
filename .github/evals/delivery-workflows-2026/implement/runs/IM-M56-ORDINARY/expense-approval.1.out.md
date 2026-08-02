경비 승인 기능을 [expense/service.py](/private/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/expense-approval-1/expense/service.py)에 구현했습니다.

- 양수 금액 제출 및 owner 범위 멱등성
- 동일 키의 payload 충돌 방지
- 같은 팀 manager만 승인/반려 가능
- 본인 경비 처리 및 중복 결정 방지
- 반려 사유 필수 검증
- 생성·결정 audit 기록
- 실패 및 멱등 재호출 시 audit 불변

검증 결과:

```text
Ran 3 tests in 0.000s
OK
```

추가 경계 사례 검사와 `git diff --check`도 통과했습니다. 기존 변경 사항인 `notes/user-draft.txt`는 수정하지 않았으며 커밋·push·외부 작업도 수행하지 않았습니다.