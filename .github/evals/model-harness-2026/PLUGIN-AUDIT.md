# WIGTN Codex 플러그인 전체 감사

감사 대상: `.codex-plugin-staging/plugins/wigtn-plugins-with-codex`의 8개 스킬.

| 스킬 | 핵심 정보 유형 | 판정 | 개선판 조치 |
|---|---|---|---|
| `acceptance-verifier` | 요구사항 ID별 코드·테스트 증거, 읽기 전용 기본값 | 프로젝트 계약·안전 경계 | 유지 |
| `design-direction` | 프로젝트 네이티브 우선, 스타일 레퍼런스 점진 로드 | 도메인 선택 규칙 | 유지 |
| `handdrawn-diagram` | Mermaid handDrawn, SVG+PNG, 렌더 검증 | 결정적 산출물 계약 | 유지 |
| `product-spec` | PRD 생성·리뷰·디깅 모드 | **계약이 추상적이라 관습 산출물이 누락될 수 있음** | SKILL은 간결화하고 template/checklist에 적용성 기반 계약 추가 |
| `release-readiness` | 커밋·푸시·PR 권한 분리, dirty worktree 보호 | 안전·권한 경계 | 유지 |
| `screen-spec` | IA·Flow·Spec·HTML·Handoff 5종 | 결정적 산출물 계약 | 유지 |
| `verified-delivery` | 명시 호출, 검증 증거, 외부 변경 별도 권한 | 안전·증거 계약 | 유지 |
| `wigtn-presentation` | WIGTN 브랜드 토큰과 시각 QA | 조직 고유 데이터 | 유지 |

## 문장 분류 결과

- 전체 SKILL 본문: 206줄
- 대규모 세대 보정용 프롬프트나 역할극: 발견되지 않음
- 유지할 이유가 명확한 항목: 산출물 계약, 권한 경계, 증거 규칙, 브랜드·스타일 자료
- 실험으로 검증할 결함: `product-spec`의 “무엇을 내놓아야 하는가”가 reference에서 충분히 구체적이지 않음

따라서 개선판은 “8개를 모두 다시 쓰는 판”이 아니라 **8개를 모두 감사하고, 결함이 확인된 계약만 바꾼 판**이다. 변경량 자체를 성공 지표로 삼지 않는다.

## 개선판의 가설

1. UI PRD에서 Pages, State Matrix, Mermaid flow, 서버 인가, GWT, FR 매핑 단계가 더 안정적으로 나온다.
2. 비UI PRD에서는 UI 계약을 억지로 생성하지 않고 `해당 없음`과 근거를 남긴다.
3. 보편 결함 검출과 깨끗한 PRD의 오탐은 현 플러그인보다 나빠지지 않는다.
4. 다른 7개 스킬은 이미 얇고 고유 가치가 있으므로 성급한 삭제보다 유지가 낫다.
