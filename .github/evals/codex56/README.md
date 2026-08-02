# GPT-5.6 하네스 비교 실험

`EXPERIMENT.md`의 Opus 5 실험을 Codex CLI와 GPT-5.6-Sol에서 재측정한다.
이 디렉터리의 결과는 **GPT-5.6 내부 arm 비교**에 사용한다. Opus 5와의 절대
우열 비교에는 사용하지 않는다. 모델뿐 아니라 런타임과 플러그인 형식도 다르기
때문이다.

## 질문

1. 순정 GPT-5.6-Sol은 짧은 제품 브리프만 받고 WIGTN의 PRD 필수 산출물을
   얼마나 자발적으로 작성하는가?
2. 현재 Codex용 `product-spec` 스킬이 그 충족률을 높이는가?
3. 절차 설명을 늘리지 않고 **산출물 계약만 명시**하면 100%를 회복하는가?

## Arm

| Arm | 조건 | 독립변수 |
|---|---|---|
| A0 | 임시 `CODEX_HOME`, 원격 플러그인·앱 비활성화, 프로젝트 밖 실행 | 하네스 없음 |
| A1 | A0 + 현재 `wigtn-plugins-with-codex` v0.1.0 | 현 Codex 하네스 |
| A2 | A1 + `arms/a2-contract.patch` | WIGTN PRD 산출물 계약 |

A2는 현재 플러그인을 임시 디렉터리에 복제한 뒤 패치한다. 제품 소스는 바꾸지
않는다. 패치는 절차·예시를 추가하지 않고 다음 출력 요구만 명시한다.

- User Roles 권한 표
- Pages 표
- Empty/Loading/Error/Success State Matrix
- Mermaid User Flow
- 정량 NFR
- Given/When/Then 수용 기준
- 인가 규칙
- 구현 Phase

## 통제

- 모델: `gpt-5.6-sol`
- reasoning effort: `high`
- 프롬프트: `prompts/prd-create.txt`
- 반복: arm당 3회
- 실행 위치: 저장소 밖의 빈 임시 디렉터리
- 세션: 매회 `--ephemeral`
- 샌드박스: `read-only`
- 외부 도구: 원격 플러그인과 앱 비활성화
- 채점기: 상위 디렉터리의 기존 `score_prd.py`

기존 채점 결과는 원 실험 재현을 위해 `RESULT.md`에 그대로 남긴다. 첫 실행
원문 감사에서 영문 `Pages` 대신 `페이지 정의`, `Non-Goals` 대신 `비목표`를
쓴 정상 산출물을 놓치는 false negative가 확인됐다. 이를 보정한 구조 채점은
`score_prd_contract.py`와 `RESULT-CONTRACT.md`에 별도로 남긴다. 보정 채점은
사후 감사 결과이며, A2 패치에 없던 새 기준을 추가하지 않는다.

## 실행

```bash
bash .github/evals/codex56/run-prd-create.sh
```

환경 변수로 모델·반복 수·CLI 경로를 바꿀 수 있다.

```bash
CODEX56_MODEL=gpt-5.6-sol \
CODEX56_EFFORT=high \
CODEX56_REPEAT=3 \
CODEX_BIN=/Applications/ChatGPT.app/Contents/Resources/codex \
bash .github/evals/codex56/run-prd-create.sh
```

실행기는 기존 결과를 덮어쓰지 않는다. 중단 후 재실행하면 없는 회차만 이어서
실행한다. 결과 원문과 실행 로그는 `runs/prd-create/`에 남긴다.

## 해석 제한

- 이 실험의 브리프는 1종이다.
- n=3이므로 1/3 차이는 신호로 해석하지 않는다.
- 채점은 섹션 존재 여부를 보는 키워드 매칭이다.
- A2가 이기더라도 “긴 프롬프트가 좋다”는 뜻이 아니다. A2가 추가한 것은
  WIGTN이 정한 산출물 이름과 형식뿐이다.
- Opus 5 원 실험과 프롬프트·런타임·플러그인 포맷이 완전히 같지 않으므로
  모델 간 순위표를 만들면 안 된다.
