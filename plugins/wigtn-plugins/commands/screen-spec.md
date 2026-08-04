---
argument-hint: "<feature name>"
description: |
  Generate screen specifications (IA / User Flow / Screen Spec / Wireframe / Dev Handoff) from an existing PRD.

  Trigger keywords:
  - Commands: "/screen-spec", "화면정의서 만들어줘", "화면 명세 만들어줘", "와이어프레임 만들어줘"

  - Natural language (바이브 코더 친화):
    - "화면 어떻게 생겼는지 보여줘", "UI 정의해줘"
    - "와이어프레임 그려줘", "프로토타입 만들어줘"
    - "화면별로 정리해줘", "페이지 명세 만들어줘"
    - "PRD 다음 단계", "화면 만들기 전에 정리"
---

# Screen Specification Generation

PRD를 입력으로 **화면정의서 5종**을 만든다. `/prd` 다음, `/implement` 이전의 선택적 게이트.

파이프라인: `/prd` → `prd-reviewer` → **`/screen-spec`** → `/implement` → `/auto-commit`

## 산출물 계약 (타협 불가)

`docs/prd/screens/<feature-name>/` 아래에 **파일 5개를 각각** 만든다. 하나의 문서로 합치지 않는다.

| # | 파일 | 내용 |
|---|---|---|
| 1 | `01-IA.md` | 정보구조도 — 페이지 ↔ FR 매핑 |
| 2 | `02-USER-FLOW.md` | 사용자 플로우 — 분기 조건 포함 |
| 3 | `03-SCREEN-SPEC.md` | 화면별 명세 — Audience / Auth / States / Components / Microcopy / Responsive |
| 4 | `04-WIREFRAME.html` | 클릭 가능한 lo-fi 와이어프레임 (흑백 + 의미색) |
| 5 | `05-DEV-HANDOFF.md` | FR ↔ 화면 ↔ 컴포넌트 매핑 |

5개 중 하나라도 없으면 실패다. 생성은 `screen-spec` 스킬이 수행한다.

## 실행 조건

PRD §5.4 Pages에서 `Has FE Components` 가 `Yes` 인 행이 **1개 이상**일 때만 실행한다.
0개면 백엔드 전용이므로 차단하고 `/implement` 로 안내한다. PRD가 없으면 `/prd <feature-name>` 이 먼저다.
PRD 골격은 `${CLAUDE_PLUGIN_ROOT}/contracts/PRD-CONTRACT.md` 가 정본 — 여기서 재진술하지 않는다.

## Usage

```bash
/screen-spec <feature-name>
/screen-spec <feature-name> --interview
/screen-spec <feature-name> --platform=mobile
/screen-spec <feature-name> --pages=/submit,/my
```

## Parameters

- `feature-name`: 기능명 (required, PRD 파일명과 일치)
- `--interview`: 화면 레이어 의사결정(네비 패턴·밀도·에러 톤·빈 상태·전환·모바일 우선순위)을 단일 턴 배치 Q&A로 끌어낸다
- `--platform=<web|mobile>`: 와이어프레임 템플릿 분기. 미지정 시 PRD §1 Overview의 모바일 시그널로 자동 판정
- `--pages=<list>`: 지정 페이지만 재생성 (쉼표 구분). 나머지 산출물은 보존
- `--verify-vision`: (선택) 04-WIREFRAME.html을 렌더·캡처해 §5.4.1 상태와 대조. 렌더 도구가 없으면 스킵

## 실행

1. `docs/prd/PRD_<feature-name>.md` 에서 §2.3 User Roles(→ 화면 Audience), §3 FR, §5.4 Pages(FE 행만), §5.4.1 Page State Matrix, §5.5 User Flow를 읽는다. §5.4.1이나 §5.5가 없으면 무엇이 없는지 알리고 stop — 추측으로 채우지 않는다.
2. `screen-spec` 스킬로 5종을 순서대로 생성한다 (뒤 산출물이 앞 산출물을 입력으로 쓴다).
3. `frontend-developer` 에이전트로 리뷰한다.

`--verify-vision` 이 주어지면, 리뷰 전에 `04-WIREFRAME.html` 을 렌더·캡처해 §5.4.1의 상태 목록과
`03-SCREEN-SPEC.md` 를 눈으로 대조한다. 렌더 도구가 없으면 스킵하고 스킵했다고 보고한다.

## 리뷰 게이트 (findings 롤업)

| 결과 | 조건 | 처리 |
|---|---|---|
| ❌ FAIL | critical ≥1 | 해당 산출물(03 또는 04)만 재생성 후 재검증 |
| ⚠️ WARN | critical 0 이고 (major ≥1 또는 minor ≥5) | 경고만 표시하고 진행 |
| ✅ PASS | 그 외 | 진행 |

점수는 매기지 않는다.

## 보고와 다음 단계

산출물 5개 경로와 게이트 결과를 보고하고, `04-WIREFRAME.html` 을 브라우저로 열어 확인하도록 안내한다.
이어서 `/implement <feature-name>` — 화면정의서가 있으면 `/implement` 는 추측 대신 03(컴포넌트 props/state) · 04(레이아웃 마크업) · 05(task 분해)를 그대로 따른다.

- 스타일·브랜드·타이포 결정은 `/screen-spec` 책임 밖이다. `design-discovery` 가 `/implement` 직전에 고른다.
- PRD에 `TBD` / 빈 셀이 5건 이상이면 `--interview` 재실행을 권한다.
