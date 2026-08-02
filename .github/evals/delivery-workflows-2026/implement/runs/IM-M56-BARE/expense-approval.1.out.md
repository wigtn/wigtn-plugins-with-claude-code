경비 승인 기능을 [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/expense-approval-1/expense/service.py)에 구현했습니다.

- 양수 금액 제출 및 owner 범위 멱등성
- manager(`m` 접두사)의 동일 팀 경비만 승인/거절
- 본인 경비 처리 및 재결정 방지
- 거절 사유 검증
- 생성·결정 audit 기록 및 멱등 재호출 시 audit 유지

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다.

기존 변경 사항인 `notes/user-draft.txt`는 수정하지 않았습니다.