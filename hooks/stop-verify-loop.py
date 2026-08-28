#!/usr/bin/env python3
"""Stop 훅: 검증 루프가 활성이면 통과하지 못한 종료를 막는다.

상태 파일이 없으면 아무것도 하지 않는다. 그래서 루프를 안 쓰는 세션에는 영향이 없다.

Ralph 식 루프와 다른 점은 판정 주체다. 여기서는 검증 명령을 훅이 직접 돌리고
그 종료 코드로만 종료 여부를 정한다. 실행 모델이 완료를 선언해도 검증이
통과하지 못하면 끝나지 않는다.
"""
import json, pathlib, subprocess, sys

STATE = pathlib.Path(".claude/skill-loop.local.json")


def read_input():
    try:
        return json.loads(sys.stdin.read() or "{}")
    except ValueError:
        return {}


def emit(obj):
    print(json.dumps(obj, ensure_ascii=False))


def main():
    if not STATE.exists():
        return 0

    hook_in = read_input()
    try:
        state = json.loads(STATE.read_text(encoding="utf-8"))
    except (ValueError, OSError):
        STATE.unlink(missing_ok=True)
        return 0

    # 상태 파일은 프로젝트 범위인데 Stop 훅은 그 프로젝트의 모든 세션에서 걸린다.
    # 다른 세션이 시작한 루프를 이 세션이 가로채면 안 된다.
    want = state.get("session_id")
    got = hook_in.get("session_id")
    if want and got and want != got:
        return 0
    if not want and got:
        # 시작할 때 세션을 안 적었으면 처음 걸린 세션이 소유권을 잡는다.
        state["session_id"] = got
        STATE.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n",
                         encoding="utf-8")

    loop_py = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "loop.py"
    proc = subprocess.run([sys.executable, str(loop_py), "tick"],
                          capture_output=True, text=True)
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except (ValueError, IndexError):
        STATE.unlink(missing_ok=True)
        emit({"systemMessage": "검증 루프: 러너 출력을 읽지 못해 루프를 끝낸다.\n"
                               + proc.stderr[-400:]})
        return 0

    action = result.get("action")
    if action == "continue":
        emit({"decision": "block", "reason": result["reason"],
              "systemMessage": "검증 루프 %d회차 -- 결함 %d건 남음"
                               % (result["iteration"], result["error_count"])})
        return 0
    if action == "verdict":
        emit({"decision": "block", "reason": result["reason"],
              "systemMessage": "검증 루프 %d회차 -- 판정할 후보 %d건 남음"
                               % (result["iteration"], result["pending_count"])})
        return 0

    detail = result.get("message", "")
    if action != "inactive" and detail:
        emit({"systemMessage": "검증 루프: " + detail})
    return 0


if __name__ == "__main__":
    sys.exit(main())
