경비 승인 기능을 [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-BARE-work/expense-approval-2/expense/service.py)에 구현했습니다.

- 양수 금액 제출 및 `PENDING` 생성
- owner 범위의 멱등성 및 payload 충돌 검증
- 같은 팀 승인 권한과 본인 경비 처리 금지
- 단일 `APPROVED`/`REJECTED` 전이
- 거절 사유 필수 검증
- 생성·결정 audit 기록 및 멱등/실패 호출 시 audit 보존
- 기존 `notes/user-draft.txt` 변경 사항은 수정하지 않음

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. 추가 경계 조건 검사와 `git diff --check`도 통과했습니다.