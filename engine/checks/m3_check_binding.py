"""M3 -- mode 와 판정기 정합."""
import pathlib

ENGINE = pathlib.Path(__file__).resolve().parent.parent


def check(rules_dir, rules):
    out = []
    referenced, bases = set(), set()
    for r in rules:
        m, f = r["meta"], str(r["path"])
        base = pathlib.Path(r.get("checks_base") or ENGINE)
        bases.add(base)
        chk = m.get("check")
        if chk:
            p = base / chk
            referenced.add(p.resolve())
            if not p.exists():
                out.append({"file": f, "line": 1, "snippet": chk,
                            "section": "(frontmatter)",
                            "message": "check 가 가리키는 판정기 파일이 없다"})

    # 고아 검사는 이 규칙 셋이 쓰는 판정기로 좁힌다. 판정기 디렉토리는 여러 셋이
    # 공유하므로, 다른 셋의 판정기까지 고아로 세면 셋마다 서로를 결함으로 만든다.
    prefixes = {r["meta"]["id"][0].lower() for r in rules if r["meta"].get("id")}
    for base in sorted(bases):
        checks_dir = base / "checks"
        if not checks_dir.exists():
            continue
        for p in sorted(checks_dir.glob("*.py")):
            if p.name.startswith("_") or p.name[0] not in prefixes:
                continue
            if p.resolve() not in referenced:
                out.append({"file": str(p), "line": 1, "snippet": p.name,
                            "section": "(orphan)",
                            "message": "어느 규칙도 이 판정기를 가리키지 않는다"})
    return out
