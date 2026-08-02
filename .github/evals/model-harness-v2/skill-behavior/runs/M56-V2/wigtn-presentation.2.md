```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="WIGTN 회사소개" />
  <title>WIGTN — Company Introduction</title>

  <style>
    :root {
      --bg: #FFFFFF;
      --surface: #FAFAFA;
      --surface-2: #F4F2F8;
      --text-primary: #1E1E28;
      --text-secondary: #5A5A6E;
      --accent: #9B51E0;
      --accent-deep: #6B2EAA;
      --line: #E6E3EE;
      --scale: 1;
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
    }

    body {
      font-family:
        Pretendard,
        "Noto Sans KR",
        "Apple SD Gothic Neo",
        sans-serif;
      color: var(--text-primary);
      word-break: keep-all;
      -webkit-font-smoothing: antialiased;
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
      z-index: 20;
      height: 2px;
      background: var(--line);
    }

    .progress__bar {
      width: 25%;
      height: 100%;
      background: var(--accent);
      transition: width 320ms ease;
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
        clamp(2.25rem, 6vh, 5rem)
        clamp(2rem, 6vw, 6rem);
      overflow: hidden;
      visibility: hidden;
      opacity: 0;
      transform: translateY(8px);
      background: var(--bg);
      pointer-events: none;
      transition:
        opacity 280ms ease,
        transform 280ms ease,
        visibility 280ms;
    }

    .slide.is-active {
      visibility: visible;
      opacity: 1;
      transform: translateY(0);
      pointer-events: auto;
    }

    .slide-header,
    .slide-footer {
      position: relative;
      z-index: 3;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .slide-header {
      min-height: clamp(2rem, 5vh, 3.5rem);
    }

    .slide-footer {
      margin-top: auto;
      padding-top: clamp(1.2rem, 3vh, 2rem);
    }

    .wordmark {
      display: inline-flex;
      align-items: baseline;
      font-family:
        "Space Grotesk",
        "Arial Black",
        Pretendard,
        sans-serif;
      font-size: clamp(1.4rem, 2.4vw, 2.15rem);
      font-weight: 800;
      line-height: 1;
      letter-spacing: -0.06em;
      color: var(--text-primary);
    }

    .wordmark__dot {
      color: var(--accent);
    }

    .eyebrow,
    .meta,
    .page-number,
    .micro-label {
      font-size: clamp(0.68rem, 0.9vw, 0.82rem);
      font-weight: 700;
      line-height: 1.4;
      letter-spacing: 0.13em;
      text-transform: uppercase;
    }

    .eyebrow,
    .micro-label {
      color: var(--accent-deep);
    }

    .meta,
    .page-number {
      color: var(--text-secondary);
    }

    .page-number {
      display: inline-flex;
      align-items: center;
      gap: 0.7rem;
      font-variant-numeric: tabular-nums;
    }

    /* 모든 슬라이드에서 같은 위치와 크기로 반복되는 시그니처 점 */
    .signature-dot {
      display: inline-block;
      width: clamp(0.55rem, 0.7vw, 0.7rem);
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--accent);
      box-shadow: 0 0 0 4px rgb(155 81 224 / 14%);
    }

    .slide-title {
      margin: 0;
      font-family:
        "Space Grotesk",
        Pretendard,
        sans-serif;
      font-size: clamp(2rem, 4.1vw, 4.2rem);
      font-weight: 750;
      line-height: 1.08;
      letter-spacing: -0.055em;
    }

    .slide-copy {
      margin: 0;
      max-width: 44rem;
      color: var(--text-secondary);
      font-size: clamp(0.94rem, 1.35vw, 1.22rem);
      line-height: 1.75;
    }

    /* Slide 1 */
    .cover__body {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: minmax(0, 1.25fr) minmax(16rem, 0.75fr);
      gap: clamp(2rem, 7vw, 8rem);
      align-items: center;
      flex: 1;
    }

    .cover__title {
      max-width: 58rem;
      margin:
        clamp(1rem, 3vh, 2.5rem)
        0
        clamp(1.2rem, 3vh, 2rem);
      font-family:
        "Space Grotesk",
        Pretendard,
        sans-serif;
      font-size: clamp(3rem, 7.6vw, 7.6rem);
      font-weight: 750;
      line-height: 0.94;
      letter-spacing: -0.075em;
    }

    .cover__title .accent {
      color: var(--accent);
    }

    .cover__statement {
      max-width: 39rem;
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(1rem, 1.6vw, 1.38rem);
      line-height: 1.65;
    }

    .cover__visual {
      position: relative;
      display: grid;
      place-items: center;
      min-height: clamp(15rem, 48vh, 34rem);
    }

    .orbit {
      position: relative;
      width: min(31vw, 25rem);
      min-width: 14rem;
      aspect-ratio: 1;
      border: 1px solid var(--line);
      border-radius: 50%;
    }

    .orbit::before,
    .orbit::after {
      position: absolute;
      content: "";
      border-radius: 50%;
    }

    .orbit::before {
      inset: 18%;
      border: 1px solid var(--line);
    }

    .orbit::after {
      top: 8%;
      right: 13%;
      width: 17%;
      aspect-ratio: 1;
      background: var(--accent);
      box-shadow: 0 0 0 10px rgb(155 81 224 / 10%);
    }

    .orbit__core {
      position: absolute;
      inset: 36%;
      display: grid;
      place-items: center;
      border-radius: 50%;
      background: var(--text-primary);
      color: #FFFFFF;
      font-size: clamp(1rem, 2vw, 1.6rem);
      font-weight: 800;
      letter-spacing: -0.04em;
    }

    /* Slide 2 */
    .intro__body {
      display: grid;
      grid-template-columns: minmax(15rem, 0.78fr) minmax(0, 1.22fr);
      gap: clamp(2.5rem, 8vw, 9rem);
      align-items: center;
      flex: 1;
    }

    .intro__lead {
      display: flex;
      flex-direction: column;
      gap: clamp(1rem, 2.4vh, 1.8rem);
    }

    .principles {
      display: grid;
      gap: clamp(1rem, 2.2vh, 1.5rem);
      margin: 0;
    }

    .principle {
      display: grid;
      grid-template-columns: clamp(2.5rem, 4vw, 4rem) 1fr;
      gap: clamp(1rem, 2vw, 2rem);
      align-items: start;
      padding: clamp(1rem, 2.5vh, 1.7rem) 0;
      border-top: 1px solid var(--line);
    }

    .principle:last-child {
      border-bottom: 1px solid var(--line);
    }

    .principle__number {
      color: var(--accent);
      font-size: clamp(0.75rem, 1vw, 0.9rem);
      font-weight: 800;
      letter-spacing: 0.08em;
    }

    .principle h3 {
      margin: 0 0 0.45rem;
      font-size: clamp(1.05rem, 1.7vw, 1.45rem);
      line-height: 1.25;
      letter-spacing: -0.03em;
    }

    .principle p {
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(0.82rem, 1.1vw, 1rem);
      line-height: 1.65;
    }

    /* Slide 3 */
    .capability__body {
      display: grid;
      grid-template-columns: minmax(16rem, 0.72fr) minmax(0, 1.28fr);
      gap: clamp(2.5rem, 7vw, 8rem);
      align-items: end;
      flex: 1;
      padding-top: clamp(1.5rem, 4vh, 3rem);
    }

    .capability__intro {
      align-self: start;
    }

    .capability__intro .slide-copy {
      margin-top: clamp(1rem, 2.5vh, 1.8rem);
    }

    .capability-list {
      border-top: 1px solid var(--text-primary);
    }

    .capability-item {
      display: grid;
      grid-template-columns: clamp(3.5rem, 6vw, 6rem) 1fr auto;
      gap: clamp(1rem, 2vw, 2rem);
      align-items: center;
      min-height: clamp(5rem, 12vh, 7.5rem);
      border-bottom: 1px solid var(--line);
    }

    .capability-item__index {
      color: var(--accent);
      font-size: clamp(0.72rem, 0.9vw, 0.85rem);
      font-weight: 800;
      letter-spacing: 0.1em;
    }

    .capability-item h3 {
      margin: 0;
      font-size: clamp(1.15rem, 2.1vw, 1.9rem);
      line-height: 1.2;
      letter-spacing: -0.04em;
    }

    .capability-item p {
      max-width: 18rem;
      margin: 0;
      color: var(--text-secondary);
      font-size: clamp(0.76rem, 1vw, 0.9rem);
      line-height: 1.5;
      text-align: right;
    }

    /* Slide 4 */
    .closing {
      background: var(--text-primary);
      color: #FFFFFF;
    }

    .closing .wordmark,
    .closing .slide-title {
      color: #FFFFFF;
    }

    .closing .meta,
    .closing .page-number,
    .closing .slide-copy {
      color: #A8A6B8;
    }

    .closing .eyebrow {
      color: #A85FEA;
    }

    .closing .signature-dot {
      background: #A85FEA;
      box-shadow: 0 0 0 4px rgb(168 95 234 / 16%);
    }

    .closing__body {
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: minmax(0, 1.18fr) minmax(16rem, 0.82fr);
      gap: clamp(3rem, 8vw, 9rem);
      align-items: center;
      flex: 1;
    }

    .closing__title {
      max-width: 55rem;
      margin:
        clamp(1rem, 3vh, 2rem)
        0
        clamp(1.2rem, 3vh, 2rem);
      font-size: clamp(2.8rem, 6.5vw, 6.6rem);
      line-height: 0.98;
    }

    .closing__title .accent {
      color: #A85FEA;
    }

    .contact {
      align-self: center;
      padding: clamp(1.5rem, 4vw, 3.2rem);
      border: 1px solid #2C2C3A;
      background: #15151E;
    }

    .contact__label {
      margin-bottom: clamp(1.5rem, 4vh, 3rem);
      color: #A85FEA;
    }

    .contact__line {
      padding: clamp(0.8rem, 2vh, 1.2rem) 0;
      border-bottom: 1px solid #2C2C3A;
    }

    .contact__line:last-child {
      border-bottom: 0;
    }

    .contact__key {
      display: block;
      margin-bottom: 0.35rem;
      color: #A8A6B8;
      font-size: clamp(0.66rem, 0.8vw, 0.76rem);
      font-weight: 700;
      letter-spacing: 0.12em;
      text-transform: uppercase;
    }

    .contact__value {
      color: #FFFFFF;
      font-size: clamp(0.9rem, 1.25vw, 1.1rem);
      font-weight: 650;
    }

    /* Navigation */
    .nav {
      position: fixed;
      z-index: 30;
      top: 50%;
      right: clamp(0.8rem, 2vw, 1.8rem);
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
      transform: translateY(-50%);
    }

    .nav__dot {
      width: 0.52rem;
      height: 0.52rem;
      padding: 0;
      border: 0;
      border-radius: 50%;
      background: #D8D4E0;
      cursor: pointer;
      transition:
        transform 200ms ease,
        background 200ms ease;
    }

    .nav__dot:hover {
      transform: scale(1.2);
    }

    .nav__dot.is-active {
      background: var(--accent);
      transform: scale(1.35);
    }

    .nav__dot:focus-visible {
      outline: 2px solid var(--accent);
      outline-offset: 4px;
    }

    .closing.is-active ~ .nav .nav__dot:not(.is-active) {
      background: #5A5A6E;
    }

    @media (max-width: 820px) {
      .cover__body,
      .intro__body,
      .capability__body,
      .closing__body {
        grid-template-columns: 1fr;
        gap: clamp(1.2rem, 4vh, 2.5rem);
      }

      .cover__visual {
        position: absolute;
        right: -8%;
        bottom: 5%;
        z-index: -1;
        min-height: 0;
        opacity: 0.32;
      }

      .intro__body,
      .capability__body {
        align-content: center;
      }

      .capability-item p {
        display: none;
      }

      .contact {
        padding: clamp(1rem, 3vw, 1.6rem);
      }

      .nav {
        top: auto;
        right: 50%;
        bottom: clamp(0.8rem, 2vh, 1.4rem);
        flex-direction: row;
        transform: translateX(50%);
      }

      .slide-footer {
        padding-bottom: 1.4rem;
      }
    }

    @media (max-height: 700px) {
      :root {
        --scale: 0.9;
      }

      .slide {
        padding-top: clamp(1.6rem, 4vh, 2.5rem);
        padding-bottom: clamp(1.4rem, 3vh, 2rem);
      }

      .principle {
        padding-top: 0.7rem;
        padding-bottom: 0.7rem;
      }
    }

    @media (max-height: 600px) {
      :root {
        --scale: 0.8;
      }

      .slide-copy {
        line-height: 1.5;
      }

      .cover__title,
      .closing__title {
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
      }

      .capability-item {
        min-height: clamp(3.6rem, 10vh, 5rem);
      }
    }

    @media (prefers-reduced-motion: reduce) {
      *,
      *::before,
      *::after {
        scroll-behavior: auto !important;
        transition: none !important;
        animation: none !important;
      }
    }

    @media print {
      html,
      body {
        height: auto;
        overflow: visible;
      }

      .deck {
        height: auto;
      }

      .progress,
      .nav {
        display: none;
      }

      .slide {
        position: relative;
        visibility: visible;
        opacity: 1;
        transform: none;
        page-break-after: always;
        break-after: page;
      }
    }
  </style>
</head>

<body>
  <main class="deck" aria-label="WIGTN 회사소개 프레젠테이션">
    <div class="progress" aria-hidden="true">
      <div class="progress__bar"></div>
    </div>

    <!-- 01. Cover -->
    <section class="slide is-active" aria-label="표지">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">
          wigtn<span class="wordmark__dot">.</span>
        </div>
        <span class="meta">Company Introduction · 2026</span>
      </header>

      <div class="cover__body">
        <div>
          <span class="eyebrow">We design what comes next</span>
          <h1 class="cover__title">
            생각을<br />
            작동하는<br />
            경험으로<span class="accent">.</span>
          </h1>
          <p class="cover__statement">
            WIGTN은 복잡한 문제를 선명한 전략과 제품 경험으로 전환합니다.
            기술과 디자인이 비즈니스의 다음 움직임을 만들도록 설계합니다.
          </p>
        </div>

        <div class="cover__visual" aria-hidden="true">
          <div class="orbit">
            <div class="orbit__core">w.</div>
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="meta">Strategy · Product · Experience</span>
        <span class="page-number">
          01 <span class="signature-dot"></span>
        </span>
      </footer>
    </section>

    <!-- 02. Who we are -->
    <section class="slide" aria-label="WIGTN 소개">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">
          wigtn<span class="wordmark__dot">.</span>
        </div>
        <span class="micro-label">Who we are</span>
      </header>

      <div class="intro__body">
        <div class="intro__lead">
          <span class="eyebrow">One clear direction</span>
          <h2 class="slide-title">
            본질을 찾고,<br />
            가능성을 설계합니다.
          </h2>
          <p class="slide-copy">
            우리는 전략, 디자인, 기술을 하나의 과정으로 연결합니다.
            보여주기 위한 결과물이 아니라 실제로 선택되고 사용되며
            성장하는 경험을 만듭니다.
          </p>
        </div>

        <div class="principles">
          <article class="principle">
            <span class="principle__number">01.</span>
            <div>
              <h3>Clarity first</h3>
              <p>
                흩어진 요구와 맥락을 정리해 모두가 공유할 수 있는
                하나의 문제와 방향으로 정의합니다.
              </p>
            </div>
          </article>

          <article class="principle">
            <span class="principle__number">02.</span>
            <div>
              <h3>Experience matters</h3>
              <p>
                기능의 완성을 넘어 사용자가 이해하고 신뢰하며
                계속 선택하는 경험을 설계합니다.
              </p>
            </div>
          </article>

          <article class="principle">
            <span class="principle__number">03.</span>
            <div>
              <h3>Built to move</h3>
              <p>
                빠르게 검증하고 유연하게 확장할 수 있도록
                아이디어를 실행 가능한 시스템으로 구체화합니다.
              </p>
            </div>
          </article>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="meta">WIGTN / Company Introduction</span>
        <span class="page-number">
          02 <span class="signature-dot"></span>
        </span>
      </footer>
    </section>

    <!-- 03. Capabilities -->
    <section class="slide" aria-label="핵심 역량">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">
          wigtn<span class="wordmark__dot">.</span>
        </div>
        <span class="micro-label">What we do</span>
      </header>

      <div class="capability__body">
        <div class="capability__intro">
          <span class="eyebrow">Connected capabilities</span>
          <h2 class="slide-title">
            전략에서<br />
            실행까지.
          </h2>
          <p class="slide-copy">
            문제를 발견하는 순간부터 제품이 시장에서 작동하는 순간까지,
            끊김 없는 하나의 팀으로 함께합니다.
          </p>
        </div>

        <div class="capability-list">
          <article class="capability-item">
            <span class="capability-item__index">01.</span>
            <h3>Business Strategy</h3>
            <p>리서치 · 문제 정의 · 사업 및 서비스 전략</p>
          </article>

          <article class="capability-item">
            <span class="capability-item__index">02.</span>
            <h3>Product Experience</h3>
            <p>UX/UI · 프로토타입 · 디자인 시스템</p>
          </article>

          <article class="capability-item">
            <span class="capability-item__index">03.</span>
            <h3>Technology Delivery</h3>
            <p>웹·앱 구축 · 시스템 연결 · 제품 고도화</p>
          </article>
        </div>
      </div>

      <footer class="slide-footer">
        <span class="meta">Strategy × Design × Technology</span>
        <span class="page-number">
          03 <span class="signature-dot"></span>
        </span>
      </footer>
    </section>

    <!-- 04. Closing -->
    <section class="slide closing" aria-label="마무리">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">
          wigtn<span class="wordmark__dot">.</span>
        </div>
        <span class="meta">Let’s make the next move</span>
      </header>

      <div class="closing__body">
        <div>
          <span class="eyebrow">Start with a question</span>
          <h2 class="slide-title closing__title">
            다음 가능성을<br />
            함께 만듭니다<span class="accent">.</span>
          </h2>
          <p class="slide-copy">
            해결해야 할 문제가 있다면, 그 문제를 가장 선명한 기회로
            바꾸는 대화부터 시작하겠습니다.
          </p>
        </div>

        <aside class="contact" aria-label="연락처">
          <div class="micro-label contact__label">Contact</div>

          <div class="contact__line">
            <span class="contact__key">Email</span>
            <span class="contact__value">hello@wigtn.com</span>
          </div>

          <div class="contact__line">
            <span class="contact__key">Web</span>
            <span class="contact__value">wigtn.com</span>
          </div>

          <div class="contact__line">
            <span class="contact__key">Based in</span>
            <span class="contact__value">Seoul, Korea</span>
          </div>
        </aside>
      </div>

      <footer class="slide-footer">
        <span class="meta">Thank you</span>
        <span class="page-number">
          04 <span class="signature-dot"></span>
        </span>
      </footer>
    </section>

    <nav class="nav" aria-label="슬라이드 이동">
      <button
        class="nav__dot is-active"
        type="button"
        aria-label="1번 슬라이드"
        aria-current="true"
        data-slide="0"
      ></button>
      <button
        class="nav__dot"
        type="button"
        aria-label="2번 슬라이드"
        data-slide="1"
      ></button>
      <button
        class="nav__dot"
        type="button"
        aria-label="3번 슬라이드"
        data-slide="2"
      ></button>
      <button
        class="nav__dot"
        type="button"
        aria-label="4번 슬라이드"
        data-slide="3"
      ></button>
    </nav>
  </main>

  <script>
    (() => {
      const slides = [...document.querySelectorAll(".slide")];
      const navDots = [...document.querySelectorAll(".nav__dot")];
      const progressBar = document.querySelector(".progress__bar");

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

        navDots.forEach((dot, i) => {
          const active = i === current;
          dot.classList.toggle("is-active", active);

          if (active) {
            dot.setAttribute("aria-current", "true");
          } else {
            dot.removeAttribute("aria-current");
          }
        });

        progressBar.style.width =
          `${((current + 1) / slides.length) * 100}%`;

        document.title =
          `WIGTN — ${String(current + 1).padStart(2, "0")} / ` +
          `${String(slides.length).padStart(2, "0")}`;
      }

      function next() {
        showSlide(current + 1);
      }

      function previous() {
        showSlide(current - 1);
      }

      document.addEventListener("keydown", (event) => {
        if (["ArrowRight", "ArrowDown", "PageDown"].includes(event.key)) {
          event.preventDefault();
          next();
        }

        if (["ArrowLeft", "ArrowUp", "PageUp"].includes(event.key)) {
          event.preventDefault();
          previous();
        }

        if (event.key === " ") {
          event.preventDefault();
          event.shiftKey ? previous() : next();
        }

        if (event.key === "Home") {
          showSlide(0);
        }

        if (event.key === "End") {
          showSlide(slides.length - 1);
        }
      });

      document.addEventListener(
        "wheel",
        (event) => {
          if (wheelLocked || Math.abs(event.deltaY) < 12) return;

          wheelLocked = true;
          event.deltaY > 0 ? next() : previous();

          window.setTimeout(() => {
            wheelLocked = false;
          }, 500);
        },
        { passive: true }
      );

      document.addEventListener(
        "touchstart",
        (event) => {
          touchStartX = event.changedTouches[0].clientX;
          touchStartY = event.changedTouches[0].clientY;
        },
        { passive: true }
      );

      document.addEventListener(
        "touchend",
        (event) => {
          const deltaX =
            event.changedTouches[0].clientX - touchStartX;
          const deltaY =
            event.changedTouches[0].clientY - touchStartY;

          if (
            Math.abs(deltaX) < 48 ||
            Math.abs(deltaX) < Math.abs(deltaY)
          ) {
            return;
          }

          deltaX < 0 ? next() : previous();
        },
        { passive: true }
      );

      navDots.forEach((dot) => {
        dot.addEventListener("click", () => {
          showSlide(Number(dot.dataset.slide));
        });
      });

      showSlide(0);
    })();
  </script>
</body>
</html>
```