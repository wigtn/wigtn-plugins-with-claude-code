# 모델이 좋아져도 하네스는 필요한가?

## GPT‑5.5/5.6 × WIGTN Codex 플러그인 확장 연구

> 2026-07-27 · Codex CLI `0.146.0-alpha.3.1`  
> 확장 연구 분석 가능 호출 **499회**, 1차 연구 126회 포함 전체 **625회**

## 초록

GPT‑5.5와 GPT‑5.6에서 WIGTN Codex 플러그인을 제거할지, 현행을 유지할지,
실패 근거로 축소·재설계할지를 비교했다. 같은 모델 안에서 순정, 현행, v2,
최종 확인 후보 v3를 반복 실행했고, 실제 스킬 선택, 일반 코딩, 실행 가능한
검증기, 저-effort 민감도, 익명 의미 품질을 별도 평가했다.

결론은 **하네스 전체 제거도, 현행 그대로 유지도 아니다.**

- 플러그인 전체 제거는 기각한다. GPT‑5.6의 PRD 생성 계약은 순정 44.6%,
  현행 62.1%, v2 80.0%, v3 **99.5%**였다.
- 현행 플러그인은 순정보다 낫지만 리뷰 계약을 안정적으로 강제하지 못했다.
  GPT‑5.6 계약 리뷰 정확도는 현행 9.0%, v2 96.7%, v3
  **98.6%**였다.
- v2는 효과 원리를 입증했지만 최종 배포 후보는 아니다. 엄격 validator
  통과율이 46.7%였고, 개념 설명 요청에서 1/20 오발동했으며, 익명 평가에서
  간결성이 현행보다 낮았다.
- v3는 v2의 실패만 수정했다. 실제 trigger 10/10, GPT‑5.5 생성 97.4%,
  엄격 validator 100%를 기록했고, GPT‑5.6 전체 확인과 블라인드 의미평가
  결과는 아래 release gate에 반영했다.
- 일반 Python 구현 30회에서는 순정·현행·v2 모두 테스트 10/10,
  테스트 변조 0, WIGTN 스킬 오발동 0이었다. 선택적 스킬 구조에서는
  “플러그인 설치”가 “매 요청마다 무거운 하네스 주입”을 뜻하지 않는다.
- low effort는 품질을 낮추지 않았지만 토큰도 줄이지 않았다. 생성은
  81.2% vs medium 79.5%, 계약 리뷰는 99.2%로 같았고, 토큰 중앙값은
  오히려 14,564 vs 12,180이었다. 기본 effort를 낮출 근거가 없다.

최종 권고는 **순정 모델을 기본 경로로 두고, 실제 산출물 요청에만 얇은
도메인 계약을 선택적으로 로드하며, 결과는 결정론적 validator로 닫는
구조**다. 일반 방법론·중복 설명·항상 켜진 체크리스트는 제거한다.
v3의 8개 `SKILL.md` 본문은 합계 197줄로 현행 206줄보다 짧고, 복잡성은
프롬프트가 아니라 독립 실행 가능한 validator로 옮겼다.

## 1. 연구 질문과 의사결정

1. 같은 현행 플러그인에서 GPT‑5.6은 GPT‑5.5보다 안정적으로 나은가?
2. 같은 GPT‑5.6에서 현행 플러그인은 순정 모델보다 값을 하는가?
3. 실패 기반으로 다시 설계한 플러그인은 모델 버전이 바뀌어도 효과가 있는가?
4. 계약 준수율 증가가 의미 품질, 비용, latency, 오발동을 희생하지 않는가?
5. 플러그인을 제거·유지·축소 중 어떤 구조가 배포에 적합한가?

비교의 인과 경계는 다음과 같다.

| 질문 | 유효한 비교 | 바꾸는 변수 |
|---|---|---|
| 현 하네스의 값 | `M56-CURRENT − M56-BARE` | 플러그인 |
| v2 개선 효과 | `M56-V2 − M56-CURRENT` | 플러그인 계약 |
| v3 확인 효과 | `M56-V3 − M56-CURRENT/V2` | 실패 수정 |
| 모델 버전 효과 | `M56-CURRENT − M55-CURRENT` | 모델 |
| 5.5 과적합 여부 | `M55-V2/V3 − M55-CURRENT` | 플러그인 계약 |

`M55-CURRENT`와 `M56-BARE`를 빼서 하네스 효과라고 부르지 않았다. 모델과
플러그인이 동시에 바뀌기 때문이다.

## 2. 시험 설계

### 2.1 실행 조건

- 모델: `gpt-5.5`, `gpt-5.6-sol`
- 기본 reasoning effort: `medium`; 민감도 시험만 `low`
- ephemeral session, read-only sandbox, approval `never`
- remote plugin과 apps 비활성화
- arm별 `CODEX_HOME`과 외부 작업 디렉터리 분리
- 순정 arm의 raw prompt input에서 WIGTN 스킬 부재 확인
- 플러그인 arm의 raw prompt input에서 정확한 후보 버전 존재 확인
- fixture·프로토콜·scorer·후보 파일 SHA-256을 호출 전에 manifest에 기록
- 주 회귀는 fixture당 5회, effort 민감도는 최초 3회끼리 비교

이는 OpenAI의 모델 migration/eval 지침처럼 같은 effort에서 대표 과제를
비교하고, 자동 grader를 비교 판정과 보완하며, 성공 기준을 호출 전에
고정하는 방식이다.

- [GPT‑5.5 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.5)
- [GPT‑5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6)
- [Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [Working with evals](https://developers.openai.com/api/docs/guides/evals)

### 2.2 호출 구성

| 단계 | 호출 | 목적 |
|---|---:|---|
| GPT‑5.6 순정/현행/v2 주 회귀 | 165 | 11 fixtures × 5회 × 3 arms |
| GPT‑5.5 현행/v2 교차검증 | 110 | 모델 과적합 확인 |
| v2 실제 trigger | 40 | 양성 20, hard-negative 20 |
| PRD 외 6개 스킬 행동 | 24 | 순정/v2 × 2회 |
| 실행 가능한 구현 | 30 | 순정/현행/v2 각 10회 |
| v2 익명 의미평가 | 6 | 5.5/5.6 dual judge |
| low-effort 민감도 | 33 | 11 fixtures × 3회 |
| v3 5.6 전체 + 5.5 표적 확인 | 75 | 55 + 20 |
| v3 실제 trigger | 10 | 양성 5, 인접 음성 5 |
| v3 익명 의미 확인 | 6 | 5.5/5.6 dual judge |
| **확장 합계** | **499** | 분석 가능 완료 호출 |
| 1차 연구 | 126 | 독립 보고서 |
| **연구 프로그램 합계** | **625** | 분석 가능 완료 호출 |

초기 과잉 병렬 실행 중 취소된 호출은 완료 표본과 호출 합계에서 제외했다.
완료된 모든 실행의 meta를 검사했고 비정상 exit는 0이었다.

### 2.3 과제와 지표

| 계열 | 과제 | 주 지표 |
|---|---|---|
| PRD 생성 | 내부 문서공유 UI, 결제 웹훅, 모바일 경비 | 13개 frozen 계약 |
| 계약 리뷰 | 조건부 계약 6종을 하나씩 제거, clean | omission recall, 42칸 정확도, specificity |
| 범용 리뷰 | 모순·인가·정성 NFR·검증 불가 AC | 결함 recall |
| 실제 trigger | 명확한 요청과 개념 설명·일반 요청 | recall, specificity |
| 일반 구현 | 실행 가능한 Python microtasks | 테스트, exit, 변조, misload |
| 다른 스킬 | acceptance·design·diagram·release·delivery·presentation | 과제별 행동 계약 |
| 의미 품질 | 익명 A/B/C PRD | 완전성·정확성·실현성·추적성·간결성 |

자동 지표는 문서가 “좋아 보이는가”가 아니라 적용성, stable ID, 권한,
상태, flow, Given/When/Then, delivery mapping이 실제로 존재하는지 본다.
구조 점수와 의미 점수는 분리했다.

## 3. 핵심 비교

### 3.1 GPT‑5.6

| Arm | 생성 계약 | 누락 recall | 계약 리뷰 | clean | 범용 리뷰 | 엄격 validator | 의미 /100 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 순정 | 44.6% | 6.7% | 5.2% | 0.0% | 100.0% | 0.0% | 83.3 |
| 현행 | 62.1% | 3.3% | 9.0% | 0.0% | 100.0% | 0.0% | 90.8 |
| v2 | 80.0% | 96.7% | 96.7% | 100.0% | 100.0% | 46.7% | 88.3 |
| **v3** | **99.5%** | **96.7%** | **98.6%** | **80.0%** | **100.0%** | **100.0%** | **90.8** |

범용 리뷰의 순정·현행·v2 값은 frozen lexical scorer의 `측정 불가능`
alias 누락을 보정한 결과다. frozen 원점수와 보정표를 모두 보존했다.
v2 validator도 frozen parser 0/15와 alias-robust 12/15, strict route
identity 7/15를 분리 보존했다.

### 3.2 GPT‑5.5

| Arm | 생성 계약 | 누락 recall | 계약 리뷰 | clean | 범용 리뷰 | 엄격 validator |
|---|---:|---:|---:|---:|---:|---:|
| 현행 | 63.1% | 16.7% | 33.8% | 0.0% | 88.0% | 0.0% |
| v2 | 93.3% | 76.7% | 77.1% | 80.0% | 96.0% | 46.7% |
| **v3** | **97.4%** | 76.7%¹ | 77.1%¹ | 80.0%¹ | **100.0%** | **100.0%** |

¹ v3가 review contract를 변경하지 않았으므로 v2의 35회 review 결과를
재사용했다. 변경된 생성·간결성·trigger 영역만 20회 다시 확인했다.

GPT‑5.5에서도 개선 효과가 유지돼 GPT‑5.6 한 버전에만 맞춘 프롬프트라고
보기 어렵다. 반대로 “새 모델이면 항상 더 좋다”도 지지되지 않는다. 현행
생성은 5.5 63.1%, 5.6 62.1%로 같았고, 현행 계약 리뷰는 5.5가 더 높았다.

### 3.3 v2의 인과 효과

| 비교 | 생성 Δ%p [95% cluster bootstrap] | 계약 리뷰 Δ%p [95% CI] |
|---|---:|---:|
| v2 − 현행 | **+17.9 [+13.8, +21.5]** | **+87.6 [+82.4, +92.9]** |
| v2 − 순정 | **+35.4 [+26.2, +43.1]** | **+91.4 [+80.5, +98.6]** |
| 현행 − 순정 | **+17.4 [+7.7, +29.2]** | +3.8 [−5.2, +11.9] |

v3의 descriptive paired effect는 현행 대비 생성 **+37.4%p
[+35.4, +38.5]**, 계약 리뷰 **+89.5%p [+84.8, +94.8]**였고, v2
대비 생성도 **+19.5%p [+13.8, +24.6]**였다. v3는 v2 결과를 본 뒤 만든
확인 후보이므로 v2와 같은 사전등록 발견으로 합치지 않는다.

## 4. v3 release gate

### 4.1 사전 고정 gate

| Gate | 기준 | 결과 |
|---|---:|---|
| GPT‑5.6 생성 계약 | ≥80% | **PASS** — 99.5% |
| 누락 recall | ≥80% | **PASS** — 96.7% |
| 계약 리뷰 정확도 | ≥90% | **PASS** — 98.6% |
| clean specificity | ≥90% | **FAIL** — 80.0% |
| 범용 결함 recall | ≥95% | **PASS** — 100.0% |
| 엄격 validator | ≥80% | **PASS** — 100.0% |
| token median | 현행 +25% 이하 | **FAIL** — 17,116 > 15,701 |
| 실제 trigger 양성/음성 | 5/5, 5/5 | **PASS** |
| GPT‑5.5 생성/validator/범용 | ≥80/80/95% | **PASS** |
| 의미 품질 | 현행 −5 이내 | **PASS** — v3 90.8, 현행 89.2 |
| 간결성 | v2 이상 | **PASS** — 3.33 vs 2.50 |
| dual-judge consensus blocker | 0 | **PASS** |

**자동 release gate 최종 판정: FAIL.**

이 판정은 인간 제품·보안 전문가 승인을 대체하지 않는다. 전문가 review
packet의 `PASS / PASS WITH HIGH / FAIL BLOCKER` 서명이 최종 배포 조건이다.

clean 실패는 parser 오판이 아니다. 3번째 반복이 실제 State Matrix 표를
확인하고도 일부 route·recovery가 불완전하다는 이유로 계약 상태를
`Missing`으로 바꿨다. 내용 결함은 finding으로 보고하되 artifact 존재
여부인 `Present/Missing`과 섞지 말아야 한다. 토큰 실패도 일부 리뷰가
중간 severity를 10건 이상 열거한 결과라, review budget이 필요하다.

### 4.2 v3가 고친 것

| v2 실패 | v3 변경 | 확인 |
|---|---|---|
| AC 개념 설명 오발동 | 실제 PRD/spec 산출물 생성·검토로 trigger 축소 | 실제 trigger 10/10 |
| route identity 7/15 실패 | page/screen ID + route/deep link/TBD+owner + roles 표 고정 | validator 100% |
| 한국어 heading parser 누락 | 적용 범위·인수·구현 계획 alias 추가 | valid/invalid fixture PASS |
| 과도한 문서 의식 | brief 비례 길이, 중복 FR/AC·추측 정책 금지 | 의미 간결성 3.33, v2 2.50 |

review contract와 나머지 일곱 스킬은 효과가 확인된 동작을 보존했다. 모든
것을 동시에 바꾸지 않아 실패 수정의 원인을 추적할 수 있게 했다.
정적 검증에서도 plugin manifest 1/1, skill schema 8/8, trigger contract
30/30, validator 정상/결함 fixture 2/2가 통과했다.

익명 의미 점수는 현행 89.2, v2 89.2, v3 90.8로 gate를 통과했다. 그러나
judge가 기록한 high finding 수는 현행 5, v2 3, v3 6이었고, 모바일 경비의
중복 차단 요구와 미결정 정책 충돌에는 두 judge가 합의했다. blocker는
아니지만, 다음 개정에서는 `Must/FR/AC`와 open decision의 상호모순을
마지막에 검사하고 인간이 이 high를 해소해야 한다.

## 5. 비용·지연·effort

| 조건 | token median | duration median | 해석 |
|---|---:|---:|---|
| GPT‑5.6 현행 | 12,561 | 137s | v3 gate 기준선 |
| GPT‑5.6 v2 | 12,327 | 131s | 현행보다 무겁지 않음 |
| GPT‑5.6 v3 | 17,116 | 153s | token gate 실패; 현행 대비 +36.3% |
| GPT‑5.6 v2 medium, matched 3회 | 12,180 | 123s | effort 기준 |
| GPT‑5.6 v2 low, matched 3회 | 14,564 | 117s | 더 빠르지만 더 싸지 않음 |

low는 이 표본에서 구조 품질이 떨어지지 않았지만 토큰이 19.6% 늘었다.
quality 차이에 대한 정식 non-inferiority 검정도 아니므로, trigger처럼
짧은 분류에는 low를 쓰되 PRD 생성·리뷰 기본값은 medium으로 유지한다.

## 6. 플러그인 전체를 없애면 안 되는 이유

1. 같은 GPT‑5.6에서 순정→현행만으로 생성 계약이 +17.4%p 상승했다.
2. 순정의 의미 품질 83.3은 나쁘지 않지만 현행 90.8보다 낮았다.
3. 화면정의 1차 연구에서 5종 산출물 계약은 순정 69.2%, 현행 84.6%였다.
4. acceptance-verifier는 순정 75%, v2 100%; WIGTN presentation은 순정
   50%, v2 100%였다.
5. 플러그인 설치 상태에서도 일반 구현은 순정과 동일하게 10/10 성공했고
   스킬 오발동은 0이었다.

따라서 제거하면 비용 절감이 아니라 검증된 도메인 계약을 포기하게 된다.
다만 현행의 generic review 프롬프트를 그대로 유지할 이유도 없다. 일반
모순·보안·실현성 검토는 모델이 이미 잘하고, WIGTN 고유 누락만 얇은 계약과
validator가 보완해야 한다.

## 7. 권장 하네스 구조

### 7.1 유지

- **좁은 trigger router:** 실제 산출물·행동 요청만 스킬을 선택한다.
- **30줄 안팎의 orchestration skill:** 결과와 성공 기준만 지시한다.
- **mode별 reference:** create, review, deep-dive를 한꺼번에 읽히지 않는다.
- **결정론적 validator:** applicability, route/screen ID, states, flow,
  GWT, delivery mapping을 문서 생성 뒤 검사한다.
- **안전 경계:** release-readiness와 verified-delivery는 명시 요청에서만
  동작하고, 외부 변경은 별도 권한을 따른다.
- **브랜드·조직 고유 지식:** presentation, screen-spec처럼 순정 모델이
  알 수 없는 WIGTN 계약을 유지한다.

### 7.2 제거

- 모든 요청에 주입되는 일반론과 중복 체크리스트
- 모델이 이미 포화인 generic code/product review 방법론
- 섹션 존재만 품질로 착각하게 만드는 장문 템플릿
- 서로 같은 내용을 반복하는 FR, AC, risk, delivery 설명
- 근거 없는 SLA·architecture·compliance·enterprise policy
- 설명 요청까지 artifact skill로 끌어오는 넓은 trigger

### 7.3 운영

1. v3 후보를 현재 배포본에 바로 덮어쓰지 말고 전문가 서명을 받는다.
2. PRD 요청 일부에 canary로 적용해 trigger, validator, 수정 요구율을
   기록한다.
3. validator 실패는 자동 보완 1회까지만 허용하고 무한 재작성하지 않는다.
4. 모델 버전·effort·skill load·token·latency·validator code를 로그에 남긴다.
5. 모델 또는 스킬 변경 시 frozen fixture 11개와 hard-negative trigger를
   release gate로 다시 실행한다.
6. 실제 팀 PRD에서 익명 human pairwise 평가를 추가한다. 현재 dual-model
   judge는 전문가를 대체하지 않는다.

## 8. 다른 스킬과 일반 구현

### 8.1 PRD 외 여섯 스킬

| Task | 순정 | v2/v3 계약 |
|---|---:|---:|
| acceptance-verifier | 75% | 100% |
| design-direction | 100% | 100% |
| handdrawn-diagram | 100% | 100% |
| release-readiness | 100% | 100% |
| verified-delivery | 100% | 100% |
| wigtn-presentation | 50% | 100% |
| **합계** | **86%** | **100%** |

v3는 이 여섯 스킬을 변경하지 않았으므로 v2의 실행 증거를 재사용한다.
점수가 같은 스킬도 조직 고유 포맷 또는 안전 경계를 제공하지만, 본문을
더 늘릴 성능 근거는 없다.

### 8.2 실행 가능한 구현

| Arm | 테스트 통과 | 정상 exit | 테스트 변조 | 스킬 misload | token median |
|---|---:|---:|---:|---:|---:|
| 순정 | 10/10 | 10/10 | 0/10 | 0/10 | 17,658 |
| 현행 | 10/10 | 10/10 | 0/10 | 0/10 | 18,449 |
| v2 | 10/10 | 10/10 | 0/10 | 0/10 | 20,488 |

이는 실제 테스트가 있는 synthetic Python microbenchmark다. production
repository의 장기 작업·대규모 refactor를 대표하지 않으므로 “코딩 성능이
완전히 같다”가 아니라 “짧은 일반 구현을 깨뜨린 증거가 없다”로 해석한다.

## 9. 위협과 한계

- 하루 동안 한 CLI/runtime에서 실행해 시간대·서비스 상태 효과가 남는다.
- 모델 출력 seed를 고정할 수 없어 fixture당 5회 반복으로 변동을 흡수했다.
- v3 비교는 이전 current/v2 출력을 재사용해 동시 실행 batch 효과가 남는다.
- 자동 계약 점수는 의미 품질이 아니다. dual-model 익명 judge도 인간
  전문가와 독립적인 gold가 아니다.
- semantic 평가는 각 arm의 deterministic 최고 출력(best-of-5)을 비교해
  평균 실행 품질이 아니라 도달 가능한 최선 품질을 본다.
- clean fixture는 계약 완전성만 통제한다. 모든 제품·보안 결함이 없는
  gold라고 주장하지 않는다.
- 구현 benchmark는 작고 synthetic하다.
- trigger 표본 40+10은 실제 팀 대화 분포를 완전히 대표하지 않는다.
- v3는 v2 실패를 보고 만들었으므로 확인 결과이며, 완전히 독립적인
  holdout 조직/도메인 검증은 남아 있다.
- frozen scorer의 lexical/parser 결함 두 건은 원점수를 삭제하지 않고
  post-hoc 보정 결과를 별도 파일로 공개했다.
- v3 의미평가의 첫 두 transport 시도는 DNS 실패로 판단을 생성하지 못해
  제외했고, network-enabled 재실행 6회만 분석했다. retry note를 보존했다.

## 10. 최종 결론

### Claude Opus 5 연구와의 수렴

별도 Opus 5 연구는 보편 코드·PRD 결함 검출에서 하네스 이득이 없고, PRD
생성 40%→100%, 화면정의 62%→100%, 프로젝트 관습 리뷰 0/3→3/3에서
하네스 가치가 있다고 보고했다. 런타임·fixture·scorer가 달라 수치를
합치지는 않았지만, 이번 GPT‑5.5/5.6 결과도 같은 방향으로 수렴한다.

> 모델이 이미 아는 보편적 추론 방법은 줄이고, 조직이 정한 산출물 계약과
> 기계적 검증은 남긴다.

서로 다른 모델 계열에서 같은 정성 결론이 나온 점은 외적 타당성에 도움이
되지만, 동일한 팀 데이터에서의 사람 평가를 대체하지 않는다.

**플러그인 전체 제거는 기각한다. 그러나 v3의 기본 배포도 보류한다.**

현행은 선택적 로딩 덕분에 일반 코딩을 깨뜨리지 않으므로 단기 기본값으로
유지한다. v3 product-spec은 생성·validator·의미 품질이 좋아 canary
후보지만, 다음 세 수정을 한 v4를 다시 확인하기 전에는 전면 승격하지 않는다.

1. 계약 감사에서 섹션이 있으면 `Present`로 두고, 내용 불완전은 별도
   finding으로 기록해 `Missing`과 혼동하지 않는다.
2. review 출력에 blocker/high 우선과 중복 억제 budget을 둬 token 중앙값을
   현행 +25% 이내로 낮춘다.
3. 최종 contradiction sweep에서 같은 제품 선택이 `Must/FR/AC`와
   open decision에 동시에 존재하지 못하게 한다.

v4는 clean control 5회와 token gate를 먼저 통과시키고, 실제 팀 PRD의 인간
pairwise review에서 high를 해소한 뒤 canary로 승격한다. 이 보류는 하네스의
가치가 없어서가 아니라, 효과가 큰 하네스를 과잉 적용하지 않기 위한 것이다.

모델이 좋아질수록 하네스가 사라지는 것이 아니라 역할이 바뀐다. 일반
추론 방법을 가르치는 장문 하네스의 가치는 줄고, 모델이 알 수 없는 조직
계약을 정확한 순간에 로드하고 기계적으로 검증하는 얇은 하네스의 가치는
남는다. WIGTN Codex 플러그인은 후자의 구조로 축소해야 한다.

테크 리포트에는 현재 작업을 다음처럼 설명하는 것이 정확하다.

> GPT‑5.5/5.6 환경에서 순정 모델, 현행 WIGTN Codex 플러그인, 실패 기반
> 개선판을 반복·블라인드·실행 평가로 비교하고, 모델 고도화에 따른
> 하네스의 잔존 가치와 최소 계약 구조를 검증했다.

## 재현 자료

- `STUDY-PROTOCOL.md` — v2 주 회귀
- `EXTENSION-PROTOCOL.md` — 교차모델·effort·trigger·구현·의미평가
- `V3-PROTOCOL.md` — 실패 기반 v3 확인 gate
- `runs-regression/` — GPT‑5.6 순정/현행/v2 원출력·점수·효과
- `runs-55/` — GPT‑5.5 현행/v2
- `runs-v3/` — GPT‑5.5/5.6 v3
- `semantic-gold/`, `semantic-v3/` — blind map, judge 원출력, human packet
- `trigger-gate/`, `v3-trigger/` — 실제 스킬 선택
- `implementation-benchmark/`, `skill-behavior/` — 실행 행동
- `candidate-v3-marketplace/` — 최종 확인 후보 플러그인
