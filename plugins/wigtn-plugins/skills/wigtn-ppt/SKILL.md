---
name: wigtn-ppt
description: >-
  WIGTN 브랜드 HTML 프레젠테이션 생성. 템플릿 없이 브랜드 원칙(잉크 네이비 +
  시그니처 퍼플 점)을 기반으로 단일 self-contained HTML 발표자료를 만든다.
  Light / Dark 두 테마를 선택할 수 있고, WIGTN 로고와 퍼플 점 시그니처를 모든
  슬라이드에 일관되게 적용한다. WIGTN 브랜드 발표자료에 한정해 동작한다(일반 PPT는
  다른 PPT 스킬을 쓴다). Triggers on: 'wigtn ppt', 'wigtn 발표자료', '위그튼 ppt',
  'wigtn 슬라이드', 'wigtn presentation', '브랜드 발표자료', '브랜드 PPT',
  '회사 PPT', '회사 발표자료'.
allowed-tools: Read, Write, Edit, Bash, Glob
---

# WIGTN PPT Generator

WIGTN 브랜드 정체성을 담은 **단일 HTML 프레젠테이션**을 만드는 스킬.
템플릿(.pptx) 없이도, 브랜드 원칙과 reference만으로 Claude가 매번 새로 디자인한다.

## 핵심 원칙

1. **원칙 기반, 템플릿 무의존** — 고정 템플릿 파일에 의존하지 않는다. `references/`의 브랜드 토큰 + 레이아웃 원칙을 읽고 그때그때 생성한다.
2. **브랜드 충실도 (Brand Fidelity)** — 정확한 HEX만 사용한다. "비슷한 색" 금지. 잉크 `#1E1E28`, 시그니처 퍼플(Pantone 265) `#9B51E0`.
3. **시그니처 퍼플 점 반복** — `wigtn.` 의 마침표에서 온 퍼플 점(`.`)이 브랜드의 시그니처다. **모든 슬라이드**에 퍼플 점 모티프를 하나 이상 일관되게 반복한다 (페이지 번호 옆 점, 섹션 번호의 점, 코너 점, 진행 도트 등).
4. **Light / Dark 듀얼 테마** — 발표 환경에 맞춰 둘 중 하나를 선택. 한 발표물 안에서 섞지 않는다.
5. **Viewport Fitting** — 모든 슬라이드는 정확히 `100vh`. 슬라이드 내부 스크롤 절대 금지.
6. **텍스트만의 슬라이드 금지** — 모든 슬라이드에 최소 하나의 시각 요소(도형·색 블록·점·라인·아이콘).
7. **Show, Don't Tell** — 디자인을 말로 묻지 않는다. 테마/콘텐츠만 확정하면 바로 생성하고, 스크린샷으로 보여준 뒤 조정한다.
8. **Zero-dependency** — 단일 HTML 파일. 브라우저에서 바로 발표 가능 (폰트는 CDN `<link>` 1줄만 허용).

## 브랜드 (요약)

| 토큰 | 값 | 용도 |
|------|-----|------|
| Ink (네이비) | `#1E1E28` | Dark 배경 / Light 텍스트 |
| Purple (Pantone 265) | `#9B51E0` | **시그니처 점**, 강조, 링크 |
| Purple Deep | `#6B2EAA` | 점 그림자, 깊이, 그라데이션 끝 |
| White | `#FFFFFF` | Light 배경 / Dark 텍스트 |

> 전체 팔레트(Light/Dark `:root` 스니펫), 로고 변형 사용 규칙, 타이포그래피, 점 시그니처 규칙은 **반드시 [references/brand.md](references/brand.md)를 Read**한 뒤 적용한다.

## 워크플로우 (4단계)

### Phase 0: 테마 + 콘텐츠 (AskUserQuestion 1회)

`AskUserQuestion`으로 **한 번에** 묶어서 묻는다:

1. **테마** — `Light` (밝은 발표장·문서형) / `Dark` (무대·키노트형). 추천 포함.
2. **목적** — 컨퍼런스 / 팀 공유 / 피치덱 / 교육 / 경영진 보고
3. **분량** — 5–10장 / 10–20장 / 20장+
4. **핵심 메시지 & 이미지** — 전달할 내용, 포함할 이미지 유무·위치

발표자명·날짜·기업/제품명 등 표지에 들어갈 메타도 함께 확인한다.

### Phase 1: 구조 설계

콘텐츠를 슬라이드 맵으로 분해한다. **밀도 제한**: 표지는 제목+부제, 본문은 슬라이드당 최대 4–6 불릿(또는 동등한 시각 블록). 초과하면 자동 분할.

기본 골격: `표지 → 목차 → (섹션 구분 → 본문 N) × 챕터 → 마무리(Thank you)`.
각 슬라이드에 어떤 본문 레이아웃을 쓸지 [references/design-guide.md](references/design-guide.md)에서 고른다.

### Phase 2: 다이어그램 (필요 시)

흐름도·아키텍처·비교 도식이 필요하면 **`editorial-diagram` 스킬을 호출한다(기본 경로).**
브랜드 발표물의 톤에 맞는 정갈한 인라인 SVG를 4px 그리드·밀도 예산·WIGTN 토큰으로 만들고,
`check.py`로 검증한 뒤 슬라이드에 삽입한다. 삽입은 둘 중 하나:

- **인라인 SVG 직접 붙여넣기** (권장) — 슬라이드와 같은 테마 토큰을 쓰므로 Light/Dark가 자동으로 맞는다
- `export.sh`로 뽑은 PNG를 `<img>`로 (외부 배포·PPTX 변환 대상일 때)

**도식을 직접 손으로 그리지 않는다.** 가이드 없는 CSS/SVG 도형이 "AI가 만든 티"의 주범이다.
손그림 톤이 어울리는 자리(해커톤·캐주얼 공유)에서만 `handdrawn-diagram`을 쓴다.

### Phase 3: HTML 생성

1. **[references/brand.md](references/brand.md)** 와 **[references/design-guide.md](references/design-guide.md)** 를 Read.
2. 선택한 테마의 `:root` 토큰을 적용한 단일 HTML을 작성한다. 필수 규칙:
   - `.slide { height: 100vh; height: 100dvh; overflow: hidden; }`
   - 모든 폰트·간격은 `clamp(min, pref, max)` (고정 px 단독 금지)
   - 높이 기반 미디어쿼리(`max-height: 700px/600px`)로 단계 축소
   - 프로그레스 바 + 네비 도트(퍼플) + 키보드/터치/스와이프 + `prefers-reduced-motion`
   - **시그니처 퍼플 점**을 모든 슬라이드에 반복
   - **로고 삽입**: 아래 "로고 사용" 규칙을 따른다
3. 콘텐츠를 채우고, 애니메이션은 절제되게(프로페셔널: 0.2–0.4s 페이드/슬라이드).

### Phase 4: 검증 및 전달

스크린샷으로 viewport fitting·브랜드 일관성·점 시그니처를 확인한다. Playwright/Chrome이 있으면 슬라이드별 PNG를 렌더해 Read로 점검하고, 없으면 사용자에게 브라우저에서 열어보도록 안내한다.

```
생성 완료:
- HTML: docs/{파일명}-presentation.html  (브라우저에서 F키 전체화면 → 방향키/스와이프)
```

## 로고 사용

WIGTN 로고는 **팀 전용 에셋**이라 공개 플러그인에 커밋하지 않는다(.gitignore). 다음 우선순위로 찾는다:

1. `${CLAUDE_PLUGIN_ROOT}/skills/wigtn-ppt/assets/logo/` — 번들된 로고(팀 로컬, `*.png`는 gitignore라 공개 레포 클론엔 없음)
2. `<project>/docs/images/` — 팀 로컬 브랜드 에셋 위치(역시 gitignore, 공개 레포엔 포함되지 않음)
3. **CSS/SVG 워드마크 폴백** — 위 두 경로에 PNG가 없으면(공개 클론·신규 환경의 기본 상태) `wigtn` + 퍼플 점을 폰트/SVG로 직접 렌더(brand.md에 스니펫). 폴백만으로도 항상 동작한다.

로고를 쓸 때는 사용할 파일을 발표물 워크스페이스(예: `docs/workspace/`)로 **복사**한 뒤 HTML에서 상대경로로 참조한다. 테마별 변형은 brand.md의 매핑 표를 따른다(Light → NAVY 로고, Dark → WHITE 로고).

## Anti-Patterns (피할 것)

- 보라 그라데이션 클리셰(`#6366f1`), 흰 배경에 기본 보라/핑크 → **WIGTN 퍼플 `#9B51E0`만** 사용
- Inter/Roboto/Arial을 display 폰트로 사용 (브랜드 톤 깨짐)
- 모든 요소 가운데 정렬, 동일 카드 그리드 반복
- `min-height` 사용(슬라이드 넘침 허용) → 반드시 `height`
- 점 시그니처 누락, 테마 혼용, "비슷한 색" 대체

## 참조

- **[references/brand.md](references/brand.md)** — WIGTN 브랜드 시스템: Light/Dark 팔레트, 로고 변형·배치, 퍼플 점 규칙, 타이포, CSS 워드마크 폴백
- **[references/design-guide.md](references/design-guide.md)** — 슬라이드 타입별 레이아웃 원칙(표지/목차/섹션/본문/마무리), viewport 규칙, 애니메이션, anti-pattern
- **`design-system-reference` 스킬** — 레이아웃 밀도·타이포 위계 아이디어 재활용(Swiss Minimal, Editorial, Minimal Corporate가 WIGTN 톤에 가장 근접). 단, 색·점·로고는 **항상 WIGTN 토큰으로 덮어쓴다**.
- **`editorial-diagram` 스킬** — 다이어그램 슬라이드의 **기본 경로**. 12개 유형 라우팅,
  4px 좌표표, 밀도 예산, WIGTN 토큰, `check.py` 검증, SVG/PNG export
- **`handdrawn-diagram` 스킬** — 손그림 톤이 어울리는 자리에서만

## 체크리스트

- [ ] Phase 0: AskUserQuestion으로 테마(Light/Dark) + 콘텐츠 1회 수집
- [ ] Phase 1: 슬라이드 맵 + 밀도 제한
- [ ] Phase 2: 다이어그램 필요 슬라이드 식별 → editorial-diagram 호출 (손그림 톤일 때만 handdrawn-diagram)
- [ ] Phase 3: brand.md + design-guide.md Read → 단일 HTML 생성 (viewport, 퍼플 점, 로고)
- [ ] Phase 4: 스크린샷 검증 → 전달
