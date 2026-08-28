"""R7 -- 문단 문장 수."""
import re
from _md import body_lines

LIMIT = 5
SPLIT = re.compile(r"(?<=[.!?。])\s+")
SKIP = re.compile(r"^\s*(\||[-*+]\s|\d+\.\s|#|>)")


def check(path, text):
    out, buf, start = [], [], None
    lines = list(body_lines(text))

    def flush():
        if not buf:
            return
        joined = " ".join(buf)
        n = len([s for s in SPLIT.split(joined) if s.strip()])
        if n > LIMIT:
            out.append({"line": start, "snippet": joined[:80],
                        "message": "문단이 %d문장으로 상한 %d 을 넘는다" % (n, LIMIT)})

    for line, raw in lines:
        if not raw.strip() or SKIP.match(raw):
            flush()
            buf, start = [], None
            continue
        if start is None:
            start = line
        buf.append(raw.strip())
    flush()
    return out
