# WIGTN Codex Plugin v3 — Failure-driven Confirmation Protocol

> 등록 시점: v2 주·확장 결과 분석 후, v3 모델 호출 전  
> 지위: v2 실패영역을 수정한 최종 후보의 확인 실험

## v2에서 관찰한 변경 근거

1. 실제 trigger hard-negative에서 acceptance-criteria 개념 설명이 product-spec을 1회 오발동했다.
2. frozen validator는 한국어 heading alias를 못 읽었고, alias 보정 후에도 UI/mobile route identity 누락이 7/10이었다.
3. 익명 의미 평가는 v2 completeness/feasibility가 높았지만 concision이 current보다 낮았다.
4. review contract와 나머지 여섯 스킬의 교정 행동 점수는 유지할 가치가 확인됐다.

## v3 변경

- product-spec trigger를 실제 PRD/spec 산출물 생성·검토·deep dive로 한정
- 개념 설명과 산출물 없는 brainstorming을 명시적으로 제외
- applicability의 세 조건부 row와 page/route-or-screen-ID/roles 표를 고정
- route 미정이면 `TBD + owner + decision point`를 표에 기록
- validator에 한국어 alias와 strict route-column 검증 추가
- brief 비례 길이, 중복 FR/AC/위험/단계 및 추측성 정책 억제
- review contract와 다른 일곱 스킬의 행동 계약은 변경하지 않음

## C1. GPT-5.6 full confirmation

- arm: `M56-V3`, `medium`
- workload: v2 주 회귀와 동일한 11 fixtures
- repetitions: 5
- calls: 55
- 비교: 기존 `M56-CURRENT`, `M56-V2`, `M56-BARE`
- gate:
  - create frozen contract ≥80%
  - omission recall ≥80%
  - contract accuracy ≥90%
  - clean specificity ≥90%
  - alias-robust universal recall ≥95%
  - strict v3 validator ≥80%
  - median tokens ≤ current +25%

## C2. GPT-5.5 targeted confirmation

- arm: `M55-V3`, `medium`
- workload: create 3종 + universal review
- repetitions: 5
- calls: 20
- 이유: v3가 바꾼 create contract, global concision rule, trigger description의 교차모델 확인.
  5.5 contract-review는 변경되지 않은 v2 review contract의 35회 결과를 재사용한다.
- gate:
  - create ≥80%
  - strict validator ≥80%
  - alias-robust universal ≥95%

## C3. Trigger regression

- v3 설치, GPT-5.6 `low`
- product-spec 양성 5개
- v2 false-positive 1개와 인접 conceptual hard-negative 4개
- calls: 10
- gate: positive 5/5, negative 5/5

## C4. Semantic confirmation

- 각 create fixture에서 `M56-CURRENT`, `M56-V2`, `M56-V3`의 frozen
  deterministic 최고 점수 출력을 선택
- SHA 기반 A/B/C 익명화
- GPT-5.5와 GPT-5.6 judge, fixture당 한 bundle
- calls: 6
- gate:
  - v3 semantic score가 current 대비 −5점 이내
  - v3 concision이 v2보다 낮지 않음
  - 두 judge가 blocker를 모두 보고한 후보가 없음

## 해석

- C1–C4는 v2 결과를 본 뒤 만든 확인 실험이므로 v2 주 회귀와 섞어 사전등록
  발견처럼 주장하지 않는다.
- v3 scorer는 v2에서 확인된 두 lexical 버그(`측정 불가능`, `Hand-drawn`)를
  호출 전에 수정한다.
- 인간 전문가 서명은 여전히 별도 release requirement다.
