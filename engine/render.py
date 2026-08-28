"""검증 산출물을 사람이 읽는 형태로 낸다.

산출물 자체는 JSON 이 원본이고 여기는 표현만 맡는다. 판정도 집계도 하지 않는다.
"""

LIMIT = 20


def _head(report):
    s = report.get("summary", {})
    ev, sk = len(report.get("rules_evaluated", [])), len(report.get("rules_skipped", []))
    return ["규칙 %d개 평가 / 건너뜀 %d" % (ev, sk),
            "error %d · warn %d · pending %d"
            % (s.get("error", 0), s.get("warn", 0), s.get("pending", 0))]


def _loc(f):
    l = f.get("location", {})
    return "%s:%s" % (l.get("file", "?"), l.get("line", "?"))


ORDER = {"error": 0, "warn": 1}


def _defects(findings, show_warn):
    keep = [f for f in findings
            if f.get("severity") == "error" or (show_warn and f.get("severity") == "warn")]
    keep = sorted(keep, key=lambda f: ORDER.get(f.get("severity"), 9))
    if not keep:
        return []
    out = [""]
    for f in keep[:LIMIT]:
        out.append("[%s] %s  %s" % (f.get("rule", "?"), _loc(f), f.get("severity", "")))
        out.append("  %s" % f.get("message", ""))
        fix = (f.get("fix") or {}).get("suggestion", "")
        if fix:
            out.append("  고침: %s" % fix)
    if len(keep) > LIMIT:
        out.append("... 외 %d건" % (len(keep) - LIMIT))
    return out


def _pending(pending):
    if not pending:
        return []
    out = ["", "확정 필요 %d건" % len(pending)]
    for f in pending[:LIMIT]:
        out.append("[%s] %s" % (f.get("rule", "?"), _loc(f)))
        out.append("  %s" % (f.get("location", {}).get("snippet", "")))
        out.append("  물음: %s" % f.get("question", f.get("message", "")))
        out.append("  id: %s" % f.get("id", ""))
    if len(pending) > LIMIT:
        out.append("... 외 %d건" % (len(pending) - LIMIT))
    return out


def _skipped(skipped):
    """이유가 같은 것은 묶는다. 한 이유로 여러 규칙이 빠지는 일이 흔하다."""
    if not skipped:
        return []
    by = {}
    for s in skipped:
        by.setdefault(s.get("reason", ""), []).append(s.get("rule", "?"))
    out = ["", "건너뛴 규칙"]
    for reason, ids in sorted(by.items()):
        out.append("  %s -- %s" % (", ".join(sorted(ids)), reason))
    return out


def _delta(report):
    d = report.get("delta") or {}
    if d.get("first_run") or not d:
        return []
    line = "회차 비교  해결 %d · 남음 %d · 새로 %d" % (
        len(d.get("resolved", [])), len(d.get("persisted", [])), len(d.get("new", [])))
    if report.get("stalled"):
        line += "  -- 진전이 없어 멈춘다"
    return ["", line]


def _fixed(fixed):
    if not fixed:
        return []
    return ["", "고침 %d건" % len(fixed)] + ["  %s" % f for f in fixed]


def to_text(report, show_warn=False):
    lines = _head(report)
    lines += _fixed(report.get("fixed", []))
    lines += _defects(report.get("findings", []), show_warn)
    lines += _pending(report.get("pending", []))
    lines += _skipped(report.get("rules_skipped", []))
    lines += _delta(report)
    s = report.get("summary", {})
    if not s.get("error") and not s.get("pending"):
        lines += ["", "통과."]
    return "\n".join(lines)
