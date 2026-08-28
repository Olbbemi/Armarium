"""M9 -- 코어 순수성. 공용 문서가 특정 스킬 이름을 지목하는지 본다."""
from _md import body_lines


def check(path, text, ctx=None):
    names = ((ctx or {}).get("names") or {}).get("skill", [])
    out = []
    for i, line in body_lines(text):
        for n in names:
            if n in line:
                out.append({"line": i, "snippet": line.strip(),
                            "message": "공용 문서에 스킬 이름이 있다: %s" % n})
                break
    return out
