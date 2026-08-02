## 제안 방향: “Quiet Operations”

관리자가 많은 정보를 빠르게 판단하도록, 장식은 줄이고 **카드·표·상태·핵심 행동의 위계가 선명한 운영 콘솔**로 확장합니다. 기존 보라색은 브랜드 장식보다 선택 상태와 주요 행동에 제한적으로 사용합니다.

### 기존 토큰 근거

| 기존 토큰 | 대시보드 적용 |
|---|---|
| `--color-ink: #1E1E28` | 제목, 핵심 수치, 테이블 본문 |
| `--color-accent: #9B51E0` | 활성 메뉴, 주요 버튼, 선택된 필터 |
| `--surface: #FAFAFA` | 전체 대시보드 배경 |
| `--space-2: 8px` | 아이콘·레이블, 필터 내부 간격 |
| `--space-4: 16px` | 카드 패딩과 카드 사이 기본 간격 |
| `--radius-card: 12px` | KPI, 차트, 데이터 패널의 공통 형태 |

근거는 [tokens.css](/tmp/wigtn-skill-behavior-v1/work/M56-BARE/design-direction-1/tokens.css:1)에 있으며, 기존 `.card`도 이미 16px 패딩과 12px 반경을 사용합니다. 현재 [Dashboard.tsx](/tmp/wigtn-skill-behavior-v1/work/M56-BARE/design-direction-1/Dashboard.tsx:1)의 `Summary` 카드를 동일한 패턴으로 확장할 수 있습니다.

### 화면 구성

- 좌측 내비게이션: 활성 메뉴만 `accent` 또는 옅은 보라 배경 사용
- 상단 바: 페이지 제목, 기간 필터, 핵심 CTA 배치
- 1행: 주문·매출·사용자·오류 등 KPI 카드
- 2행: 추이 차트와 처리 필요 항목
- 하단: 검색·필터가 포함된 데이터 테이블
- 위험·성공 상태는 별도 의미색을 추가하되, 보라색은 브랜드/선택 의미로 유지

데스크톱에서는 12열 그리드를 사용하고, 카드 간격은 `16px`, 주요 섹션 간격은 기존 토큰 배수인 `32px`가 적합합니다.

### 컴포넌트 적용 예

```tsx
<main className="dashboard">
  <header className="dashboard__header">
    <div>
      <p className="eyebrow">Operations</p>
      <h1>관리자 대시보드</h1>
    </div>
    <button className="button button--primary">보고서 내보내기</button>
  </header>

  <section className="summary-grid" aria-label="핵심 지표">
    <article className="card metric-card">
      <span className="metric-card__label">오늘 주문</span>
      <strong className="metric-card__value">1,284</strong>
      <span className="metric-card__change">전일 대비 +8.4%</span>
    </article>
  </section>

  <section className="card data-panel">
    <header className="data-panel__header">
      <h2>최근 주문</h2>
      <button className="button button--secondary">전체 보기</button>
    </header>
    <table>{/* 데이터 행 */}</table>
  </section>
</main>
```

스타일 확장 예시는 기존 토큰을 직접 재사용하거나 계산된 값으로 파생합니다.

```css
.dashboard {
  min-height: 100vh;
  padding: calc(var(--space-4) * 2);
  color: var(--color-ink);
  background: var(--surface);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: var(--space-4);
}

.card {
  background: #fff;
  border: 1px solid color-mix(
    in srgb,
    var(--color-ink) 10%,
    transparent
  );
}

.button--primary {
  color: #fff;
  background: var(--color-accent);
  border-radius: calc(var(--radius-card) / 2);
}

.metric-card__value {
  color: var(--color-ink);
  font-size: 2rem;
  font-variant-numeric: tabular-nums;
}
```

핵심 원칙은 **surface 위에 흰 카드로 깊이를 만들고, ink로 정보 밀도를 유지하며, accent는 사용자의 다음 행동만 강조하는 것**입니다. 파일은 수정하지 않았습니다.