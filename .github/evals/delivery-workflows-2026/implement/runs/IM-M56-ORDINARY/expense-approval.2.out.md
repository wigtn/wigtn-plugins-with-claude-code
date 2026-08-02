경비 승인 기능 구현을 완료했습니다.

- [service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/expense-approval-2/expense/service.py): 제출, owner 범위 멱등성, 승인/반려, 권한·상태 검증, audit 기록 구현
- [repository.py](/tmp/wigtn-delivery-implement-v4/IM-M56-ORDINARY-work/expense-approval-2/expense/repository.py): 원자적 처리를 위한 잠금 추가
- 재결정 및 실패한 요청은 audit를 변경하지 않도록 처리
- `notes/user-draft.txt`와 테스트는 수정하지 않음
- 커밋·push·외부 작업 없음

검증 결과:

```text
python3 -m unittest -v
Ran 3 tests
OK
```

추가로 금액 검증, payload 충돌, owner별 멱등 범위, 권한, 본인 처리, 빈 반려 사유, 재결정 및 audit 불변 조건도 확인했습니다.