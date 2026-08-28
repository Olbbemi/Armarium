"""R5 -- 중첩 리스트 깊이 상한."""
import re
from _md import body_lines

LIMIT = 3
ITEM = re.compile(r"^(\s*)([-*+]|\d+\.)\s+")


def check(path, text):
    out = []
    for line, raw in body_lines(text):
        m = ITEM.match(raw)
        if not m:
            continue
        indent = len(m.group(1).expandtabs(4))
        depth = indent // 2 + 1
        if depth > LIMIT:
            out.append({"line": line, "snippet": raw.strip()[:80],
                        "message": "리스트 중첩 깊이 %d 가 상한 %d 을 넘는다" % (depth, LIMIT)})
    return out
