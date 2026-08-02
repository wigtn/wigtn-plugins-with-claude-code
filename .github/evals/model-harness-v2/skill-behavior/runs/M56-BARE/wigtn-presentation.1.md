아래 HTML은 WIGTN [공식 홈페이지](https://wigtn.com/)의 소개와 활동 내용을 반영한 4장 구성입니다. 외부 폰트·이미지·라이브러리 없이 동작하며 파일은 생성하지 않았습니다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta
    name="viewport"
    content="width=device-width, initial-scale=1, viewport-fit=cover"
  />
  <meta name="theme-color" content="#111A36" />
  <title>wigtn. — Company Introduction</title>

  <style>
    /*
      WIGTN BRAND TOKENS
      Navy  : #111A36
      Purple: #7557FF
      Cream : #F6F4EE
      White : #FFFFFF
      Ink   : #14162B
    */
    :root {
      --wigtn-navy: #111A36;
      --wigtn-purple: #7557FF;
      --wigtn-cream: #F6F4EE;
      --wigtn-white: #FFFFFF;
      --wigtn-ink: #14162B;
      --wigtn-muted: #77788B;
      --wigtn-line: rgba(17, 26, 54, 0.14);

      --slide-width: 1600;
      --slide-height: 900;
      --ease: cubic-bezier(.22, 1, .36, 1);
    }

    * {
      box-sizing: border-box;
    }

    html,
    body {
      width: 100%;
      height: 100%;
      margin: 0;
      overflow: hidden;
      background: #090E20;
    }

    body {
      color: var(--wigtn-ink);
      font-family:
        Inter, Pretendard, "Noto Sans KR", "Apple SD Gothic Neo",
        "Segoe UI", Arial, sans-serif;
      -webkit-font-smoothing: antialiased;
      word-break: keep-all;
    }

    button,
    a {
      font: inherit;
    }

    button:focus-visible,
    a:focus-visible {
      outline: 3px solid var(--wigtn-purple);
      outline-offset: 4px;
    }

    .presentation {
      position: fixed;
      inset: 0;
      display: grid;
      place-items: center;
      background:
        radial-gradient(
          circle at 50% 20%,
          rgba(117, 87, 255, 0.16),
          transparent 42%
        ),
        #090E20;
    }

    .deck {
      position: relative;
      width: 1600px;
      height: 900px;
      overflow: hidden;
      background: var(--wigtn-cream);
      box-shadow: 0 40px 100px rgba(0, 0, 0, 0.42);
      transform-origin: center;
    }

    .slide {
      position: absolute;
      inset: 0;
      display: grid;
      padding: 68px 76px 62px;
      overflow: hidden;
      visibility: hidden;
      opacity: 0;
      transform: translateX(50px);
      transition:
        opacity 500ms var(--ease),
        transform 650ms var(--ease),
        visibility 500ms;
    }

    .slide.active {
      z-index: 2;
      visibility: visible;
      opacity: 1;
      transform: translateX(0);
    }

    .slide.previous {
      transform: translateX(-50px);
    }

    .slide::before {
      content: "";
      position: absolute;
      right: -180px;
      bottom: -260px;
      width: 620px;
      height: 620px;
      border: 1px solid rgba(117, 87, 255, 0.14);
      border-radius: 50%;
      pointer-events: none;
    }

    .slide::after {
      content: "";
      position: absolute;
      right: -60px;
      bottom: -140px;
      width: 380px;
      height: 380px;
      border: 1px solid rgba(117, 87, 255, 0.18);
      border-radius: 50%;
      pointer-events: none;
    }

    .brand-header {
      position: absolute;
      z-index: 5;
      top: 58px;
      left: 76px;
      right: 76px;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .wordmark {
      color: inherit;
      font-size: 31px;
      font-weight: 850;
      line-height: 1;
      letter-spacing: -1.8px;
      text-decoration: none;
    }

    .wordmark-period {
      color: var(--wigtn-purple);
    }

    /*
      동일한 위치·크기를 유지하는 WIGTN 퍼플 점.
      모든 슬라이드의 우측 상단에 표시된다.
    */
    .purple-dot {
      width: 18px;
      height: 18px;
      flex: 0 0 18px;
      border-radius: 50%;
      background: var(--wigtn-purple);
      box-shadow: 0 0 0 7px rgba(117, 87, 255, 0.10);
    }

    .eyebrow {
      display: flex;
      gap: 14px;
      align-items: center;
      margin: 0 0 25px;
      color: var(--wigtn-purple);
      font-size: 15px;
      font-weight: 800;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .eyebrow::before {
      width: 36px;
      height: 2px;
      content: "";
      background: currentColor;
    }

    h1,
    h2,
    h3,
    p {
      margin-top: 0;
    }

    h1,
    h2,
    h3 {
      letter-spacing: -0.055em;
    }

    h1 {
      max-width: 1160px;
      margin-bottom: 34px;
      font-size: 104px;
      font-weight: 840;
      line-height: 0.98;
    }

    h2 {
      max-width: 1050px;
      margin-bottom: 24px;
      font-size: 76px;
      font-weight: 820;
      line-height: 1.02;
    }

    .accent {
      color: var(--wigtn-purple);
    }

    .lead {
      max-width: 880px;
      color: var(--wigtn-muted);
      font-size: 25px;
      font-weight: 520;
      line-height: 1.6;
      letter-spacing: -0.025em;
    }

    .slide-number {
      position: absolute;
      z-index: 4;
      right: 76px;
      bottom: 52px;
      display: flex;
      align-items: center;
      gap: 13px;
      color: var(--wigtn-muted);
      font-size: 14px;
      font-weight: 750;
      letter-spacing: 0.12em;
    }

    .slide-number::before {
      width: 45px;
      height: 1px;
      content: "";
      background: currentColor;
      opacity: 0.5;
    }

    /* Slide 01 */
    .hero {
      grid-template-rows: 1fr auto;
      padding-top: 190px;
      background:
        linear-gradient(
          115deg,
          rgba(117, 87, 255, 0.07),
          transparent 37%
        ),
        var(--wigtn-cream);
    }

    .hero-copy {
      align-self: center;
      transform: translateY(-28px);
    }

    .hero h1 {
      max-width: 1250px;
    }

    .hero-meta {
      display: grid;
      grid-template-columns: 1.45fr 0.75fr 0.75fr;
      gap: 0;
      width: calc(100% - 130px);
      border-top: 1px solid var(--wigtn-line);
    }

    .meta-item {
      min-height: 112px;
      padding: 25px 35px 0 0;
    }

    .meta-item + .meta-item {
      padding-left: 34px;
      border-left: 1px solid var(--wigtn-line);
    }

    .meta-label {
      display: block;
      margin-bottom: 11px;
      color: var(--wigtn-muted);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }

    .meta-value {
      font-size: 20px;
      font-weight: 720;
      letter-spacing: -0.025em;
    }

    .orb {
      position: absolute;
      top: 250px;
      right: 80px;
      width: 210px;
      height: 210px;
      border-radius: 50%;
      background:
        radial-gradient(
          circle at 34% 28%,
          #A996FF,
          var(--wigtn-purple) 46%,
          #39209F 100%
        );
      box-shadow:
        0 35px 65px rgba(67, 44, 177, 0.24),
        inset -16px -20px 45px rgba(17, 26, 54, 0.24);
    }

    .orb::after {
      position: absolute;
      top: 20%;
      left: 22%;
      width: 38%;
      height: 22%;
      content: "";
      border-radius: 50%;
      background: rgba(255, 255, 255, 0.22);
      filter: blur(12px);
      transform: rotate(-24deg);
    }

    /* Slide 02 */
    .activities {
      grid-template-rows: auto 1fr;
      padding-top: 172px;
      background: var(--wigtn-white);
    }

    .section-intro {
      display: flex;
      align-items: end;
      justify-content: space-between;
      margin-bottom: 44px;
    }

    .section-intro .lead {
      max-width: 500px;
      margin-bottom: 4px;
      font-size: 21px;
    }

    .activity-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      min-height: 390px;
      border-top: 1px solid var(--wigtn-line);
      border-bottom: 1px solid var(--wigtn-line);
    }

    .activity-card {
      position: relative;
      padding: 34px 30px 30px 0;
    }

    .activity-card + .activity-card {
      padding-left: 30px;
      border-left: 1px solid var(--wigtn-line);
    }

    .activity-index {
      display: block;
      margin-bottom: 72px;
      color: var(--wigtn-purple);
      font-size: 14px;
      font-weight: 850;
      letter-spacing: 0.1em;
    }

    .activity-card h3 {
      min-height: 76px;
      margin-bottom: 22px;
      font-size: 31px;
      font-weight: 790;
      line-height: 1.14;
    }

    .activity-card p {
      max-width: 265px;
      margin-bottom: 28px;
      color: var(--wigtn-muted);
      font-size: 17px;
      line-height: 1.55;
    }

    .tag-list {
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }

    .tag {
      padding: 8px 11px;
      border: 1px solid rgba(117, 87, 255, 0.24);
      border-radius: 999px;
      color: var(--wigtn-purple);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: 0.04em;
    }

    /* Slide 03 */
    .proof {
      grid-template-columns: 0.9fr 1.1fr;
      gap: 82px;
      padding-top: 175px;
      color: var(--wigtn-white);
      background: var(--wigtn-navy);
    }

    .proof::before,
    .proof::after {
      border-color: rgba(117, 87, 255, 0.28);
    }

    .proof .brand-header {
      color: var(--wigtn-white);
    }

    .proof-copy {
      align-self: start;
    }

    .proof-copy h2 {
      max-width: 560px;
      margin-bottom: 33px;
    }

    .proof-copy .lead {
      max-width: 545px;
      color: rgba(255, 255, 255, 0.58);
      font-size: 21px;
    }

    .proof-list {
      align-self: start;
      border-top: 1px solid rgba(255, 255, 255, 0.18);
    }

    .proof-item {
      display: grid;
      grid-template-columns: 145px 1fr;
      gap: 30px;
      padding: 27px 0 29px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.18);
    }

    .proof-value {
      color: var(--wigtn-purple);
      font-size: 45px;
      font-weight: 840;
      line-height: 1;
      letter-spacing: -0.06em;
    }

    .proof-label {
      margin-bottom: 8px;
      color: var(--wigtn-white);
      font-size: 20px;
      font-weight: 720;
      letter-spacing: -0.025em;
    }

    .proof-description {
      margin: 0;
      color: rgba(255, 255, 255, 0.52);
      font-size: 15px;
      line-height: 1.5;
    }

    .proof .slide-number {
      color: rgba(255, 255, 255, 0.5);
    }

    /* Slide 04 */
    .closing {
      place-items: center;
      padding: 120px;
      color: var(--wigtn-white);
      text-align: center;
      background:
        radial-gradient(
          circle at 50% 52%,
          rgba(117, 87, 255, 0.34),
          transparent 31%
        ),
        var(--wigtn-navy);
    }

    .closing::before {
      right: auto;
      bottom: auto;
      width: 720px;
      height: 720px;
      border-color: rgba(117, 87, 255, 0.24);
    }

    .closing::after {
      right: auto;
      bottom: auto;
      width: 510px;
      height: 510px;
      border-color: rgba(117, 87, 255, 0.33);
    }

    .closing .brand-header {
      color: var(--wigtn-white);
    }

    .closing-content {
      position: relative;
      z-index: 2;
      max-width: 1160px;
    }

    .closing .eyebrow {
      justify-content: center;
    }

    .closing h2 {
      max-width: 1080px;
      margin: 0 auto 34px;
      font-size: 88px;
    }

    .closing .lead {
      max-width: 760px;
      margin: 0 auto 40px;
      color: rgba(255, 255, 255, 0.64);
      font-size: 22px;
    }

    .contact-link {
      display: inline-flex;
      align-items: center;
      gap: 15px;
      padding: 17px 25px;
      border: 1px solid rgba(255, 255, 255, 0.26);
      border-radius: 999px;
      color: var(--wigtn-white);
      font-size: 17px;
      font-weight: 760;
      text-decoration: none;
      transition:
        background 180ms ease,
        border-color 180ms ease,
        transform 180ms ease;
    }

    .contact-link::after {
      content: "↗";
      color: var(--wigtn-purple);
      font-size: 20px;
    }

    .contact-link:hover {
      border-color: var(--wigtn-purple);
      background: rgba(117, 87, 255, 0.12);
      transform: translateY(-2px);
    }

    .closing .slide-number {
      color: rgba(255, 255, 255, 0.5);
    }

    /* Navigation */
    .controls {
      position: fixed;
      z-index: 20;
      right: max(24px, env(safe-area-inset-right));
      bottom: max(22px, env(safe-area-inset-bottom));
      display: flex;
      gap: 8px;
      align-items: center;
      padding: 7px;
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 999px;
      background: rgba(9, 14, 32, 0.82);
      box-shadow: 0 12px 30px rgba(0, 0, 0, 0.22);
      backdrop-filter: blur(14px);
    }

    .control-button {
      display: grid;
      width: 38px;
      height: 38px;
      padding: 0;
      border: 0;
      border-radius: 50%;
      place-items: center;
      color: var(--wigtn-white);
      background: transparent;
      cursor: pointer;
    }

    .control-button:hover {
      background: rgba(255, 255, 255, 0.1);
    }

    .control-button:disabled {
      cursor: default;
      opacity: 0.28;
    }

    .counter {
      min-width: 52px;
      color: rgba(255, 255, 255, 0.74);
      font-size: 12px;
      font-weight: 800;
      letter-spacing: 0.08em;
      text-align: center;
    }

    .progress {
      position: fixed;
      z-index: 21;
      bottom: 0;
      left: 0;
      width: 25%;
      height: 3px;
      background: var(--wigtn-purple);
      transition: width 420ms var(--ease);
    }

    .keyboard-help {
      position: fixed;
      z-index: 20;
      bottom: 31px;
      left: max(26px, env(safe-area-inset-left));
      color: rgba(255, 255, 255, 0.52);
      font-size: 11px;
      font-weight: 650;
      letter-spacing: 0.05em;
    }

    @media (max-width: 760px) {
      .keyboard-help {
        display: none;
      }

      .controls {
        right: 50%;
        transform: translateX(50%);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .slide,
      .progress,
      .contact-link {
        transition: none;
      }
    }

    @media print {
      @page {
        size: 16in 9in;
        margin: 0;
      }

      html,
      body {
        width: auto;
        height: auto;
        overflow: visible;
        background: white;
      }

      .presentation {
        position: static;
        display: block;
        background: white;
      }

      .deck {
        width: 1600px;
        height: auto;
        overflow: visible;
        box-shadow: none;
        transform: none !important;
      }

      .slide {
        position: relative;
        width: 1600px;
        height: 900px;
        visibility: visible;
        opacity: 1;
        transform: none;
        page-break-after: always;
        break-after: page;
      }

      .controls,
      .progress,
      .keyboard-help {
        display: none;
      }
    }
  </style>
</head>

<body>
  <main
    class="presentation"
    aria-label="WIGTN 회사소개 프레젠테이션"
  >
    <div class="deck" id="deck">

      <!-- 01 / Cover -->
      <section
        class="slide hero active"
        aria-label="1장: WIGTN 소개"
        aria-hidden="false"
      >
        <header class="brand-header">
          <a class="wordmark" href="https://wigtn.com">
            wigtn<span class="wordmark-period">.</span>
          </a>
          <span class="purple-dot" aria-label="WIGTN 퍼플 점"></span>
        </header>

        <div class="hero-copy">
          <p class="eyebrow">AI-native builder crew</p>
          <h1>
            We learn, build,<br />
            and share AI <span class="accent">in the open.</span>
          </h1>
          <p class="lead">
            WIGTN은 연구하고, 만들고, 배운 것을 다시 공개하는
            AI 빌더 커뮤니티입니다.
          </p>
        </div>

        <div class="hero-meta">
          <div class="meta-item">
            <span class="meta-label">What we are</span>
            <span class="meta-value">Open community of AI builders</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Based in</span>
            <span class="meta-value">Seoul, Korea</span>
          </div>
          <div class="meta-item">
            <span class="meta-label">Established</span>
            <span class="meta-value">2025</span>
          </div>
        </div>

        <div class="orb" aria-hidden="true"></div>
        <div class="slide-number">01 / 04</div>
      </section>

      <!-- 02 / Activities -->
      <section
        class="slide activities"
        aria-label="2장: 주요 활동"
        aria-hidden="true"
      >
        <header class="brand-header">
          <a class="wordmark" href="https://wigtn.com">
            wigtn<span class="wordmark-period">.</span>
          </a>
          <span class="purple-dot" aria-label="WIGTN 퍼플 점"></span>
        </header>

        <div class="section-intro">
          <div>
            <p class="eyebrow">Activities · 01–04</p>
            <h2>What we do <span class="accent">together.</span></h2>
          </div>
          <p class="lead">
            오픈 연구에서 오픈소스까지,
            그리고 배움을 직접 나누는 커뮤니티까지.
          </p>
        </div>

        <div class="activity-grid">
          <article class="activity-card">
            <span class="activity-index">01</span>
            <h3>Open<br />Research</h3>
            <p>
              AI를 공개적으로 연구하고,
              실험과 발견을 논문과 벤치마크로 공유합니다.
            </p>
            <div class="tag-list">
              <span class="tag">ACL</span>
              <span class="tag">EMNLP</span>
              <span class="tag">Benchmarks</span>
            </div>
          </article>

          <article class="activity-card">
            <span class="activity-index">02</span>
            <h3>Open<br />Source</h3>
            <p>
              모델과 도구, 플러그인을 실제로 사용할 수 있는
              코드로 공개합니다.
            </p>
            <div class="tag-list">
              <span class="tag">GitHub</span>
              <span class="tag">Hugging Face</span>
              <span class="tag">npm</span>
            </div>
          </article>

          <article class="activity-card">
            <span class="activity-index">03</span>
            <h3>Meetups &amp;<br />Seminars</h3>
            <p>
              빌더들이 직접 만나 지식과 시행착오,
              실제 데모를 나눕니다.
            </p>
            <div class="tag-list">
              <span class="tag">Meetups</span>
              <span class="tag">Seminars</span>
              <span class="tag">Study</span>
            </div>
          </article>

          <article class="activity-card">
            <span class="activity-index">04</span>
            <h3>Hackathons &amp;<br />Challenges</h3>
            <p>
              팀으로 빠르게 만들고 공개하며,
              아이디어를 작동하는 결과로 증명합니다.
            </p>
            <div class="tag-list">
              <span class="tag">Team builds</span>
              <span class="tag">Build in public</span>
            </div>
          </article>
        </div>

        <div class="slide-number">02 / 04</div>
      </section>

      <!-- 03 / Proof -->
      <section
        class="slide proof"
        aria-label="3장: 주요 성과"
        aria-hidden="true"
      >
        <header class="brand-header">
          <a class="wordmark" href="https://wigtn.com">
            wigtn<span class="wordmark-period">.</span>
          </a>
          <span class="purple-dot" aria-label="WIGTN 퍼플 점"></span>
        </header>

        <div class="proof-copy">
          <p class="eyebrow">Built fast. Shipped often.</p>
          <h2>
            Ideas become<br />
            <span class="accent">working systems.</span>
          </h2>
          <p class="lead">
            WIGTN은 연구를 논문에만 두지 않습니다.
            실제 환경에서 작동하는 시스템으로 만들고,
            검증 가능한 결과와 코드로 공개합니다.
          </p>
        </div>

        <div class="proof-list">
          <article class="proof-item">
            <div class="proof-value">ACL</div>
            <div>
              <div class="proof-label">WIGVO · System Demonstrations</div>
              <p class="proof-description">
                일반 전화망에서 작동하는 실시간 양방향 음성 번역 시스템.
              </p>
            </div>
          </article>

          <article class="proof-item">
            <div class="proof-value">#1</div>
            <div>
              <div class="proof-label">WigtnOCR · Korean Gov. Documents</div>
              <p class="proof-description">
                한국 공공문서 검색 평가에서 6개 파서 중 최고 성능.
              </p>
            </div>
          </article>

          <article class="proof-item">
            <div class="proof-value">2B</div>
            <div>
              <div class="proof-label">Practical domain VLM</div>
              <p class="proof-description">
                더 작은 모델로 실제 문서 구조를 보존하는 파싱 성능 구현.
              </p>
            </div>
          </article>

          <article class="proof-item">
            <div class="proof-value">🏆</div>
            <div>
              <div class="proof-label">Build with TRAE Seoul</div>
              <p class="proof-description">
                멀티 에이전트 토론 시스템 WIGENT로 Grand Prize 수상.
              </p>
            </div>
          </article>
        </div>

        <div class="slide-number">03 / 04</div>
      </section>

      <!-- 04 / Closing -->
      <section
        class="slide closing"
        aria-label="4장: 함께하기"
        aria-hidden="true"
      >
        <header class="brand-header">
          <a class="wordmark" href="https://wigtn.com">
            wigtn<span class="wordmark-period">.</span>
          </a>
          <span class="purple-dot" aria-label="WIGTN 퍼플 점"></span>
        </header>

        <div class="closing-content">
          <p class="eyebrow">Join the community</p>
          <h2>
            If you build AI,<br />
            <span class="accent">there’s a seat for you.</span>
          </h2>
          <p class="lead">
            밋업에 참여하고, 스터디를 함께하고,
            오픈소스 프로젝트에 기여하거나 가볍게 인사를 건네주세요.
          </p>
          <a class="contact-link" href="mailto:contact@wigtn.com">
            contact@wigtn.com
          </a>
        </div>

        <div class="slide-number">04 / 04</div>
      </section>
    </div>
  </main>

  <div class="keyboard-help" aria-hidden="true">
    ← → 이동 · Space 다음 · Home / End · F 전체화면
  </div>

  <nav class="controls" aria-label="슬라이드 탐색">
    <button
      class="control-button"
      id="previousButton"
      type="button"
      aria-label="이전 슬라이드"
    >
      ←
    </button>
    <span class="counter" id="counter" aria-live="polite">01 / 04</span>
    <button
      class="control-button"
      id="nextButton"
      type="button"
      aria-label="다음 슬라이드"
    >
      →
    </button>
  </nav>

  <div class="progress" id="progress" aria-hidden="true"></div>

  <script>
    (() => {
      const deck = document.getElementById("deck");
      const slides = [...document.querySelectorAll(".slide")];
      const previousButton = document.getElementById("previousButton");
      const nextButton = document.getElementById("nextButton");
      const counter = document.getElementById("counter");
      const progress = document.getElementById("progress");

      let currentIndex = 0;
      let touchStartX = 0;
      let touchStartY = 0;

      function pad(value) {
        return String(value).padStart(2, "0");
      }

      function fitDeck() {
        const scale = Math.min(
          window.innerWidth / 1600,
          window.innerHeight / 900
        );

        deck.style.transform = `scale(${scale})`;
      }

      function showSlide(nextIndex) {
        const boundedIndex = Math.max(
          0,
          Math.min(nextIndex, slides.length - 1)
        );

        slides.forEach((slide, index) => {
          slide.classList.toggle("active", index === boundedIndex);
          slide.classList.toggle("previous", index < boundedIndex);
          slide.setAttribute(
            "aria-hidden",
            index === boundedIndex ? "false" : "true"
          );
        });

        currentIndex = boundedIndex;
        counter.textContent =
          `${pad(currentIndex + 1)} / ${pad(slides.length)}`;

        progress.style.width =
          `${((currentIndex + 1) / slides.length) * 100}%`;

        previousButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === slides.length - 1;

        history.replaceState(
          null,
          "",
          `#slide-${currentIndex + 1}`
        );
      }

      function nextSlide() {
        showSlide(currentIndex + 1);
      }

      function previousSlide() {
        showSlide(currentIndex - 1);
      }

      function toggleFullscreen() {
        if (!document.fullscreenElement) {
          document.documentElement.requestFullscreen?.();
        } else {
          document.exitFullscreen?.();
        }
      }

      previousButton.addEventListener("click", previousSlide);
      nextButton.addEventListener("click", nextSlide);
      window.addEventListener("resize", fitDeck);

      window.addEventListener("keydown", (event) => {
        const nextKeys = ["ArrowRight", "PageDown", " ", "Enter"];
        const previousKeys = ["ArrowLeft", "PageUp", "Backspace"];

        if (nextKeys.includes(event.key)) {
          event.preventDefault();
          nextSlide();
        }

        if (previousKeys.includes(event.key)) {
          event.preventDefault();
          previousSlide();
        }

        if (event.key === "Home") {
          event.preventDefault();
          showSlide(0);
        }

        if (event.key === "End") {
          event.preventDefault();
          showSlide(slides.length - 1);
        }

        if (event.key.toLowerCase() === "f") {
          event.preventDefault();
          toggleFullscreen();
        }
      });

      window.addEventListener(
        "wheel",
        (event) => {
          if (Math.abs(event.deltaY) < 25) return;

          if (event.deltaY > 0) {
            nextSlide();
          } else {
            previousSlide();
          }
        },
        { passive: true }
      );

      window.addEventListener(
        "touchstart",
        (event) => {
          touchStartX = event.changedTouches[0].clientX;
          touchStartY = event.changedTouches[0].clientY;
        },
        { passive: true }
      );

      window.addEventListener(
        "touchend",
        (event) => {
          const deltaX =
            event.changedTouches[0].clientX - touchStartX;
          const deltaY =
            event.changedTouches[0].clientY - touchStartY;

          if (
            Math.abs(deltaX) > 55 &&
            Math.abs(deltaX) > Math.abs(deltaY)
          ) {
            deltaX < 0 ? nextSlide() : previousSlide();
          }
        },
        { passive: true }
      );

      const hashIndex = Number(
        window.location.hash.replace("#slide-", "")
      );

      fitDeck();
      showSlide(
        Number.isInteger(hashIndex) &&
        hashIndex >= 1 &&
        hashIndex <= slides.length
          ? hashIndex - 1
          : 0
      );
    })();
  </script>
</body>
</html>
```