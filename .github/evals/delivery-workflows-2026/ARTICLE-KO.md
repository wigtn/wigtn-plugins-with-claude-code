# 강한 코딩 모델에 더 많은 지시를 넣지 않기로 했다

## 701회 실행 평가로 다시 만든 Codex 전용 플러그인

> 2026-07-27 · WIGTN Engineering  
> 평가 모델: GPT‑5.5, GPT‑5.6 Sol (`gpt-5.6-sol`, reasoning effort
> `medium`)  
> 대상: [WIGTN Plugins for Codex v0.2.0](https://github.com/wigtn/wigtn-plugins-codex)

코딩 모델이 약할 때 하네스의 역할은 비교적 명확했다. 긴 체크리스트를
주고, 역할을 나누고, 계획과 검토 단계를 강제하면 모델이 놓치는 부분을
줄일 수 있었다.

그런데 기본 모델이 강해진 뒤에도 같은 처방이 유효할까?

우리는 처음에 Claude Code용 WIGTN 플러그인의 PRD, 구현, 리뷰, 커밋
워크플로를 Codex로 옮기려 했다. 역할 에이전트와 단계별 지시를 그대로
이식하는 편이 가장 쉬웠다. 하지만 초기 실험에서 이상한 결과가 나왔다.
일반 구현 과제는 순정 Codex도 이미 모두 통과했고, 검증 단계를 더한
하네스는 정답을 늘리지 못한 채 token과 시간만 늘렸다.

반대로 PRD와 릴리스 권한에서는 순정 모델이 반복해서 같은 종류의 실수를
했다. 필수 산출물 계약을 빠뜨렸고, “작업 완료해줘”라는 모호한 문장을
commit 권한으로 해석하기도 했다.

이 차이가 Codex 전용 플러그인의 출발점이 됐다.

> 모델의 일반 추론을 다시 가르치지 않는다.  
> 팀이 원하는 결과물의 계약, 실행 가능한 검증, 외부 상태를 바꾸는 권한만
> 필요한 순간에 추가한다.

이 글은 플러그인이 모델을 무조건 더 똑똑하게 만든다는 성공담이 아니다.
오히려 어떤 하네스가 이미 감가상각됐고, 무엇은 여전히 남겨야 하는지를
701회의 Codex 모델 호출로 분해한 엔지니어링 기록이다.

## 먼저, “강한 모델일수록 하네스가 방해된다”는 말은 절반만 맞다

우리가 확인한 것은 보편 법칙이 아니다.

일반적인 중소 규모 구현처럼 기본 모델의 성공률이 이미 포화된 과제에서는
범용 지시, 중복 리뷰, 고정된 역할 분담이 추가 이득 없이 비용을 늘릴 수
있다. 하지만 장시간 자율 실행, 조직 고유 산출물, 보안 정책, 릴리스 권한처럼
모델 밖의 상태와 계약이 중요한 과제에서는 하네스가 여전히 필요하다.

Anthropic의 장기 애플리케이션 개발 실험도 planner–generator–evaluator
구조가 multi-hour 작업에 도움을 줄 수 있음을 보여 준다. 동시에 그 글은
하네스의 각 구성요소가 “모델이 스스로 못할 것”이라는 가정을 담고 있으므로,
모델이 개선될 때마다 그 가정을 다시 검증해야 한다고 지적한다.
([Harness design for long-running application development](https://www.anthropic.com/engineering/harness-design-long-running-apps))

따라서 우리가 검증하려 한 명제는 다음과 같다.

> 더 강한 모델에는 더 많은 하네스가 아니라, 같은 모델에서 효과가 입증된
> 최소 하네스가 필요하다.

## 무엇을 어떻게 테스트했나

분석 가능한 Codex 모델 호출은 기존 연구 499회와 전달 워크플로 확장
202회를 합해 701회다. 701개의 서로 다른 과제를 뜻하지는 않는다. 여러
task cluster를 반복 실행한 trial 수이며, task 다양성보다 treatment 차이를
통제하는 데 초점을 맞췄다.

### 비교 원칙

플러그인 효과는 반드시 같은 모델끼리 비교했다.

| 연구 질문 | 유효한 비교 | 고정한 것 |
|---|---|---|
| 플러그인 자체의 효과 | 5.6 plugin − 5.6 bare | 모델, effort, fixture, runtime |
| 모델 세대의 차이 | 5.6 plugin − 5.5 plugin | plugin, effort, fixture, runtime |
| 명시 검증의 효과 | 5.6 verified − 5.6 ordinary | 모델, plugin, fixture |

`5.5 plugin`과 `5.6 bare`의 차이는 모델과 플러그인이 동시에 바뀌므로
플러그인 효과로 해석하지 않았다.

### 평가 단위

| 평가군 | 호출 수 | 주된 판정 기준 |
|---|---:|---|
| 기존 PRD·Reviewer·Screen Spec | 499 | 고정된 산출물 계약, validator, blind judge |
| Auto Commit / Release | 90 | Git ref, status, commit path, hash, local remote |
| Implement | 48 | visible·hidden test, test hash, scope, Git HEAD |
| Product Spec v4 | 51 | 계약, 누락 recall, clean specificity, validator |
| scorer robustness | 5 | 표현 차이에 강한 결함 판정 |
| 익명 코드 판정 | 8 | 모델·arm·비용 정보를 제거한 diff |
| **전체** | **701** | 위 판정의 결합 |

### 모델의 자기보고를 정답으로 쓰지 않았다

“테스트를 통과했습니다”라는 문장은 통과 증거가 아니다. 모델 실행이 끝난
뒤 별도 프로세스가 hidden test를 실행했다. Git 과제는 최종 ref, status,
commit에 포함된 경로, 원본 파일 hash와 remote ref를 검사했다. PRD는
필수 섹션과 요구사항 ID를 결정론적 validator로 확인했다.

실행 환경도 arm별로 분리했다.

- 별도 `CODEX_HOME`과 fresh repository
- remote plugin과 app 비활성화
- 호출 전 protocol·fixture·scorer·treatment hash 기록
- hidden test를 모델 작업 디렉터리 밖에 보관
- 기존 dirty draft, test file, Git HEAD와 허용 경로 보존 확인
- 안전 위반을 평균 점수로 희석하지 않고 별도 zero-tolerance 지표로 집계
- 익명 diff에서 모델, arm, token, 시간 제거
- scorer 오류와 제외 실행을 삭제하지 않고 errata로 보존

이 설계는 outcome, transcript, grader를 분리하고 code-based grader,
model-based grader, human review를 겹쳐 쓰라는 최근 agent eval 실무와
같은 방향이다.
([Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents))

## 결과 1: 일반 구현에서는 하네스가 정답을 늘리지 못했다

네 개 구현 fixture를 세 번씩 반복해 네 arm을 비교했다.

| Arm | visible | hidden | 완전 성공 | token 중앙값 | 시간 중앙값 |
|---|---:|---:|---:|---:|---:|
| 5.6 순정 | 12/12 | 12/12 | 12/12 | 26,562 | 117초 |
| 5.6 플러그인·일반 | 12/12 | 12/12 | 12/12 | 29,278 | 138초 |
| 5.6 플러그인·verified | 12/12 | 12/12 | 12/12 | 32,461 | 146초 |
| 5.5 플러그인·verified | 12/12 | 12/12 | 12/12 | 31,857 | 108초 |

모든 arm이 visible·hidden test를 통과했고 test tamper, 기존 draft 손실,
의도하지 않은 commit, scope violation도 없었다.

이 fixture bank에서 `verified`의 deterministic correctness 증분은 0이었다.
5.6 순정과 비교하면 token은 22.2%, 시간은 24.8% 늘었다. 익명 모델
판정에서 verified가 1.3점 높았지만 과제는 네 개, 판정 모델은 두 개,
인간 판정자는 0명이었다.

여기서 “verified가 코드 품질을 높인다”고 말하면 안 된다. 확인된 사실은
더 좁다.

1. 이 구현 과제에서는 순정 5.6이 이미 포화돼 있었다.
2. 장문 검증 하네스는 결정론적 성공을 늘리지 못했다.
3. 증거를 더 남기는 대가로 token과 시간이 늘었다.

그래서 일반적인 “구현해줘”는 플러그인이 가로채지 않도록 했다.
`verified-delivery`는 더 좋은 코드를 보장하는 모드가 아니라,
requirement→code→executed check의 추적 기록이 필요한 고위험 작업에서
사용자가 명시적으로 선택하는 beta가 됐다.

## 결과 2: PRD에서는 모델의 약점보다 조직의 계약이 중요했다

순정 GPT‑5.6은 의미상 그럴듯한 PRD를 작성했지만, 우리가 실제 구현
입력으로 요구한 구조를 안정적으로 지키지 못했다.

| Arm | 생성 계약 | 계약 리뷰 | clean | validator |
|---|---:|---:|---:|---:|
| 순정 5.6 | 44.6% | 5.2% | 0.0% | 0.0% |
| 초기 플러그인 | 62.1% | 9.0% | 0.0% | 0.0% |
| v2 | 80.0% | 96.7% | 100.0% | 46.7% |
| v3 | **99.5%** | **98.6%** | 80.0% | **100.0%** |

초기에는 긴 리뷰 지시와 점수표를 추가했다. 효과가 고르지 않았고 token도
늘었다. 이후 prompt를 더 길게 만드는 대신 생성·검토·deep dive 계약을
분리하고, 조건부 섹션과 안정적인 요구사항 ID를 정의하고, 결과를 확인하는
validator를 붙였다.

v4 확인 결과는 다음과 같다.

| Arm | 생성 | 누락 recall | 계약 리뷰 | clean | validator |
|---|---:|---:|---:|---:|---:|
| 5.6 v4 | 115/117 | 18/18 | 150/150 | 7/7 | 9/9 |
| 5.5 v4 | 38/39 | 5/6 | 53/54 | 3/3 | 3/3 |

이 결과를 “플러그인이 PRD를 2배 잘 쓴다”고 요약해서는 안 된다. validator가
측정한 것은 우리의 산출물 계약이다. 더 방어 가능한 해석은 다음과 같다.

> 기본 모델은 일반적인 문서 작성에는 강하지만, WIGTN이 요구하는
> 구현 준비 상태를 추측할 수 없다. 조직 고유 계약을 짧게 제공하고
> 실행 가능한 validator로 닫으면 누락을 안정적으로 줄일 수 있다.

## 결과 3: Auto Commit의 가치는 Git 지식이 아니라 권한 경계였다

명시적으로 “commit해줘”, “push해줘”라고 한 경우 세 arm 모두 기계적인
Git 작업을 잘 수행했다. 차이는 “작업 완료해줘”처럼 애매한 요청에서
발생했다.

| Arm | 완전 성공 | 의도 action | zero-tolerance 위반 |
|---|---:|---:|---:|
| 5.6 순정 | 27/30 | 27/30 | **3** |
| 5.6 플러그인 | 30/30 | 30/30 | **0** |
| 5.5 플러그인 | 30/30 | 30/30 | **0** |

모호한 완료 요청에서 순정 5.6은 3/3 commit했고, 플러그인 arm은 3/3
Git mutation을 만들지 않았다.

플러그인이 Git을 더 잘 알아서가 아니다. 구현, 검토, commit, push, PR,
배포를 서로 다른 권한으로 취급하는 짧은 계약을 제공했기 때문이다.

다만 30/30도 절대 안전을 뜻하지 않는다. 현재 Codex v0.2의
`release-readiness`는 skill-level 계약이며 강제 보안 경계는 아니다.
Codex가 제공하는 trusted lifecycle hook으로 Git mutation을 결정론적으로
차단하는 방식은 가능하지만, hook 자체의 오호출과 trust 비용을 먼저
평가해야 한다.
([Codex Hooks](https://learn.chatgpt.com/docs/hooks))

## 그래서 플러그인을 어떻게 다시 만들었나

초기 아이디어는 “모델 앞에 더 좋은 프로세스를 세운다”였다. v0.2의 구조는
“모델이 실제로 틀리는 경계만 좁게 보강한다”에 가깝다.

```text
일반 코딩
  └─> 기본 Codex가 직접 탐색·구현·테스트

산출물 요청
  └─> 좁은 skill router
       └─> 작업별 계약·reference
            └─> 기본 Codex
                 └─> validator 또는 실행 증거

외부 상태 변경
  └─> release-readiness
       └─> review / prepare / commit / push / PR 권한을 각각 확인
```

Codex의 공식 plugin 구조는 하나 이상의 skill, MCP server, connector,
asset, lifecycle hook을 하나의 설치 단위로 묶는다. skill은 이름과
description만 먼저 노출되고, 요청이 일치할 때 전체 지시와 reference를
불러오는 점진적 로딩 구조다.
([Package your plugin](https://developers.openai.com/plugins/build/plugins),
[Skills](https://developers.openai.com/plugins/concepts/skills))

우리는 이 구조를 이용해 Codex 전용 플러그인을 여덟 개의 좁은 skill로
재구성했다.

| Skill | 가능한 일 | 개입 정책 |
|---|---|---|
| `product-spec` | PRD 생성·검토·deep dive, 요구사항 ID, validator | 산출물 요청에 자동 |
| `screen-spec` | IA, user flow, 화면 명세, lo-fi wireframe, handoff | 화면정의 요청에 자동 |
| `acceptance-verifier` | 요구사항별 code·executed-test evidence matrix | read-only 검증 |
| `design-direction` | 기존 디자인 시스템을 먼저 읽고 UI 방향 도출 | 제한적 자동 |
| `verified-delivery` | 위험 invariant, focused test, diff review, 증거 closeout | **명시 호출 전용** |
| `release-readiness` | review·prepare·commit·push·PR 권한 분리 | 외부 변경 요청에 제한적 자동 |
| `handdrawn-diagram` | Mermaid 원본과 검증된 SVG·PNG | 산출물 요청에 자동 |
| `wigtn-presentation` | WIGTN 브랜드 발표자료 | 브랜드 요청에 제한적 자동 |

반대로 다음은 넣지 않았다.

- 범용 frontend/backend/mobile 역할 persona
- 모든 구현에 적용되는 장문 체크리스트
- 자동 architecture review와 다중 agent fan-out
- 주관적인 100점 품질 게이트
- 매 Edit·Stop마다 실행되는 reminder
- 자동 commit·push·PR·배포
- MVP에 필요하지 않은 MCP와 connector

기존 Claude Code 플러그인을 수정하거나 디렉터리째 복사하지도 않았다.
플러그인 형식, tool 이름, skill discovery, 권한과 설치 표면이 다르기
때문이다. 이번 개혁과 배포 대상은 Codex 플러그인뿐이다.

## 2026년 7월의 플러그인 흐름과 비교하면

최근 생태계는 하나의 거대한 prompt보다 installable package, 필요할 때
불러오는 skill, 외부 시스템을 위한 MCP, 결정론적 hook, 격리된 subagent를
조합하는 방향으로 빠르게 수렴하고 있다.

Codex의 public plugin은 ChatGPT와 Codex가 하나의 directory를 공유하며,
skills, connectors, MCP servers, hooks 등을 묶을 수 있다. 2026년 7월에는
Codex CLI에서 remote plugin이 기본 활성화되고 npm marketplace source와
remote/local version 표시가 추가됐다.
([Codex Plugins](https://learn.chatgpt.com/docs/plugins),
[Codex changelog](https://learn.chatgpt.com/docs/changelog#month-2026-07))

Claude Code plugin은 skills뿐 아니라 agents, hooks, MCP, LSP, background
monitors까지 묶을 수 있다. Copilot도 skills, hooks, custom agents, MCP를
동일한 customization surface로 제공한다.
([Claude Code Plugins](https://code.claude.com/docs/en/plugins),
[Copilot customization](https://docs.github.com/en/copilot/reference/customization-cheat-sheet))

이 환경에서 WIGTN의 실제 위치를 과장 없이 비교하면 다음과 같다.

| 대상 | 강한 점 | WIGTN이 앞서는 지점 | WIGTN이 뒤지는 지점 |
|---|---|---|---|
| GitHub Spec Kit | Spec→Plan→Tasks→Implement 전체 수명주기, 35개 integration, extensions·presets·workflows | 더 작은 Codex-native 설치, PRD 계약 validator와 release authority 실험 | 생태계, 범용성, workflow engine, 문서와 사용자 기반 |
| Superpowers | 자동 brainstorming, plan, TDD, subagent 개발; 다수 coding harness 지원; skill 행동 테스트 문화 | 일반 코딩 기본 경로에 개입하지 않는 더 얇은 정책 | 개발 방법론 완성도, cross-platform 지원, 커뮤니티 검증 |
| BMAD Method | 34+ workflow, 전문 agent, 분석부터 구현까지 scale-adaptive process | persona와 ceremony가 필요 없는 작은 팀·빠른 작업에 단순함 | 제품 수명주기 범위, customization, 다중 역할 협업 |
| Claude Code native plugin | agents·hooks·MCP·LSP·monitors까지 넓은 확장 표면 | Codex 동작과 설치 방식에 맞춘 독립 설계 | 기능 폭과 장기 orchestration |
| Codex/Copilot 기본 customization | 공식 hooks, skills, MCP, custom/subagents | WIGTN의 제품 산출물 계약과 평가 fixture | platform primitive 자체는 거의 재사용할 뿐 독점 기술이 아님 |

비교 대상:
[GitHub Spec Kit](https://github.github.com/spec-kit/index.html),
[Superpowers](https://github.com/obra/superpowers),
[BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD).

이 표는 기능과 설계의 비교이지 head-to-head 성능 benchmark가 아니다.
우리는 Spec Kit, Superpowers, BMAD를 같은 fixture에서 실행하지 않았다.
따라서 “WIGTN이 더 빠르다”거나 “더 품질이 높다”는 주장은 할 수 없다.

냉정하게 말하면 WIGTN v0.2는 완성된 agent platform이 아니다. 공식 분류로는
plugin이지만 구조적으로는 **평가 근거를 가진 얇은 Codex skill bundle**에
가깝다. 현재 차별점은 기능 수가 아니라 다음 세 가지다.

1. 같은 모델의 bare/plugin arm을 분리해 negative result까지 공개했다.
2. 일반 구현을 자동으로 가로채지 않는다.
3. PRD 산출물 계약과 release authority처럼 측정된 결손에만 집중한다.

이 차별점이 제품 우위로 이어지는지는 아직 사용자 사용 데이터로
검증되지 않았다.

## 우리가 아직 입증하지 못한 것

이 연구에는 분명한 한계가 있다.

- 701회는 701개의 독립 과제가 아니라 제한된 task cluster의 반복 trial이다.
- 701회 전체가 하나의 사전등록 실험은 아니다. 기존 499회 연구와 사전
  고정한 202회 확장 연구를 합친 프로그램 총량이다.
- Implement는 네 과제 모두 포화돼 capability 차이를 측정하기 어려웠다.
- 실제 대형 저장소 3개·6과제·54회 프로토콜은 고정했지만, 저장소 코드를
  외부 모델 서비스로 전송하는 명시적 승인이 없어 실행하지 않았다.
- 코드 blind judge는 모델 판정자 두 개뿐이고 인간 reviewer는 0명이다.
- PRD의 높은 점수는 WIGTN 계약 충족을 뜻하며 보편적인 제품 판단력을
  뜻하지 않는다.
- 플러그인 작성자와 평가 설계자가 같아 confirmation bias 위험이 있다.
- v0.2 개혁 전후의 직접 3-arm 비교와 실제 사용자 A/B test가 남아 있다.
- 현재 재현 자료는 로컬 연구 디렉터리에 있다. 외부 공개 전에는 raw run,
  fixture, scorer, manifest hash와 errata를 영구 URL로 함께 배포해야 한다.
- latency와 infrastructure configuration은 agent 평가 결과를 바꿀 수 있다.
  작은 점수 차이는 특히 신중하게 해석해야 한다.
  ([Quantifying infrastructure noise in agentic coding evals](https://www.anthropic.com/engineering/infrastructure-noise))

## 결론

WIGTN Codex 플러그인은 모델 위에 또 하나의 개발 조직을 올리는 시도가
아니다.

일반 코딩은 기본 Codex에 맡긴다. PRD, screen handoff, acceptance evidence,
release authority처럼 모델이 조직의 의도를 추측할 수 없거나 외부 상태를
잘못 바꿀 수 있는 지점에만 작은 계약을 추가한다. 주관적인 “잘했다” 대신
validator, hidden test, Git state와 실행 로그로 닫는다.

이번 평가에서 확인된 결론은 다음 정도다.

> 강한 모델에서는 범용 하네스의 가치가 자동으로 유지되지 않는다.
> 같은 모델의 bare/plugin 비교에서 이득이 없는 절차는 제거하고,
> 실제 실패를 줄이는 도메인 계약과 권한 경계만 남겨야 한다.

플러그인을 쓰면 모든 코드가 더 좋아진다는 결론은 나오지 않았다.
대신 바이브 코딩에서 자주 비어 있는 “무엇을 만들 것인가”, “요구사항이
실제로 반영됐는가”, “어디까지 실행할 권한이 있는가”를 더 명시적으로
관리할 수 있다는 근거는 얻었다.

우리에게는 그 정도가 더 정직하고, 더 유용한 제품 정의였다.

---

## 재현 자료

- [전체 701회 보고서](REPORT.md)
- [Frozen protocol](PROTOCOL.md)
- [Protocol errata](PROTOCOL-ERRATA.md)
- [Methodology audit](METHODOLOGY-AUDIT.md)
- [Statistical appendix](STATISTICS.md)
- [기능별 evidence matrix](../plugin-function-audit-2026/FUNCTION-MATRIX.md)
- [실제 저장소 확장 프로토콜](../plugin-function-audit-2026/PROTOCOL.md)
- [WIGTN Plugins for Codex v0.2.0](https://github.com/wigtn/wigtn-plugins-codex/releases/tag/v0.2.0)
