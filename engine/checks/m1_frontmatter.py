"""M1 -- 규칙 파일 프론트매터."""
import re

REQUIRED = ("id", "group", "title", "mode", "applies_to", "severity", "why")
MODES = ("script", "hybrid")
SEVERITIES = ("error", "warn")
ID_RE = re.compile(r"^[A-Z]\d+$")


def check(rules_dir, rules):
    out = []
    for r in rules:
        m, f = r["meta"], str(r["path"])
        for k in REQUIRED:
            if not m.get(k):
                out.append({"file": f, "line": 1, "snippet": r["path"].name,
                            "section": "(frontmatter)",
                            "message": "필수 필드 %s 가 없거나 비어 있다" % k})
        if m.get("id") and not ID_RE.match(m["id"]):
            out.append({"file": f, "line": 1, "snippet": m["id"],
                        "section": "(frontmatter)",
                        "message": "id 는 대문자 한 글자 + 숫자여야 한다"})
        for k, allowed in (("mode", MODES), ("severity", SEVERITIES)):
            if m.get(k) and m[k] not in allowed:
                out.append({"file": f, "line": 1, "snippet": "%s: %s" % (k, m[k]),
                            "section": "(frontmatter)",
                            "message": "%s 값이 허용 목록 %s 밖이다" % (k, list(allowed))})
        if not m.get("check"):
            out.append({"file": f, "line": 1, "snippet": r["path"].name,
                        "section": "(frontmatter)",
                        "message": "check 필드가 없다. 판정기 없는 규칙은 규칙이 아니다"})
    return out
