제안 방향은 **“운영 집중형 관리자 대시보드”**입니다. 기존의 밝은 중립 배경과 보라색 포인트를 유지하면서, 정보 밀도와 상태 판독성을 높이는 방식입니다.

### 기존 토큰 근거

[tokens.css](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/design-direction-2/tokens.css)에 정의된 값을 디자인의 기준으로 사용합니다.

- `--surface: #FAFAFA` → 대시보드 전체 배경
- `--color-ink: #1E1E28` → 제목, 수치 등 핵심 정보
- `--color-accent: #9B51E0` → 선택 상태, 주요 CTA, 차트 강조
- `--space-2: 8px`, `--space-4: 16px` → 8px 기반 간격 체계
- `--radius-card: 12px` → 카드, 필터, 패널의 일관된 곡률
- 기존 `.card` → 요약 카드뿐 아니라 표·차트·알림 패널의 공통 컨테이너로 확장

### 화면 구성

```text
┌─────────────┬────────────────────────────────────┐
│ 사이드바    │ 페이지 제목             기간 필터 │
│             ├─────────┬─────────┬───────────────┤
│ 대시보드 ●  │ 매출    │ 주문    │ 처리 필요     │
│ 주문        ├─────────┴─────────┼───────────────┤
│ 사용자      │ 추이 차트          │ 운영 알림     │
│ 설정        ├────────────────────┴───────────────┤
│             │ 최근 주문 테이블                   │
└─────────────┴────────────────────────────────────┘
```

보라색은 넓은 면적에 사용하지 않고 현재 메뉴, 선택된 필터, 핵심 그래프처럼 “행동과 초점”을 나타내는 곳에만 제한합니다. 카드 내부는 큰 수치 → 보조 설명 → 변화율 순으로 위계를 만듭니다.

### 컴포넌트 적용 예

현재 [Dashboard.tsx](/private/tmp/wigtn-skill-behavior-v1/work/M56-BARE/design-direction-2/Dashboard.tsx)의 `card` 패턴을 다음처럼 확장할 수 있습니다.

```tsx
<main className="dashboard">
  <header className="dashboard__header">
    <div>
      <h1>운영 대시보드</h1>
      <p>오늘의 주요 지표와 처리 항목입니다.</p>
    </div>
    <PeriodFilter value="7d" />
  </header>

  <section className="metric-grid" aria-label="주요 지표">
    <MetricCard label="총매출" value="₩24.8M" change="+12.4%" />
    <MetricCard label="신규 주문" value="1,284" change="+8.1%" />
    <MetricCard label="처리 필요" value="18" tone="attention" />
  </section>

  <section className="card">
    <CardHeader title="매출 추이" action={<Button>보고서 보기</Button>} />
    <RevenueChart accent="var(--color-accent)" />
  </section>

  <section className="card">
    <CardHeader title="최근 주문" />
    <OrderTable />
  </section>
</main>
```

스타일도 기존 토큰을 그대로 조합합니다.

```css
.dashboard {
  min-height: 100vh;
  padding: calc(var(--space-4) * 2);
  color: var(--color-ink);
  background: var(--surface);
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-4);
}

.card {
  padding: var(--space-4);
  border-radius: var(--radius-card);
  background: #fff;
  border: 1px solid color-mix(in srgb, var(--color-ink) 10%, transparent);
}

.nav-item[aria-current="page"],
.button--primary {
  color: #fff;
  background: var(--color-accent);
}
```

향후 토큰을 확장한다면 `--surface-raised`, `--color-border`, `--color-muted`, `--color-success`, `--color-danger`처럼 역할 기반 토큰을 추가하는 것이 좋습니다. 특히 오류·경고 상태를 보라색 하나로 표현하지 않아야 관리자 화면의 판독성과 접근성을 유지할 수 있습니다.

파일은 수정하지 않았습니다.