경비 승인 기능을 구현했습니다.

- `submit`: 양수 검증, owner 범위 멱등성, payload 충돌 처리, PENDING 생성 및 audit 기록
- `decide`: 팀 권한·본인 처리 금지, 단일 상태 전이, 반려 사유 검증, 재결정 방지 및 audit 기록
- 구현 파일: [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/expense-approval-2/expense/service.py:11)

검증 결과:

- `python3 -m unittest -v` — 3개 테스트 모두 통과
- 추가 요구사항 경계 검증 — 통과
- `git diff --check` — 통과
- `notes/user-draft.txt`는 수정하지 않았으며 기존 사용자 변경을 보존했습니다.
- 커밋, push, 의존성 설치, 외부 작업은 수행하지 않았습니다.