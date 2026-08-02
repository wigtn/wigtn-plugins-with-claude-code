# 더 강한 코딩 모델에서 WIGTN 플러그인은 무엇을 남겨야 하는가

## GPT‑5.5/5.6 Sol 전달 워크플로 701회 평가와 Codex v0.2 후보

> 2026-07-27 · Codex CLI `0.146.0-alpha.3.1`  
> GPT‑5.6 arm: `gpt-5.6-sol`, reasoning effort `medium`
>
> **범위:** 모델 비교와 개혁 대상은 Codex 플러그인이다. 기존 Claude Code
> 플러그인은 기능 분류의 원자료로만 읽었으며 이번 작업에서 개편하지 않았다.

## 초록

이 연구는 WIGTN 플러그인의 핵심인 Product Spec(PRD), PRD review,
Screen Spec, Implement/Verified Delivery, Auto Commit/Release Readiness가
강한 기본 모델에서도 필요한지 평가한다. 모델의 자기평가를 정답으로 쓰지
않고 PRD 계약 validator, hidden test, test hash, Git ref, 변경 경로,
익명 diff를 조합했다. 분석 가능한 Codex 모델 호출은 기존 499회와 이번
확장 202회를 합한 **701회**다.

결론은 명확하다.

- **범용 코딩 하네스는 기본 경로에서 제거해야 한다.** 네 개 구현
  fixture에서 GPT‑5.6 순정·일반 플러그인·verified가 모두 hidden test
  12/12였고, verified는 순정 대비 token 중앙값이 22.2% 늘었다.
- **조직 고유 계약과 권한 경계는 남겨야 한다.** GPT‑5.6 순정 PRD 생성
  계약은 44.6%였고, 모호한 “작업 완료” 요청에서는 3/3 무단 commit했다.
  플러그인 arm은 같은 요청에서 3/3 Git mutation을 막았다.
- **verified가 코드 품질을 높인다는 주장은 아직 성립하지 않는다.**
  deterministic 결과는 동률이고, 익명 모델 판정은 +1.3점뿐이며 과제 4개,
  판정자 2개, 인간 판정 0명이다.
- **모든 실제 저장소에 일반화된다는 근거도 없다.** 세 실제 저장소·6과제
  프로토콜은 사전 고정했지만, 로컬 저장소 코드를 외부 모델 서비스에
  전송하는 명시적 사용자 승인이 없어 호출을 실행하지 않았다.

따라서 Codex v0.2 후보는 긴 추론법·점수표·자동 fan-out을 버리고 PRD 계약,
acceptance evidence, screen handoff, Git 권한, opt-in 검증만 남긴다.
현재 공개 가능한 것은 “플러그인이 항상 코드를 더 잘 짠다”는 논문이
아니라, **어떤 기능은 남고 어떤 하네스는 감가상각되는지 보여 주는
재현 가능한 엔지니어링 보고서**다.

### 한 문장으로 답하면

이 플러그인은 모델 자체를 더 똑똑하거나 token-efficient하게 만드는
가속기가 아니다. **모호한 아이디어를 구현 가능한 계약으로 바꾸고,
요구사항 누락과 무단 release action을 줄이는 바이브 코딩용
가드레일**이다. 구현만 놓고 보면 순정 GPT‑5.6이 이미 강했고,
`verified-delivery`는 같은 정답에 더 많은 token과 시간을 썼다. 따라서
일상 코딩에는 개입하지 않고 PRD, acceptance evidence, screen handoff,
release authority처럼 결과물의 형태와 책임 경계가 필요한 순간에만
좁게 개입해야 한다.

## 1. 연구 질문과 비교 경계

1. GPT‑5.6 순정이 충분히 강하면 플러그인을 없애도 되는가?
2. 모델의 일반 추론과 팀 고유 산출물·권한 계약 중 무엇을 남겨야 하는가?
3. 효과가 GPT‑5.5에서도 유지되는가?
4. Auto Commit과 Implement 장문 하네스를 그대로 유지할 가치가 있는가?
5. verified가 deterministic correctness 또는 blind quality를 높이는가?

| 질문 | 유효한 비교 | 고정한 것 |
|---|---|---|
| 플러그인 효과 | 5.6 plugin − 5.6 bare | 모델, effort, fixture, runtime |
| 모델 세대 효과 | 5.6 plugin − 5.5 plugin | plugin, effort, fixture, runtime |
| 명시 검증 효과 | 5.6 verified − 5.6 ordinary | 모델, plugin, fixture |

`5.5 plugin − 5.6 bare`처럼 모델과 treatment가 동시에 바뀌는 차이는
플러그인 효과로 해석하지 않는다.

## 2. 표본과 신뢰 장치

### 2.1 분석 표본

| 층 | 모델 호출 | 주 grader |
|---|---:|---|
| 기존 PRD/Reviewer/Screen Spec | 499 | frozen 계약, validator, blind judge |
| Auto Commit | 90 | Git ref, committed paths, status, hash, local remote |
| Implement | 48 | visible/hidden tests, test hash, scope, Git HEAD |
| v4 Product Spec | 51 | 계약, clean specificity, validator, tokens |
| GPT‑5.5 scorer robustness | 5 | alias-robust defect scorer |
| 코드 blind judge | 8 | 익명 diff의 GPT‑5.5/5.6 독립 평가 |
| **확장 연구** | **202** | 위 grader 결합 |
| **전체 Codex 프로그램** | **701** | 분석 가능한 호출만 합산 |

Auto Commit sandbox pilot 4회는 분석에서 제외하고 원본과 이유를 보존했다.

### 2.2 설계

- arm별 별도 `CODEX_HOME`, fresh repository, ephemeral session
- remote plugins/apps 비활성화와 raw prompt 격리 확인
- 호출 전 protocol·fixture·scorer·treatment hash 고정
- 같은 fixture를 세 번 반복
- hidden test는 모델 종료 후 별도 프로세스가 실행
- 무관한 dirty draft, test hash, Git HEAD, changed-path 보존 검사
- 안전 위반은 평균과 분리한 zero-tolerance gate
- blind 후보에서 모델·arm·token·시간 제거
- scorer 오류는 원본·수정본·영향을 erratum으로 함께 보존

Agent 평가의 권장 방식처럼 결정론적 grader, 모델 판정, 인간 판정을 서로
대체하지 않고 층으로 분리했다. 재현 가능한 격리 실행과 outcome test를
우선하는 원칙은
[SWE-bench](https://github.com/swe-bench/SWE-bench)의 실행형 평가 방식과
일치한다.

세부 설계는 [PROTOCOL.md](PROTOCOL.md), 불확실성은
[STATISTICS.md](STATISTICS.md), 감사표는
[METHODOLOGY-AUDIT.md](METHODOLOGY-AUDIT.md)에 있다.

## 3. 핵심 결과

### 3.1 Product Spec / PRD

기존 GPT‑5.6 결과:

| Arm | 생성 계약 | 계약 리뷰 | clean | validator | 의미 /100 |
|---|---:|---:|---:|---:|---:|
| 순정 | 44.6% | 5.2% | 0.0% | 0.0% | 83.3 |
| 현행 | 62.1% | 9.0% | 0.0% | 0.0% | 90.8 |
| v2 | 80.0% | 96.7% | 100.0% | 46.7% | 88.3 |
| v3 | **99.5%** | **98.6%** | 80.0% | **100.0%** | **90.8** |

v3는 계약을 높였지만 clean specificity와 token gate에 실패했다. v4는
artifact 존재와 내용 결함을 분리하고 review finding을 최대 다섯 개로
제한했다.

| Arm | 생성 | 누락 recall | 계약 리뷰 | clean | 범용 | validator | token 중앙값 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 5.6 v4 | 115/117 | 18/18 | 150/150 | 7/7 | 15/15 | 9/9 | 13,784 |
| 5.5 v4 | 38/39 | 5/6 | 53/54 | 3/3 | 9/10 | 3/3 | 9,452 |

5.6은 모든 사전 gate를 통과했다. 5.5의 범용 9/10 실패는 실제 답변이
결함을 지적했지만 lexical scorer가 표현 alias를 놓친 false negative였다.
사후 고정한 robustness 5회는 25/25였다. frozen 결과는 소급 변경하지
않는다.

**판정:** 팀 고유 PRD 계약과 validator는 핵심 기능이다. 주관적 장문
review와 점수표는 아니다.

### 3.2 Auto Commit / Release Readiness

| Arm | 완전 성공 | 의도 action | zero-tolerance 위반 | token 중앙값 | 시간 중앙값 |
|---|---:|---:|---:|---:|---:|
| 5.6 순정 | 27/30 | 27/30 | **3** | 16,196 | 30초 |
| 5.6 플러그인 | 30/30 | 30/30 | **0** | 18,874 | 48초 |
| 5.5 플러그인 | 30/30 | 30/30 | **0** | 14,086 | 47초 |

차이는 모호한 완료 요청 한 task cluster에서 발생했다.

| 조건 | 5.6 순정 | 5.6 플러그인 | 5.5 플러그인 |
|---|---:|---:|---:|
| “작업 완료해줘”에서 Git mutation 없음 | 0/3 | 3/3 | 3/3 |

명시 commit/push 같은 Git 기계 동작은 세 arm이 같았다. 플러그인의 이득은
Git 사용법이 아니라 **구현·commit·push·PR을 서로 다른 권한으로 보는
경계**다. 다만 30/30의 95% Wilson 하한도 약 88.6%이므로, “절대 안전”을
뜻하지 않는다.

**판정:** 짧은 권한 매핑과 객관 hook은 핵심이다. 자동 commit 자체를
구현 완료에 연결해서는 안 된다.

### 3.3 Implement / Verified Delivery

| Arm | visible | hidden | 완전 성공 | token 중앙값 | 시간 중앙값 |
|---|---:|---:|---:|---:|---:|
| 5.6 순정 | 12/12 | 12/12 | 12/12 | 26,562 | 117초 |
| 5.6 플러그인·일반 | 12/12 | 12/12 | 12/12 | 29,278 | 138초 |
| 5.6 플러그인·verified | 12/12 | 12/12 | 12/12 | 32,461 | 146초 |
| 5.5 플러그인·verified | 12/12 | 12/12 | 12/12 | 31,857 | 108초 |

48회 모두 test tamper, draft 손실, 의도치 않은 commit, scope violation이
0건이었다. 이 fixture bank에서 verified의 correctness 증분은 **0**이고,
5.6 순정 대비 token +22.2%, 시간 +24.8%다. 12/12의 Wilson 하한은 약
75.8%라서 네 과제의 완벽한 결과를 광범위 일반화할 수 없다.

**판정:** 장문 Implement 하네스는 기본값에서 제거한다. verified는
“코드를 더 잘 짜는 모드”가 아니라 requirement→code→executed check
증거를 남기는 명시적 옵션으로만 유지한다.

### 3.4 익명 코드 품질

| Arm | 품질 /100 | 완결성 | 정확성 | scope | 유지보수성 | 증거 |
|---|---:|---:|---:|---:|---:|---:|
| 5.6 순정 | 93.1 | 3.62 | 3.38 | 4.00 | 3.75 | 3.88 |
| 5.6 플러그인·일반 | 93.1 | 3.88 | 3.62 | 3.62 | 3.62 | 3.88 |
| 5.6 플러그인·verified | 94.4 | 3.62 | 3.38 | 4.00 | 4.00 | 3.88 |
| 5.5 플러그인·verified | 82.5 | 3.50 | 2.75 | 3.50 | 3.00 | 3.75 |

5.6 verified의 +1.3점은 과제별 후보 1개와 모델 판정자 2명에서 나온 작은
신호다. expense fixture에는 manager 판별 API가 없어 구현 가정도
통제되지 않았다. 인간 reviewer 제출은 아직 0명이다.

**판정:** “verified가 코드 품질을 높인다”의 신뢰도는 **낮음**이다.
보고서 본문이나 홍보 문구에서 효과로 표현하면 안 된다.

## 4. 기능별 판정

전체 세부표는
[FUNCTION-MATRIX.md](../plugin-function-audit-2026/FUNCTION-MATRIX.md)에
있다.

| 기능군 | 증거등급 | 결정 |
|---|---:|---|
| Product Spec + validator | A | 기본 핵심 유지 |
| Release authority + objective gate | A | 기본 핵심 유지 |
| Screen Spec 5종 계약 | B | 좁은 산출물 기능으로 유지 |
| Acceptance Verifier | B | read-only evidence matrix로 유지 |
| Verified Delivery | B− | explicit beta; 품질 향상 문구 금지 |
| WIGTN presentation / handdrawn | B | 브랜드·포맷 전용 유지, 표본 확대 필요 |
| Design direction/reference | B− | 프로젝트 근거 기반 explicit reference |
| PR review posting | C | 읽기 전용 기본, 외부 게시 명시 승인 |
| 범용 frontend/backend/mobile/AI persona | D | explicit experimental |
| architecture / parallel review / parallel digging / team build | D | explicit experimental; 기본 경로 금지 |
| formatter persona / 100점 reviewer / review-level prose | D·중복 | 제거 |
| 매 Edit/Stop reminder | D·노이즈 | 제거 |

## 5. Codex v0.2 후보에 실제 반영한 개혁

이번 결론은 **`.codex-plugin-staging/`의 Codex 후보에만** 반영했다.
Claude Code 플러그인의 agents, commands, skills, hooks, README와 manifest는
개편 대상이 아니다.

| Codex 영역 | v0.2 후보 | 의도 |
|---|---:|---|
| registered skills | 8개 | WIGTN 고유 계약·산출물·권한만 유지 |
| skill entrypoints | 235줄 | 트리거와 실행 계약을 짧게 유지 |
| implicit heavy workflow | 0개 | 일상 구현에 하네스가 자동 개입하지 않음 |
| explicit heavy workflow | `verified-delivery` 1개 | 사용자가 qualified name으로 요청할 때만 |
| trigger regression | 30 cases | 일반 코딩 오호출과 기능 누락 방지 |
| plugin/eval validation | manifest + skill + trigger 검사 | 정적 구조와 라우팅 회귀 방지 |

핵심 변경:

1. 일반 “구현해줘”는 기본 Codex가 직접 처리하고 플러그인이 가로채지 않는다.
2. `product-spec`은 PRD 생성·검토·deep dive를 한 계약으로 통합하고,
   conditional section과 validator를 사용한다.
3. `release-readiness`는 review, prepare, commit, push, PR 권한을 사용자의
   문장에 맞춰 분리한다. “완료해줘”는 Git 권한이 아니다.
4. `verified-delivery`는 explicit-only이며 risk invariant, focused test,
   final diff review, requirement evidence를 남긴다. 품질 향상 기능으로
   홍보하지 않는다.
5. `acceptance-verifier`는 요구사항별 code/test evidence matrix를 만드는
   read-only 기능이다.
6. `screen-spec`, `design-direction`, `handdrawn-diagram`,
   `wigtn-presentation`은 각각 화면 5종, 프로젝트 고유 디자인 방향,
   검증된 렌더, WIGTN 브랜드라는 좁은 산출물 계약만 담당한다.
7. formatter persona, 범용 framework persona, 자동 team fan-out은 Codex
   후보에 넣지 않았다. 필요하면 기본 모델이나 명시적 별도 작업으로 수행한다.

이 후보의 구조·트리거 회귀는 통과시킬 수 있지만, 개혁 전후의 행동 효과는
아직 같은 fixture에서 직접 측정하지 않았다. 따라서 이 절은 **구현 완료
목록**이지 성능 개선 결과가 아니다.

## 6. 실제 저장소 확장 시험 상태

게임(Next.js 16), 홈페이지(Next.js 15), 플러그인(Bash/Python)의 실제
snapshot에서 각 2과제, 5.6 bare/5.6 reformed/5.5 reformed 각 3반복인
**54회** 프로토콜을 호출
전에 고정했다.

- game timeline malformed/non-mutation
- game deterministic shortest path
- YouTube URL authority/shape validation
- usage API URL normalization
- shell commit-command detection
- plugin contract diagnostics JSON

visible/hidden test, frozen hash, dirty draft, Git HEAD, allowed path, token,
duration을 기록하며 source repositories는 수정하지 않는다. 설계와 scorer는
[actual-repos protocol](../plugin-function-audit-2026/PROTOCOL.md)에 있다.
플러그인 효과의 주 비교는 같은 모델인 5.6 reformed−bare이고, 5.5
reformed는 같은 개혁의 세대 간 robustness 확인으로만 해석한다.

그러나 실행은 하지 않았다. 실제 로컬 저장소 코드가 외부 모델 서비스로
전송된다는 점에 대한 명시적 승인이 필요하기 때문이다. 따라서 이 보고서는
**실제 저장소에서 verified가 더 낫다거나 모든 저장소에서 같다는 결과를
포함하지 않는다.**

## 7. 이 보고서는 공개할 가치가 있는가

### 냉정한 판정

| 공개 형태 | 판정 | 이유 |
|---|---|---|
| 내부 기술 의사결정 기록 | **공개 가능** | raw runs, frozen protocol, errata, negative result가 있음 |
| 엔지니어링 테크 리포트 | **조건부 공개 가능** | “701-call controlled evaluation”과 좁은 claim이면 가치 있음 |
| “플러그인이 코드 품질을 높인다” 성능 리포트 | **공개 불가** | deterministic 동률, +1.3 blind, 인간 0명 |
| 모든 실제 저장소 일반화 | **공개 불가** | 실제 저장소 모델 호출 미실행 |
| 학술적/동료평가 논문 수준 | **아님** | convenience fixture, task cluster가 작고 인간 판정 미완료 |

가치는 높은 점수를 보여 주는 데 있지 않다. 강한 모델에서 하네스의
일반 코딩 지시는 비용만 늘 수 있고, 조직 고유 계약과 권한 경계는 여전히
측정 가능한 실패를 막는다는 **기능별 분해 결과**, 실패 scorer를 숨기지
않은 errata, 그리고 그 결과를 Codex의 얇은 opt-in 구조로 옮긴
설계 결정이 보고서의 가치다.

권장 제목과 한 줄 결론도 그 범위에 맞춰야 한다.

> 강한 코딩 모델에서 범용 하네스는 줄이고, 조직 고유 계약과 권한 경계는
> 실행형 평가로 남긴다.

## 8. 남은 release gate

우선순위 순:

1. 실제 저장소 코드의 외부 모델 전송을 명시 승인받은 뒤 사전 고정한
   54회 actual-repository study 실행
2. 기존 4과제와 실제 6과제의 anonymized candidate를 제품·보안 인간
   reviewer 각 1명 이상이 독립 평가
3. 개혁 전/후 `verified-delivery`를 같은 모델·fixture로 직접 비교
4. manager identity처럼 fixture 계약이 불완전한 요구사항 수정 후 재실행
5. GitHub 인증, branch protection, PR template, failing CI 환경에서
   release-readiness E2E
6. explicit experimental agent별 3-arm ablation:
   direct model vs one specialist vs coordinator; correctness뿐 아니라 token,
   latency, conflict, scope를 함께 측정
7. 1–2주 read-only shadow telemetry에서 trigger false positive, override,
   authority violation, check failure, token을 버전별 기록

배포 판단:

- Product Spec / Release Readiness: candidate
- Screen Spec / Acceptance Verifier: narrow beta
- Verified Delivery: explicit beta, quality-boost claim 금지
- generic and parallel agents: experimental, default-off
- 전체 v0.2 behavioural release: actual-repository + human blind 완료 전 hold

## 9. 재현 자료

- [Frozen protocol](PROTOCOL.md)
- [Protocol errata](PROTOCOL-ERRATA.md)
- [Methodology audit](METHODOLOGY-AUDIT.md)
- [Statistical appendix](STATISTICS.md)
- [Auto Commit raw runs and scorer](autocommit/)
- [Implement hidden tests and raw runs](implement/)
- [Blind protocol and human packet](blind/)
- [v4 Product Spec runs](v4-prd/)
- [Function audit and actual-repository protocol](../plugin-function-audit-2026/)
- [기존 499회 Codex 보고서](../model-harness-v2/REPORT.md)
