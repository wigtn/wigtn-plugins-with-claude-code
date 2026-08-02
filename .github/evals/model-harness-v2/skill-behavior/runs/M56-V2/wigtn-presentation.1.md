```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>WIGTN — Company Introduction</title>

  <style>
    :root {
      /* WIGTN Brand — exact HEX */
      --ink: #1E1E28;
      --ink-deep: #15151E;
      --purple: #9B51E0;
      --purple-bright: #A85FEA;
      --purple-deep: #6B2EAA;
      --white: #FFFFFF;
      --off-white: #FAFAFA;

      /* Dark presentation theme */
      --bg: var(--ink-deep);
      --surface: var(--ink);
      --surface-2: rgba(38, 38, 51, 0.25);
      --text-primary: #F5F4FA;
      --text-secondary: #A8A6B8;
      --accent: var(--purple-bright);
      --line: #2C2C3A;

      --scale: 1;
      --ease: cubic-bezier(.22, 1, .36, 1);
      --font: Pretendard, "Apple SD Gothic Neo", "Noto Sans KR",
              system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
      --display: "Space Grotesk", Pretendard, "Apple SD Gothic Neo",
                 system-ui, sans-serif;
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
      background: var(--bg);
      color: var(--text-primary);
      font-family: var(--font);
      word-break: keep-all;
    }

    button {
      font: inherit;
    }

    .deck {
      position: relative;
      width: 100%;
      height: 100%;
      background: var(--bg);
    }

    .progress {
      position: fixed;
      inset: 0 0 auto;
      z-index: 100;
      height: clamp(0.125rem, 0.16vw, 0.175rem);
      background: rgba(255, 255, 255, 0.06);
    }

    .progress__bar {
      width: 25%;
      height: 100%;
      background: var(--accent);
      transform-origin: left;
      transition: width 420ms var(--ease);
    }

    .slides {
      width: 100%;
      height: 100%;
    }

    .slide {
      position: absolute;
      inset: 0;
      display: flex;
      flex-direction: column;
      width: 100%;
      height: 100vh;
      height: 100dvh;
      padding:
        clamp(2.4rem, 6vh, 5rem)
        clamp(2rem, 6vw, 6rem);
      overflow: hidden;
      visibility: hidden;
      opacity: 0;
      transform: translateY(clamp(0.4rem, 1vh, 0.75rem));
      pointer-events: none;
      background: var(--bg);
      transition:
        opacity 420ms var(--ease),
        transform 520ms var(--ease),
        visibility 0s linear 520ms;
    }

    .slide.is-active {
      visibility: visible;
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
      transition-delay: 0s;
    }

    .slide__header {
      position: relative;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: clamp(1rem, 3vw, 2rem);
    }

    .wordmark {
      display: inline-flex;
      align-items: baseline;
      color: var(--text-primary);
      font-family: var(--display);
      font-size: clamp(1.4rem, 2.2vw, 2rem);
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.055em;
      text-decoration: none;
    }

    .wordmark__dot {
      color: var(--purple);
    }

    .eyebrow {
      display: flex;
      align-items: center;
      gap: clamp(0.55rem, 1vw, 0.8rem);
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(0.68rem, 0.9vw, 0.82rem);
      font-weight: 700;
      letter-spacing: 0.16em;
      text-transform: uppercase;
    }

    .eyebrow::before {
      width: clamp(1.4rem, 2.5vw, 2.6rem);
      height: 0.125rem;
      background: var(--purple);
      content: "";
    }

    .slide__body {
      position: relative;
      z-index: 2;
      display: flex;
      flex: 1;
      align-items: center;
    }

    .slide__footer {
      position: relative;
      z-index: 5;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 1rem;
      color: var(--text-secondary);
      font-size: clamp(0.65rem, 0.8vw, 0.78rem);
      font-weight: 600;
      letter-spacing: 0.08em;
    }

    .page {
      display: inline-flex;
      align-items: center;
      gap: clamp(0.5rem, 0.8vw, 0.7rem);
      font-variant-numeric: tabular-nums;
    }

    /* 모든 슬라이드에서 같은 위치·크기로 반복되는 시그니처 점 */
    .page__dot {
      width: clamp(0.5rem, 0.65vw, 0.62rem);
      height: clamp(0.5rem, 0.65vw, 0.62rem);
      flex: 0 0 auto;
      border-radius: 50%;
      background: var(--purple);
      box-shadow: 0 0 0 clamp(0.18rem, 0.25vw, 0.25rem)
                  rgba(155, 81, 224, 0.16);
    }

    .display-title {
      max-width: 12ch;
      margin:
        clamp(1.2rem, 3vh, 2.2rem) 0
        clamp(1rem, 2.5vh, 1.8rem);
      font-family: var(--display);
      font-size: calc(clamp(3rem, 7.4vw, 7.2rem) * var(--scale));
      font-weight: 750;
      line-height: 0.94;
      letter-spacing: -0.065em;
    }

    .display-title .accent {
      color: var(--accent);
    }

    .lead {
      max-width: 41rem;
      margin: 0;
      color: var(--text-secondary);
      font-size: calc(clamp(1rem, 1.55vw, 1.35rem) * var(--scale));
      font-weight: 450;
      line-height: 1.72;
    }

    .section-title {
      max-width: 15ch;
      margin:
        clamp(0.8rem, 2vh, 1.4rem) 0
        clamp(1.4rem, 3.5vh, 2.8rem);
      font-family: var(--display);
      font-size: calc(clamp(2.1rem, 4.4vw, 4.5rem) * var(--scale));
      font-weight: 730;
      line-height: 1.04;
      letter-spacing: -0.05em;
    }

    /* Slide 01 */
    .cover-copy {
      position: relative;
      z-index: 3;
      width: min(70%, 62rem);
    }

    .cover-meta {
      display: flex;
      flex-wrap: wrap;
      gap: clamp(1rem, 3vw, 2.6rem);
      margin-top: clamp(1.5rem, 4vh, 3rem);
    }

    .meta-item {
      display: grid;
      gap: 0.3rem;
    }

    .meta-label {
      color: #747287;
      font-size: clamp(0.62rem, 0.74vw, 0.72rem);
      font-weight: 700;
      letter-spacing: 0.14em;
      text-transform: uppercase;
    }

    .meta-value {
      color: var(--text-primary);
      font-size: clamp(0.78rem, 0.95vw, 0.92rem);
      font-weight: 600;
    }

    .cover-visual {
      position: absolute;
      top: 50%;
      right: clamp(-11rem, -8vw, -4rem);
      width: clamp(20rem, 43vw, 46rem);
      aspect-ratio: 1;
      transform: translateY(-48%);
    }

    .orbit {
      position: absolute;
      inset: 0;
      border: 1px solid rgba(168, 95, 234, 0.18);
      border-radius: 50%;
    }

    .orbit:nth-child(2) {
      inset: 14%;
      border-color: rgba(255, 255, 255, 0.1);
    }

    .orbit:nth-child(3) {
      inset: 31%;
      border-color: rgba(168, 95, 234, 0.25);
    }

    .orbit::after {
      position: absolute;
      top: 12%;
      left: 18%;
      width: clamp(0.65rem, 1.2vw, 1rem);
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--purple);
      box-shadow: 0 0 0 clamp(0.3rem, 0.7vw, 0.6rem)
                  rgba(155, 81, 224, 0.12);
      content: "";
    }

    .visual-core {
      position: absolute;
      inset: 42%;
      border-radius: 50%;
      background: var(--purple);
      box-shadow:
        0 0 0 clamp(1.2rem, 2.5vw, 2.4rem) rgba(155, 81, 224, 0.08),
        0 0 clamp(2rem, 6vw, 5rem) rgba(155, 81, 224, 0.28);
    }

    /* Slide 02 */
    .services-layout {
      display: grid;
      width: 100%;
      grid-template-columns: minmax(15rem, 0.82fr) minmax(27rem, 1.35fr);
      gap: clamp(2rem, 7vw, 7rem);
      align-items: center;
    }

    .service-list {
      display: grid;
      border-top: 1px solid var(--line);
    }

    .service {
      display: grid;
      grid-template-columns: clamp(2.5rem, 4vw, 4rem) 1fr auto;
      gap: clamp(0.8rem, 1.8vw, 1.5rem);
      align-items: center;
      padding: clamp(0.9rem, 2.3vh, 1.55rem) 0;
      border-bottom: 1px solid var(--line);
    }

    .service__number {
      color: var(--accent);
      font-family: var(--display);
      font-size: clamp(0.72rem, 0.9vw, 0.85rem);
      font-weight: 700;
    }

    .service__title {
      margin: 0 0 0.25rem;
      font-size: clamp(1rem, 1.5vw, 1.3rem);
      font-weight: 700;
      letter-spacing: -0.025em;
    }

    .service__description {
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(0.72rem, 0.95vw, 0.88rem);
      line-height: 1.55;
    }

    .service__arrow {
      color: #6D6B7E;
      font-size: clamp(1rem, 1.5vw, 1.35rem);
    }

    /* Slide 03 */
    .method-layout {
      width: 100%;
    }

    .method-heading {
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: clamp(2rem, 6vw, 6rem);
      margin-bottom: clamp(2rem, 6vh, 4.5rem);
    }

    .method-heading .section-title {
      margin-bottom: 0;
    }

    .method-heading .lead {
      max-width: 29rem;
    }

    .process {
      position: relative;
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: clamp(1rem, 2.3vw, 2rem);
    }

    .process::before {
      position: absolute;
      top: clamp(1rem, 1.5vw, 1.35rem);
      right: 2%;
      left: 2%;
      height: 1px;
      background: var(--line);
      content: "";
    }

    .step {
      position: relative;
      padding-top: clamp(3rem, 6vh, 4.3rem);
    }

    .step__dot {
      position: absolute;
      z-index: 2;
      top: clamp(0.65rem, 1.1vw, 0.95rem);
      left: 0;
      width: clamp(0.7rem, 0.85vw, 0.85rem);
      aspect-ratio: 1;
      border: clamp(0.16rem, 0.2vw, 0.2rem) solid var(--bg);
      border-radius: 50%;
      background: var(--purple);
      box-shadow: 0 0 0 1px var(--purple);
    }

    .step__number {
      display: block;
      margin-bottom: clamp(0.55rem, 1.2vh, 0.9rem);
      color: var(--accent);
      font-family: var(--display);
      font-size: clamp(0.68rem, 0.85vw, 0.8rem);
      font-weight: 700;
      letter-spacing: 0.12em;
    }

    .step__title {
      margin: 0 0 clamp(0.5rem, 1vh, 0.75rem);
      font-size: clamp(1rem, 1.45vw, 1.3rem);
      font-weight: 720;
      letter-spacing: -0.025em;
    }

    .step__text {
      max-width: 15rem;
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(0.72rem, 0.92vw, 0.86rem);
      line-height: 1.65;
    }

    /* Slide 04 */
    .closing {
      width: 100%;
    }

    .closing-title {
      max-width: 13ch;
      margin:
        clamp(1.2rem, 3vh, 2rem) 0
        clamp(1.4rem, 3vh, 2.4rem);
      font-family: var(--display);
      font-size: calc(clamp(3rem, 7vw, 6.7rem) * var(--scale));
      font-weight: 760;
      line-height: 0.98;
      letter-spacing: -0.065em;
    }

    .closing-title .accent {
      color: var(--accent);
    }

    .contact-row {
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      gap: clamp(1.1rem, 3vw, 2.8rem);
      margin-top: clamp(2rem, 5vh, 3.8rem);
    }

    .contact-link {
      color: var(--text-primary);
      font-size: clamp(0.78rem, 1vw, 0.95rem);
      font-weight: 650;
      text-decoration: none;
    }

    .contact-link:hover {
      color: var(--accent);
    }

    .closing-block {
      position: absolute;
      right: clamp(2rem, 8vw, 8rem);
      bottom: clamp(5rem, 13vh, 9rem);
      width: clamp(10rem, 18vw, 17rem);
      aspect-ratio: 1;
      border: 1px solid rgba(168, 95, 234, 0.25);
      transform: rotate(12deg);
    }

    .closing-block::before,
    .closing-block::after {
      position: absolute;
      content: "";
    }

    .closing-block::before {
      inset: 18%;
      border: 1px solid rgba(255, 255, 255, 0.12);
    }

    .closing-block::after {
      right: -4%;
      bottom: -4%;
      width: 18%;
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--purple);
      box-shadow: 0 0 0 clamp(0.45rem, 0.9vw, 0.8rem)
                  rgba(155, 81, 224, 0.12);
    }

    /* Navigation */
    .nav {
      position: fixed;
      z-index: 100;
      top: 50%;
      right: clamp(0.7rem, 1.5vw, 1.4rem);
      display: grid;
      gap: clamp(0.55rem, 1vh, 0.8rem);
      transform: translateY(-50%);
    }

    .nav__dot {
      width: clamp(0.45rem, 0.55vw, 0.55rem);
      height: clamp(0.45rem, 0.55vw, 0.55rem);
      padding: 0;
      border: 0;
      border-radius: 50%;
      background: #4A4859;
      cursor: pointer;
      transition:
        background 200ms ease,
        transform 200ms ease,
        box-shadow 200ms ease;
    }

    .nav__dot:hover {
      background: #787589;
    }

    .nav__dot.is-active {
      background: var(--purple);
      transform: scale(1.22);
      box-shadow: 0 0 0 clamp(0.2rem, 0.3vw, 0.3rem)
                  rgba(155, 81, 224, 0.15);
    }

    .hint {
      position: fixed;
      z-index: 90;
      right: clamp(2rem, 6vw, 6rem);
      bottom: clamp(0.9rem, 2vh, 1.35rem);
      color: #656375;
      font-size: clamp(0.58rem, 0.7vw, 0.68rem);
      letter-spacing: 0.08em;
    }

    .slide.is-active .reveal {
      animation: reveal 520ms var(--ease) both;
    }

    .slide.is-active .reveal:nth-child(2) {
      animation-delay: 70ms;
    }

    .slide.is-active .reveal:nth-child(3) {
      animation-delay: 140ms;
    }

    @keyframes reveal {
      from {
        opacity: 0;
        transform: translateY(clamp(0.4rem, 1vh, 0.6rem));
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }

    @media (max-width: 800px) {
      .services-layout {
        grid-template-columns: 1fr;
        gap: clamp(1.2rem, 3vh, 2rem);
      }

      .services-layout .section-title {
        max-width: 12ch;
        margin-bottom: 0.8rem;
      }

      .method-heading {
        display: block;
      }

      .method-heading .lead {
        margin-top: 1rem;
      }

      .process {
        grid-template-columns: repeat(2, 1fr);
      }

      .process::before {
        display: none;
      }

      .step {
        padding-top: 1.8rem;
      }

      .step__dot {
        top: 0;
      }

      .cover-copy {
        width: 88%;
      }

      .cover-visual,
      .closing-block {
        opacity: 0.55;
      }

      .hint {
        display: none;
      }
    }

    @media (max-height: 700px) {
      :root {
        --scale: 0.9;
      }

      .cover-meta {
        margin-top: 1.2rem;
      }

      .method-heading {
        margin-bottom: 1.5rem;
      }
    }

    @media (max-height: 600px) {
      :root {
        --scale: 0.8;
      }

      .slide {
        padding-top: 1.8rem;
        padding-bottom: 1.8rem;
      }

      .service {
        padding-top: 0.65rem;
        padding-bottom: 0.65rem;
      }

      .step {
        padding-top: 2.2rem;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
        animation: none !important;
        transition: none !important;
      }
    }
  </style>
</head>

<body>
  <main class="deck" aria-label="WIGTN 회사소개 프레젠테이션">
    <div class="progress" aria-hidden="true">
      <div class="progress__bar" id="progressBar"></div>
    </div>

    <div class="slides">
      <!-- 01. Cover -->
      <section class="slide is-active" aria-label="표지">
        <header class="slide__header">
          <div class="wordmark" aria-label="wigtn">
            wigtn<span class="wordmark__dot">.</span>
          </div>
          <p class="eyebrow">Company Introduction</p>
        </header>

        <div class="slide__body">
          <div class="cover-copy">
            <h1 class="display-title reveal">
              Ideas into<br />
              impact<span class="accent">.</span>
            </h1>

            <p class="lead reveal">
              전략, 디자인, 기술을 하나의 실행력으로 연결해
              좋은 아이디어를 작동하는 디지털 경험으로 만듭니다.
            </p>

            <div class="cover-meta reveal">
              <div class="meta-item">
                <span class="meta-label">What we build</span>
                <span class="meta-value">Digital products & experiences</span>
              </div>
              <div class="meta-item">
                <span class="meta-label">How we work</span>
                <span class="meta-value">Strategy × Design × Technology</span>
              </div>
            </div>
          </div>

          <div class="cover-visual" aria-hidden="true">
            <div class="orbit"></div>
            <div class="orbit"></div>
            <div class="orbit"></div>
            <div class="visual-core"></div>
          </div>
        </div>

        <footer class="slide__footer">
          <span>WIGTN © 2026</span>
          <span class="page">01 <i class="page__dot"></i></span>
        </footer>
      </section>

      <!-- 02. What we do -->
      <section class="slide" aria-label="우리가 하는 일">
        <header class="slide__header">
          <div class="wordmark" aria-label="wigtn">
            wigtn<span class="wordmark__dot">.</span>
          </div>
          <p class="eyebrow">What we do</p>
        </header>

        <div class="slide__body">
          <div class="services-layout">
            <div>
              <p class="eyebrow reveal">One integrated team</p>
              <h2 class="section-title reveal">
                복잡함을<br />명확한 경험으로.
              </h2>
              <p class="lead reveal">
                발견부터 출시까지 끊김 없는 팀으로 움직이며,
                사용자와 비즈니스가 함께 성장하는 접점을 설계합니다.
              </p>
            </div>

            <div class="service-list reveal">
              <article class="service">
                <span class="service__number">01.</span>
                <div>
                  <h3 class="service__title">Product Strategy</h3>
                  <p class="service__description">
                    문제 정의, 고객 인사이트, 제품 방향과 우선순위
                  </p>
                </div>
                <span class="service__arrow" aria-hidden="true">↗</span>
              </article>

              <article class="service">
                <span class="service__number">02.</span>
                <div>
                  <h3 class="service__title">Experience Design</h3>
                  <p class="service__description">
                    사용자 흐름, 인터페이스, 브랜드 경험과 프로토타입
                  </p>
                </div>
                <span class="service__arrow" aria-hidden="true">↗</span>
              </article>

              <article class="service">
                <span class="service__number">03.</span>
                <div>
                  <h3 class="service__title">Technology</h3>
                  <p class="service__description">
                    확장 가능한 웹·모바일 제품과 지능형 서비스 구현
                  </p>
                </div>
                <span class="service__arrow" aria-hidden="true">↗</span>
              </article>

              <article class="service">
                <span class="service__number">04.</span>
                <div>
                  <h3 class="service__title">Growth & Evolution</h3>
                  <p class="service__description">
                    데이터 기반 개선, 운영 체계와 지속적인 제품 진화
                  </p>
                </div>
                <span class="service__arrow" aria-hidden="true">↗</span>
              </article>
            </div>
          </div>
        </div>

        <footer class="slide__footer">
          <span>CAPABILITIES</span>
          <span class="page">02 <i class="page__dot"></i></span>
        </footer>
      </section>

      <!-- 03. How we work -->
      <section class="slide" aria-label="일하는 방식">
        <header class="slide__header">
          <div class="wordmark" aria-label="wigtn">
            wigtn<span class="wordmark__dot">.</span>
          </div>
          <p class="eyebrow">How we work</p>
        </header>

        <div class="slide__body">
          <div class="method-layout">
            <div class="method-heading">
              <h2 class="section-title reveal">
                생각에서 실행까지,<br />하나의 리듬으로.
              </h2>
              <p class="lead reveal">
                빠르게 가설을 확인하고, 결정의 근거를 공유하며,
                완성도 높은 결과를 반복적으로 만들어갑니다.
              </p>
            </div>

            <div class="process reveal">
              <article class="step">
                <i class="step__dot" aria-hidden="true"></i>
                <span class="step__number">01 / DISCOVER</span>
                <h3 class="step__title">본질을 발견합니다</h3>
                <p class="step__text">
                  사용자, 시장, 비즈니스를 함께 보고 풀어야 할 핵심 문제를 찾습니다.
                </p>
              </article>

              <article class="step">
                <i class="step__dot" aria-hidden="true"></i>
                <span class="step__number">02 / DEFINE</span>
                <h3 class="step__title">방향을 선명하게 합니다</h3>
                <p class="step__text">
                  성공 기준과 우선순위를 정렬하고 실행 가능한 제품 전략을 만듭니다.
                </p>
              </article>

              <article class="step">
                <i class="step__dot" aria-hidden="true"></i>
                <span class="step__number">03 / BUILD</span>
                <h3 class="step__title">빠르게 구현합니다</h3>
                <p class="step__text">
                  디자인과 개발이 동시에 움직이며 실제 사용 가능한 결과를 만듭니다.
                </p>
              </article>

              <article class="step">
                <i class="step__dot" aria-hidden="true"></i>
                <span class="step__number">04 / EVOLVE</span>
                <h3 class="step__title">계속 진화시킵니다</h3>
                <p class="step__text">
                  데이터와 피드백을 학습해 제품의 가치와 완성도를 높입니다.
                </p>
              </article>
            </div>
          </div>
        </div>

        <footer class="slide__footer">
          <span>PROCESS</span>
          <span class="page">03 <i class="page__dot"></i></span>
        </footer>
      </section>

      <!-- 04. Closing -->
      <section class="slide" aria-label="마무리">
        <header class="slide__header">
          <div class="wordmark" aria-label="wigtn">
            wigtn<span class="wordmark__dot">.</span>
          </div>
          <p class="eyebrow">Let’s build what matters</p>
        </header>

        <div class="slide__body">
          <div class="closing">
            <h2 class="closing-title reveal">
              다음 가능성을<br />
              함께 만듭니다<span class="accent">.</span>
            </h2>

            <p class="lead reveal">
              더 나은 질문과 선명한 실행으로<br />
              의미 있는 변화를 시작하세요.
            </p>

            <div class="contact-row reveal">
              <a class="contact-link" href="mailto:hello@wigtn.com">
                hello@wigtn.com
              </a>
              <a class="contact-link" href="https://wigtn.com">
                wigtn.com ↗
              </a>
            </div>
          </div>

          <div class="closing-block" aria-hidden="true"></div>
        </div>

        <footer class="slide__footer">
          <span>THANK YOU</span>
          <span class="page">04 <i class="page__dot"></i></span>
        </footer>
      </section>
    </div>

    <nav class="nav" aria-label="슬라이드 탐색">
      <button class="nav__dot is-active" aria-label="1번 슬라이드" data-slide="0"></button>
      <button class="nav__dot" aria-label="2번 슬라이드" data-slide="1"></button>
      <button class="nav__dot" aria-label="3번 슬라이드" data-slide="2"></button>
      <button class="nav__dot" aria-label="4번 슬라이드" data-slide="3"></button>
    </nav>

    <span class="hint" aria-hidden="true">← → · SPACE · SWIPE</span>
  </main>

  <script>
    (() => {
      const slides = [...document.querySelectorAll(".slide")];
      const dots = [...document.querySelectorAll(".nav__dot")];
      const progressBar = document.getElementById("progressBar");

      let current = 0;
      let wheelLocked = false;
      let touchStartX = 0;
      let touchStartY = 0;

      function showSlide(index) {
        current = Math.max(0, Math.min(index, slides.length - 1));

        slides.forEach((slide, i) => {
          const active = i === current;
          slide.classList.toggle("is-active", active);
          slide.setAttribute("aria-hidden", String(!active));
        });

        dots.forEach((dot, i) => {
          const active = i === current;
          dot.classList.toggle("is-active", active);
          dot.setAttribute("aria-current", active ? "true" : "false");
        });

        progressBar.style.width =
          `${((current + 1) / slides.length) * 100}%`;
      }

      function next() {
        showSlide(current + 1);
      }

      function previous() {
        showSlide(current - 1);
      }

      dots.forEach(dot => {
        dot.addEventListener("click", () => {
          showSlide(Number(dot.dataset.slide));
        });
      });

      window.addEventListener("keydown", event => {
        if (["ArrowRight", "ArrowDown", "PageDown", " "].includes(event.key)) {
          event.preventDefault();
          next();
        }

        if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
          event.preventDefault();
          previous();
        }

        if (event.key === "Home") showSlide(0);
        if (event.key === "End") showSlide(slides.length - 1);
      });

      window.addEventListener("wheel", event => {
        if (wheelLocked || Math.abs(event.deltaY) < 12) return;

        wheelLocked = true;
        event.deltaY > 0 ? next() : previous();

        window.setTimeout(() => {
          wheelLocked = false;
        }, 650);
      }, { passive: true });

      window.addEventListener("touchstart", event => {
        touchStartX = event.changedTouches[0].clientX;
        touchStartY = event.changedTouches[0].clientY;
      }, { passive: true });

      window.addEventListener("touchend", event => {
        const deltaX = event.changedTouches[0].clientX - touchStartX;
        const deltaY = event.changedTouches[0].clientY - touchStartY;

        if (Math.abs(deltaX) < 45 || Math.abs(deltaX) < Math.abs(deltaY)) return;
        deltaX < 0 ? next() : previous();
      }, { passive: true });

      showSlide(0);
    })();
  </script>
</body>
</html>
```