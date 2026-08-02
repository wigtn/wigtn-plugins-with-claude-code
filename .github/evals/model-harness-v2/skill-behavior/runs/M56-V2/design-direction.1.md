## 제안 방향: “Ink & Purple Operations”

장식보다 정보 위계와 작업 효율을 강조하는 미니멀 관리자 콘솔입니다. 기존의 잉크색·보라색 조합을 브랜드 축으로 유지하고, 중립 표면과 촘촘한 데이터 컴포넌트를 확장합니다.

### 기존 시스템 근거

[tokens.css](/private/tmp/wigtn-skill-behavior-v1/work/M56-V2/design-direction-1/tokens.css:1)에 이미 핵심 언어가 정의되어 있습니다.

| 기존 토큰 | 해석 | 대시보드 적용 |
|---|---|---|
| `--color-ink: #1E1E28` | 강한 정보색 | 제목, 본문, 주요 수치 |
| `--color-accent: #9B51E0` | 브랜드 액센트 | 주요 액션, 선택 상태, 차트 강조 |
| `--surface: #FAFAFA` | 앱 배경 | 전체 대시보드 캔버스 |
| `--space-2: 8px` | 기본 간격 단위 | 아이콘·라벨, 인라인 요소 |
| `--space-4: 16px` | 컴포넌트 간격 | 카드 내부 여백, 그리드 간격 |
| `--radius-card: 12px` | 부드러운 표면 | KPI·차트·테이블 카드 |

기존 `.card`도 `16px` 패딩과 `12px` 라운드를 사용하므로 이를 기본 카드 규격으로 유지합니다. 현재 [Dashboard.tsx](/private/tmp/wigtn-skill-behavior-v1/work/M56-V2/design-direction-1/Dashboard.tsx:1)의 `Summary` 카드는 KPI 요약 영역으로 확장하기 적합합니다.

### 권장 토큰 확장

기존 값을 교체하지 않고 의미 토큰을 추가하는 방식입니다.

```css
/* 제안 사항 — 실제 파일에는 반영하지 않음 */
--surface-raised: #FFFFFF;
--surface-selected: #F5EDFC;
--color-text-muted: #686872;
--color-border: #E6E4E9;

--space-3: 12px;
--space-6: 24px;

--radius-control: 8px;

--color-success: #16845B;
--color-warning: #A56400;
--color-danger: #C33A4A;

--motion-fast: 150ms;
```

`#9B51E0`과 흰색의 명암비는 약 `4.52:1`이므로 일반 크기 버튼 텍스트에도 사용할 수 있습니다. 반면 보라색 위에 잉크색 텍스트를 올리는 조합은 피하고 흰색을 사용합니다.

### 화면 구성

- 240px 사이드바: 흰색 표면, 선택 메뉴는 연한 보라 배경과 3px 액센트 바
- 상단 헤더: 페이지 제목, 기간 선택, 주요 액션
- KPI 카드 4개: 동일 크기로 수치 비교에 집중
- 본문 2열: 추이 차트 2/3, 상태 요약 1/3
- 하단 전체 폭: 검색·필터가 결합된 데이터 테이블
- 1024px 이하에서는 사이드바를 축소하고 KPI를 2열로 전환

### 컴포넌트 적용 예

**KPI 카드**

```tsx
<section className="card metric-card">
  <span className="metric-label">활성 사용자</span>
  <strong className="metric-value">12,480</strong>
  <span className="metric-change is-positive">+8.4%</span>
</section>
```

- 배경: `--surface-raised`
- 패딩·라운드: 기존 `.card`
- 수치: `--color-ink`
- 증감률만 상태색 적용
- 카드 전체에 보라색을 칠하지 않고, 선택되거나 중요한 KPI에만 상단 액센트 선 사용

**필터와 버튼**

- 기본 컨트롤 높이: 40px
- 좌우 패딩: `--space-3`
- 컨트롤 라운드: `--radius-control`
- Primary 버튼: 보라색 배경 + 흰색 텍스트
- Secondary 버튼: 흰색 배경 + 중립 테두리
- 포커스: 2px 보라색 링과 2px 오프셋

**데이터 테이블**

- 헤더는 연한 중립 표면, 본문은 흰색
- 행 높이 44–48px로 운영 화면의 밀도 확보
- 행 구분은 그림자 대신 `--color-border`
- 선택 행은 `--surface-selected`
- 위험·성공 상태는 별도 상태색으로 표시하고 보라색을 상태 의미로 재사용하지 않음

### 시각 계약

- 타이포그래피: 기존 제품 글꼴 우선, 없으면 시스템 sans-serif. 제목 24/32·600, 카드 제목 14/20·500, 주요 수치 28/36·600, 본문 14/20.
- 표면: 배경 `#FAFAFA`, 카드 `#FFFFFF`, 그림자는 모달·팝오버에만 제한.
- 간격: 8px 리듬을 유지하고 12px는 밀집 컨트롤, 16px는 카드, 24px는 섹션 간격에 사용.
- 모션: hover·focus·정렬 전환만 150ms. KPI 카드의 들썩이는 hover 효과는 사용하지 않음.
- 접근성: 색상 외에 아이콘·텍스트를 함께 사용하고, 테이블 행과 모든 컨트롤에 키보드 포커스를 제공합니다.

파일은 수정하지 않았습니다.