공식 [WIGTN 소개](https://wigtn.com/)와 [ACL Anthology의 WIGVO 발표 정보](https://aclanthology.org/2026.acl-demo.33/)를 바탕으로 구성했습니다.

```html
<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="description" content="WIGTN 회사소개 — AI-native builder crew" />
  <title>WIGTN — Company Introduction</title>

  <style>
    :root {
      /* WIGTN brand palette */
      --wigtn-navy: #101828;
      --wigtn-purple: #7c3aed;
      --wigtn-purple-soft: #ede9fe;
      --wigtn-white: #ffffff;
      --wigtn-ink: #16161d;
      --wigtn-muted: #667085;
      --wigtn-line: #e4e7ec;

      --slide-ratio: 16 / 9;
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
      background: #090d17;
      color: var(--wigtn-ink);
      font-family:
        Pretendard,
        "Noto Sans KR",
        "Apple SD Gothic Neo",
        Inter,
        Arial,
        sans-serif;
    }

    button,
    a {
      font: inherit;
    }

    button {
      color: inherit;
    }

    .deck {
      position: relative;
      width: 100%;
      height: 100%;
    }

    .slide {
      position: absolute;
      inset: 0;
      display: grid;
      grid-template-rows: auto 1fr auto;
      width: 100%;
      height: 100%;
      padding: clamp(30px, 5vw, 76px);
      overflow: hidden;
      background: var(--wigtn-white);
      opacity: 0;
      visibility: hidden;
      transform: translateX(5%);
      transition:
        opacity .55s var(--ease),
        transform .7s var(--ease),
        visibility .55s;
    }

    .slide.active {
      z-index: 2;
      opacity: 1;
      visibility: visible;
      transform: translateX(0);
    }

    .slide.previous {
      transform: translateX(-5%);
    }

    .slide::after {
      position: absolute;
      right: -12vw;
      bottom: -20vw;
      width: 44vw;
      height: 44vw;
      border: 1px solid rgba(124, 58, 237, .1);
      border-radius: 50%;
      content: "";
      pointer-events: none;
    }

    .slide--dark {
      color: var(--wigtn-white);
      background:
        radial-gradient(
          circle at 82% 12%,
          rgba(124, 58, 237, .22),
          transparent 28%
        ),
        var(--wigtn-navy);
    }

    .slide--purple {
      color: var(--wigtn-white);
      background:
        linear-gradient(135deg, #5b21b6 0%, var(--wigtn-purple) 55%, #8b5cf6 100%);
    }

    .slide-header,
    .slide-footer {
      position: relative;
      z-index: 2;
      display: flex;
      align-items: center;
      justify-content: space-between;
    }

    .wordmark {
      display: inline-flex;
      align-items: baseline;
      color: inherit;
      font-size: clamp(24px, 2.2vw, 38px);
      font-weight: 900;
      letter-spacing: -.075em;
      line-height: 1;
      text-decoration: none;
    }

    .wordmark-dot {
      color: var(--wigtn-purple);
    }

    .slide--purple .wordmark-dot {
      color: #d8b4fe;
    }

    .section-label {
      color: var(--wigtn-muted);
      font-size: clamp(10px, .85vw, 14px);
      font-weight: 750;
      letter-spacing: .18em;
      text-transform: uppercase;
    }

    .slide--dark .section-label,
    .slide--purple .section-label {
      color: rgba(255, 255, 255, .6);
    }

    /* Consistent purple point on every slide */
    .brand-point {
      display: inline-block;
      width: clamp(11px, 1vw, 16px);
      aspect-ratio: 1;
      border-radius: 50%;
      background: var(--wigtn-purple);
      box-shadow: 0 0 0 8px rgba(124, 58, 237, .1);
    }

    .slide--purple .brand-point {
      background: var(--wigtn-white);
      box-shadow: 0 0 0 8px rgba(255, 255, 255, .14);
    }

    .slide-body {
      position: relative;
      z-index: 1;
      align-self: center;
      width: 100%;
    }

    h1,
    h2,
    h3,
    p {
      margin: 0;
    }

    h1 {
      max-width: 1000px;
      font-size: clamp(54px, 7.2vw, 124px);
      font-weight: 850;
      letter-spacing: -.065em;
      line-height: .94;
    }

    h2 {
      max-width: 930px;
      font-size: clamp(42px, 5.2vw, 88px);
      font-weight: 840;
      letter-spacing: -.055em;
      line-height: 1;
    }

    .accent {
      color: var(--wigtn-purple);
    }

    .slide--purple .accent {
      color: #ede9fe;
    }

    .lead {
      max-width: 760px;
      margin-top: clamp(24px, 3vw, 48px);
      color: var(--wigtn-muted);
      font-size: clamp(17px, 1.65vw, 29px);
      font-weight: 450;
      letter-spacing: -.025em;
      line-height: 1.55;
    }

    .slide--dark .lead,
    .slide--purple .lead {
      color: rgba(255, 255, 255, .7);
    }

    .eyebrow {
      display: flex;
      gap: 12px;
      align-items: center;
      margin-bottom: clamp(22px, 3vw, 42px);
      color: var(--wigtn-purple);
      font-size: clamp(12px, 1vw, 16px);
      font-weight: 800;
      letter-spacing: .15em;
      text-transform: uppercase;
    }

    .eyebrow::before {
      width: 28px;
      height: 2px;
      background: currentColor;
      content: "";
    }

    .slide--dark .eyebrow,
    .slide--purple .eyebrow {
      color: #c4b5fd;
    }

    .hero-meta {
      display: flex;
      gap: clamp(24px, 5vw, 72px);
      margin-top: clamp(40px, 6vw, 88px);
    }

    .hero-meta-item {
      display: grid;
      gap: 7px;
    }

    .hero-meta strong {
      font-size: clamp(16px, 1.4vw, 24px);
      font-weight: 750;
    }

    .hero-meta span {
      color: rgba(255, 255, 255, .48);
      font-size: clamp(11px, .85vw, 14px);
      letter-spacing: .08em;
      text-transform: uppercase;
    }

    .grid-four {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: clamp(12px, 1.4vw, 24px);
      margin-top: clamp(38px, 5vw, 72px);
    }

    .activity {
      min-height: clamp(170px, 20vw, 310px);
      padding: clamp(20px, 2.2vw, 36px);
      border: 1px solid var(--wigtn-line);
      border-radius: 3px;
      background: rgba(255, 255, 255, .74);
      transition:
        color .25s ease,
        border-color .25s ease,
        transform .25s ease;
    }

    .activity:hover {
      color: var(--wigtn-white);
      border-color: var(--wigtn-purple);
      background: var(--wigtn-purple);
      transform: translateY(-8px);
    }

    .activity-number {
      display: block;
      margin-bottom: clamp(42px, 5vw, 78px);
      color: var(--wigtn-purple);
      font-size: 13px;
      font-weight: 850;
    }

    .activity:hover .activity-number {
      color: #ddd6fe;
    }

    .activity h3 {
      font-size: clamp(18px, 1.65vw, 28px);
      letter-spacing: -.035em;
    }

    .activity p {
      margin-top: 12px;
      color: var(--wigtn-muted);
      font-size: clamp(12px, 1vw, 16px);
      line-height: 1.55;
    }

    .activity:hover p {
      color: rgba(255, 255, 255, .75);
    }

    .project-layout {
      display: grid;
      grid-template-columns: .8fr 1.2fr;
      gap: clamp(44px, 7vw, 110px);
      align-items: end;
    }

    .projects {
      display: grid;
      border-top: 1px solid rgba(255, 255, 255, .18);
    }

    .project {
      display: grid;
      grid-template-columns: 56px 1fr auto;
      gap: 20px;
      align-items: center;
      padding: clamp(17px, 2vw, 28px) 0;
      border-bottom: 1px solid rgba(255, 255, 255, .18);
    }

    .project-index {
      color: #c4b5fd;
      font-size: 12px;
      font-weight: 850;
    }

    .project h3 {
      font-size: clamp(19px, 1.8vw, 31px);
      letter-spacing: -.035em;
    }

    .project p {
      margin-top: 5px;
      color: rgba(255, 255, 255, .57);
      font-size: clamp(11px, .9vw, 15px);
    }

    .project-tag {
      padding: 7px 10px;
      border: 1px solid rgba(196, 181, 253, .35);
      border-radius: 999px;
      color: #ddd6fe;
      font-size: 10px;
      font-weight: 800;
      letter-spacing: .08em;
      text-transform: uppercase;
      white-space: nowrap;
    }

    .cta-layout {
      display: grid;
      grid-template-columns: 1.3fr .7fr;
      gap: 8vw;
      align-items: end;
    }

    .contact-card {
      padding: clamp(24px, 3vw, 46px);
      border: 1px solid rgba(255, 255, 255, .22);
      background: rgba(255, 255, 255, .08);
      backdrop-filter: blur(18px);
    }

    .contact-card span {
      display: block;
      color: rgba(255, 255, 255, .55);
      font-size: 11px;
      font-weight: 800;
      letter-spacing: .14em;
      text-transform: uppercase;
    }

    .contact-card a {
      display: block;
      margin-top: 12px;
      color: var(--wigtn-white);
      font-size: clamp(18px, 1.65vw, 28px);
      font-weight: 700;
      letter-spacing: -.03em;
      text-decoration: none;
    }

    .contact-card a + span {
      margin-top: 34px;
    }

    .slide-footer {
      color: var(--wigtn-muted);
      font-size: 11px;
      font-weight: 650;
      letter-spacing: .1em;
      text-transform: uppercase;
    }

    .slide--dark .slide-footer,
    .slide--purple .slide-footer {
      color: rgba(255, 255, 255, .42);
    }

    .slide-number {
      font-variant-numeric: tabular-nums;
    }

    .controls {
      position: fixed;
      right: 22px;
      bottom: 20px;
      z-index: 20;
      display: flex;
      gap: 8px;
    }

    .control {
      display: grid;
      width: 42px;
      height: 42px;
      padding: 0;
      border: 1px solid rgba(255, 255, 255, .18);
      border-radius: 50%;
      color: var(--wigtn-white);
      background: rgba(16, 24, 40, .82);
      cursor: pointer;
      place-items: center;
      backdrop-filter: blur(12px);
    }

    .control:hover {
      background: var(--wigtn-purple);
    }

    .progress {
      position: fixed;
      bottom: 0;
      left: 0;
      z-index: 30;
      width: 100%;
      height: 4px;
      background: rgba(124, 58, 237, .16);
    }

    .progress-bar {
      width: 25%;
      height: 100%;
      background: var(--wigtn-purple);
      transition: width .55s var(--ease);
    }

    @media (max-width: 900px) {
      .grid-four {
        grid-template-columns: repeat(2, 1fr);
      }

      .activity {
        min-height: 150px;
      }

      .activity-number {
        margin-bottom: 28px;
      }

      .project-layout,
      .cta-layout {
        grid-template-columns: 1fr;
      }

      .project-layout {
        gap: 40px;
      }
    }

    @media (max-width: 580px) {
      .slide {
        padding: 26px 24px 60px;
      }

      .grid-four {
        gap: 9px;
      }

      .activity {
        min-height: 132px;
        padding: 16px;
      }

      .activity-number {
        margin-bottom: 20px;
      }

      .activity p {
        display: none;
      }

      .project {
        grid-template-columns: 34px 1fr;
      }

      .project-tag {
        display: none;
      }

      .hero-meta {
        flex-wrap: wrap;
      }
    }

    @media print {
      html,
      body {
        height: auto;
        overflow: visible;
        background: white;
      }

      .deck {
        height: auto;
      }

      .slide {
        position: relative;
        width: 100vw;
        height: 56.25vw;
        page-break-after: always;
        opacity: 1;
        visibility: visible;
        transform: none;
      }

      .controls,
      .progress {
        display: none;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .slide,
      .progress-bar {
        transition: none;
      }
    }
  </style>
</head>

<body>
  <main class="deck" aria-label="WIGTN 회사소개 슬라이드">
    <!-- 01 / Cover -->
    <section class="slide slide--dark active" aria-labelledby="slide-1-title">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">wigtn<span class="wordmark-dot">.</span></div>
        <span class="brand-point" aria-hidden="true"></span>
      </header>

      <div class="slide-body">
        <div class="eyebrow">AI-native builder crew</div>
        <h1 id="slide-1-title">
          Learn. Build.<br />
          Share <span class="accent">in the open.</span>
        </h1>

        <p class="lead">
          WIGTN은 연구와 제품 사이의 거리를 좁히는 AI 빌더 커뮤니티입니다.
          배우고, 만들고, 검증한 모든 것을 다시 오픈 생태계에 돌려줍니다.
        </p>

        <div class="hero-meta" aria-label="WIGTN 핵심 정보">
          <div class="hero-meta-item">
            <strong>Seoul, Korea</strong>
            <span>Based in</span>
          </div>
          <div class="hero-meta-item">
            <strong>AI · Open Source</strong>
            <span>What we build</span>
          </div>
          <div class="hero-meta-item">
            <strong>Research → Product</strong>
            <span>How we work</span>
          </div>
        </div>
      </div>

      <footer class="slide-footer">
        <span>Company introduction · 2026</span>
        <span class="slide-number">01 / 04</span>
      </footer>
    </section>

    <!-- 02 / Activities -->
    <section class="slide" aria-labelledby="slide-2-title">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">wigtn<span class="wordmark-dot">.</span></div>
        <span class="brand-point" aria-hidden="true"></span>
      </header>

      <div class="slide-body">
        <div class="eyebrow">What we do together</div>
        <h2 id="slide-2-title">
          아이디어를 <span class="accent">공개된 결과</span>로.
        </h2>

        <div class="grid-four">
          <article class="activity">
            <span class="activity-number">01</span>
            <h3>Open Research</h3>
            <p>AI를 공개적으로 연구하고 발견한 내용을 논문과 벤치마크로 공유합니다.</p>
          </article>

          <article class="activity">
            <span class="activity-number">02</span>
            <h3>Open Source</h3>
            <p>모델과 도구, 플러그인을 실제로 사용할 수 있는 코드로 배포합니다.</p>
          </article>

          <article class="activity">
            <span class="activity-number">03</span>
            <h3>Meetups</h3>
            <p>세미나와 스터디, 데모를 통해 빌더가 직접 경험을 나눕니다.</p>
          </article>

          <article class="activity">
            <span class="activity-number">04</span>
            <h3>Challenges</h3>
            <p>해커톤과 도전을 통해 빠르게 만들고 공개적으로 검증합니다.</p>
          </article>
        </div>
      </div>

      <footer class="slide-footer">
        <span>Research · Source · Community · Challenge</span>
        <span class="slide-number">02 / 04</span>
      </footer>
    </section>

    <!-- 03 / Work -->
    <section class="slide slide--dark" aria-labelledby="slide-3-title">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">wigtn<span class="wordmark-dot">.</span></div>
        <span class="brand-point" aria-hidden="true"></span>
      </header>

      <div class="slide-body project-layout">
        <div>
          <div class="eyebrow">Selected work</div>
          <h2 id="slide-3-title">
            빠르게 만들고,<br />
            <span class="accent">깊게 증명합니다.</span>
          </h2>
          <p class="lead">
            프로토타입에 머물지 않습니다. 코드로 배포하고, 현장에서 검증하고,
            연구 결과로 남깁니다.
          </p>
        </div>

        <div class="projects">
          <article class="project">
            <span class="project-index">01</span>
            <div>
              <h3>WIGVO</h3>
              <p>일반 전화망 기반 실시간 양방향 음성 번역</p>
            </div>
            <span class="project-tag">ACL 2026</span>
          </article>

          <article class="project">
            <span class="project-index">02</span>
            <div>
              <h3>WigtnOCR</h3>
              <p>한국 공공문서에 특화된 VLM 문서 파서</p>
            </div>
            <span class="project-tag">Open model</span>
          </article>

          <article class="project">
            <span class="project-index">03</span>
            <div>
              <h3>WIGENT</h3>
              <p>여러 AI 에이전트가 논쟁하며 답을 검증하는 토론 아레나</p>
            </div>
            <span class="project-tag">Grand prize</span>
          </article>

          <article class="project">
            <span class="project-index">04</span>
            <div>
              <h3>WIGTN Flake</h3>
              <p>데이터 위에서 목적 중심 의사결정을 돕는 AI 전문가 토론</p>
            </div>
            <span class="project-tag">2nd place</span>
          </article>
        </div>
      </div>

      <footer class="slide-footer">
        <span>Built fast. Shipped often. Sometimes peer-reviewed.</span>
        <span class="slide-number">03 / 04</span>
      </footer>
    </section>

    <!-- 04 / Closing -->
    <section class="slide slide--purple" aria-labelledby="slide-4-title">
      <header class="slide-header">
        <div class="wordmark" aria-label="wigtn">wigtn<span class="wordmark-dot">.</span></div>
        <span class="brand-point" aria-hidden="true"></span>
      </header>

      <div class="slide-body cta-layout">
        <div>
          <div class="eyebrow">Build with us</div>
          <h2 id="slide-4-title">
            함께 만들면,<br />
            더 멀리 <span class="accent">공개할 수 있습니다.</span>
          </h2>
          <p class="lead">
            연구, 오픈소스, 세미나, 공동 프로젝트까지.<br />
            만들고 있는 것이 있다면 WIGTN과 이야기를 시작하세요.
          </p>
        </div>

        <aside class="contact-card" aria-label="WIGTN 연락처">
          <span>Email</span>
          <a href="mailto:contact@wigtn.com">contact@wigtn.com</a>

          <span>Web</span>
          <a href="https://wigtn.com">wigtn.com</a>
        </aside>
      </div>

      <footer class="slide-footer">
        <span>Everything we learn, we share.</span>
        <span class="slide-number">04 / 04</span>
      </footer>
    </section>
  </main>

  <nav class="controls" aria-label="슬라이드 이동">
    <button class="control" id="previous" type="button" aria-label="이전 슬라이드">←</button>
    <button class="control" id="next" type="button" aria-label="다음 슬라이드">→</button>
  </nav>

  <div class="progress" aria-hidden="true">
    <div class="progress-bar" id="progressBar"></div>
  </div>

  <script>
    (() => {
      const slides = [...document.querySelectorAll(".slide")];
      const progressBar = document.getElementById("progressBar");
      const previousButton = document.getElementById("previous");
      const nextButton = document.getElementById("next");
      let current = 0;
      let touchStartX = 0;

      function showSlide(index) {
        current = Math.max(0, Math.min(index, slides.length - 1));

        slides.forEach((slide, slideIndex) => {
          slide.classList.toggle("active", slideIndex === current);
          slide.classList.toggle("previous", slideIndex < current);
          slide.setAttribute("aria-hidden", slideIndex !== current);
        });

        progressBar.style.width = `${((current + 1) / slides.length) * 100}%`;
        history.replaceState(null, "", `#${current + 1}`);
      }

      function next() {
        showSlide(current + 1);
      }

      function previous() {
        showSlide(current - 1);
      }

      previousButton.addEventListener("click", previous);
      nextButton.addEventListener("click", next);

      window.addEventListener("keydown", event => {
        if (["ArrowRight", "PageDown", " "].includes(event.key)) {
          event.preventDefault();
          next();
        }

        if (["ArrowLeft", "PageUp"].includes(event.key)) {
          event.preventDefault();
          previous();
        }

        if (event.key === "Home") showSlide(0);
        if (event.key === "End") showSlide(slides.length - 1);
      });

      window.addEventListener("wheel", event => {
        if (Math.abs(event.deltaY) < 24) return;
        event.deltaY > 0 ? next() : previous();
      }, { passive: true });

      window.addEventListener("touchstart", event => {
        touchStartX = event.changedTouches[0].clientX;
      }, { passive: true });

      window.addEventListener("touchend", event => {
        const distance = event.changedTouches[0].clientX - touchStartX;
        if (Math.abs(distance) < 50) return;
        distance < 0 ? next() : previous();
      }, { passive: true });

      const initial = Number(location.hash.slice(1)) - 1;
      showSlide(Number.isFinite(initial) && initial >= 0 ? initial : 0);
    })();
  </script>
</body>
</html>
```