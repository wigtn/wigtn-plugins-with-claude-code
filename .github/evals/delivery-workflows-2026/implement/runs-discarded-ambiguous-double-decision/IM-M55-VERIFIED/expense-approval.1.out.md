구현 완료했습니다.

변경 파일:
- [expense/service.py](/tmp/wigtn-delivery-implement-v3/IM-M55-VERIFIED-work/expense-approval-1/expense/service.py:9): `submit` 양수 검증, owner 범위 idempotency, payload 충돌 `ValueError`, 생성 audit 기록
- [expense/service.py](/tmp/wigtn-delivery-implement-v3/IM-M55-VERIFIED-work/expense-approval-1/expense/service.py:35): `decide` 팀/manager/본인 처리 제한, 단일 상태 전이, rejection reason 필수, 중복 결정 audit 방지

검증:
- `python3 -m unittest -v` 통과: 3 tests OK
- 추가 일회성 요구사항 검증 통과: 양수 금액, idempotency 충돌/owner 범위, 권한 제한, 중복 audit, reject reason, 재결정 방지

`notes/user-draft.txt`는 기존 변경 상태로 남아 있었고 수정하지 않았습니다. 커밋, push, 외부 작업도 하지 않았습니다.