경비 승인 기능을 구현했습니다.

- 양수 금액만 `PENDING` 생성
- owner 범위 idempotency 및 payload 충돌 검증
- 동일 팀 승인 권한 및 본인 경비 처리 차단
- 단일 상태 전이와 reject reason 검증
- 생성·결정 audit 기록 및 중복 호출 방지
- 동시 요청에도 중복 생성/audit를 막는 잠금 적용

변경 파일:

- [expense/service.py](/tmp/wigtn-delivery-implement-v3/IM-M56-BARE-work/expense-approval-1/expense/service.py)
- [expense/repository.py](/tmp/wigtn-delivery-implement-v3/IM-M56-BARE-work/expense-approval-1/expense/repository.py)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. 추가 경계 조건 검증과 `git diff --check`도 통과했습니다.

`notes/user-draft.txt`의 기존 변경은 수정하지 않았으며, 커밋·push·외부 작업도 수행하지 않았습니다.