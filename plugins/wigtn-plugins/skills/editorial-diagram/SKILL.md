---
name: editorial-diagram
description: >-
  구조·흐름·비교를 설명하는 정갈한(editorial) 다이어그램을 단일 HTML + 인라인 SVG로
  생성한다. 4px 그리드·밀도 예산·단일 악센트 규칙으로 "AI가 그린 티"를 제거하고,
  WIGTN 브랜드 토큰(또는 클라이언트 토큰)을 적용한다. 발표 슬라이드·제안서·문서용.
  SVG/PNG로 export 가능. 손그림 톤이 필요하면 handdrawn-diagram, 수치 차트는
  dataviz 스킬을 쓴다. Triggers on: '다이어그램', '아키텍처 다이어그램', '구조도',
  '도식', '플로우 그려줘', '시스템 구성도', '스윔레인', '타임라인 그려줘', '로드맵 도식',
  '2x2', '사분면', '레이어 구조', 'diagram', 'architecture diagram', 'flow diagram',
  'swimlane', 'quadrant', 'layer stack', 'editorial diagram', '슬라이드용 도식'.
allowed-tools: Read, Write, Edit, Bash, Glob, Grep
---

# Editorial Diagram (단일 HTML + 인라인 SVG)

좌표를 손으로 찍는 SVG는 **규칙 없이 그리면 반드시 어긋난다.** 이 스킬은 산문 조언이
아니라 **고정된 좌표표 + 검증 스크립트**로 그 실패를 막는다. 좌표를 창작하지 말고
[references/geometry.md](references/geometry.md)의 표에서 **읽어 쓴다.**

## 이 스킬을 쓰지 않는 경우

| 요청 | 대신 | 이유 |
|---|---|---|
| 손그림·스케치 톤, README/Devpost | `handdrawn-diagram` | Mermaid `look:handDrawn` |
| 막대·꺾은선·산점도·히트맵 등 **수치 차트** | `dataviz` | 축·스케일·팔레트 규칙이 다름 |
| 화면 레이아웃/와이어프레임 | `screen-spec` | UI 명세 도메인 |
| 목록·전후 비교표·도형 1개 | 그냥 텍스트/표 | 다이어그램이 값을 더하지 않음 |

**판별 질문**: *"잘 쓴 문단 하나보다 이 그림이 더 알려주는가?"* 아니면 그리지 않는다.

## 워크플로우

### Step 1 — 요청 계약 (4요소)

아래 4가지가 확정되어야 그린다. 빠진 것은 **한 번에 묶어** 묻거나, 맥락에서
명백하면 가정하고 **명시적으로 선언**한다.

| 요소 | 예시 | 없으면 생기는 일 |
|---|---|---|
| **내용** | "프론트 → 게이트웨이 → 주문 서비스 → DB" | 무엇을 그릴지 모름 |
| **도착지** | 16:9 슬라이드 / 문서 인라인 / OG 이미지 | 캔버스·타이포 램프 결정 불가 |
| **청중** | 임원 / 혼합 / 엔지니어 | 용어 깊이·노드 수 결정 불가 |
| **강조점** | "주문 서비스 병목만 강조" | 악센트를 어디 쓸지 모름 (→ 전부 균일 = 밋밋) |

### Step 2 — 렌더 전 선언 (필수)

그리기 **전에** 한 단락으로 말한다. 이걸 건너뛰면 사용자는 완성된 뒤에야
잘못된 유형이었음을 안다.

```
유형: 파이프라인 (4노드 가로) · 캔버스: slide-16x9 (1280×720)
강조: 주문 서비스 1개 (퍼플 점)
뺀 것: 캐시 계층, 리트라이 로직 — 임원 청중이라 3단계로 압축
```

### Step 3 — 유형 선택

[references/types.md](references/types.md)에서 고른다. 12개 유형 각각에
"언제 쓰나 / 언제 쓰면 안 되나 / 노드 예산 / 어느 좌표표를 쓰나"가 있다.

### Step 4 — 토큰 로드

[references/tokens.md](references/tokens.md)를 Read. 기본은 **WIGTN Light**.
클라이언트 제안서면 클라이언트 토큰으로 오버라이드(같은 파일에 절차 있음).

### Step 5 — 작성

1. `assets/template.html`을 복사해 시작한다. 스캐폴드에 토큰·마커·a11y·폰트가 이미 있다.
2. [references/geometry.md](references/geometry.md)의 좌표표를 **그대로 옮겨 적는다.**
   계산하지 않는다. 표에 없는 배치가 필요하면 표의 규칙(마진 64, 4의 배수)으로 파생한다.
3. 라벨은 **글자 수 예산**을 지킨다(geometry.md §라벨 예산). 초과하면 줄이거나 `<tspan>` 2줄.

### Step 6 — 검증 (건너뛰지 않는다)

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/editorial-diagram/scripts/check.py" out.html
```

4px 위반·밀도 초과·라벨 오버플로·악센트 남용·a11y 누락·대비 미달을 잡는다.
**FAIL이면 고치고 다시 돌린다.** PASS 후 PNG를 렌더해 눈으로 한 번 더 본다.

### 검증기의 계약 (지키면 통과, 벗어나면 FAIL)

`check.py`는 **임의 SVG 검증기가 아니다.** 브라우저를 다시 구현하지 않으므로,
`template.html`이 만드는 *정규 형태*만 검증하고 그 밖은 조용히 통과시키지 않고 끊는다.
검증할 수 없는 것을 통과시키면 게이트가 꺼진 줄도 모르게 꺼진다.

| 규칙 | 벗어나면 |
|---|---|
| 색은 **3/6자리 HEX 또는 선언된 `var(--토큰)`만** — 토큰뿐 아니라 **모든 도형의 `fill`/`stroke`**에 적용 (`rgb()`·`color-mix()`·색이름 금지, `none`/`transparent`는 허용) | FAIL |
| 노드는 `rect`/`polygon`/`circle`/`ellipse` + `class="node"` (`g`·`path` 노드 금지) | FAIL |
| 폰트 크기는 `px`/`rem`/`em`만 (`pt`·`%`·`calc()` 금지) | FAIL |
| 색·폰트·정렬은 **클래스 규칙**으로 (`text`/`tspan`/`g`의 표현 속성·인라인 style 금지) | FAIL |
| `<g>`는 묶기 전용, `<tspan>`은 줄바꿈 전용 — 둘 다 `class`·`style` 금지 | FAIL |
| 루트 `<svg>`에 `fill`/`stroke`/`font-*`/`text-anchor` 선언 금지 (상속으로 전부 바뀐다) | FAIL |
| `--토큰`은 **루트에서만** 선언 (테마 변형 `[data-theme=…]`은 허용) | FAIL |
| 셀렉터는 `type`/`.class`/`#id`/`[attr]`/`[attr=v]`만 (결합자·부분일치 `^=` 금지, 콤마 목록은 지원) | FAIL |
| 렌더 요소는 화이트리스트만 (`use`/`foreignObject`/`image`/**중첩 `svg`** 금지) | FAIL |
| 좌표에 단위 접미사 금지 (`x="64px"`), `rx`·`ry` ∈ {0,4,8}, 음수 폭 금지 | FAIL |
| 악센트로 초점을 **채우지** 않고, 노드 테두리에 `--line`을 쓰지 않는다 (리터럴 HEX도 검사) | FAIL |
| 캔버스는 `viewBox`로 지정 (export도 여기서 크기를 읽는다) | FAIL |

**다크 블록을 선언하면 다크 팔레트도 함께 검증한다** — 두 테마 모두 대비를 통과해야
한다. `--theme`으로 한쪽만 강제할 수 있다.

`text-anchor`를 지정하지 않으면 **SVG 기본값 `start`**로 측정한다. 가운데 정렬 라벨은
`.node-name`처럼 클래스에 `text-anchor: middle`을 명시해야 한다(템플릿에 이미 있다).

템플릿에서 시작하면 이 계약은 자동으로 지켜진다. 어겼다는 FAIL이 나오면 문법을
템플릿 형태로 되돌리는 게 정답이지, 검증기를 우회할 방법을 찾는 게 아니다.

검증기 자체를 고쳤다면 회귀 스위트를 돌린다(우회 경로마다 픽스처 1개):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/skills/editorial-diagram/scripts/selftest.py"
```

### Step 7 — Export (요청 시)

```bash
bash "${CLAUDE_PLUGIN_ROOT}/skills/editorial-diagram/scripts/export.sh" out.html --scale 2
```

`--svg-only` / `--png-only` / `--scale 3`. 상세는 스크립트 `--help`.

## 하드 규칙 (위반 시 check.py FAIL)

1. **4px 그리드** — **도형**(`rect`/`circle`/`line`/`polygon`/`path`)의 모든 좌표·폭·
   높이·간격·반지름이 4의 배수. 예외: `<text>`의 x/y(광학 중심 정렬), `stroke-width`,
   `opacity`, `font-size`, `viewBox`. 이 규칙 하나가 "어설퍼 보임"의 대부분을 없앤다.
2. **밀도 예산** — 노드 4~5개가 이상적, **9개 초과 금지**. 초과하면 그룹으로 묶거나
   다이어그램을 쪼갠다. *가장 좋은 수정은 삭제다.*
3. **단일 악센트, 1~2개 요소** — 악센트(퍼플)는 초점 요소에만. 나머지는 중립.
   초점은 **화려한 채움이 아니라 WIGTN 시그니처 퍼플 점 + 2px 테두리**로 표시한다.
4. **1px 헤어라인, 그림자 금지, `rx` ∈ {0, 4, 8}** — `rx`도 4px 검사 대상이라 10은 통과하지
   못한다(기본 8). 카드 그림자·글로우·그라데이션 배경 금지.
5. **3폰트 역할 고정** — 제목 Space Grotesk / 노드명 Pretendard / 기술 라벨 JetBrains Mono.
   역할을 섞지 않는다.
6. **a11y** — `role="img"` + `<title>` + `<desc>`, `aria-labelledby`로 연결.
   ID는 다이어그램마다 접두사를 달리한다(한 페이지에 여러 개 인라인될 수 있다).
7. **토큰은 `<svg>` 안 `<style>`에 정의** — HTML `:root`가 아니라. 그래야 `<svg>`만
   떼어내도 그대로 렌더된다(export가 순수 복사가 된다).

## Anti-Patterns

- 노드마다 다른 색 → 위계 소멸. 색은 **의미**일 때만 쓴다(악센트 = 초점, 그 외 중립).
- 커넥터 스파게티. 교차가 3개 이상이면 유형이 틀린 것이다 — 스윔레인이나 레이어로 바꾼다.
- 노드에 문장을 넣기. 노드명은 **명사구**, 부연은 sublabel 한 줄(모노, 13px).
- 이모지 노드 라벨 (PNG 렌더 시 tofu 위험, 톤도 안 맞음).
- 좌표를 눈대중으로 조정하기 → 4px 위반의 주범. 표로 돌아간다.
- 보라 그라데이션 클리셰(`#6366f1` 등) → WIGTN `#9B51E0`만.

## 참조

- **[references/types.md](references/types.md)** — 12개 유형: 선택 기준·노드 예산·좌표표 매핑
- **[references/geometry.md](references/geometry.md)** — 캔버스·좌표표·노드 내부 스펙·라벨 예산
- **[references/tokens.md](references/tokens.md)** — 시맨틱 토큰, WIGTN 기본값, 클라이언트 오버라이드, 대비 규칙
- **`assets/template.html`** — 스캐폴드 (토큰·마커·a11y·폰트 포함)
- **`scripts/check.py`** — 출력 검증기 (fail-closed) · **`scripts/selftest.py`** — 검증기 회귀 스위트 · **`scripts/export.sh`** — SVG/PNG 반출
- **`wigtn-ppt` 스킬** — 슬라이드에 삽입할 때. 이 스킬이 wigtn-ppt Phase 2의 기본 경로다.
- **`handdrawn-diagram` 스킬** — 손그림 톤 대안

> 유형 라우팅·4px 그리드·밀도 예산·시맨틱 토큰 개념은
> [cathrynlavery/diagram-design](https://github.com/cathrynlavery/diagram-design) (MIT)에서
> 차용해 WIGTN 브랜드·한국어 환경에 맞게 재작성했다.

## 체크리스트

- [ ] Step 1: 4요소(내용·도착지·청중·강조점) 확보
- [ ] Step 2: 유형·캔버스·뺀 것을 **렌더 전에** 선언
- [ ] Step 3: types.md에서 유형 확정 (노드 예산 확인)
- [ ] Step 4: tokens.md Read (WIGTN 기본 / 클라이언트 오버라이드)
- [ ] Step 5: template.html 복사 → geometry.md 좌표표 그대로 적용
- [ ] Step 6: `check.py` PASS + PNG 육안 확인
- [ ] Step 7: 요청 시 export (SVG / PNG @2x·@3x)
