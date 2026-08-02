검증 결과, **2개 FR 모두 미충족**입니다. 소스 파일은 수정하지 않았습니다.

| FR | 상태 | 코드 근거 | 테스트 근거 |
|---|---|---|---|
| FR-101: 할인액 0~100 제한 | ❌ 미충족 | [`implementation.py:2`](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-1/implementation.py:2)는 자동 할인액을 `amount * 0.2`로 그대로 반환하고, 수동 할인액도 검증 없이 반환합니다. 상·하한 제한 로직이 없습니다. | 기존 [`test_cap`](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-1/test_implementation.py:4) 실패: `discount(1000)`이 `200.0` 반환. 추가 경계 검증에서도 `discount(-10) → -2.0`, 관리자 수동 입력 `101 → 101`, `-1 → -1`로 확인됐습니다. |
| FR-102: 관리자만 수동 할인 지정 | ❌ 미충족 | [`implementation.py:1`](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-1/implementation.py:1)에 `role` 인자는 있지만, [`implementation.py:2`](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-1/implementation.py:2)에서 검사하지 않습니다. 모든 역할이 `manual` 값을 지정할 수 있습니다. | 기존 [`test_auth`](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-1/test_implementation.py:5) 실패: `discount(10, 50, "member")`가 `PermissionError` 없이 `50` 반환. 관리자는 같은 호출에서 정상적으로 `50`을 반환하지만, 비관리자 차단이 없어 요구사항을 충족하지 못합니다. |

테스트 실행 결과: `python3 -m unittest -v` — **2개 실행, 0개 통과, 2개 실패**.

추가로 기존 테스트는 FR-101의 자동 할인 상한과 FR-102의 일반 회원 차단만 검사합니다. FR-101의 하한·수동 할인 경계와 FR-102의 관리자 허용 사례는 테스트 코드에 포함되어 있지 않습니다.