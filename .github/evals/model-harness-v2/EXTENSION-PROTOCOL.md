# WIGTN Codex Plugin v2 — Pre-registered Extensions

> 등록 시점: 5.6 주 회귀 진행 중, 아래 확장 실험 실행 전  
> 지위: 주 회귀의 release gate를 변경하지 않는 사전등록 2차 분석

## 연구 질문

1. v2 효과가 GPT-5.6에만 맞춘 과적합인가?
2. `medium`에서 얻은 이득이 `low`에서도 유지되는가?
3. 일반 코딩에서 하네스가 불필요하게 개입하거나 성공률을 낮추는가?
4. PRD 외 여섯 스킬도 순정 모델 대비 행동 차이를 만드는가?
5. 실제 자동 선택에서 양성 호출과 음성 억제가 함께 작동하는가?
6. 구조 점수가 아니라 의미 품질과 치명적 결함도 개선되는가?

## E1. GPT-5.5 교차검증

- arms: `M55-CURRENT`, `M55-V2`
- model/effort: `gpt-5.5`, `medium`
- workload: 주 회귀와 동일한 11 fixtures
- repetitions: 5
- calls: 110
- primary interpretation: v2−current within GPT-5.5
- 성공 기준:
  - v2 omission recall, contract accuracy, validator pass가 모두 current 이상
  - create와 universal은 current 대비 −5%p 이내
  - median tokens는 current 대비 +25% 이내

GPT-5.5와 GPT-5.6의 절대 차이는 모델 효과와 실행 시점 효과가 섞이므로 보조 해석만 한다.

## E2. Effort sensitivity

- arm: `M56-V2`
- effort: `low`
- workload: 동일 11 fixtures
- repetitions: 3
- calls: 33
- 비교: 주 회귀의 `M56-V2 medium` 각 fixture 최초 3회
- 성공 기준:
  - primary quality aggregate 감소 ≤5%p
  - median tokens 또는 duration 중 하나 ≥15% 절감

## E3. 일반 구현 비간섭

- arms: `M56-BARE`, `M56-CURRENT`, `M56-V2`
- 10개 독립 Python 수정 과제, arm당 1회
- calls: 30
- 평가지표:
  - 원본 테스트 해시가 유지된 유효 test pass
  - model exit
  - WIGTN skill 오발동
  - duration, tokens
- 성공 기준:
  - v2 유효 pass가 bare/current보다 1개를 초과해 낮지 않음
  - test tampering 0
  - WIGTN skill misload 0

## E4. 실제 trigger gate

- v2 설치 상태, GPT-5.6 `low`
- 양성 20개, hard-negative 20개
- calls: 40
- CLI skill-load marker로 실제 선택을 채점
- 성공 기준: positive recall ≥95%, negative specificity ≥95%, ambiguous load 0

## E5. 여섯 스킬 행동검증

- 대상: acceptance verifier, design direction, handdrawn diagram,
  release readiness, verified delivery, WIGTN presentation
- arms: `M56-BARE`, `M56-V2`
- task당 2회
- calls: 24
- 정적 산출물 계약, 파일 변경, Git HEAD 변경, 실행 테스트를 조합해 채점
- 성공 기준:
  - v2 aggregate ≥90%
  - v2가 bare보다 task별 1개 criterion을 초과해 낮지 않음
  - 권한 밖 commit/stage 또는 read-only task mutation 0

## E6. 의미 품질 및 gold review packet

- 주 회귀의 세 create fixture에서 arm별 최고 deterministic score 출력을 선택
- arm 표시는 SHA 기반 A/B/C 익명화
- GPT-5.5와 GPT-5.6 judge가 각각 completeness, correctness, feasibility,
  traceability, concision을 0–4로 판정
- 각 judge는 blocker/high 결함을 구조화해 기록
- 모델 judge 합의는 인간 전문가 판정을 대체하지 않으며,
  최종 release 전 사람이 확인할 packet을 별도 생성
- 성공 기준:
  - v2 평균 semantic score가 current보다 낮지 않음
  - 두 judge가 합의한 blocker 0
  - high 결함은 current보다 많지 않음

## 다중 비교와 해석

- 주 회귀 gate만 confirmatory이다.
- E1–E6는 이름 붙인 secondary 결과이며 p-value를 주장하지 않는다.
- 비율에는 분자/분모를 항상 함께 표시한다.
- 동일 fixture 반복은 독립된 제품 도메인 표본으로 과장하지 않는다.
- scorer 수정이 필요하면 원본 점수와 post-hoc 점수를 함께 남긴다.
- 실행 실패는 숨기지 않고 분모, 재실행 이유, 재실행 횟수를 기록한다.
