"""R8 -- 표 열 수."""
import re
from _md import body_lines

LIMIT = 5
SEP = re.compile(r"^\s*\|?[\s:|-]+\|[\s:|-]*$")


def check(path, text):
    out = []
    lines = list(body_lines(text))
    for idx, (line, raw) in enumerate(lines):
        if "|" not in raw or not SEP.match(raw) or "-" not in raw:
            continue
        cols = len([c for c in raw.strip().strip("|").split("|") if c.strip()])
        if cols > LIMIT:
            out.append({"line": line, "snippet": raw.strip()[:80],
                        "message": "표가 %d열로 상한 %d 을 넘는다" % (cols, LIMIT)})
    return out
