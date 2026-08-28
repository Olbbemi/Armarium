"""R2 -- 헤딩 깊이 상한."""
from _md import headings

LIMIT = 3


def check(path, text):
    out = []
    for line, level, title in headings(text):
        if level > LIMIT:
            out.append({"line": line, "snippet": "#" * level + " " + title,
                        "message": "헤딩 깊이 %d 가 상한 %d 을 넘는다" % (level, LIMIT)})
    return out
