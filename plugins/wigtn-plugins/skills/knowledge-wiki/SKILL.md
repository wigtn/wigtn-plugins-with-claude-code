---
name: knowledge-wiki
description: 세션에서 배운 것을 정책 게이트를 통과시켜 팀 위키에 자동 축적한다. 전역 설정(~/.config/wigtn/knowledge-wiki.yml)에 지정한 경로에서만 동작하며, 시크릿·개인정보·고객 식별 정보는 4단 게이트로 차단한다. 위키 설정·정책 확인·수동 축적·문제 진단에 사용한다.
allowed-tools: Read, Write, Edit, Glob, Bash
---

# Knowledge Wiki

세션 지식을 **일반화된 article**로 컴파일해서 팀 위키에 쌓는다.
Karpathy KB 패턴 — 매번 찾는 게 아니라 위키 자체가 자란다.

> **한 줄**: 세션에서 *배운 것*만 쌓는다. *있었던 일*은 쌓지 않는다.

## 켜는 법 — 없음. 설치하면 켜집니다

첫 세션이 끝나면 플러그인이 알아서 만듭니다:

```
~/.wigtn/knowledge-wiki.yml   설정 (자동 생성)
~/.wigtn/wiki/                위키 repo (자동 git init)
```

그리고 한 번만 안내합니다:

```
[wigtn] 지식 위키를 켰습니다 → ~/.wigtn/wiki
        세션에서 배운 것이 자동으로 쌓입니다 (로컬 전용, push 없음).
```

**기본값 = 로컬 축적만.** `remote` 가 없으면 push 하지 않습니다. transcript 는 이미
로컬에 있으므로, 로컬 article 은 새로운 노출이 아닙니다. **기계 밖으로 나가는 것만
명시적 설정을 요구합니다.**

### 팀과 공유하려면 — remote 한 줄

```yaml
wiki:
  remote: git@github.com:myteam/team-wiki.git   # 추가하면 push 시작
  path: ~/Dev/team-wiki                          # 없는 경로면 자동 clone
  subdir: per-user/harry
```

`path` 가 없고 `remote` 가 있으면 **자동으로 clone** 합니다. 새 팀원은 이 두 줄만 받으면
됩니다. clone 실패 시에는 축적하지 않습니다 (fail-closed).

### 범위 조정

```yaml
include:            # 기본값 = 홈 전체 (로컬 전용이라 허용)
  - ~/Dev
exclude:            # 고객사·NDA repo. include 와 repo 마커보다 강하다
  - ~/Dev/client-nda
```

**`remote` 가 있어도 `include` 가 홈/루트 전체면 push 는 보류됩니다.**
축적과 로컬 커밋은 계속되고, 로그에 사유가 남습니다. `include` 를 좁히면 그때 push 가 켜집니다.
로컬 축적과 팀 공유는 위험도가 다르고, 그 경계는 권고가 아니라 코드가 집행합니다.

`subdir` 은 `per-user/` 또는 `ouroboros/` 아래만 허용됩니다. `shared/` 는 사람이 PR 로 승격합니다.

템플릿: `scripts/knowledge_wiki/knowledge-wiki.example.yml`

### repo 마커 (선택) — 예외 처리용

보통은 필요 없다. 아래 세 경우에만 repo 루트에 `.wigtn-wiki.yml` 을 둔다:

| 상황 | 마커 내용 |
|---|---|
| `include` 밖 repo를 개별 opt-in | `enabled: true` |
| 이 repo만 다른 위키로 | `wiki: {path: ..., subdir: ...}` |
| 이 repo만 끄기 | `enabled: false` |

⚠️ **전역 `exclude` 와 전역 `enabled: false` 는 마커보다 강하다.**
exclude 된 경로, 그리고 전역으로 꺼 둔 상태는 마커가 있어도 거부된다.
마커는 *범위 opt-in* 이지 *kill-switch 해제* 가 아니다.

## 어떻게 동작하나

세션 종료(Stop 훅) 시 4단 게이트를 통과한 것만 커밋·push 된다.

```
G0 스코프 게이트   include 밖·exclude·자기오염이면 즉시 종료
G1 결정론 차단    원문에 키·자격증명·주민번호 → 1건이라도 hit면 세션 폐기
G2 LLM 컴파일     transcript → 일반화 article (원문 인용 금지)
G3 LLM 감사       별도 호출로 반출 위반 탐지 (통과 판정 권한 없음)
G4 결정론 재검사   article에 전체 패턴 적용 — 이메일·사설 IP·절대경로까지
     ↓
per-user/ 커밋 + push
```

**모든 실패는 폐기다.** 판정 불가·타임아웃·파싱 실패 전부 버린다.
위키 항목 하나 잃는 건 싸고, 유출은 되돌릴 수 없다.

정책 정본: [`../../contracts/INGEST-POLICY.md`](../../contracts/INGEST-POLICY.md)

## 사용자가 할 일

**두 가지뿐이다.**

1. **아무것도 안 함** — 설치하면 로컬에 쌓이기 시작한다
2. 팀 공유를 원하면 `remote` 한 줄 추가 + `per-user/` 에서 **PR로 `shared/` 승격**

항목별 검토는 안 해도 된다. 그게 정책의 목적이다.

## 진단

축적이 안 될 때 확인 순서:

```bash
# 1. 전역 설정이 있나 / include 에 이 경로가 들어있나
cat ~/.config/wigtn/knowledge-wiki.yml 2>/dev/null || cat ~/.wigtn/knowledge-wiki.yml

# 2. 게이트 통과 여부 — 위키 repo의 로그
tail -20 <wiki>/.knowledge-wiki.log
```

로그 예시와 의미:

| 로그 | 뜻 | 조치 |
|---|---|---|
| (로그 자체가 없음) | G0에서 종료 — include 밖/exclude/자기오염 | `~/.wigtn/knowledge-wiki.yml` 확인 |
| `G1 폐기: D1 API 키` | 세션에 시크릿이 있었다 | 정상 동작. 조치 불필요 |
| `G2 폐기: 기록 가치 없음` | 단순 작업 세션 | 정상 동작 |
| `G3 폐기: 위반 탐지 D3` | 고객 식별 정보 등이 남아 있었다 | 정상 동작 |
| `G4 폐기` | LLM이 금지 항목을 되살렸다 | 정상 동작 |
| `게시 … push 보류: include 범위가 홈/루트 전체` | 로컬에는 쌓였고 push만 안 했다 | `include` 를 좁히면 켜진다 |
| `게시 실패` | git 문제 | 위키 repo 권한·remote 확인 |

**폐기 로그가 많은 건 문제가 아니다.** 게이트가 일하고 있다는 뜻이다.

## 수동 축적

훅을 기다리지 않고 지금 쌓고 싶으면:

```bash
echo '{"cwd":"'$PWD'","transcript_path":"<transcript.jsonl>"}' \
  | python3 <plugin>/scripts/knowledge_wiki/accumulate.py
```

## 끄는 법

- 특정 repo만: `exclude` 에 경로 추가 (또는 그 repo에 `enabled: false` 마커)
- 전체 일시 중지: `~/.wigtn/knowledge-wiki.yml` 에 `enabled: false`
- push만 중지: `remote` 줄 삭제 (로컬 축적은 유지)
- 전체 비활성: 플러그인 hooks.json 의 Stop 훅에서 해당 항목 제거

## 설계 배경

이전 세대 도구를 쓰다가 **통째로 끈 경험**에서 나왔다. 당시 문제는 기능이 아니라 경계였다.

| 이전 | 지금 |
|---|---|
| 전역 적용 — cwd 무관하게 흡수 | **G0 스코프 게이트 (include 지정 필수, fail-closed)** |
| "사용자에게 묻지 않는다" | 캡처는 자동, **`shared/` 게시는 사람** |
| 필터 없이 transcript 컴파일 | **4단 게이트** |
| 파이프라인이 죽어도 모름 | **로그 파일에 매 실행 기록** |

경계를 코드로 만들면 기능은 그대로 쓸 수 있다.
