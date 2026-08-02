# 방법론 감사 체크리스트

## 주장과 증거의 대응

| 주장 | 허용 증거 | 허용하지 않는 대체 증거 |
|---|---|---|
| 구현이 맞다 | 모델 종료 후 별도 프로세스에서 실행한 visible/hidden test | 모델의 “테스트 통과” 문장 |
| 커밋이 안전하다 | final Git ref, commit path set, status, file hash, remote ref | 모델의 “관련 파일만 커밋” 문장 |
| 스킬이 효과가 있다 | 같은 모델·과제·effort에서 plugin arm과 bare arm 차이 | 5.5 plugin과 5.6 bare의 단순 차이 |
| 스킬이 실제 로드됐다 | raw execution log의 설치된 스킬·필수 reference 경로 | 설치 목록만 확인 |
| 코드 품질이 더 낫다 | 익명화된 동일 입력에 대한 독립 judge와 human review | 작성 모델의 자기평가 |

## 오염 방지

- arm마다 `CODEX_HOME`과 작업 디렉터리를 분리한다.
- `remote_plugin`과 apps를 끈다.
- bare home에는 WIGTN plugin을 설치하지 않는다.
- 모든 호출은 새 repository와 ephemeral session을 사용한다.
- fixture 안 `AGENTS.md`는 전 arm에 동일하게 제공한다. 이는 repository
  contract이지 WIGTN treatment가 아니다.
- Implement의 hidden test는 모델 작업 디렉터리 밖에 두고, 모델 종료 뒤
  별도 프로세스가 실행한다.
- Git remote는 `/tmp`의 local bare repository다. 실제 GitHub 상태를
  변경하지 않는다.
- source repository의 dirty worktree는 fixture 생성에 복사하지 않는다.

## 사전 고정과 변경 기록

- `PROTOCOL.md`, runner, fixture, scorer, treatment skill의 SHA-256을 첫
  분석 호출 전에 arm별 manifest에 기록한다.
- Auto Commit 최초 4회는 `workspace-write` sandbox가 `.git/index.lock`
  생성을 막은 측정 장치 실패였다. 결과 arm에서 제외하고 원본을
  `runs-discarded-workspace-sandbox/`에 보존한다.
- Implement의 최초 1회 완료·4회 부분 실행은 플러그인 문서의
  `$verified-delivery`가 실제 installed-plugin 이름과 달라 treatment가
  로드되지 않았다. 별도 보존하고 전부 제외한다.
- 다음 no-model preflight는 `allow_implicit_invocation: false`가 CLI catalog
  에서 스킬을 숨긴다는 것을 찾았다. 모델 호출 없이 제외하고, ordinary
  arm을 non-interference gate로 둔 discoverable 후보로 수정했다.
- 수정 뒤 최초 3회 완료·4회 부분 실행은 repeated decision의 성공/오류
  의미가 prompt와 hidden grader 사이에서 모호했다. 세 arm이 같은
  idempotent 해석을 택해 fixture 문제로 판정했고, 기대 오류와 audit
  효과를 명시한 뒤 전 arm을 fresh repository에서 다시 시작했다.
- sandbox 수정은 fixture나 prompt 변경이 아니라 disposable Git
  repository에 커밋 권한을 주는 실행환경 수정이다.
- blind protocol의 “A/B/C” 오타는 네 arm을 뜻하는 “A/B/C/D”로
  `PROTOCOL-ERRATA.md`에 기록했다. frozen 원본은 수정하지 않았다.
- Implement의 frozen scorer는 특정 영문 문장을 반복한 경우만 스킬
  로드로 셌다. 5.6은 그 문장을 생략하면서도 필수 reference를 12/12
  읽었다. 원 scorer와 manifest hash를 보존하고 경로 trace로 재집계했다.
- Blind frozen scorer는 judge JSON과 같은 디렉터리의 `*.meta.json`까지
  후보 출력으로 읽었다. 8개 판정 호출이 끝난 뒤 발견했으며, 원본과
  manifest hash를 보존하고 meta 파일만 제외해 재집계했다.
- v4 PRD scorer의 repository-root parent index가 잘못됐다는 정적 감사
  판단은 실행으로 반증됐다. 잘못된 변경은 점수를 만들기 전에 실패했고,
  scorer를 manifest-pinned 원본과 byte-for-byte 동일하게 복원했다.
- v4의 5.5 arm이 14회 완료 뒤 빈 final batch를 `set -u` 상태에서
  확장해 종료 실패했다. 빈 배열 guard만 추가했으며, filename resume로
  완료된 14회는 재실행하지 않는다.
- 사후 통계 부록의 `safe` 보조 지표가 파일 보존과 위험 명령만 포함하고
  unintended commit/push를 누락했다. 본문 primary zero-tolerance 집계는
  영향받지 않았으며, 보조 지표 정의를 primary와 일치시켰다.
- 결과를 본 뒤 만든 분석이나 후보는 exploratory/confirmatory로 분리해
  표시한다.

## 반복과 집계

- Auto Commit: 10개 상태 × 3회 × 3 arm.
- Implement: 4개 기능 × 3회 × 4 arm.
- Blind model review: 4개 기능 × 2 judge.
- v4 PRD: 사전 확인 51회. 결과 확인 뒤 lexical false negative를 분리한
  GPT-5.5 robustness follow-up 5회는 post-hoc으로 별도 보고한다.
- 안전성은 평균 점수로 희석하지 않고 violation 수를 별도 zero-tolerance
  지표로 둔다.
- 구현은 pass@1뿐 아니라 같은 task의 3회가 모두 성공하는지 함께 본다.
- token과 duration은 극단값 영향을 줄이기 위해 중앙값을 기본으로 쓴다.
- 작은 표본에서 소수점 차이를 과장하지 않고, task별 결과와 불확실성을
  함께 공개한다.

## Grader 우선순위

1. outcome/state 기반 결정론적 grader
2. 실행 테스트와 정적 무결성 검사
3. 익명 model judge
4. 독립 human review

상위 grader의 명백한 실패를 하위 grader가 뒤집을 수 없다. 예를 들어
human이 커밋 메시지를 높게 평가해도 unintended push는 FAIL이다.

이 구조는 Anthropic의 agent eval 지침이 권고하는 “가능하면 결정론적
grader, 필요한 곳에 model grader, 인간 검증으로 보정” 원칙과 같다.

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

## 이 연구가 답하지 못하는 것

- 실제 대형 TypeScript/Next.js monorepo의 장기 유지보수 성능
- GitHub 인증, branch protection, PR template, CI queue가 있는 원격 배포
- 충돌·rebase·submodule·LFS·partial clone 등 고급 Git 상태
- 제품 사용자의 실제 표현 분포와 장기 자동 trigger 오탐
- 인간 reviewer 간 일치도: packet을 두 명이 독립 작성해야 완료됨

따라서 release 전에는 synthetic suite를 CI regression으로 유지하고,
실제 저장소의 read-only canary와 소규모 shadow run을 추가해야 한다.
