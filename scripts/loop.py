#!/usr/bin/env python3
"""검증 명령을 반복해 돌리는 루프 러너.

완료 판정을 검증 명령의 종료 코드로만 한다. 실행 모델이 완료를 선언해도
종료 코드가 0 이 아니면 끝나지 않는다.

무엇을 검증하는지는 이 파일이 모른다. 상태 파일에 담긴 명령을 그대로 돌리고
종료 코드만 본다. 그래서 어느 스킬에나 쓸 수 있다.

사용:
  loop.py start --verify <cmd...> [--report <path>] [--max N] [--label L] [--session S]
  loop.py tick
  loop.py status
  loop.py stop

종료 코드 규약(검증 명령이 지켜야 한다):
  0  통과       루프를 끝낸다
  1  결함 있음  결함을 실어 다시 돌린다
  2  헛돎       진전이 없어 멈춘다
  3  미확정     판정해야 할 후보를 실어 다시 돌린다
"""
import argparse, json, pathlib, subprocess, sys

STATE = pathlib.Path(".claude/skill-loop.local.json")
MAX_FINDINGS_IN_REASON = 12


def load():
    if not STATE.exists():
        return None
    try:
        return json.loads(STATE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return None


def save(state):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                     encoding="utf-8")


def clear():
    if STATE.exists():
        STATE.unlink()


def cmd_start(args):
    if not args.verify:
        print("검증 명령이 비어 있다", file=sys.stderr)
        return 1
    save({"label": args.label, "session_id": args.session,
          "verify_cmd": args.verify, "report": args.report,
          "iteration": 0, "max_iterations": args.max})
    print(json.dumps({"action": "started", "label": args.label,
                      "max_iterations": args.max}, ensure_ascii=False))
    return 0


def read_findings(state):
    """검증 산출물에서 결함 목록을 뽑는다. 없으면 빈 목록."""
    path = state.get("report")
    if not path or not pathlib.Path(path).exists():
        return [], {}
    try:
        d = json.loads(pathlib.Path(path).read_text(encoding="utf-8"))
    except (ValueError, OSError):
        return [], {}
    errs = [f for f in d.get("findings", []) if f.get("severity") == "error"]
    return errs, d.get("delta", {}), d.get("pending", [])


def format_pending(state, pending):
    """확정이 필요한 후보를 실어 보낸다. 판정기가 답할 수 없는 질문만 여기로 온다."""
    lines = ["검증이 후보를 냈고 아직 확정되지 않았다. 아래 하나하나를 판정한다.",
             "",
             "회차 %d / 상한 %d" % (state["iteration"], state["max_iterations"]),
             ""]
    for f in pending[:MAX_FINDINGS_IN_REASON]:
        loc = f.get("location", {})
        lines.append("- [%s] %s:%s" % (f.get("rule", "?"), loc.get("file", "?"),
                                       loc.get("line", "?")))
        lines.append("    %s" % loc.get("snippet", ""))
        lines.append("    물음: %s" % f.get("question", f.get("message", "")))
        lines.append("    id: %s" % f.get("id", ""))
    if len(pending) > MAX_FINDINGS_IN_REASON:
        lines.append("- ... 외 %d건" % (len(pending) - MAX_FINDINGS_IN_REASON))
    lines += ["",
              "판정 결과를 검증 명령의 --verdicts 가 가리키는 JSON 에 id 별로 적는다.",
              '형식: {"<id>": {"verdict": "ok" 또는 "defect", "evidence": "왜 그런지"}}',
              "근거를 비우면 확정으로 세지 않는다.",
              "",
              "루프를 중단하려면 %s 를 지운다." % STATE]
    return "\n".join(lines)


def format_reason(state, findings, delta):
    lines = ["검증이 통과하지 못했다. 아래 결함을 고친 뒤 다시 끝내려 하면 다시 검증된다.",
             "",
             "회차 %d / 상한 %d" % (state["iteration"], state["max_iterations"]),
             ""]
    for f in findings[:MAX_FINDINGS_IN_REASON]:
        loc = f.get("location", {})
        lines.append("- [%s] %s:%s  %s" % (
            f.get("rule", "?"), loc.get("file", "?"), loc.get("line", "?"),
            f.get("message", "")))
        fix = (f.get("fix") or {}).get("suggestion", "")
        if fix:
            lines.append("    고침: %s" % fix)
    if len(findings) > MAX_FINDINGS_IN_REASON:
        lines.append("- ... 외 %d건" % (len(findings) - MAX_FINDINGS_IN_REASON))
    if delta.get("persisted"):
        lines += ["", "직전 회차에서 안 고쳐진 결함 %d건이 그대로 남아 있다."
                  % len(delta["persisted"])]
    if delta.get("new"):
        lines += ["", "이번 수정이 새 결함 %d건을 만들었다. 그 수정을 되돌리고 다른 방향으로 고친다."
                  % len(delta["new"])]
    lines += ["", "루프를 중단하려면 %s 를 지운다." % STATE]
    return "\n".join(lines)


def cmd_tick(args):
    state = load()
    if state is None:
        print(json.dumps({"action": "inactive"}, ensure_ascii=False))
        return 0

    state["iteration"] += 1
    if state["max_iterations"] > 0 and state["iteration"] > state["max_iterations"]:
        clear()
        print(json.dumps({"action": "exhausted",
                          "message": "반복 상한 %d 에 도달해 루프를 끝낸다. 결함은 남아 있다."
                                     % state["max_iterations"]}, ensure_ascii=False))
        return 0

    proc = subprocess.run(state["verify_cmd"], capture_output=True, text=True)
    code = proc.returncode
    findings, delta, pending = read_findings(state)

    if code == 0:
        clear()
        out = {"action": "done", "iteration": state["iteration"],
               "message": "검증 통과. 루프를 끝낸다."}
    elif code == 2:
        clear()
        out = {"action": "stalled", "iteration": state["iteration"],
               "message": "진전 없는 회차가 이어져 멈춘다. 남은 결함 %d건은 사람이 본다."
                          % len(findings),
               "persisted": delta.get("persisted", [])}
    elif code == 1:
        save(state)
        out = {"action": "continue", "iteration": state["iteration"],
               "reason": format_reason(state, findings, delta),
               "error_count": len(findings)}
    elif code == 3:
        save(state)
        out = {"action": "verdict", "iteration": state["iteration"],
               "reason": format_pending(state, pending),
               "pending_count": len(pending)}
    else:
        clear()
        out = {"action": "failed", "iteration": state["iteration"],
               "message": "검증 명령이 예상 밖 종료 코드 %d 를 냈다. 루프를 끝낸다." % code,
               "stderr": proc.stderr[-800:]}
    print(json.dumps(out, ensure_ascii=False))
    return 0


def cmd_status(args):
    state = load()
    print(json.dumps(state or {"action": "inactive"}, ensure_ascii=False, indent=2))
    return 0


def cmd_stop(args):
    clear()
    print(json.dumps({"action": "stopped"}, ensure_ascii=False))
    return 0


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("start")
    s.add_argument("--verify", nargs=argparse.REMAINDER, required=True)
    s.add_argument("--report", default=None)
    s.add_argument("--max", type=int, default=20)
    s.add_argument("--label", default="verify")
    s.add_argument("--session", default=None)
    s.set_defaults(func=cmd_start)

    for name, fn in (("tick", cmd_tick), ("status", cmd_status), ("stop", cmd_stop)):
        p = sub.add_parser(name)
        p.set_defaults(func=fn)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
