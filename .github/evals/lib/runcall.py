#!/usr/bin/env python3
"""
Portable, process-group-safe call runner for eval arms.

Fixes three instrumentation defects this repo already booked:
  E-01  `timeout` is absent on macOS -> 16 calls silently never invoked the model.
  E-02  silent fallback mixed "no output" with "a result".
  E-06  watchdog killed the subshell but the `claude` child survived as an orphan,
        producing rc=137 that *looked* like a timeout but was our own kill.

Here the child is started in its own process group (setsid) and the watchdog
signals the whole group, so nothing is orphaned. The exit reason is recorded
explicitly rather than inferred from the exit code.

Usage:
  runcall.py --meta OUT.meta --stdout OUT.stdout --stderr OUT.stderr \
             --timeout 1800 --cwd DIR -- <command> [args...]

Writes a key=value .meta including verdict, exit_reason and token usage.
Exit code is 0 if the call completed (whatever the model said), 1 otherwise.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--meta", required=True)
    p.add_argument("--stdout", required=True)
    p.add_argument("--stderr", required=True)
    p.add_argument("--timeout", type=int, required=True)
    p.add_argument("--cwd", required=True)
    p.add_argument("--kv", action="append", default=[],
                   help="extra key=value pairs to record in the meta")
    p.add_argument("cmd", nargs=argparse.REMAINDER)
    a = p.parse_args()
    if a.cmd and a.cmd[0] == "--":
        a.cmd = a.cmd[1:]
    if not a.cmd:
        p.error("no command given")
    return a


def kill_group(proc, sig):
    """Signal the child's entire process group; never leave orphans."""
    try:
        os.killpg(os.getpgid(proc.pid), sig)
    except (ProcessLookupError, PermissionError):
        pass


def run(a):
    out_f = open(a.stdout, "wb")
    err_f = open(a.stderr, "wb")
    # E-10: macOS 의 time.monotonic() 은 시스템 슬립 중 멈춘다. proc.wait(timeout=)
    # 는 그 시계를 쓰므로 맥이 자면 워치독이 뜨지 않는다. 벽시계만 흘러가
    # seconds=9448 인데 timeout=1800 이 안 터지는 상황이 실제로 발생했다.
    # 두 시계를 모두 재서 어긋난 만큼을 슬립으로 기록한다 — 조용히 넘어가지 않는다.
    started, started_mono = time.time(), time.monotonic()
    proc = subprocess.Popen(
        a.cmd, cwd=a.cwd, stdout=out_f, stderr=err_f,
        stdin=subprocess.DEVNULL, start_new_session=True,
    )
    exit_reason = "completed"
    try:
        rc = proc.wait(timeout=a.timeout)
    except subprocess.TimeoutExpired:
        exit_reason = "watchdog_timeout"
        kill_group(proc, signal.SIGTERM)
        try:
            rc = proc.wait(timeout=30)
        except subprocess.TimeoutExpired:
            exit_reason = "watchdog_sigkill"
            kill_group(proc, signal.SIGKILL)
            rc = proc.wait()
    finally:
        out_f.close()
        err_f.close()
    wall = time.time() - started
    mono = time.monotonic() - started_mono
    return rc, exit_reason, wall, mono


def extract_usage(stdout_path):
    """Pull token usage out of `claude --output-format json` output.

    Returns a dict of meta keys. Absence is recorded explicitly as `unknown`
    rather than defaulted to zero -- a zero would be indistinguishable from a
    real zero-token call.
    """
    keys = ["input_tokens", "output_tokens", "cache_read_input_tokens",
            "cache_creation_input_tokens", "total_cost_usd", "num_turns",
            "duration_api_ms"]
    blank = {k: "unknown" for k in keys}
    try:
        raw = open(stdout_path, "rb").read().decode("utf-8", "replace").strip()
    except OSError:
        return blank
    if not raw:
        return blank
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        return blank
    if isinstance(doc, list):
        doc = next((d for d in reversed(doc)
                    if isinstance(d, dict) and d.get("type") == "result"), None)
        if doc is None:
            return blank
    if not isinstance(doc, dict):
        return blank
    usage = doc.get("usage") or {}
    got = dict(blank)
    for k in ("input_tokens", "output_tokens", "cache_read_input_tokens",
              "cache_creation_input_tokens"):
        if isinstance(usage.get(k), int):
            got[k] = usage[k]
    for k in ("total_cost_usd", "num_turns", "duration_api_ms"):
        if isinstance(doc.get(k), (int, float)):
            got[k] = doc[k]
    billed = [got[k] for k in ("input_tokens", "output_tokens",
                               "cache_read_input_tokens",
                               "cache_creation_input_tokens")]
    if all(isinstance(v, int) for v in billed):
        got["billed_tokens"] = sum(billed)
    else:
        got["billed_tokens"] = "unknown"
    return got


def main():
    a = parse_args()
    os.makedirs(os.path.dirname(os.path.abspath(a.meta)) or ".", exist_ok=True)
    rc, exit_reason, wall, mono = run(a)

    # E-10: 벽시계와 monotonic 이 어긋난 만큼이 시스템 슬립이다. 30초를 넘으면
    # 이 콜은 슬립을 거쳤다는 뜻이고, 그동안 네트워크가 끊겨 API 오류가 났을 수
    # 있다. 소요시간도 실제 계산 시간이 아니다. 채점에서 제외할 수 있게 표시한다.
    slept = max(0.0, wall - mono)
    sleep_suspect = slept > 30

    # verdict distinguishes the outcomes E-02 required us to keep apart.
    if sleep_suspect:
        verdict = "sleep_contaminated"
    elif rc == 0:
        verdict = "ok"
    elif exit_reason.startswith("watchdog"):
        verdict = "timeout"
    else:
        verdict = "fail"

    meta = {
        "status": rc,
        "exit_reason": exit_reason,
        "verdict": verdict,
        "seconds": int(mono),          # 실제 경과(슬립 제외)
        "wall_seconds": int(wall),
        "slept_seconds": int(slept),
        "sleep_suspect": str(sleep_suspect).lower(),
        "timeout_limit": a.timeout,
        "cmd": " ".join(a.cmd),
    }
    meta.update(extract_usage(a.stdout))
    for kv in a.kv:
        k, _, v = kv.partition("=")
        meta[k] = v

    with open(a.meta, "w") as f:
        for k, v in meta.items():
            f.write(f"{k}={v}\n")

    note = f" SLEPT{int(slept)}s" if sleep_suspect else ""
    print(f"[{verdict}] rc={rc} reason={exit_reason} {int(mono)}s{note} "
          f"tokens={meta.get('billed_tokens')}", file=sys.stderr)
    return 0 if verdict == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
