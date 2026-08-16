# Tokens — 시맨틱 8개 + 폰트 3개

다이어그램은 **브랜드를 직접 참조하지 않는다.** 항상 시맨틱 토큰만 쓰고, 브랜드는
토큰에 값을 주입한다. 그래야 같은 도식을 WIGTN 톤으로도, 클라이언트 톤으로도 렌더할 수 있다.

## 1. 시맨틱 토큰 (이 8개가 전부)

| 토큰 | 역할 | 쓰는 곳 |
|---|---|---|
| `--paper` | 캔버스 배경 | `<rect>` 전체 배경 |
| `--paper-2` | 노드·컨테이너 채움 | 노드 rect, 레인 줄무늬 |
| `--ink` | 1차 텍스트 | 제목, 노드명 |
| `--muted` | 2차 텍스트 | sublabel, 축 라벨, 각주 |
| `--line` | **장식용** 얇은 선 | 격자, 구분선, 점선 그룹 박스 |
| `--line-strong` | **의미 있는** 선 | 노드 테두리, 커넥터, 축 |
| `--accent` | 초점 1~2개 | 초점 노드 테두리 + 시그니처 점 |
| `--accent-deep` | 악센트 보조 | 점 그림자/헤일로 (선택) |

### 절대 규칙

- **`--accent`는 텍스트 색으로 쓰지 않는다.** Light/Dark 양쪽에서 본문 크기 대비
  4.5:1을 못 넘긴다(`--paper-2` 위에서 각각 4.07:1, 4.32:1). `--paper` 위에서는 각각
  4.52:1 / 4.74:1로 아슬하게 통과하지만, 노드는 `--paper-2`로 채우므로 **최악값이 규칙을
  정한다.** 악센트는 **테두리와 점**만.
- **노드 테두리는 `--line-strong`.** `--line`은 대비가 1.3:1 수준이라 노드 경계로
  쓰면 접근성 위반이다. `--line`은 격자·구분선 같은 장식 전용.
- 채움으로 위계를 만들지 않는다. 위계는 **위치·크기·악센트 1개**로 낸다.

## 2. WIGTN 기본값

`assets/template.html`에 이미 들어 있다. 값은 [wigtn-ppt/references/brand.md](../../wigtn-ppt/references/brand.md)의 실측 HEX에서 유도했다.

### Light (기본)

```css
svg.ed { /* :root 아니라 svg에 정의 — SVG만 떼어내도 렌더되게 */
  --paper:        #FFFFFF;
  --paper-2:      #F4F2F8;   /* brand surface-2 */
  --ink:          #1E1E28;   /* brand Ink */
  --muted:        #5A5A6E;   /* brand text-secondary */
  --line:         #E6E3EE;   /* brand line — 장식 전용 */
  --line-strong:  #85819B;   /* 유도값: 흰 배경 대비 3.74:1 */
  --accent:       #9B51E0;   /* brand Purple (시그니처) */
  --accent-deep:  #6B2EAA;
}
```

### Dark

```css
svg.ed[data-theme="dark"] {
  --paper:        #15151E;   /* brand Ink Deep */
  --paper-2:      #1E1E28;   /* brand Ink */
  --ink:          #F5F4FA;
  --muted:        #A8A6B8;
  --line:         #2C2C3A;
  --line-strong:  #6E6C84;   /* 유도값: Ink Deep 대비 3.58:1 */
  --accent:       #A85FEA;   /* brand Purple Bright */
  --accent-deep:  #6B2EAA;
}
```

### 검산된 대비 (WCAG)

| 조합 | 비율 | 기준 |
|---|---|---|
| Light `--ink` on `--paper-2` | 14.9:1 | AA 본문 4.5 ✓ |
| Light `--muted` on `--paper-2` | 6.1:1 | AA 본문 4.5 ✓ |
| Light `--line-strong` on `--paper` | 3.7:1 | 비텍스트 3.0 ✓ |
| Dark `--ink` on `--paper-2` | 15.1:1 | AA 본문 4.5 ✓ |
| Dark `--muted` on `--paper-2` | 6.9:1 | AA 본문 4.5 ✓ |
| Dark `--line-strong` on `--paper` | 3.6:1 | 비텍스트 3.0 ✓ |

`check.py`가 이 계산을 실제 토큰 값으로 다시 돌린다 — 오버라이드해도 검증된다.

## 3. 폰트 — 역할 3개, 섞지 않는다

| 역할 | 폰트 | 스펙 | 쓰는 곳 |
|---|---|---|---|
| **title** | Space Grotesk 600 | 28px / `--ink` | 다이어그램 제목 |
| **node-name** | Pretendard 500 | 18px / `--ink` | 노드명, 레인명, 축 이름 |
| **sublabel** | JetBrains Mono 400 | 13px / `--muted` | 기술 라벨, 수치, 각주(12px) |

- 한글이 들어가면 노드명은 **반드시 Pretendard** (Space Grotesk에 한글 글리프가 없다).
- 제목이 한글이면 title 역할도 Pretendard 600으로 대체한다.
- 폴백 스택은 template.html에 이미 있다. 폰트가 로드 실패해도 레이아웃이 깨지지
  않도록 폭 예산(geometry.md §7)은 항상 지킨다.

## 4. 클라이언트 브랜드 오버라이드

WIGTN이 아닌 제안서·납품물에서는 아래 절차로 토큰만 갈아끼운다. **구조·간격·
4px 규칙은 그대로 둔다.**

1. 클라이언트 홈페이지/브랜드 가이드에서 채집:
   - 배경색 → `--paper`
   - 본문 텍스트색 → `--ink`
   - 보조 텍스트색 → `--muted`
   - 카드/섹션 배경 → `--paper-2`
   - CTA·링크색 → `--accent`
   - 제목 폰트 / 본문 폰트 / 코드 폰트 → title / node-name / sublabel
2. `--line`, `--line-strong`은 대개 브랜드에 없다. `--ink`를 `--paper` 쪽으로
   섞어 만든다 — `--line` ≈ 12% ink, `--line-strong` ≈ 45% ink. 그 뒤 3:1을 검산.
3. `check.py`를 돌려 대비 FAIL이 나오면 **조정하고 그 사실을 사용자에게 말한다.**
   조용히 브랜드 색을 바꾸지 않는다.
4. **출처 영수증**을 남긴다: 어느 URL의 어느 값에서 왔고, 무엇을 대비 때문에
   조정했는지 한 단락. 나중에 브랜드팀과 다툴 일을 없앤다.

> 이 스킬은 클라이언트 홈페이지를 자동으로 크롤링하지 않는다. 사용자가 URL이나
> 브랜드 가이드를 주면 그때 채집한다.
