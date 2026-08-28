"""R9 -- 링크 대상 존재. 마크다운 링크가 가리키는 파일이 실재하는지 본다."""
import pathlib
import re

from _md import body_lines

LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP_PREFIX = ("http://", "https://", "mailto:", "#")


def check(path, text):
    here = pathlib.Path(path).parent
    out = []
    for i, line in body_lines(text):
        for m in LINK.finditer(line):
            target = m.group(1).split("#")[0]
            if not target or target.startswith(SKIP_PREFIX):
                continue
            if pathlib.Path(target).exists() or (here / target).exists():
                continue
            out.append({"line": i, "snippet": m.group(0),
                        "message": "링크가 가리키는 %s 가 없다" % target})
    return out
