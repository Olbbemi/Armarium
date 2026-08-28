"""R6 -- 문장 길이."""
import re
from _md import body_lines

LIMIT = 100
SPLIT = re.compile(r"(?<=[.!?。])\s+")
SKIP = re.compile(r"^\s*(\||[-*+]\s|\d+\.\s|#|>)")


def check(path, text):
    out = []
    for line, raw in body_lines(text):
        if not raw.strip() or SKIP.match(raw):
            continue
        for s in SPLIT.split(raw.strip()):
            if len(s) > LIMIT:
                out.append({"line": line, "snippet": s[:80],
                            "message": "문장이 %d자로 상한 %d 을 넘는다" % (len(s), LIMIT)})
    return out
