# 하네스 사실 — 프로브 기록

## 왜 이 파일이 있나

이 저장소는 **같은 사실 하나(서브에이전트의 도구 가용성)를 네 번 왕복**했다.

| 회차 | 주장 | 근거 | 결과 |
|---|---|---|---|
| 1 | `TaskCreate` 사용 불가 | 감사 | (맞았음) |
| 2 | "정정 — 둘 다 사용 가능" | **메인 루프**의 도구 표면 | ❌ 틀림. 참조는 전부 서브에이전트에 있었다 |
| 3 | "`TodoWrite`도 없다" | `ToolSearch` 결과 없음 | ❌ 틀림. ToolSearch는 deferred만 색인한다 |
| 4 | "`TodoWrite`는 있다" | **공식 문서 인용** | ❌ 틀림 (아래 프로브) |

네 번 다 **실행해보지 않고** 판단했다. 그래서 규칙을 하나 세운다.

> ## 하네스 사실은 실행 프로브로만 확정한다.
> **문서 인용은 가설이지 근거가 아니다.** 특히 "X가 없다"는 부재 주장은
> 프로브 기록 없이 PRD·CLAUDE.md·README 어디에도 쓰지 않는다.
> 부정 결과는 도구의 의미론(무엇을 색인/노출하는가)을 확인한 뒤에만 증거가 된다.

기능을 미검증 사실 위에 걸지 않는다. 기록이 없으면 먼저 프로브한다.

---

## 확정된 사실

### P-1 · background 서브에이전트의 도구 집합

- **날짜**: 2026-07-26
- **방법**: `general-purpose` 서브에이전트를 띄워 ① 자신의 도구 목록 열거 ② 각 도구 실제 호출 시도
- **환경**: Claude Code (로컬 1대), 모델 `claude-opus-5`

| 도구 | 결과 | 근거 |
|---|---|---|
| `TaskCreate` / `TaskUpdate` / `TaskList` / `TaskGet` | **없음** | 호출 시 `exists but is not enabled in this context` |
| `TodoWrite` | **없음** | 동일 에러. **공식 문서는 "있다"고 기술 — 문서와 실제가 다르다** |
| `Grep` / `Glob` | **없음** | 도구 목록에 부재. 공식 문서와 불일치 |
| `TaskStop` | **있음** | deferred 목록에 존재, `ToolSearch select:` 로 스키마 로드 성공 |
| `Read` / `Write` / `Edit` / `Bash` / `Agent` / `Skill` / `ToolSearch` / `Artifact` | **있음** | 스키마 즉시 로드됨 |
| `WebFetch` / `WebSearch` / `SendMessage` / `Monitor` / `NotebookEdit` / `EnterWorktree` / `ExitWorktree` | **있음** (deferred) | deferred 목록 |

**함의**
- 크로스 에이전트 상태 공유의 실행 가능한 수단은 **파일 기반 PLAN 원장 + `SHARED_CONTEXT` 뿐**이다.
- `TodoWrite` 대체안도 성립하지 않는다.
- README가 광고하던 "Layer 3 — TaskCreate/Update"는 **실행되지 않는 계층**이었다 → 제거됨.
- 에러 문구가 *"exists but is **not enabled in this context**"* 이므로, 원인은 "구현 없음"이 아니라 **서브에이전트 도구 세트에서 제외**다. 버전에 따라 바뀔 수 있다 → 재확인 대상.

### P-2 · `git commit --no-verify` 가 Claude Code hook을 우회하는가

- **날짜**: 2026-07-26
- **방법**: `.github/scripts/test_gate.sh` 픽스처에서 `--no-verify` / `-n` 로 커밋 시도
- **결과**: **우회하지 못한다.** `--no-verify`는 *git 자체의* pre-commit/commit-msg 훅을 끄는 플래그이고, Claude Code의 `PreToolUse`는 Bash 도구 호출 자체를 가로채므로 무관하다.
- **회귀 고정**: `test_gate.sh` 에 케이스 존재

### P-3 · `${CLAUDE_PLUGIN_ROOT}` 가 hook command에서 확장되는가

- **날짜**: 2026-07-26
- **상태**: **확정 — 확장된다**
- **방법**: 격리 프로브 플러그인(hook 하나만 든)을 만들어 헤드리스 자식 세션으로 실행.
  ```bash
  claude -p "Run exactly: echo probe-ok" --plugin-dir <probe-plugin> --allowedTools Bash
  ```
  hook이 `${CLAUDE_PLUGIN_ROOT}` 를 파일에 기록하게 했다.
- **결과**: `RAW=[/…/probe-plugin]` (절대경로로 확장), `RESOLVES=yes`(그 경로 아래 파일 접근 성공).
  → 문서 상충에서 "확장된다" 쪽이 맞다. `hooks.json` 이 `${CLAUDE_PLUGIN_ROOT}/hooks/gate.sh` 를 호출하는 설계는 유효하다.
- **부수 확인**: `SessionStart` fail-loud 경고(E-5)는 그대로 둔다 — 플러그인 설치가 깨진 경우를 여전히 잡는다.

### P-3b · 게이트 end-to-end 동작 (실제 세션에서)

- **날짜**: 2026-07-26
- **방법**: 임시 git 저장소 + 헤드리스 자식 세션. 실제 플러그인을 `--plugin-dir` 로 로드하고 `git commit` 을 시켰다.

| 시나리오 | 기대 | 결과 |
|---|---|---|
| `.wigtn/checks.sh` 가 `exit 1` | 차단 | ✅ `BLOCKED: WIGTN 객관 체크 실패` — 커밋 로그에 남지 않음 |
| `.wigtn/checks.sh` 가 `exit 0` | 통과 | ✅ 커밋 생성됨 |

→ 33개 단위 테스트뿐 아니라 **실제 Claude Code 세션에서도 게이트가 작동한다.**

### P-5 · `--plugin-dir` 는 마켓플레이스 설치본을 대체하는가

- **날짜**: 2026-07-26
- **상태**: **확정 — 대체하지 않는다. 둘 다 로드된다.**
- **증거**: `settings.json` 의 `enabledPlugins["wigtn-plugins@wigtn-plugins"] = true` 인 상태에서 `--plugin-dir` 로 로컬 사본을 추가해도, 마켓플레이스 클론(`~/.claude/plugins/marketplaces/wigtn-plugins`, GitHub `wigtn/wigtn-plugins-with-claude-code`, `autoUpdate: true`)의 **구버전 hook이 계속 발화**했다.
- **함의 (개발 시 필수)**: 로컬 수정본만 테스트하려면 **마켓플레이스 설치본을 먼저 비활성화**해야 한다(`/plugin` 또는 `enabledPlugins` 를 `false`). 안 그러면 구버전과 신버전 hook이 **동시에** 돈다.
- **함정**: 저장소를 편집해도 실행되는 것은 GitHub 클론이다. "고쳤는데 왜 안 바뀌지"의 원인이 대개 이것.

### P-4 · 플러그인 hook을 끌 수 있는 경로

- **날짜**: 2026-07-26
- **방법**: 공식 문서 조사 (⚠️ 프로브 아님 — **가설 등급**)
- **내용**: `.claude/settings.json`(또는 gitignore되는 `settings.local.json`)의 `disableAllHooks: true` 한 줄로 모든 hook 비활성화. managed settings 계층만 override 불가.
- **함의 (사실이라면)**: 플러그인은 자기가 꺼진 것을 감지할 수 없다(SessionStart도 안 돌므로). → 광고를 낮추고(E-7), 하드닝 레시피를 제공한다(E-6).
- **확정 필요**: 실제로 설정해보고 hook이 안 도는지 확인. **확정 전까지 이 항목에 기능을 걸지 않는다.**

---

## 재확인 주기

- Claude Code **마이너 버전이 올라갈 때** P-1·P-3 재프로브
- 기능을 이 표의 사실 위에 새로 걸 때 해당 항목 재프로브
- 프로브 결과가 바뀌면 이 파일을 먼저 고치고, 그 다음 코드를 고친다
