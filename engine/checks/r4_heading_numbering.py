"""R4 -- 형제 헤딩 번호 일관성."""
import re
from _md import headings

NUMBERED = re.compile(r"^\d+\.\s")


def check(path, text):
    groups, stack = {}, []
    for line, level, title in headings(text):
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else "(root)"
        groups.setdefault((parent, level), []).append((line, title))
        stack.append((level, title))

    out = []
    for (_parent, level), items in groups.items():
        if len(items) < 2:
            continue
        numbered = [bool(NUMBERED.match(t)) for _l, t in items]
        if any(numbered) and not all(numbered):
            for (line, title), has in zip(items, numbered):
                if not has:
                    out.append({"line": line, "snippet": "#" * level + " " + title,
                                "message": "형제 헤딩 중 일부만 번호를 가져 이 헤딩만 번호가 없다"})
    return out
