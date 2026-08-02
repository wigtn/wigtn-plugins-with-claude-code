<div align="center">

[English](README.md) | [한국어](README.ko.md) | [中文](README.cn.md)

# WIGTN Plugins

**하나의 플러그인. 12개 에이전트. 아이디어에서 프로덕션까지.**

![Version](https://img.shields.io/badge/v0.1.14-Unified_Plugin-FF6B6B?style=for-the-badge)
![Agents](https://img.shields.io/badge/13-Agents-5A67D8?style=for-the-badge)
![Commands](https://img.shields.io/badge/5-Commands-38B2AC?style=for-the-badge)
![Skills](https://img.shields.io/badge/6-Skills-00D4AA?style=for-the-badge)
![Styles](https://img.shields.io/badge/20-Design_Styles-F59E0B?style=for-the-badge)

[![GitHub Stars](https://img.shields.io/github/stars/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/stargazers)
[![License](https://img.shields.io/badge/license-Apache_2.0-blue?style=flat-square)](LICENSE)
[![Contributors](https://img.shields.io/github/contributors/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/graphs/contributors)
[![Last Commit](https://img.shields.io/github/last-commit/wigtn/wigtn-plugins?style=flat-square)](https://github.com/wigtn/wigtn-plugins/commits/main)

</div>

---

## 왜 WIGTN-Coding인가?

**이 플러그인 없이:**
Claude Code 열기 → 두루뭉술한 프롬프트 작성 → 범용적인 코드 생성 → 30분 동안 수정 → 반복.

**WIGTN-Coding과 함께:**
`/prd` 실행 → 구조화된 스펙 생성 → 12개 에이전트가 병렬로 빌드 → 첫 시도에 프로덕션 수준 코드 완성.

---

## 뭘 하는 플러그인인가

WIGTN Plugins은 Claude Code 플러그인입니다. 만들고 싶은 걸 설명하면, 12개의 전문 에이전트가 나머지를 처리합니다 — 요구사항, 아키텍처, 코드, 리뷰, 커밋까지, 전부 병렬로.

```
/prd "OAuth 기반 SaaS 대시보드"  →  PRD + 작업 계획 30초 만에 생성
/screen-spec dashboard           →  (UI 있을 때) IA + 플로우 + 화면 명세 + 클릭 가능한 HTML 와이어프레임
/implement --parallel            →  백엔드 + 프론트엔드 + AI + 운영 팀이 동시 빌드
/auto-commit                     →  3-에이전트 리뷰, 품질 게이트, 80점 이상이면 자동 커밋
```

---

## 빠른 시작

```bash
# 설치
/plugin marketplace add wigtn/wigtn-plugins
/install wigtn-plugins

# 체험 — 이게 전체 워크플로우입니다
/prd 모던 디자인의 AI 스타트업 랜딩 페이지
/implement ai-landing
/auto-commit
```

끝입니다. 플러그인이 PRD 생성, 4카테고리 품질 분석, 아키텍처 결정, 디자인 스타일 선택, 병렬 빌드, 코드 리뷰, 커밋까지 전부 처리합니다.

---

## 파이프라인

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  /prd "OAuth 기반 SaaS 대시보드"                                             │
│                                                                             │
│  1. 컨텍스트 수집 ──── 프로젝트 구조, 기술 스택, package.json 스캔           │
│  2. AskUserQuestion ── 스케일 등급? (Hobby / Startup / Growth / Enterprise)  │
│  3. PRD 생성 ────────── PRD_{feature}.md  (7개 섹션, Gherkin 스토리)         │
│  4. 작업 계획 ────────── PLAN_{feature}.md (단계별 + 태스크)                  │
│                                                                             │
│  ┌─── prd-reviewer — 4개 적대적 렌즈 ─────────────────────────────────┐    │
│  │  Phase 0: 컨텍스트 수확 (CLAUDE.md, 코드 패턴, 의존성)              │    │
│  │  Phase 1: PRD 구조 파싱                                            │    │
│  │  Phase 2: ════════════ 4개 에이전트 병렬 실행 ═══════════           │    │
│  │           │ 완전성       │ 실현가능성    │ 보안        │ 일관성    │   │    │
│  │           │ FR/NFR/엣지  │ 스택 적합도   │ OWASP       │ 네이밍   │   │    │
│  │           │ 케이스, 중복  │ 변경 영향도   │ 인증/인가    │ PRD↔코드 │   │    │
│  │  Phase 3: 교차 카테고리 종합 (복합 위험 탐지)                        │    │
│  │  Phase 4: 품질 게이트 ─── PASS / WARN / BLOCKED                    │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                          BLOCKED → 중단
                                    │ PASS / WARN
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /implement ai-landing                                                      │
│                                                                             │
│  ┌─── DESIGN 단계 ───────────────────────────────────────────────────┐     │
│  │  ═══════════════ 3개 에이전트 병렬 실행 ═══════════════            │     │
│  │  │ Agent A          │ Agent B              │ Agent C          │   │     │
│  │  │ PRD 로드 +       │ architecture-decision│ 프로젝트 스캔 +  │   │     │
│  │  │ 품질 게이트      │ Mono/Modular/MSA     │ 갭 분석          │   │     │
│  │  ══════════════════════════════════════════════════════════════    │     │
│  │                          │                                        │     │
│  │  팀 배정 ─────────────── 파일 패턴 매칭 → 팀 결정                 │     │
│  │    api/, services/   → 백엔드                                     │     │
│  │    components/, app/ → 프론트엔드                                  │     │
│  │    ai/, llm/         → AI 서버                                    │     │
│  │    Dockerfile, CI/   → 운영                                       │     │
│  │                                                                   │     │
│  │  디자인 디스커버리 (프론트엔드 전용, 기존 스타일 없을 시) ────────  │     │
│  │    VS 기법: 4개 질문 → 스타일별 적합도 % → 선택                   │     │
│  │                                                                   │     │
│  │  ✋ 체크포인트: AskUserQuestion ── 진행 / 상세 검토 / 취소         │     │
│  └───────────────────────────────────────────────────────────────────┘     │
│                                                                             │
│  ┌─── BUILD 단계 ─── team-build-coordinator ─────────────────────────┐     │
│  │                                                                   │     │
│  │  Phase 0: 셋업 ─── SHARED_CONTEXT_{feature}.md + TodoWrite       │     │
│  │           컨텍스트 수확: 기존 코드 샘플링 → 패턴 학습              │     │
│  │                                                                   │     │
│  │  Phase 1: 기반 구축 (백엔드 + 의존 팀 존재 시)                    │     │
│  │           백엔드: DB 스키마, 공유 타입, API 계약서 작성             │     │
│  │                    ↓ 다른 팀 언블록                                │     │
│  │                                                                   │     │
│  │  Phase 2: ════════════ 최대 4개 팀 병렬 실행 ════════════          │     │
│  │           │ 백엔드          │ 프론트엔드     │ AI 서버    │ 운영  │     │
│  │           │ backend-       │ frontend-      │ ai-agent   │ gen  │     │
│  │           │ architect      │ developer      │            │ pur  │     │
│  │           │                │ + 스타일 가이드 │            │      │     │
│  │           │ API, 서비스    │ 페이지, 컴포넌트│ LLM, STT  │ CI   │     │
│  │           │ DB, 미들웨어   │ 상태, 스타일링  │ 프롬프트   │ CD   │     │
│  │           ════════════════════════════════════════════════════     │     │
│  │           ▲ 읽기                   │ 쓰기                         │     │
│  │           └──── SHARED_CONTEXT ────┘                              │     │
│  │                                                                   │     │
│  │  Phase 3: 통합 검증 ─── API 계약 매칭, 타입 일관성,               │     │
│  │           Phase 0 학습 패턴 대비 패턴 검증                         │     │
│  │                                                                   │     │
│  │  Phase 4: 빌드 & 테스트 ─── typecheck + test + build              │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  /auto-commit                                                               │
│                                                                             │
│  Step 1: 브랜치 전략                                                        │
│          피처 브랜치 → 재사용 │ main + PLAN → feat/<name>                   │
│                                                                             │
│  Step 2: 품질 게이트                                                        │
│  ┌─── 파일 ≤5개 & blast radius LOW: code-reviewer (단일) ─────────┐        │
│  │     파일 6개+ 또는 blast radius MEDIUM/HIGH → 카테고리 분할     │        │
│  │                                                                 │        │
│  │  Phase 0: 컨텍스트 수확 (린트 설정, 인접 코드)                   │        │
│  │  Phase 1: 영향 범위 분석 ─── 호출자, 임포터, 영향 점수           │        │
│  │  Phase 2: ═══════════ 3개 에이전트 병렬 실행 ════════════        │        │
│  │           │ 가독성 +          │ 성능 +         │ 모범 사례     │        │
│  │           │ 유지보수성         │ 테스트 가능성   │ + 보안        │        │
│  │           │     (40점)        │   (40점)       │   (20점)      │        │
│  │           ══════════════════════════════════════════════════     │        │
│  │  Phase 3: 계약 검증 (호출자 호환성, 경계, 테스트)                 │        │
│  │                                                                 │        │
│  │  점수 병합: 합산 + 계약 위반 감점 + 보안 오버라이드              │        │
│  │  보안 치명적 → 59점 상한 → FAIL                                 │        │
│  └─────────────────────────────────────────────────────────────────┘        │
│                                                                             │
│  ┌────────────────────────────────────────┐                                 │
│  │ ≥ 80 (PASS)  → Step 4                 │                                 │
│  │ 60-79 (WARN) → code-formatter 자동 수정 → 재평가                        │
│  │ < 60 (FAIL)  → 차단                   │                                 │
│  └────────────────────────────────────────┘                                 │
│                                                                             │
│  Step 4: 커밋 메시지 ─── <type>(<scope>): <subject> + 품질 점수            │
│  ✋ 체크포인트: AskUserQuestion ── PR / Draft PR / 커밋만 / 취소            │
│  Step 5: git commit → git push -u → gh pr create                           │
└─────────────────────────────────────────────────────────────────────────────┘

공유 메모리 (3계층):
  Layer 1 — MEMORY.md ─────────── 세션 간 지속되는 프로젝트 컨벤션
  Layer 2 — SHARED_CONTEXT ────── 세션 스코프 API 계약, 타입, 패턴
  Layer 3 — TodoWrite ─── 대화 내 팀별 작업 추적
```

각 단계는 가능한 곳에서 병렬 실행됩니다. 전체 파이프라인: ~6분 (순차 시 ~20분).

---

## 명령어

| 명령어 | 기능 |
|--------|------|
| `/prd <기능>` | 기능 아이디어로부터 PRD + 단계별 작업 계획 생성 (UI가 있는 기능은 User Roles, Page State Matrix, User Flow 섹션이 추가됨) |
| `/screen-spec <기능>` | 선택적 UI 게이트: IA + 유저 플로우 + 화면별 명세 + 클릭 가능한 HTML 와이어프레임 + Dev Handoff. 흑백 + 의미색 lo-fi 와이어프레임 (스타일 결정은 `/implement` 단계) |
| `/implement <기능>` | 자동 병렬 모드 감지, 설계 + 빌드 (screen-spec 산출물이 있으면 입력으로 사용) |
| `/auto-commit` | 3-에이전트 병렬 리뷰 → 품질 게이트 → 커밋 + PR |
| `/review-pr <PR>` | 터미널에서 GitHub PR 리뷰: diff 분석, 품질 점수, 인라인 코멘트 |

---

<details>
<summary><b>에이전트 (12개)</b> — 클릭하여 펼치기</summary>

### 코디네이터

| 에이전트 | 역할 |
|---------|------|
| `team-build-coordinator` | 백엔드, 프론트엔드, AI, 운영 팀을 병렬 배정 |
| `architecture-decision` | MSA vs 모놀리식 vs 모듈러 모놀리스 |

### 개발자

| 에이전트 | 역할 |
|---------|------|
| `frontend-developer` | React 19, Next.js 16+, 20개 디자인 스타일 |
| `backend-architect` | API 설계, 데이터베이스 스키마, 백엔드 패턴 |
| `mobile-developer` | React Native / Expo, 네이티브 모듈 |
| `ai-agent` | WhisperX STT, OpenAI/Anthropic 통합 |

### 품질

| 에이전트 | 역할 |
|---------|------|
| `code-reviewer` | 5개 카테고리 100점 만점 품질 평가 |
| `pr-reviewer` | GitHub PR diff 리뷰, 100점 만점 평가, 인라인 리뷰 코멘트 (`/review-pr`에서 사용) |
| `prd-reviewer` | 완전성, 실현가능성, 보안, 일관성에서 갭 탐지 |
| `code-formatter` | 다중 언어 자동 포맷팅 및 린트 수정 |
| `design-discovery` | VS 기법 기반 Web/Mobile 스타일 추천 |

</details>

<details>
<summary><b>스킬 (6개)</b> — 클릭하여 펼치기</summary>

| 스킬 | 제공하는 것 |
|------|-----------|
| `code-review-levels` | 심층 리뷰 (Level 3: 호출 체인, 에지 케이스, 동시성) 및 아키텍처 리뷰 (Level 4: SOLID, 계층 위반, 확장성) |
| `design-system-reference` | 20개 스타일 가이드 — 타이포그래피, 색상, 컴포넌트, 모션, 안티패턴. design-discovery와 연동하여 컨텍스트 기반 추천 |
| `handdrawn-diagram` | Mermaid `look:handDrawn`로 손그림(스케치) 스타일 아키텍처/플로우 다이어그램을 커밋 가능한 SVG + PNG로 생성. README, GitHub, Devpost, 슬라이드에서 동일하게 렌더 |
| `screen-spec` | PRD로부터 5종 UI 산출물 생성 — IA, User Flow, 화면별 명세, 클릭 가능한 Wireframe HTML, Dev Handoff. 흑백 + 의미색 lo-fi 와이어프레임(스타일은 `/implement`에서 결정). `/screen-spec`에서 호출 |
| `team-memory-protocol` | 병렬 빌드 중 에이전트 간 공유 컨텍스트(SHARED_CONTEXT) 관리 |
| `wigtn-ppt` | 브랜드 토큰 기반 WIGTN 브랜드 HTML 프레젠테이션 생성(Light/Dark 테마, 템플릿 불필요). 모든 슬라이드에 시그니처 퍼플 점, 로고 에셋이 없으면 CSS/SVG 워드마크 폴백 |

</details>

<details>
<summary><b>디자인 스타일 (20개)</b> — 클릭하여 펼치기</summary>

각 스타일 가이드는 철학, 타이포그래피, 레이아웃, 색상, 컴포넌트, 모션, 안티패턴 체크리스트를 포함합니다.

| 스타일 | 분위기 |
|--------|--------|
| Editorial | 매거진 레이아웃, 강렬한 세리프 타이포그래피 |
| Brutalist | 날것의 대담함, 파격적 |
| Glassmorphism | 블러와 투명도의 젖빛 유리 효과 |
| Swiss Minimal | 그리드 기반, 타이포그래피 중심 |
| Neomorphism | 소프트 UI, 인셋/아웃셋 그림자 |
| Bento Grid | 카드 기반 그리드 (Apple 스타일) |
| Dark Mode First | 처음부터 다크 인터페이스로 설계 |
| Minimal Corporate | 깔끔한 비즈니스 감성 |
| Retro Pixel | CRT 효과, 모노스페이스, 터미널 향수 |
| Organic Shapes | 블롭, 자연 곡선, 대지 색감 |
| Maximalist | 대담한 타이포, 강렬한 색상, 레이어드 |
| 3D Immersive | CSS 3D 변환, 패럴랙스, 깊이감 |
| Liquid Glass | 유체 반투명 유리, 동적 반사 |
| Claymorphism | 부드러운 3D 클레이, 파스텔 톤 |
| Minimalism | 극도의 단순, 여백 중심 |
| Neobrutalism | 컬러풀 악센트, 대담한 보더 |
| Skeuomorphism | 현실적 텍스처, 물리적 메타포 |
| Aurora / Gradient Mesh | 메시 그라디언트, 앰비언트 글로우, 몽환적 |
| Terminal / Hacker | 모노스페이스 중심, 정보 밀도 높은, 시맨틱 컬러 |
| Kinetic Typography | 스크롤 기반 텍스트 애니메이션, 분할 리빌 |

`design-discovery` 에이전트가 VS (Verbalized Sampling) 기법으로 프로젝트에 최적의 스타일을 추천합니다.

</details>

<details>
<summary><b>훅 (4개)</b> — 클릭하여 펼치기</summary>

| 훅 | 트리거 | 기능 |
|----|--------|------|
| 위험 명령 차단 | `Bash` PreToolUse | `rm -rf /`, `git push --force`, `DROP TABLE` 차단 |
| 파이프라인 완료 | Stop | 푸시 전 변경사항 검토 알림 |
| 프론트엔드 포맷팅 | `Write\|Edit` PostToolUse | `.tsx`, `.jsx`, `.css` 파일 prettier/eslint 알림 |
| 백엔드 패턴 준수 | `Write\|Edit` PostToolUse | `.ts`, `.py`, `.go` 파일 에러 핸들링, 입력 검증, 로깅 확인 |

</details>

---

## 시나리오

<details>
<summary><b>풀스택 SaaS 처음부터</b></summary>

```bash
/prd 칸반 보드와 팀 협업이 있는 프로젝트 관리 도구
# → 4-에이전트 분석: "누락: 실시간 동기화, 역할 권한"

/implement --parallel project-management
# 백엔드: API 엔드포인트, Prisma 스키마, 인증 미들웨어
# 프론트엔드: 칸반 보드, 팀 뷰, 대시보드
# 운영: Dockerfile, GitHub Actions CI/CD

/auto-commit
# 3 리뷰어 → 87/100 → 자동 커밋
```

</details>

<details>
<summary><b>React Native 모바일 앱</b></summary>

```bash
/prd 운동 기록, 진행 차트, Apple Health 동기화가 있는 피트니스 트래커

/implement fitness-tracker
# Expo Router + Zustand + MMKV + React Query
# 생체 인증, 햅틱 피드백, 오프라인 동기화
```

</details>

<details>
<summary><b>디자인 주도 랜딩 페이지</b></summary>

```bash
/prd 모던 디자인의 AI 스타트업 랜딩 페이지

/implement ai-landing
# design-discovery 활성화 → Glassmorphism 또는 Liquid Glass 추천
# 프론트엔드 팀: Hero, Features, Pricing, CTA — 선택된 스타일 적용
```

</details>

<details>
<summary><b>백엔드 API + AI 기능</b></summary>

```bash
/prd WhisperX STT와 LLM 요약이 있는 전사 서비스

/implement --parallel transcription-service
# 백엔드 → API + DB + 인증
# AI → WhisperX + OpenAI/Anthropic 패턴
# 프론트엔드 → 업로드 UI + 전사 뷰어
```

</details>

---

## 기술 스택

| 도메인 | 기술 |
|--------|------|
| 프론트엔드 | React 19, Next.js 16+, Tailwind CSS, Radix UI |
| 백엔드 | NestJS, Express, FastAPI, Prisma, Drizzle |
| 모바일 | React Native 0.73+, Expo SDK 52+ |
| AI | WhisperX, OpenAI GPT, Anthropic Claude |
| DevOps | Docker, Kubernetes, GitHub Actions |
| 디자인 | 20개 스타일 시스템, VS 기반 디스커버리, HIG, MD3 |

---

## 기여하기

```bash
git checkout -b feature/amazing-skill
# 변경사항 작성
git commit -m 'feat: Add amazing skill'
git push origin feature/amazing-skill
# PR 생성
```

---

## 라이선스

Apache License 2.0 — [LICENSE](LICENSE) 참조.

---

<div align="center">

**Built by [WIGTN Crew](https://github.com/wigtn)**

AI 엔지니어 5명. AI를 연구하지 않습니다 — 그냥 만듭니다.

</div>
