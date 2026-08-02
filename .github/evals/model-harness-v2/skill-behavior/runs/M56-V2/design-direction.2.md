## 제안 방향: “Quiet Control”

장식은 줄이고 운영 상태와 우선순위가 빠르게 읽히는 미니멀 관리자 대시보드입니다. 기존 보라색은 브랜드 장식이 아니라 **선택·포커스·핵심 행동을 알리는 신호색**으로 제한합니다.

### 기존 시스템 근거

현재 확인되는 디자인 언어는 다음과 같습니다.

| 기존 토큰 | 역할 | 대시보드 적용 |
|---|---|---|
| `--color-ink: #1E1E28` | 강한 전경색 | 제목, 주요 수치, 사이드바 |
| `--color-accent: #9B51E0` | 단일 강조색 | 현재 메뉴, 주 버튼, 포커스 링 |
| `--surface: #FAFAFA` | 밝은 중성 배경 | 전체 대시보드 캔버스 |
| `--space-2: 8px` | 기본 간격 | 아이콘·라벨, 테이블 셀 내부 간격 |
| `--space-4: 16px` | 컴포넌트 간격 | 카드 패딩, 필터 그룹, 그리드 간격 |
| `--radius-card: 12px` | 부드러운 표면 형태 | KPI·차트·테이블 카드 |

근거는 [tokens.css](/tmp/wigtn-skill-behavior-v1/work/M56-V2/design-direction-2/tokens.css:1)에 있으며, 기존 `Dashboard`도 이미 `.card`를 기본 콘텐츠 단위로 사용합니다. [Dashboard.tsx](/tmp/wigtn-skill-behavior-v1/work/M56-V2/design-direction-2/Dashboard.tsx:1)

### 확장 계약

- 타이포그래피: 별도 폰트 토큰이 없으므로 우선 제품 기본 sans-serif를 유지합니다. 페이지 제목 24px/600, 카드 제목 14px/600, 본문·테이블 14px/400, 보조 정보 12px/400을 권장합니다. KPI와 숫자 열에는 `font-variant-numeric: tabular-nums`를 적용합니다.
- 색상: `ink`는 정보, `accent`는 조작과 선택에 사용합니다. 성공·경고·오류는 보라색 변형으로 표현하지 않고 별도의 의미 토큰을 추가해야 합니다.
- 간격: 8px 단위를 기본 리듬으로 유지합니다. 카드 내부 16px, 카드 간 16px, 페이지 가장자리 24px, 큰 섹션 사이 32px처럼 확장합니다.
- 표면: `--surface`는 페이지 배경으로 두고, 카드에는 흰색 표면과 `ink` 10–12% 수준의 얇은 경계를 추가합니다. 그림자는 모달·팝오버처럼 실제로 떠 있는 요소에만 씁니다.
- 모서리: 카드는 기존 12px을 그대로 사용합니다. 입력·버튼은 카드보다 작은 8px을 제안해 계층을 구분합니다.
- 인터랙션: hover는 배경 또는 테두리 변화만, focus는 2px 보라색 링, active는 색 농도 변화로 표현합니다. 카드 자체를 불필요하게 떠오르게 만들지 않습니다.
- 모션: 120–160ms의 짧은 상태 전환만 사용하고 `prefers-reduced-motion`을 지원합니다.
- 접근성: `#9B51E0` 위 흰색 텍스트 대비는 약 4.52:1이므로 일반 텍스트의 AA 경계는 충족합니다. 작은 텍스트나 얇은 글꼴은 피하고, 상태는 색상뿐 아니라 아이콘과 문구를 함께 표시합니다.

권장하는 의미 토큰 확장 방식은 다음과 같습니다.

```css
/* 제안이며 현재 파일에는 반영하지 않음 */
--surface-card: #FFFFFF;
--color-border: color-mix(in srgb, var(--color-ink) 12%, transparent);
--color-muted: color-mix(in srgb, var(--color-ink) 62%, white);
--color-accent-soft: color-mix(in srgb, var(--color-accent) 10%, white);

--space-3: 12px;
--space-6: 24px;
--space-8: 32px;
--radius-control: 8px;
```

### 컴포넌트 적용 예

```tsx
<main className="dashboard">
  <header className="pageHeader">
    <div>
      <h1>운영 현황</h1>
      <p>최근 업데이트: 2분 전</p>
    </div>
    <button className="button buttonPrimary">보고서 내보내기</button>
  </header>

  <section className="metricGrid" aria-label="핵심 지표">
    <article className="card metricCard">
      <span className="metricLabel">활성 사용자</span>
      <strong className="metricValue">12,480</strong>
      <span className="trend trendPositive">↑ 8.4%</span>
    </article>
  </section>

  <section className="card tableCard">
    <header className="cardHeader">
      <h2>처리 대기 항목</h2>
      <button className="button buttonSecondary">전체 보기</button>
    </header>
    <table>{/* 상태, 담당자, 갱신 시각, 행 작업 */}</table>
  </section>
</main>
```

적용 원칙은 다음과 같습니다.

- KPI 카드는 기존 `.card`의 `16px` 패딩과 `12px` 라운드를 그대로 상속합니다.
- KPI 숫자는 `ink`, 상승·하락 값은 별도 상태색을 사용합니다.
- 활성 사이드바 항목은 `accent-soft` 배경과 `accent` 아이콘으로 표시합니다.
- 테이블 헤더는 카드 안에서 별도 회색 박스를 만들지 않고 얇은 구분선으로 계층화합니다.
- 행 작업은 기본적으로 숨기지 말고 마지막 열에 일관되게 배치합니다.
- 보라색 그라데이션, 과도한 그림자, 모든 카드의 강조색 테두리, 상태값을 전부 보라색으로 표현하는 패턴은 피합니다.

파일은 수정하지 않았습니다.