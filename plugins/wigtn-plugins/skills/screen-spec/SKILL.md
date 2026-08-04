---
name: screen-spec
description: |
  PRD를 입력으로 화면정의서 5종(IA, User Flow, Screen Spec, Wireframe HTML, Dev Handoff)을
  순차 생성한다. Wireframe은 흑백 + 의미색만 사용하는 lo-fi 산출물(스타일/브랜드는 별도 단계).
  frontend-developer 자동 리뷰 지원. /screen-spec 명령어에서 호출되며,
  /prd → /implement 사이의 선택적 게이트로 동작한다.
allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
---

# Screen Spec Skill

`/screen-spec` 의 실행 엔진. PRD 하나를 읽어 **화면정의서 5종을 각각 별도 파일로** 만든다.

## 출력 계약 (타협 불가)

`docs/prd/screens/<feature>/` 아래에 아래 5개 파일을 만든다. **하나의 문서로 합치지 않는다.**
각 산출물은 해당 보일러플레이트를 Read해서 PRD 데이터로 채운다.

| # | 파일 | 보일러플레이트 (`${CLAUDE_PLUGIN_ROOT}/skills/screen-spec/`) |
|---|---|---|
| 1 | `01-IA.md` | `templates/01-IA.md` — 정보구조도, 페이지 ↔ FR 매핑 |
| 2 | `02-USER-FLOW.md` | `templates/02-USER-FLOW.md` — 분기 조건까지 명시한 플로우 |
| 3 | `03-SCREEN-SPEC.md` | `templates/03-SCREEN-SPEC.md` — 화면당 7개 슬롯 |
| 4 | `04-WIREFRAME.html` | `templates/04-WIREFRAME.html` (web) / `templates/04-WIREFRAME-mobile.html` (mobile) |
| 5 | `05-DEV-HANDOFF.md` | `templates/05-DEV-HANDOFF.md` — FR ↔ 화면 ↔ 컴포넌트 |

01 → 02 → 03 → 04 → 05 순서로 만든다. 앞 산출물이 뒤 산출물의 입력이다.

## 입력 — PRD가 단일 진실원

`docs/prd/PRD_<feature>.md` 를 읽는다. Role Key · FR ID · Route · 상태는 PRD에서 **그대로 인용**하고 새로 지어내지 않는다.

| PRD 섹션 | 쓰이는 곳 |
|---|---|
| §2.3 User Roles | 각 화면의 Audience (Role Key를 그대로) |
| §3 Functional Requirements | 페이지 ↔ FR 매핑 (01, 05) |
| §5.4 Pages | 대상 페이지 목록 (route / auth / responsive) |
| §5.4.1 Page State Matrix | 화면별 상태 명세 (03) |
| §5.5 User Flow | 플로우 확장의 출발점 (02) |

§5.4에서는 `Has FE Components: Yes` 인 행만 대상으로 한다. PRD 골격 정본은 `${CLAUDE_PLUGIN_ROOT}/contracts/PRD-CONTRACT.md`.

상태 어휘는 5개로 고정: `loading` / `empty` / `error` / `success` / `no-permission`.
§5.4.1에서 체크된 상태는 03-SCREEN-SPEC.md에 **1줄 이상 명세**한다 (누락은 리뷰의 critical).

**중단 조건** — 추측으로 메우지 말고 stop한다:
- FE 페이지 0개 → "백엔드 전용 PRD입니다. `/implement` 로 진행하세요"
- §5.4.1 누락 → "Page State Matrix가 필요합니다"
- §5.5 누락 → "User Flow가 필요합니다"

## 플랫폼 판정

`--platform` 명시값이 있으면 그것이 우선. 없으면 PRD §1 Overview의 **모바일 시그널**(`React Native`, `RN`, `iOS`, `Android`, `네이티브`, `앱스토어`, `모바일 앱`, `mobile`)을 보고 `mobile` 로 자동 전환하며, 전환했음과 `--platform=web` 으로 덮어쓸 수 있음을 사용자에게 알린다. 시그널이 없으면 `web`.

⚠️ 단독 `앱`은 시그널이 아니다 — `웹앱` / `web app` 에 부분 매칭되어 오탐한다.

모바일 템플릿은 네비 패턴 3종을 모두 담고 있으므로, 실제 산출물에서는 **쓰지 않는 패턴 섹션을 제거**한다.

## INTERVIEW (`--interview` 일 때만)

PRD가 다루지 않는 화면 레이어 결정을 **한 메시지에 번호 매긴 5~7개 객관식**으로 묻고 1회 응답으로 끝낸다. 질문을 한 개씩 쪼개 보내지 않는다(라운드트립 폭증).

네비게이션(top / side / bottom / drawer) · 정보 밀도(compact / spacious) · 에러 톤(공식 / 친근) · 빈 상태 철학(일러스트+CTA / 최소 텍스트+CTA) · 전환 방식(page / modal / drawer) · 모바일 우선순위(desktop-first / mobile-first / parity) · 첫 화면 후크(value / action / story-first).

받은 답변은 03-SCREEN-SPEC.md에 명시적으로 반영한다. 플래그가 없으면 이 단계를 건너뛴다(PRD 추론 모드).
PRD에 `TBD` / `???` / 빈 셀이 5건 이상이면 종료 안내에서 `--interview` 재실행을 권한다.

## 생성 시 고정 규칙

**실행 분기 (컨텍스트 절약)**
- 01~03은 메인 스레드에서 만든다 — 짧고, 뒤 단계에서 계속 참조된다.
- 04·05는 `general-purpose` subagent에 분리 발주한다 — 출력이 가장 크고 재참조가 적다. subagent에 PRD 경로 · 01~03 경로 · 사용할 템플릿 경로 · INTERVIEW 결정사항 · 출력 경로를 넘기고, **파일 경로와 검증 요약만** 돌려받는다(본문을 메인 컨텍스트에 싣지 않는다).

**와이어프레임은 lo-fi다**
- 흑백(`neutral-*`) + 의미색만: error=red, success=green, warning·no-permission=amber.
- 브랜드/액센트 컬러, 폰트·그림자·그라데이션 등 실제 디자인 금지. 스타일은 다음 단계의 결정이다.
- 회색 점선 박스 + 라벨로 영역을 표현하고, 페이지 간 이동은 `<a href="#screen-<slug>">` anchor로 클릭 가능하게 만든다.
- 페이지 ≥6개 또는 04가 600줄 초과 → `04-wireframes/<slug>.html` 로 쪼개고 `04-WIREFRAME.html` 은 인덱스로 둔다.

**연결 무결성**
- 03의 Wireframe Anchor와 04의 `<section id="screen-<slug>">` 가 일치해야 한다.
- 모든 페이지는 1개 이상의 FR에, 모든 FR은 1개 이상의 화면에 연결된다(양방향).
- 모든 폼 필드는 validation과 microcopy를 둘 다 갖는다.

## 리뷰 (필수)

`frontend-developer` 에이전트에 산출물 디렉토리와 `${CLAUDE_PLUGIN_ROOT}/skills/screen-spec/references/handoff-checklist.md` 를 넘겨 검증한다. INTERVIEW 결정사항이 있으면 그것이 일관되게 반영됐는지도 확인한다.

판정은 findings 롤업이다 — critical ≥1이면 **FAIL**(해당 산출물만 재생성 후 재검증), critical 0이고 major ≥1 또는 minor ≥5면 **WARN**(표시하고 진행), 그 외 **PASS**. 점수는 매기지 않는다.

## 부분 재실행

`--pages=<list>` 나 "와이어프레임만 다시 만들어" 같은 요청은 **지정된 파일만 통째로 덮어쓰고 나머지 산출물은 보존**한다. diff 머지는 하지 않는다.

## 참고

- `${CLAUDE_PLUGIN_ROOT}/skills/screen-spec/references/state-checklist.md` — 상태별 UI 패턴
- `${CLAUDE_PLUGIN_ROOT}/skills/screen-spec/references/microcopy-patterns.md` — 마이크로카피 패턴
- `${CLAUDE_PLUGIN_ROOT}/skills/screen-spec/references/handoff-checklist.md` — 리뷰 체크리스트 + 반환 스키마
- 스타일/브랜드 선택은 이 스킬 밖이다. `design-discovery` 가 `/implement` 직전에 담당한다.
- 산출물은 `/implement` 의 입력이다: 03 → 컴포넌트 props/state, 04 → 레이아웃 마크업, 05 → task 분해.
