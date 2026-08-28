"""M6 -- 인덱스 정합. README 의 생성 블록이 rules/ 실제와 같은지 본다."""
import pathlib

START = "<!-- rules-index:start -->"
END = "<!-- rules-index:end -->"


def render(rules):
    lines = ["| id | 항목 | mode | 대상 | severity |", "|---|---|---|---|---|"]
    for r in sorted(rules, key=lambda x: (x["meta"].get("group", ""), x["meta"].get("id", ""))):
        m = r["meta"]
        lines.append("| %s | %s | %s | %s | %s |" % (
            m.get("id", ""), m.get("title", ""), m.get("mode", ""),
            m.get("applies_to", ""), m.get("severity", "")))
    return "\n".join(lines)


def check(rules_dir, rules):
    readme = pathlib.Path(rules_dir) / "README.md"
    if not readme.exists():
        return [{"file": str(readme), "line": 1, "snippet": "README.md",
                 "section": "(index)", "message": "README.md 가 없다"}]
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return [{"file": str(readme), "line": 1, "snippet": START,
                 "section": "(index)", "message": "인덱스 블록 마커가 없다"}]
    cur = text.split(START, 1)[1].split(END, 1)[0].strip()
    want = render(rules).strip()
    if cur != want:
        return [{"file": str(readme), "line": 1, "snippet": "rules-index",
                 "section": "(index)", "autofixable": True,
                 "message": "인덱스가 실제 규칙과 다르다"}]
    return []


def fix(rules_dir, rules):
    """인덱스 블록을 다시 생성한다. 생성물이라 고칠 결과가 하나로 정해진다."""
    readme = pathlib.Path(rules_dir) / "README.md"
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        return []
    head, rest = text.split(START, 1)
    _old, tail = rest.split(END, 1)
    readme.write_text(head + START + "\n" + render(rules) + "\n" + END + tail,
                      encoding="utf-8")
    return ["%s 인덱스 갱신 -- 규칙 %d개" % (readme, len(rules))]
