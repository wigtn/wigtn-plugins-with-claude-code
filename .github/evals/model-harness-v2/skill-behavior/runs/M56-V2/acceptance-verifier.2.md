현재 구현은 **FR-101, FR-102 모두 미충족**입니다.

| Requirement | 상태 | 코드 근거 | 테스트 근거 | 미충족 사항 |
|---|---|---|---|---|
| FR-101: 할인액은 0 이상 100 이하 | **Not satisfied** | [`discount()`](/private/tmp/wigtn-skill-behavior-v1/work/M56-V2/acceptance-verifier-2/implementation.py:1)은 자동 할인액 `amount * 0.2`와 수동 할인액을 범위 검증 없이 반환합니다. | `test_cap` 실패: `discount(1000)`이 `200.0` 반환. 추가 실행 결과 `discount(-10) → -2.0`, 관리자 수동 할인 `101 → 101`. | 하한 0과 상한 100이 자동·수동 할인 모두에 적용되지 않습니다. |
| FR-102: 관리자만 수동 할인액 지정 | **Not satisfied** | [`implementation.py:2`](/private/tmp/wigtn-skill-behavior-v1/work/M56-V2/acceptance-verifier-2/implementation.py:2)에서 `role`을 검사하지 않고 `manual`을 그대로 반환합니다. | [`test_auth`](/private/tmp/wigtn-skill-behavior-v1/work/M56-V2/acceptance-verifier-2/test_implementation.py:5) 실패: 일반 회원의 수동 할인 호출에서 `PermissionError`가 발생하지 않음. 추가 실행 결과 `discount(10, 50, "member") → 50`. | 비관리자의 수동 할인 지정 차단 및 권한 오류 처리가 없습니다. |

검증 명령:

- `python -m unittest -v` → 종료 코드 `127` (`python` 실행 파일 없음)
- `python3 -m unittest -v` → 종료 코드 `1`, 2개 테스트 모두 실패
- `python3` 경계값 직접 호출 → 종료 코드 `0`, 위 위반 결과 재현

제한사항: Git 저장소가 아니므로 커밋이나 변경분 비교가 아닌 현재 작업 디렉터리의 PRD·구현·테스트 파일을 기준으로 검증했습니다. 소스 파일은 수정하지 않았으며 테스트가 만든 `__pycache__`만 제거했습니다.