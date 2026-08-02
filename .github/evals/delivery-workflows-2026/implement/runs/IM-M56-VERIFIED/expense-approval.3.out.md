경비 승인 기능을 구현했습니다.

변경 파일:

- [expense/service.py](/tmp/wigtn-delivery-implement-v4/IM-M56-VERIFIED-work/expense-approval-3/expense/service.py:11)
  - 양수 금액 검증과 `PENDING` 생성
  - owner 범위 멱등성 및 payload 충돌 검증
  - 동일 팀 manager(`m…` ID) 권한과 자기 경비 처리 금지
  - 단일 승인/반려 상태 전이
  - 반려 사유 필수 검증
  - 생성·결정 audit 기록 및 실패/멱등 재호출 시 audit 보존

검증 결과:

- `python3 -m unittest -v` — 3개 테스트 모두 통과
- 추가 수용 조건 검증 — 통과
- `git diff --check` — 통과
- `notes/user-draft.txt` — 기존 수정 상태 그대로 보존
- 커밋, push, 외부 접근, 의존성 설치 — 수행하지 않음

별도 역할 모델이 없는 기존 API와 테스트의 `m1`/`m2` 표현에 맞춰 manager 여부는 actor ID의 `m` 접두사로 판별했습니다.