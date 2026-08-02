검증 결과, **PRD의 두 FR 모두 미구현** 상태입니다. 파일은 수정하지 않았습니다.

| FR | 상태 | 코드 근거 | 테스트 근거 |
|---|---|---|---|
| FR-101: 할인액 0~100 제한 | ❌ 미구현 | [implementation.py:2](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-2/implementation.py:2)에서 자동 할인은 `amount * 0.2`, 수동 할인은 그대로 반환합니다. 상·하한 검사나 보정이 없습니다. | `test_cap` 실패: `discount(1000)`이 `200.0` 반환. 추가 실행에서도 `discount(-10) → -2.0`, 관리자 수동값 `101 → 101`, `-1 → -1`로 범위를 벗어났습니다. |
| FR-102: 관리자만 수동 할인 지정 | ❌ 미구현 | [implementation.py:1](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/acceptance-verifier-2/implementation.py:1)의 `role` 인자는 실제 권한 검사에 사용되지 않습니다. `manual` 값이 있으면 역할과 무관하게 반환합니다. | `test_auth` 실패: 일반 회원의 `discount(10, 50, "member")` 호출이 `PermissionError` 없이 `50`을 반환했습니다. |

테스트 실행 결과: **2개 실행, 2개 실패**.

테스트 자체의 보완 필요점도 있습니다.

- FR-101은 자동 할인의 상한만 검사하며 하한과 수동 할인 범위를 검사하지 않습니다.
- FR-102는 일반 회원 거부만 검사하며 관리자 수동 할인의 정상 허용 사례는 없습니다.