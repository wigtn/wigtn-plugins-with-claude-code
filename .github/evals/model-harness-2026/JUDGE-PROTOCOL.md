# 익명 pairwise/ranking 평가 프로토콜

자동 구조 점수는 “형식은 갖췄지만 내용이 틀린 문서”와 “동등 표현”을 완전히 다루지 못한다. 이를 보완하기 위해 각 동일 픽스처·반복의 네 arm 출력을 익명화하고 순서를 결정적으로 섞어 두 모델이 독립 평가한다.

## Judge

- `J55`: `gpt-5.5`, effort `medium`, WIGTN 플러그인 없음
- `J56`: `gpt-5.6-sol`, effort `medium`, WIGTN 플러그인 없음

Judge 모델이 후보 생성 모델과 일부 겹치므로 완전한 독립 인간 평가가 아니다. arm 이름과 모델 이름은 숨기지만 문체로 추측할 가능성도 있다.

## 단위

- 1차 7개 픽스처 × 2회 = 14 bundle
- 보충 2개 픽스처 × 2회 = 4 bundle
- judge별 18회, 총 36회

## 기준

각 후보를 0~4점으로 독립 채점한다.

1. `task_fidelity`: 요청한 산출물과 범위를 지켰는가
2. `correctness`: 모순, 근거 없는 요구, 보안·상태 오류가 없는가
3. `specificity_traceability`: 구현·검증 가능한 구체성과 추적성이 있는가
4. `restraint`: 근거 없는 SLA·아키텍처·과도한 범위·finding을 만들지 않았는가
5. `usability`: 실제 제품·개발팀이 바로 사용할 수 있는가

긴 출력 자체, finding 개수, 특정 제목이나 형식 자체에는 가점을 주지 않는다. 다만 사용자가 요구한 다중 산출물이나 구현 계약에 필요한 구조는 task fidelity와 usability에 반영한다.

## 출력

Judge는 후보별 다섯 점수와 총점, 동점 허용 ranking, material error를 JSON으로 반환한다. 생성 arm과의 매핑은 `blind-map.json`에 보존하고 judge 종료 전에는 집계하지 않는다.

## 해석

- 주 지표: arm별 평균 총점(100점 환산), 단독 1위 비율
- 보조: judge 간 1위 일치율, 각 기준 평균
- 두 judge가 반대하거나 자동 점수와 충돌하면 확정 우열이 아니라 “불확실”로 표시하고 대표 원문을 공개한다.
