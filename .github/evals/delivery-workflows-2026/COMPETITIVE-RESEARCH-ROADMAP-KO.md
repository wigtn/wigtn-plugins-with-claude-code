# WIGTN Codex 플러그인 경쟁력·연구 신뢰도 로드맵

> 2026-07-28 · 제품/연구 의사결정안  
> 기준 버전: WIGTN Plugins for Codex v0.2.0

## 결론부터

WIGTN이 Spec Kit, Superpowers, BMAD의 기능 수를 따라가려고 하면 늦고,
현재 장점도 잃는다.

세 프로젝트는 이미 각자의 해자가 있다.

- Spec Kit: 전체 spec-driven lifecycle과 확장 생태계
- Superpowers: 강제력 있는 개발 방법론과 cross-harness 배포
- BMAD: agent persona와 조직형 workflow의 폭

WIGTN이 이길 수 있는 축은 다르다.

> **요구사항 → 코드 → 실행 테스트 → 릴리스 권한을 하나의 기계 판독 가능한
> evidence contract로 연결하면서, 일반 코딩에는 개입하지 않는 Codex-native
> 플러그인**

현재 제품은 이 방향의 절반까지 왔다. `product-spec`,
`acceptance-verifier`, `verified-delivery`, `release-readiness`가 각각
필요한 내용을 갖고 있지만, 결과가 하나의 공통 artifact와 validator로
연결되지 않는다. 평가 자료도 제품 저장소에서 독립적으로 재실행할 수 없다.

따라서 다음 버전은 agent를 추가하는 버전이 아니라 **evidence layer와 공개
eval kit를 만드는 버전**이어야 한다.

## 현재 점수의 냉정한 분해

### 제품 경쟁력

| 축 | 현재 | 이유 |
|---|---:|---|
| Codex-native 설치·호출 | 7/10 | 공식 plugin·skill 구조와 marketplace를 사용한다 |
| 기능 폭 | 3/10 | 8개 skill이며 planning, task state, resume, connector가 없다 |
| 방법론 완결성 | 4/10 | PRD부터 release까지 개념적 흐름은 있으나 공통 상태가 없다 |
| 검증 가능성 | 6/10 | PRD validator와 실행 증거 규칙은 있으나 공개 runner가 약하다 |
| 안전·권한 | 6/10 | behavior 차이는 확인했지만 skill contract이고 강제 경계는 아니다 |
| 상호운용성 | 2/10 | Spec Kit/BMAD/GitHub issue artifact를 공식적으로 import하지 않는다 |
| 생태계·커뮤니티 | 2/10 | 외부 fixture, contributor, integration이 거의 없다 |
| non-interference | 7/10 | ordinary coding을 가로채지 않는 정책이 선명하다 |

### 연구 신뢰도

현재 **3/10**이 맞다.

강점:

- 같은 모델의 bare/plugin arm을 분리했다.
- hidden test, Git state, hash, dirty draft를 검사했다.
- 제외 실행과 scorer 오류를 errata로 보존했다.
- 성능 향상이 없었던 결과를 숨기지 않았다.

감점 요인:

- 701회가 701개의 독립 task가 아니다.
- 독립 task cluster가 작고 implementation suite가 포화됐다.
- 실제 저장소 confirmatory 54회가 미실행이다.
- 인간 blind reviewer가 0명이다.
- 전체 raw evidence가 제품 저장소의 영구 URL에 없다.
- plugin author와 eval designer가 같다.
- v0.2 개혁 전후 직접 비교가 없다.
- 경쟁 plugin과 같은 모델·과제로 비교하지 않았다.

## 경쟁 프로젝트를 따라잡는 올바른 방법

### Spec Kit: lifecycle을 복제하지 말고 연결한다

Spec Kit은 Spec→Plan→Tasks→Implement 전체 흐름과 integration,
extension, preset, workflow를 제공한다. WIGTN이 같은 구조를 새로 만들
이유가 없다.

대신 다음을 지원한다.

1. Spec Kit의 `spec.md`, `plan.md`, `tasks.md`에서 stable requirement ID를
   읽는다.
2. WIGTN `acceptance-verifier`가 해당 ID를 code/test evidence에 연결한다.
3. WIGTN `release-readiness`가 미충족 requirement와 Git 권한을 release
   gate로 표시한다.
4. WIGTN PRD가 있으면 동일 schema로 내보내 Spec Kit에서도 소비할 수 있게
   한다.

즉 Spec Kit과 “더 큰 lifecycle”로 경쟁하지 않고, **마지막 검증과 권한
레이어**로 붙는다.

### Superpowers: mandatory methodology가 아니라 risk-adaptive verification

Superpowers는 brainstorming, plan, TDD, debugging, subagent development,
review를 강하게 연결한다. 이 방식은 긴 작업에 장점이 있지만 ordinary
task에도 자동 개입할 수 있다.

WIGTN은 반대 위치를 명확히 한다.

- 기본: Codex direct
- evidence 요청: acceptance verification
- 고위험·명시 요청: verified delivery
- 외부 상태 변경: release authority

따라잡아야 할 것은 TDD 지시문 개수가 아니라 다음 세 가지다.

1. skill behavior test를 공개 CI에서 실제 모델 없이도 최대한 검증
2. plugin 사용 전후를 같은 task로 비교하는 eval culture
3. failure transcript를 새로운 regression fixture로 승격하는 운영

### BMAD: persona를 추가하지 말고 resumable artifact state를 만든다

BMAD의 강점은 많은 역할과 workflow가 장기 프로젝트 상태를 이어 준다는
점이다. WIGTN에 PM·Architect·Developer persona를 추가하면 prompt와
유지보수만 늘 가능성이 높다.

대신 하나의 작은 상태 파일을 도입한다.

```text
.wigtn/delivery-state.json
```

최소 필드:

```json
{
  "schema_version": "1.0",
  "source_artifacts": [],
  "requirements": [],
  "checks": [],
  "release_authority": {
    "commit": false,
    "push": false,
    "pull_request": false,
    "deploy": false
  },
  "open_gaps": []
}
```

이 파일은 agent의 기억이 아니라 artifact 상태다. 새 작업에서도 다시 읽을
수 있고, validator와 CI가 검사할 수 있으며, 사람도 diff로 검토할 수 있다.

## v0.3: 기능 추가보다 먼저 만들 것

### 1. Evidence Contract

하나의 공개 schema를 만든다.

- `schemas/wigtn-evidence.schema.json`
- `scripts/validate-evidence.py`
- Markdown human report와 JSON machine report를 함께 생성
- PRD requirement ID, code location, executed command, exit code, test name,
  Git authority를 같은 record로 연결
- `Unknown`과 `Not verifiable`을 정상 상태로 허용
- 실행하지 않은 테스트를 passing으로 기록할 수 없게 한다

이 schema가 WIGTN의 실질적인 기술 자산이 된다. skill prompt는 다른
프로젝트도 복제할 수 있지만, versioned evidence artifact와 validator,
fixture bank는 시간이 쌓일수록 복제하기 어려워진다.

### 2. Public Eval Kit

현재 제품 저장소의 `scripts/run-evals.sh`는 trigger fixture 30개를 정적으로
검사하는 수준이다. 이름과 문서를 바꿔 오해를 없앤다.

- `run-static-contracts.sh`: manifest, schema, trigger vocabulary
- `run-behavior-evals.sh`: 실제 Codex arm 실행
- `score-evals.py`: deterministic outcome scorer
- `evals/tasks/`: 공개 task definition
- `evals/manifests/`: model, CLI, plugin, fixture, scorer hash
- `evals/results/`: raw transcript 또는 공개 가능한 normalized trace
- `evals/errata/`: 제외·수정 이력

공개 runner는 최소 다음 arm을 fresh environment에서 만들 수 있어야 한다.

```text
bare
placebo-context
wigtn-v0.2
wigtn-candidate
```

`placebo-context`는 WIGTN과 비슷한 token 길이의 관련 없는 일반 지시를
추가한다. 이것이 있어야 “WIGTN 내용의 효과”와 “context가 길어진 효과”를
분리할 수 있다.

### 3. Interop Reader

새 lifecycle을 만들기 전에 다음 입력을 읽는다.

- WIGTN PRD
- GitHub issue와 acceptance criteria
- Spec Kit `spec.md`·`tasks.md`
- BMAD story·PRD artifact
- 사용자 제공 Markdown checklist

처음에는 쓰기보다 read-only import만 지원한다. 외부 format 변경에 강한
adapter와 fixture를 만든다.

### 4. Release Guard는 별도 실험으로

Codex는 plugin-bundled lifecycle hook을 지원하며, hook은 trust review를
통과해야 실행된다. 따라서 hook을 추가할 수는 있지만 바로 기본 탑재하면
안 된다.

후보 arm:

| Arm | 설명 |
|---|---|
| skill only | 현재 `release-readiness` |
| hook only | Git mutation preflight만 실행 |
| skill + hook | 설명과 기계적 차단을 함께 사용 |

hook은 Bash 전체를 통제하지 않고 commit, push, PR에 해당하는 mutation만
대상으로 해야 한다. wrapper, quoting, alias, `git -C`, `gh pr create`,
subshell을 포함한 adversarial fixture에서 우회율과 오탐을 측정한다.

release gate:

- unauthorized mutation 0건
- 명시적 commit/push/PR 성공률이 사전 고정한 non-inferiority margin 안
- ordinary command 오탐이 실제 prompt 분포에서 정한 product tolerance 안
- hook latency가 pilot에서 정한 interaction budget 안

non-inferiority margin, false-positive tolerance, latency budget은 결과를 본
뒤 고르지 않는다. 먼저 pilot과 실제 사용자 tolerance로 정하고 confirmatory
호출 전에 고정한다. gate를 못 넘으면 skill-only를 유지한다.

### 5. 새 agent는 추가하지 않는다

다음 조건을 모두 만족할 때만 새 skill 또는 agent를 추가한다.

1. 실제 사용자 실패 사례가 최소 5개 있다.
2. 기존 Codex direct 또는 기존 skill이 반복 실패한다.
3. deterministic 또는 human-calibrated grader가 있다.
4. bare 대비 효과를 같은 모델에서 확인했다.
5. ordinary task false trigger가 허용 기준 안이다.

이 조건 전에는 feature request를 fixture로만 추가한다.

## 학술·벤치마크 점수를 3/10에서 올리는 방법

제품 기능을 많이 만드는 것은 연구 점수를 올리지 않는다. 독립 task,
사전등록, 인간 검증, 공개 재현성, 외부 복제가 올린다.

### 1단계: 3 → 4점

비교적 적은 비용으로 가능하다.

- 전체 protocol, task, runner, scorer, raw result, errata 공개
- 701 `calls`와 독립 `tasks`를 모든 표에서 분리
- v0.2 이전/이후 treatment hash 공개
- 세 인간 reviewer가 blind packet을 독립 평가
- reviewer agreement와 adjudication 전 원점수 공개
- primary endpoint와 exploratory endpoint 분리

인간 평가는 최소 세 명이 같은 익명 candidate를 독립 평가한다.

- 제품/요구사항 reviewer
- 코드/유지보수 reviewer
- 보안/릴리스 reviewer

ordinal rubric은 Krippendorff’s alpha 같은 agreement 지표를 보고하고,
합의 회의는 초기 점수가 잠긴 뒤에만 한다.

### 2단계: 4 → 5점

독립 task 수와 현실성을 높인다.

- 공개 저장소 6개 이상
- 독립 implementation task 24개 이상
- PRD·review task 15개 이상
- authority state task 15개 이상
- trigger positive/negative prompt 각 50개 이상
- task마다 gold/reference 또는 solvability check
- 모델이 보지 못하는 hidden outcome grader

Anthropic은 초기 agent eval에 실제 실패에서 뽑은 20–50개 task를 권장하고,
capability suite와 regression suite를 분리한다. SWE-bench Verified는
문제 명확성, test correctness, solvability를 인간이 검토한 500개
instance와 일관된 harness를 사용한다.

WIGTN도 두 suite를 분리한다.

| Suite | 목표 | 시작 pass rate |
|---|---|---:|
| capability | arm 차이를 측정 | bare 20–70% |
| regression | 이미 되는 행동 보호 | candidate 95–100% |

현재 implementation 12/12 suite는 capability benchmark가 아니라 regression
suite로 이동해야 한다.

### 3단계: 5 → 6점

이 단계부터 “우리 팀 내부 평가”를 넘어선다.

- plugin author가 아닌 사람이 runner를 재실행
- task author와 treatment author 분리
- Spec Kit 또는 Superpowers와 head-to-head secondary study
- 적어도 두 모델 세대에서 방향 재현
- infrastructure, timeout, concurrency, 날짜와 장애를 공개
- production shadow telemetry 또는 익명 실제 사용자 prompt 분포로
  fixture 대표성 점검
- workshop, artifact track 또는 독립 기술 리뷰 제출

현실적으로 다음 연구 한 번으로 노릴 수 있는 상한은 **5–5.5/10**이다.
외부 재현과 실제 사용자 분포 없이 6점 이상을 주장하면 다시 과장이다.

## 다음 confirmatory study

### 연구 질문

1. WIGTN candidate가 같은 모델의 bare보다 product contract 누락을 줄이는가?
2. evidence contract가 human reviewer의 검증 시간과 누락을 줄이는가?
3. release guard가 정상 action을 방해하지 않으면서 unauthorized mutation을
   줄이는가?
4. ordinary coding에서 plugin의 false trigger와 비용이 허용 범위 안인가?
5. 효과가 GPT‑5.5와 GPT‑5.6 Sol에서 방향상 유지되는가?

### Primary arm

| Arm | 목적 |
|---|---|
| A. bare | 기본 모델 기준 |
| B. placebo-context | context 길이 자체의 영향 |
| C. v0.2 | 현행 제품 |
| D. candidate | evidence contract 개혁 |

경쟁 plugin은 primary causal arm에 섞지 않는다. 권장 사용법과 workflow가
달라 treatment 정의가 흐려지기 때문이다. 별도 secondary study에서 같은
모델·task와 각 제품의 권장 설정을 고정한다.

### Primary endpoint

하나의 종합점수를 만들지 않는다.

| 기능군 | Primary endpoint | Safety endpoint |
|---|---|---|
| Product Spec | 필수 contract 충족과 material omission recall | fabricated requirement |
| Acceptance | requirement별 verified evidence precision/recall | unexecuted test를 pass로 표기 |
| Implement | hidden outcome pass@1과 pass^3 | test tamper, scope, draft loss |
| Release | intended action success | unauthorized mutation |
| Trigger | required skill recall | ordinary-task false activation |

token, wall time, tool call, human preference는 secondary다. 결과는 평균
종합점수보다 quality–cost Pareto frontier로 제시한다.

### 표본과 통계

- 분석 단위는 call이 아니라 task cluster다.
- 동일 task를 모든 arm에 paired 배정한다.
- 순서와 candidate label을 무작위화한다.
- 반복 횟수보다 독립 task를 먼저 늘린다.
- cluster bootstrap confidence interval을 기본으로 사용한다.
- binary paired endpoint에는 사전 고정한 paired test를 추가한다.
- 여러 secondary 비교는 Holm correction을 적용한다.
- task random effect를 둔 hierarchical model은 보조 분석으로 사용한다.
- 최종 task 수는 “호출 500회”처럼 먼저 정하지 않고, 검출하려는 최소
  효과에 대한 power simulation 뒤 고정한다.

### 권장 최소 규모

첫 공개 confirmatory release의 현실적인 안:

```text
30 independent core tasks
× 4 primary arms
× 3 trials
= 360 model runs
```

추가:

- live trigger 100 prompts는 저비용 별도 suite
- 경쟁 plugin 비교는 대표 task 12개로 제한
- GPT‑5.5 robustness는 전체가 아니라 사전 선택한 10개 task
- human blind는 arm별 모든 trial이 아니라 task별 사전 고정 candidate

호출 수는 기존 701보다 작아도 된다. 독립 task, 실제성, blind human,
공개 재현성이 더 중요하다.

## 경쟁 plugin head-to-head 설계

### 하지 말아야 할 비교

- WIGTN의 PRD validator 점수로 Superpowers 구현을 평가
- Spec Kit 전체 workflow와 WIGTN 한 skill의 token만 비교
- BMAD quick flow와 full lifecycle을 한 표에 혼합
- 각 framework의 권장 사용법을 무시한 동일 prompt 던지기
- 서로 다른 모델을 사용하고 framework 효과라고 부르기

### 가능한 비교

두 개의 track으로 분리한다.

#### Native-use track

각 framework의 권장 workflow와 기본 설정을 사용한다.

- 성공 결과
- 총 token·시간
- 사용자 개입 횟수
- 생성 artifact 수
- 외부 mutation

이는 “제품을 실제로 쓰면 무엇을 얻는가”를 측정한다.

#### Matched-budget track

같은 모델, task, 최대 token, timeout, tool과 repository snapshot을 고정한다.

- contract coverage
- hidden test
- human pairwise preference
- non-interference

이는 “동일 예산에서 어떤 설계가 효율적인가”를 측정한다.

첫 상대는 **Superpowers**가 적절하다. Codex plugin으로 직접 설치할 수 있고
ordinary coding에 자동 개입하는 철학이 WIGTN과 가장 선명하게 대비된다.
Spec Kit은 다음 연구에서 artifact interoperability 대상으로 비교하는 편이
좋다. BMAD는 workflow 범위가 너무 넓어 첫 matched study의 treatment가
불명확하다.

## 90일 우선순위

### P0 — 공개 신뢰 기반

1. raw evidence bundle을 Codex 제품 저장소 또는 별도 공개 eval 저장소로 이전
2. `run-evals.sh`를 static contract와 behavior eval로 분리
3. evidence JSON schema와 validator 구현
4. 701 calls / unique tasks / excluded runs manifest 생성
5. 인간 blind packet 세 명 배포

완료 기준: 외부 사용자가 README만 보고 최소 한 arm을 재실행할 수 있다.

### P1 — 제품 차별화

1. PRD→acceptance→release 공통 requirement ID
2. Markdown + JSON evidence report
3. Spec Kit/GitHub issue read-only importer
4. capability/regression suite 분리
5. actual public repository task bank 구축

완료 기준: 새 세션에서도 artifact만으로 요구사항 상태와 release gap을
복원할 수 있다.

### P2 — 검증된 확장

1. release guard 3-arm 실험
2. v0.2 vs candidate confirmatory 360-run study
3. 세 인간 reviewer agreement
4. Superpowers secondary head-to-head
5. 외부 재실행 요청

완료 기준: primary endpoint, confidence interval, raw evidence가 공개되고
사전 gate에 따라 기능을 keep/revert한다.

## 기능별 결정

| 제안 | 결정 | 이유 |
|---|---|---|
| agent 10개 추가 | 하지 않음 | BMAD의 약한 복제품이 된다 |
| 전체 SDLC 강제 | 하지 않음 | Spec Kit과 중복되고 non-interference를 잃는다 |
| mandatory TDD | 하지 않음 | 포화 task의 overhead 위험이 있다 |
| evidence schema | 최우선 | 네 핵심 skill을 하나의 제품으로 묶는다 |
| public eval kit | 최우선 | 연구 신뢰와 contributor 진입점을 함께 만든다 |
| Spec Kit importer | 진행 | 경쟁보다 상호운용이 유리하다 |
| Git authority hook | 실험 후 결정 | 강제력은 생기지만 오탐·trust 비용이 있다 |
| MCP server | 보류 | 현재는 live data/auth/action 요구가 없다 |
| GitHub/Jira connector | 실제 수요 후 | MCP가 필요한 명확한 use case가 생길 때만 |
| cross-platform plugin | 보류 | Codex-native 집중을 흐리지 않는다 |

공식 Codex 구조에서도 skill은 workflow, MCP는 live data·authentication·
controlled action, hook은 lifecycle enforcement를 담당한다. 기능 수를
맞추려고 MCP나 hook을 넣는 대신 필요한 primitive만 선택해야 한다.

## 성공 시 예상 점수

| 상태 | 제품 경쟁력 | 연구 신뢰도 |
|---|---:|---:|
| 현재 v0.2 | 4–5/10 | 3/10 |
| evidence schema + public eval | 5–6/10 | 4/10 |
| real task + human blind + preregistered study | 6/10 | 5/10 |
| external reproduction + production distribution | 6–7/10 | 6/10 |

Spec Kit·Superpowers·BMAD의 전체 기능 폭을 이기지는 못한다. 대신
**Codex의 자율성을 보존하면서 제품 계약과 릴리스 증거를 닫는 가장 얇은
검증 레이어**라는 카테고리를 만들 수 있다.

그 카테고리를 주장하려면 다음 한 문장을 제품과 연구 양쪽에서 입증해야
한다.

> WIGTN은 ordinary coding의 성공률과 비용을 악화시키지 않으면서,
> 요구사항 누락·검증 불가능 상태·무단 release action을 측정 가능하게
> 줄인다.

## 근거

- [WIGTN 701회 평가 보고서](REPORT.md)
- [방법론 감사](METHODOLOGY-AUDIT.md)
- [경쟁·공개 가치 편집 검토](EDITORIAL-REVIEW-KO.md)
- [OpenAI Codex plugin packaging](https://developers.openai.com/plugins/build/plugins)
- [OpenAI Codex skills](https://developers.openai.com/plugins/concepts/skills)
- [OpenAI Codex hooks](https://learn.chatgpt.com/docs/hooks)
- [Anthropic: Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [SWE-bench Verified](https://www.swebench.com/verified.html)
- [GitHub Spec Kit](https://github.github.com/spec-kit/index.html)
- [Superpowers](https://github.com/obra/superpowers)
- [BMAD Method](https://github.com/bmad-code-org/BMAD-METHOD)
