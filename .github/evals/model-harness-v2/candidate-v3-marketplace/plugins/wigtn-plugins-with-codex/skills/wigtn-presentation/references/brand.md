# WIGTN Brand System (PPT)

WIGTN 발표자료의 브랜드 토대. **정확한 HEX만 사용한다. "비슷한 색" 금지.**

## 1. 브랜드 정체성

- **워드마크**: `wigtn.` — 소문자, 기하학적 그로테스크 산세리프, 헤비 웨이트
- **시그니처**: 워드마크 끝의 **퍼플 마침표(`.`)**. 이것이 WIGTN의 단 하나뿐인 시그니처 요소다.
- **톤**: 미니멀, 자신감, 테크. 잉크 네이비 위에 퍼플 한 점.

## 2. 컬러 팔레트 (실측 HEX)

| 이름 | HEX | RGB | 비고 |
|------|-----|-----|------|
| Ink | `#1E1E28` | 30, 30, 40 | 워드마크 네이비. Dark 배경 / Light 본문 텍스트 |
| Ink Deep | `#15151E` | 21, 21, 30 | Dark 테마 최하단 배경 |
| Purple | `#9B51E0` | 155, 81, 224 | **시그니처 점** (Pantone 265 계열, 로고 실측) |
| Purple Bright | `#A85FEA` | 168, 95, 234 | Dark 배경에서 점이 더 튀어야 할 때 |
| Purple Deep | `#6B2EAA` | 107, 46, 170 | 점 그림자 / 깊이 / 그라데이션 끝 |
| White | `#FFFFFF` | 255, 255, 255 | Light 배경 / Dark 텍스트 |
| Off-White | `#FAFAFA` | 250, 250, 250 | Light 보조 배경(surface) |

> 그라데이션이 꼭 필요하면 **퍼플 단색 계열만** (`#9B51E0 → #6B2EAA`). 무지개·보라/핑크 클리셰 금지.

## 3. 두 가지 테마 (`:root` 토큰)

발표 환경에 따라 하나를 고른다. 한 발표물 안에서 섞지 않는다.

### Light 테마 (`wigtn-light`) — 밝은 발표장·문서형

```css
:root {
  --bg:            #FFFFFF;
  --surface:       #FAFAFA;
  --surface-2:     #F4F2F8;   /* 퍼플 기 살짝 도는 중립 */
  --text-primary:  #1E1E28;
  --text-secondary:#5A5A6E;
  --accent:        #9B51E0;   /* 시그니처 점·강조 */
  --accent-deep:   #6B2EAA;
  --line:          #E6E3EE;
  --logo:          NAVY;      /* WIGTN_LOGO_NAVY.png / wigtn_mark_dark.png */
}
```

### Dark 테마 (`wigtn-dark`) — 무대·키노트형

```css
:root {
  --bg:            #15151E;
  --surface:       #1E1E28;
  --surface-2:     #26263340;
  --text-primary:  #F5F4FA;
  --text-secondary:#A8A6B8;
  --accent:        #A85FEA;   /* Dark에선 Bright 퍼플로 점을 띄움 */
  --accent-deep:   #6B2EAA;
  --line:          #2C2C3A;
  --logo:          WHITE;     /* WIGTN_LOGO_WHITE.png / wigtn_mark_light.png */
}
```

## 4. 시그니처 퍼플 점 규칙

**모든 슬라이드**에 퍼플 점 모티프를 하나 이상, 일관된 방식으로 반복한다. 슬라이드마다 다른 자리에 흩뿌리지 말고 — 한 발표물 안에서는 한 가지 규칙을 정해 끝까지 유지한다.

가능한 적용처(한 가지를 골라 통일):
- 페이지 번호 옆 점: `12 ●`
- 섹션 번호의 마침표: `01.` 의 점만 퍼플
- 우하단 코너 점 (고정 위치, 지름 ~10px)
- 제목 끝 강조점: `Our Vision●`
- 진행 도트/네비게이션 도트를 퍼플로

점 스펙: 정원, `background: var(--accent)`, 살짝의 `box-shadow: 0 0 0 4px color-mix(in srgb, var(--accent) 18%, transparent)` 정도의 은은한 헤일로 허용(과한 글로우 금지).

```css
.wigtn-dot {              /* 재사용 점 */
  display:inline-block; width:.5em; height:.5em; border-radius:50%;
  background:var(--accent); vertical-align:baseline;
}
```

## 5. 로고 변형 & 사용

5종이 팀 로컬의 `assets/logo/`(또는 `docs/images/`)에 있다 — 둘 다 gitignore라 공개 레포 클론엔 포함되지 않는다(팀원이 별도로 받아 둔다). 테마/맥락에 맞춰 고르고, 없으면 6절의 워드마크 폴백을 쓴다.

| 파일 | 형태 | 사용처 |
|------|------|--------|
| `WIGTN_LOGO_NAVY.png` | 풀 워드마크, 잉크 | **Light 배경**의 표지·헤더 |
| `WIGTN_LOGO_WHITE.png` | 풀 워드마크, 화이트 | **Dark 배경**의 표지·헤더 |
| `wigtn_mark_dark.png` | 정사각 마크(어두움) | Light 배경의 작은 코너 마크 |
| `wigtn_mark_light.png` | 정사각 마크(밝음) | Dark 배경의 작은 코너 마크 |
| `wigtn_mark_purple.png` | 정사각 마크(퍼플 배경, `w.`) | 표지 배지·앱 아이콘 톤. Light/Dark 공용 |

**배치 규칙**
- 표지: 풀 워드마크를 상단 좌측 또는 하단에. 충분한 여백(clear space ≥ 로고 높이의 0.5배).
- 본문/마무리: 작은 마크를 우하단 코너에 고정(섹션·본문 슬라이드 공통). 표지·Thank you에는 코너 마크 대신 풀 워드마크.
- 로고를 늘리거나(비율 왜곡), 회전·그림자·색 변경하지 않는다. 퍼플 점은 로고 자체에 이미 포함되어 있으므로 로고 옆에 점을 또 찍지 않는다.

**삽입 방법**: 사용할 파일을 발표물 워크스페이스(예: `docs/workspace/`)로 복사한 뒤 HTML에서 상대경로(`src="workspace/WIGTN_LOGO_NAVY.png"`)로 참조한다. 스킬 템플릿 절대경로를 직접 쓰지 않는다.

## 6. CSS / SVG 워드마크 폴백 (항상 동작)

PNG가 없어도 워드마크는 단순해서 직접 렌더할 수 있다. 폴백만으로도 브랜드가 성립한다.

```html
<!-- 폰트: 기하학 그로테스크 (Pretendard / Space Grotesk 등) -->
<span class="wigtn-wordmark">wigtn<span class="wigtn-dot-char">.</span></span>
```
```css
.wigtn-wordmark{
  font-family:"Space Grotesk","Pretendard",sans-serif;
  font-weight:700; letter-spacing:-.02em;
  color:var(--text-primary); font-size:clamp(1.4rem,2.4vw,2.2rem);
}
.wigtn-dot-char{ color:var(--accent); }   /* 마침표만 퍼플 */
```

SVG가 필요하면 동일 원칙: 텍스트 `wigtn` + 퍼플 원(점). 점 지름은 글자 높이의 약 22%, 베이스라인에 정렬.

## 7. 타이포그래피

| 역할 | 권장 폰트 | 비고 |
|------|-----------|------|
| Display / 제목 | Space Grotesk, Sora, Clash Grotesk | 기하학 그로테스크, 헤비. 워드마크 톤과 일치 |
| 본문 (한국어 포함) | Pretendard, Noto Sans KR | 한글·영문·숫자 한 서체 톤으로 통일 |
| 코드 | JetBrains Mono, IBM Plex Mono | 필요 시 |

- 한국어가 포함되면 **Pretendard**를 기본으로. Google Fonts/CDN `<link>` 1줄로 로드.
- 위계: 제목 SemiBold/Bold, 본문 Regular/Medium, 캡션 Light. 한 슬라이드에 3단계 이내.

## 8. Do / Don't

**Do** — 정확한 HEX, 퍼플 점 일관 반복, 넉넉한 여백, 테마 1택, 잉크+퍼플 절제.
**Don't** — 비슷한 보라색 대체, 점 누락/남발, 로고 왜곡, 테마 혼용, 보라/핑크 그라데이션 클리셰, 가운데 정렬 떡칠.
