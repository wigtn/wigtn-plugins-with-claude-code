# ERRATA — 3-arm 실행 중 발견한 계측 결함

> `PROTOCOL.md`는 실행 전에 커밋됐고 **수정하지 않는다.** 일탈·수정은 여기에 append 한다.

## E-08 · cwd 기반 격리는 재현되지 않는다 (PROTOCOL 일탈)

- **PROTOCOL이 정한 것**: *"격리는 cwd로 한다. 저장소 밖 임시 디렉터리에서 시작한다."*
  근거는 실측이었다 — 저장소 안에서는 설치본 23개가 보이고, `/private/tmp/...`의
  scratchpad에서는 `NONE`이었다.
- **증상**: 러너가 `mktemp -d`(macOS에서 `/var/folders/.../T/tmp.XXXX`)로 만든 디렉터리에서는
  **다시 23개가 보였다.** 같은 "저장소 밖"인데 경로에 따라 결과가 갈렸다.

  | cwd | wigtn 항목 |
  |---|---|
  | 저장소 안 | 23 |
  | `/private/tmp/claude-501/.../scratchpad/iso/wd3` | **0** |
  | `mktemp -d` → `/var/folders/.../T/tmp.XXXX` | **23** |

- **진짜 원인**: `~/.claude/settings.json`이 **user 스코프**에서
  `"wigtn-plugins@wigtn-plugins": true`로 전역 활성화하고 있었다. cwd는 애초에
  격리 수단이 아니었다. `/private/tmp` 경로에서 0이 나온 것은 **우연**이며,
  그 우연을 격리 메커니즘으로 사전등록한 것이 잘못이었다.
- **왜 심각한가**: 이 저장소는 이미 같은 함정에 두 번 빠졌다 —
  `P-6`(`enabledPlugins`가 교체가 아니라 병합), `E-07`(`--plugin-dir`가 조용히 무시됨).
  세 번 모두 **"관측이 원하는 대로 나왔으니 메커니즘도 맞을 것"** 이라고 가정한 사고다.
  원인을 모른 채 관측만 보고 프로토콜을 쓰면 다음 환경에서 조용히 깨진다.
- **처방**: 문서화된 메커니즘으로 교체한다.
  `--setting-sources project` — user 스코프 설정을 아예 로드하지 않으므로
  설치본이 적재되지 않는다. cwd에 의존하지 않는다.

  실측 재검증 (전부 `mktemp -d` cwd에서):

  | arm | 인자 | 관측 | 기대 |
  |---|---|---|---|
  | A0 | `--setting-sources project` | wigtn **0** | 0 |
  | A1 | 위 + `--plugin-dir <A1>` | parallel-coordinator **2** | ≥1 |
  | A2 | 위 + `--plugin-dir <A2>` | wigtn **21**, parallel **0** | ≥1, 0 |

- **유지되는 것**: arm 서명 검증(양성+음성)은 그대로다. 격리 수단이 바뀌어도
  **매 실행 전 "어느 arm이 실제로 적재됐는지" 확인한다**는 계약은 변하지 않는다.
  실제로 이 결함을 잡아낸 것도 그 가드였다 — A0 검증이 `ABORT`로 실행을 막았다.

## E-09 · `mapfile` 부재 (macOS bash 3.2)

- 러너가 `mapfile -t`로 arm 인자를 배열에 담았는데 macOS 기본 bash 3.2에는 없다.
- `E-01`(GNU `timeout` 부재로 16콜이 모델을 호출조차 못 함)과 같은 계열의
  이식성 결함이다. 이번에는 arm 검증 단계에서 즉시 드러나 실행 전에 잡혔다.
- **처방**: 전역 배열을 직접 채우는 `set_arm_args()`로 교체.

## 참고 · 이번 실행에서 새로 발견해 PROTOCOL에 반영한 것

`E-07`(`--plugin-dir`는 name+version이 설치본과 같으면 조용히 무시된다)은
사전등록 **전에** 발견해 `PROTOCOL.md`에 직접 실었다. 여기 다시 적지 않는다.
