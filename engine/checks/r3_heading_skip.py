"""R3 -- 헤딩 레벨 건너뜀."""
from _md import headings


def check(path, text):
    out, prev = [], None
    for line, level, title in headings(text):
        if prev is not None and level - prev >= 2:
            out.append({"line": line, "snippet": "#" * level + " " + title,
                        "message": "레벨 %d 다음에 레벨 %d 가 와서 %d단계를 건너뛴다"
                                   % (prev, level, level - prev)})
        prev = level
    return out
