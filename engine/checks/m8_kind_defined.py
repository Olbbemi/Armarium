"""M8 -- 대상 종류 정의. 규칙이 가리키는 종류가 매니페스트에 있는지 본다."""


def check(rules_dir, rules):
    out = []
    for r in rules:
        if r.get("granularity"):
            continue
        m = r["meta"]
        out.append({"file": str(r["path"]), "line": 1,
                    "snippet": "applies_to: %s" % m.get("applies_to", ""),
                    "section": "(frontmatter)",
                    "message": "applies_to 가 매니페스트에 없는 종류를 가리킨다"})
    return out
