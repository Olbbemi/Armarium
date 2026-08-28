"""M2 -- 규칙 본문 고정 섹션."""
EXPECTED = ["판정 기준", "수정 지침", "예시"]


def check(rules_dir, rules):
    out = []
    for r in rules:
        f = str(r["path"])
        titles = [t for t, _ in r["sections"]]
        if titles != EXPECTED:
            out.append({"file": f, "line": 1, "snippet": " / ".join(titles) or "(없음)",
                        "section": "(sections)",
                        "message": "고정 섹션이 %s 여야 하는데 %s 이다" % (EXPECTED, titles)})
            continue
        for t, body in r["sections"]:
            if not body.strip():
                out.append({"file": f, "line": 1, "snippet": t,
                            "section": t,
                            "message": "섹션 %s 가 비어 있다" % t})
    return out
