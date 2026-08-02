경비 승인 기능을 구현했습니다.

- 양수 금액만 `PENDING` 생성
- owner 범위 멱등성 및 payload 충돌 검사
- 같은 팀 manager만 승인·거절 가능
- 본인 경비 처리 방지
- 단일 상태 전이 및 거절 사유 검증
- 생성·결정 audit 기록 및 중복 호출 방지
- 동시 호출 보호 추가

변경 파일:

- [expense/service.py](/tmp/wigtn-delivery-implement-v3/IM-M56-ORDINARY-work/expense-approval-1/expense/service.py)
- [expense/repository.py](/tmp/wigtn-delivery-implement-v3/IM-M56-ORDINARY-work/expense-approval-1/expense/repository.py)

검증 결과: `python3 -m unittest -v` — 3개 테스트 모두 통과했습니다. 추가 경계 조건 검사도 통과했으며, `notes/user-draft.txt`의 기존 변경은 건드리지 않았습니다.