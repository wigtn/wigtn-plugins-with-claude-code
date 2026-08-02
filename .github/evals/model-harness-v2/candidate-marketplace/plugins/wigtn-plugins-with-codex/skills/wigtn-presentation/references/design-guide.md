# WIGTN PPT Design Guide

슬라이드를 **템플릿 없이** 일관되게 만들기 위한 레이아웃 원칙. 색·로고·점은 [brand.md](brand.md)를 따른다. 여기서는 구조·viewport·슬라이드 타입·애니메이션을 다룬다.

## 1. Viewport 규칙 (필수)

```css
.slide{
  height:100vh; height:100dvh;     /* min-height 금지 */
  overflow:hidden;                 /* 슬라이드 내부 스크롤 절대 금지 */
  position:relative;
  display:flex; flex-direction:column;
  padding:clamp(2.5rem,6vh,5rem) clamp(2rem,6vw,6rem);
  background:var(--bg); color:var(--text-primary);
}
```

- 모든 폰트·간격은 `clamp(min, preferred, max)`. 고정 px/rem 단독 금지.
- 높이 기반 미디어쿼리로 단계 축소:
  ```css
  @media (max-height:700px){ :root{ --scale:.9 } }
  @media (max-height:600px){ :root{ --scale:.8 } }
  ```
- 콘텐츠가 넘치면 슬라이드를 **분할**한다(폰트를 무리하게 줄이지 않는다).

## 2. 필수 UI 크롬

- **프로그레스 바**: 상단 또는 하단 1~2px, `var(--accent)` 채움.
- **네비 도트**: 우측 또는 하단, 현재 슬라이드는 퍼플 점.
- **페이지 번호**: 우하단, `02 ●` 형태로 퍼플 점 동반(시그니처).
- **네비게이션**: 키보드(←/→/Space), 터치/스와이프, 마우스 휠. `prefers-reduced-motion` 존중.

## 3. 슬라이드 타입

각 타입은 brand.md의 테마 토큰을 그대로 쓴다. **모든 타입에 퍼플 점 시그니처 1개 이상.**

### 3.1 표지 (Cover)
- 풀 워드마크 로고(Light→NAVY, Dark→WHITE) 상단 좌측 또는 하단.
- 제목 `clamp(2.4rem,5vw,4.5rem)` SemiBold + 부제 Medium.
- 발표자·날짜·기업/제품명 메타는 하단 또는 우상단.
- 시각 요소: 좌측 세로 퍼플 라인 또는 대형 잉크/퍼플 컬러 블록 1개. (텍스트만 금지)
- 점 시그니처: 제목 끝 강조점 또는 우하단 코너 점.

### 3.2 목차 (Contents / Agenda)
- "Contents" 제목 + 번호 매긴 리스트. 번호의 마침표만 퍼플(`01.`).
- 좌/우 2분할 또는 좌측 제목 + 우측 리스트.

### 3.3 섹션 구분 (Section Divider)
- 각 챕터 시작. 대형 번호 `01` + 섹션 제목.
- Dark 테마면 잉크 배경에 화이트 텍스트로 대비를 주는 것이 효과적(Light 발표물 안에서도 섹션만 잉크 배경으로 전환 가능 — 단 텍스트 색을 화이트로).
- 번호 옆/끝에 퍼플 점.

### 3.4 본문 (Body) — 레이아웃 변형
필요한 것을 골라 쓴다. 한 슬라이드 = 한 메시지.

| 레이아웃 | 용도 | 핵심 |
|---------|------|------|
| Title + Bullets | 일반 설명 | 슬라이드당 4–6 불릿, 불릿 마커를 퍼플 점으로 |
| Two-Column | 비교/대조 | 좌/우 분할, 가운데 1px `--line` 또는 퍼플 구분 |
| Cards (2–4열) | 항목 나열 | 동일 카드, 헤더 라벨에 퍼플 악센트 |
| Big Number / KPI | 지표 강조 | 초대형 숫자 + 라벨, 숫자 끝 퍼플 점 |
| Quote | 인용/메시지 | 대형 인용문, 좌측 퍼플 세로바 |
| Image + Text | 이미지 설명 | 좌 41% 텍스트 / 우 이미지(또는 반대) |
| Diagram | 흐름/구조 | handdrawn-diagram 또는 CSS/SVG 도형 |
| Timeline | 단계/로드맵 | 가로/세로 라인 + 노드(노드를 퍼플 점으로) |

공통: Slide Title 좌상단(`clamp(1.4rem,2.6vw,2rem)` Bold), 우하단 작은 마크 로고 + 페이지 번호.

### 3.5 마무리 (Thank you)
- 표지와 같은 톤. 대형 "Thank you" + 한 줄 클로징.
- 풀 워드마크 로고 + 연락/CTA. 퍼플 점 시그니처 유지.

## 4. 애니메이션 매핑

WIGTN 기본 톤은 **프로페셔널/미니멀**: 절제되고 빠르게.

| 느낌 | 스타일 | 속도 |
|------|--------|------|
| 기본(프로페셔널) | 미세 페이드 + 8px 슬라이드업, 스태거 | 0.2–0.4s |
| 키노트/임팩트(Dark) | 느린 페이드 + 대형 스케일(0.96→1) | 0.5–0.8s |
| 강조 포인트 | 퍼플 점 팝(scale 0→1, 약한 스프링) | 0.3s |

- 진입 애니메이션은 슬라이드당 1~2종으로 제한. 동기 없는 그림자/글래스/패럴랙스 금지.
- `@media (prefers-reduced-motion:reduce)`에서 모든 트랜지션 제거.

## 5. Anti-Patterns

- `min-height`로 슬라이드 넘침 허용 → 반드시 `height`.
- 보라/핑크 그라데이션, `#6366f1` 등 일반 AI 보라 → **WIGTN `#9B51E0`만**.
- Inter/Roboto/Arial display 폰트, 모든 요소 가운데 정렬, 동일 카드 그리드 반복.
- 텍스트만의 슬라이드, 점 시그니처 누락, 테마 혼용.
- 로고 옆에 점 중복(로고에 이미 점 포함), 로고 비율 왜곡.

## 6. design-system-reference 재활용

같은 플러그인의 `design-system-reference/styles/`에서 **레이아웃 밀도·타이포 위계·여백 감각**만 빌린다. WIGTN 톤에 가장 근접한 셋:
- `swiss-minimal` — 그리드·여백·타이포 위계
- `editorial` — 강한 타이포·인용·리듬
- `minimal-corporate` — 보고/경영진 톤

> 빌리는 것은 **구조 감각**뿐. 색·폰트 강조·로고·점은 **항상 WIGTN 토큰으로 덮어쓴다.** 다른 스타일의 시그니처(네온, 브루탈리즘 등)를 섞지 않는다.
