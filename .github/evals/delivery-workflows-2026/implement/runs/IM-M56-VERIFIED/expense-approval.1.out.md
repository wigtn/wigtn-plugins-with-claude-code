경비 승인 기능을 구현했습니다.

변경 파일:

- [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/expense-approval-1/expense/service.py:11)
  - 양수 금액 제출 및 `PENDING` 생성
  - owner 범위 멱등성 및 payload 충돌 검증
  - 동일 팀 관리자 승인/반려
  - 본인 경비 처리와 재결정 차단
  - 반려 사유 필수 검증
  - 생성·결정 audit 기록 및 멱등 재호출 audit 방지

검증 결과:

- `python3 -m unittest -v` — 3개 테스트 통과
- 추가 수용 기준 시나리오 — 통과
- `git diff --check` — 통과

`notes/user-draft.txt`는 수정하지 않았으며 기존 변경을 그대로 보존했습니다. 커밋, push, 외부 작업, 의존성 설치는 수행하지 않았습니다.