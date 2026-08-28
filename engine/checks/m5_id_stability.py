"""M5 -- id 안정성."""
import pathlib


def check(rules_dir, rules):
    out, seen = [], {}
    retired_path = pathlib.Path(rules_dir) / "retired.txt"
    retired = set()
    if retired_path.exists():
        retired = {l.split("#")[0].strip() for l in
                   retired_path.read_text(encoding="utf-8").splitlines()
                   if l.split("#")[0].strip()}

    for r in rules:
        m, p = r["meta"], r["path"]
        rid = m.get("id")
        if not rid:
            continue
        if rid in seen:
            out.append({"file": str(p), "line": 1, "snippet": rid,
                        "section": "(id)",
                        "message": "id %s 가 %s 와 중복된다" % (rid, seen[rid])})
        seen[rid] = p.name
        if rid in retired:
            out.append({"file": str(p), "line": 1, "snippet": rid,
                        "section": "(id)",
                        "message": "id %s 는 retired.txt 에 폐기로 적혀 있다" % rid})
        if not p.name.startswith(rid + "-"):
            out.append({"file": str(p), "line": 1, "snippet": p.name,
                        "section": "(id)",
                        "message": "파일명이 id %s 로 시작하지 않는다" % rid})
    return out
