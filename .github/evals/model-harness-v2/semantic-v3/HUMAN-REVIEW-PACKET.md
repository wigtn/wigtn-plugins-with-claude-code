# V3 human expert review packet

모델 judge 합의는 전문가 판정을 대체하지 않는다. 제품 또는 보안 전문가
두 명이 아래 원문을 독립 검토한 뒤 불일치를 합의한다.

- [ ] source brief와 정면 충돌하는 정책 또는 범위가 없는가
- [ ] 권한·테넌트·민감정보·재시도·중복 처리의 치명적 누락이 없는가
- [ ] 주요 요구사항이 관찰 가능한 acceptance criteria로 연결되는가
- [ ] N/A 판정에 실제 brief 근거가 있는가
- [ ] 미결정 사항에 owner와 decision point가 있는가
- [ ] 단계별 delivery가 요구사항 ID와 연결되는가
- [ ] 중복·추측성 요구사항이 구현 위험을 만들지 않는가
- [ ] 구조 형식이 의미 품질을 가리지 않는가

각 문서에 `PASS`, `PASS WITH HIGH`, `FAIL BLOCKER`와 정확한 section/ID
근거를 기록한다.

## create-ui-internal

- [ ] M56-CURRENT — `runs-regression/M56-CURRENT/create-ui-internal.1.md`
- [ ] M56-V2 — `runs-regression/M56-V2/create-ui-internal.1.md`
- [ ] M56-V3 — `runs-v3/M56-V3/create-ui-internal.1.md`

## create-backend-webhook

- [ ] M56-CURRENT — `runs-regression/M56-CURRENT/create-backend-webhook.1.md`
- [ ] M56-V2 — `runs-regression/M56-V2/create-backend-webhook.1.md`
- [ ] M56-V3 — `runs-v3/M56-V3/create-backend-webhook.1.md`

## create-mobile-expense

- [ ] M56-CURRENT — `runs-regression/M56-CURRENT/create-mobile-expense.1.md`
- [ ] M56-V2 — `runs-regression/M56-V2/create-mobile-expense.5.md`
- [ ] M56-V3 — `runs-v3/M56-V3/create-mobile-expense.1.md`

## Sign-off

| Reviewer | Role | Decision | Date | Notes |
|---|---|---|---|---|
|  |  |  |  |  |
|  |  |  |  |  |
