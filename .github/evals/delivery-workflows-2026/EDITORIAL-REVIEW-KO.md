# 공개 전 냉정한 편집 검토

> 검토 대상: [ARTICLE-KO.md](ARTICLE-KO.md)  
> 기준일: 2026-07-27

구체적인 제품·연구 개선 순서와 다음 confirmatory study 설계는
[COMPETITIVE-RESEARCH-ROADMAP-KO.md](COMPETITIVE-RESEARCH-ROADMAP-KO.md)에
분리했다.

## 최종 판정

**현재 원고는 기술 블로그·엔지니어링 케이스 스터디로는 공개할 가치가
있다. 연구 논문이나 “성능 우위 입증” 리포트로 내면 안 된다.**

단, 지금 파일만 외부에 올리면 재현 링크가 로컬 상대경로라서 핵심 장점이
사라진다. raw run, fixture, scorer, protocol, errata를 공개 저장소의
영구 URL로 먼저 배포하는 것이 공개의 선행 조건이다.

“플러그인을 붙였더니 GPT‑5.6이 더 좋은 코드를 만들었다”는 제목이면
바이브 코딩 홍보글에 가깝다. 실제 deterministic 결과가 동률이고,
blind 차이는 +1.3점에 불과하기 때문이다.

반대로 “강한 모델에서 범용 하네스를 줄이고, 측정된 도메인 계약과 권한
경계만 남긴 과정”으로 쓰면 읽을 이유가 있다. 높은 점수를 자랑하는 글보다
negative result를 제품 구조 변경으로 연결했다는 점이 드물고 유용하다.

## 점수

| 항목 | 점수 | 냉정한 이유 |
|---|---:|---|
| 문제 정의 | 8/10 | “강한 모델에 기존 하네스를 그대로 이식해도 되는가”는 현재성 있고 실무적이다 |
| 방법 투명성 | 8/10 | raw run, frozen hash, hidden test, errata, 제외 사유가 남아 있다 |
| 인과 비교 | 7/10 | 같은 모델 bare/plugin 비교는 좋지만 전체 701회가 하나의 사전등록 실험은 아니다 |
| task 다양성 | 4/10 | 701 trial에 비해 독립 task cluster가 작다 |
| 코드 품질 입증 | 2/10 | deterministic 동률, 모델 judge 2개, 인간 0명 |
| PRD 계약 입증 | 8/10 | 효과가 크고 validator가 있으나 WIGTN 자체 계약에 한정된다 |
| release 권한 입증 | 7/10 | 모호한 요청의 차이는 명확하지만 한 cluster이며 강제 hook은 아니다 |
| 외적 타당성 | 3/10 | 실제 저장소 54회가 미실행이다 |
| 재현 가능성 | 8/10 | protocol과 scorer가 보존됐지만 외부 재현 보고는 없다 |
| 생태계 차별성 | 5/10 | 얇은 evidence-first 설계는 선명하지만 기능 자체는 대체로 commodity다 |
| **기술 블로그 가치** | **7/10** | claim을 좁히면 충분히 읽을 만하다 |
| **학술·벤치마크 가치** | **3/10** | 표본과 독립 검증이 부족하다 |

## 이 글이 “똥글”이 되는 다섯 가지 방식

1. 제목을 “플러그인으로 GPT‑5.6 성능을 향상시켰다”로 잡는다.
2. 701회를 701개의 서로 다른 실전 과제로 보이게 쓴다.
3. PRD 구조 validator 점수를 보편적 PRD 품질 점수로 표현한다.
4. `verified`의 +1.3 blind 점을 품질 향상으로 홍보한다.
5. 실제 저장소 연구와 인간 blind가 끝난 것처럼 생략한다.

원고는 이 다섯 가지를 모두 명시적으로 피했다.

## 실제로 통하는 서사

가장 강한 서사는 모델 성능 자랑이 아니라 **가설 폐기와 제품 축소**다.

```text
Claude용 하네스를 Codex에 이식하려 함
  → 같은 모델 bare/plugin ablation
  → 일반 구현은 동률인데 비용 증가
  → PRD 계약과 Git 권한에서는 반복 실패 발견
  → 범용 agent·fan-out 제거
  → 8개 좁은 skill + validator + explicit verification으로 재설계
```

이 흐름에는 문제, 실험, 실패, 설계 결정이 모두 있다. 독자가 가져갈 수 있는
일반 원칙도 하나다.

> 새 모델이 나올 때 prompt를 더 잘 쓰는 것보다, 기존 prompt의 각 줄이
> 아직 load-bearing인지 같은 모델 ablation으로 다시 확인하라.

## 최신 경쟁 구도에서의 실제 위치

### 1. 플랫폼 primitive는 이미 평준화되고 있다

Codex, Claude Code, GitHub Copilot 모두 skills, hooks, MCP, custom/subagents,
installable plugin을 지원하는 방향으로 수렴했다. `SKILL.md` 몇 개를
패키징한 것 자체는 더 이상 기술적 차별점이 아니다.

WIGTN이 “우리는 plugin을 만들었다”만 말하면 약하다. 공식 Codex plugin도
skill 하나만으로 만들 수 있으므로 기술적으로는 맞지만, 독자는 이를
“얇은 skill pack”으로 볼 가능성이 높다.

### 2. Spec Kit보다 작고 덜 범용적이다

Spec Kit은 Spec→Plan→Tasks→Implement, integrations, extensions, presets,
workflows와 조직용 catalog까지 갖춘다. WIGTN은 생태계와 범용성에서
비교가 되지 않는다.

WIGTN의 방어 가능한 차이는 Codex에서 모든 phase를 강제하지 않고,
PRD 계약과 release authority만 선택적으로 연다는 점이다. 이는 우위라기보다
다른 제품 선택이다. head-to-head eval 없이는 “더 효율적”이라고 쓰면 안 된다.

### 3. Superpowers보다 덜 침습적이지만 방법론은 덜 완성됐다

Superpowers는 brainstorming, plan, TDD, debugging, code review,
subagent-driven development를 자동 연결하고 여러 harness를 지원한다.
skill 자체를 agent로 실험하는 문화도 강하다.

WIGTN은 일반 구현을 가로채지 않는다는 점이 명확하지만, end-to-end 개발
방법론과 community validation은 훨씬 약하다. “덜 한다”는 것이 장점이 되려면
non-interference와 낮은 비용을 실제 사용자 분포에서 계속 입증해야 한다.

### 4. BMAD보다 단순하지만 process-heavy 팀에는 기능이 부족하다

BMAD는 PRD, UX, architecture, story, sprint, review를 전문 agent와
34개 이상의 workflow로 연결한다. enterprise ceremony나 역할 기반 협업이
필요한 팀에는 WIGTN이 빈약해 보일 수 있다.

반대로 소규모 팀과 개인 개발자에게 BMAD의 persona와 단계가 과할 수 있다.
WIGTN의 시장은 “full agile operating system”보다 “Codex를 방해하지 않는
제품·릴리스 가드레일”에 가깝다.

### 5. 현재 가장 큰 기술적 약점은 강제 경계가 없다는 점이다

`release-readiness`는 90회 실험에서 좋은 행동 차이를 보였지만 v0.2는
Codex lifecycle hook을 번들하지 않는다. 즉 권한 경계가 prompt contract에
남아 있고 보안 경계는 아니다.

v0.3에서 고려할 수 있는 것은 broad hook이 아니라 아주 좁은
Git mutation preflight다.

- commit·push·PR마다 현재 사용자 요청에서 해당 authority가 존재하는지 확인
- 불명확하면 차단이 아니라 사용자 확인 요청
- 일반 Bash와 file edit에는 개입하지 않음
- trigger false positive와 우회 명령을 adversarial fixture로 측정
- hook trust UX와 latency를 별도 비용으로 기록

이 hook이 skill-only보다 실제로 낫다는 결과가 나온 뒤에만 기본 탑재해야
한다.

## 공개 전에 반드시 손볼 표현

권장:

- “701회 모델 호출을 포함한 controlled engineering evaluation”
- “일반 구현 fixture에서 추가 correctness를 관찰하지 못했다”
- “WIGTN PRD output contract 충족률”
- “모호한 완료 요청 cluster에서 Git mutation을 줄였다”
- “Codex-native thin harness”

금지:

- “701개 실전 과제로 입증”
- “코드 품질 1.3점 향상”
- “강한 모델일수록 하네스는 항상 해롭다”
- “PRD 품질 99.5%”
- “무단 commit을 완벽히 방지”
- “업계 최초”

## 리포트 수준을 한 단계 올리는 최소 추가 연구

우선순위는 호출 수를 더 늘리는 것이 아니라 독립성과 실제성을 늘리는 것이다.

1. raw evidence bundle을 공개 저장소와 영구 URL로 배포
2. 사전 고정한 실제 저장소 3개·6과제·54회 실행
3. 제품 reviewer와 보안 reviewer 각 1명 이상의 독립 blind 평가
4. 개혁 전 verified vs v0.2 verified vs bare의 같은-model 3-arm 비교
5. plugin author가 아닌 제3자의 protocol 재실행
6. 실제 사용자 prompt를 익명화한 trigger shadow test
7. GitHub auth, branch protection, failing CI, PR template가 있는 release E2E
8. Superpowers 또는 Spec Kit 하나를 선정한 head-to-head 비교

마지막 비교는 전체 제품을 한 점수로 줄이면 안 된다. 같은 문제에서 다음을
분리해 측정해야 한다.

- task completion과 hidden test
- 산출물 계약 충족
- 잘못된 trigger와 불필요한 질문
- token, wall time, tool calls
- 의도하지 않은 Git·외부 mutation
- 요구사항 추적성과 인간 reviewer 선호

## 배포·홍보 문구 판정

| 문구 | 판정 |
|---|---|
| “Codex를 더 똑똑하게 만듭니다” | 사용 금지 |
| “모든 코드의 품질을 높입니다” | 사용 금지 |
| “일반 코딩은 Codex에 맡기고 제품 계약과 릴리스 경계만 보강합니다” | 사용 가능 |
| “PRD 요구사항과 실행 증거를 연결합니다” | 사용 가능 |
| “검증된 delivery mode” | beta와 증거 범위를 함께 쓰면 가능 |
| “무단 commit을 방지합니다” | “평가 fixture에서 줄였습니다”로 제한 |

## 한 줄 냉정평

**지금 공개하면 ‘프론티어 모델을 이긴 플러그인’ 리포트로는 약하고,
‘새 모델 앞에서 자기 하네스를 실제로 줄인 팀의 평가 기록’으로는 꽤 좋다.**
