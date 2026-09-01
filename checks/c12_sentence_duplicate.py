"""C12 같은 문장이 두 번 이상 나타나지 않는다.

판단하고 처리하지 않은 형식이 셋 있다. 저장소에 그 형식이 없어 지금은 아무것도
놓치지 않는다. 실제 사례가 생기면 그때 고친다.

  들여쓰기 코드 블록    목록의 이어지는 줄과 형식이 같다. 제외하면 목록 내용이
                       통째로 빠져 미탐이 커진다
  선행 파이프 없는 표    행이 한 블록으로 합쳐진다. 오탐이 아니라 미탐이다
  별표 구분선           길이 문턱에서 걸러진다
"""
import re

import common

ID = "C12"
NAME = "문장 중복 금지"
FULL_ONLY = False

MIN_LENGTH = 12
BOLD = re.compile(r"\*\*(.*?)\*\*")
ATX = re.compile(r"^\s*#")
SETEXT = re.compile(r"^\s*(?:=+|-+)\s*$")
MARKER = re.compile(r"^\s*(?:[-*+]\s+|\d+[.)]\s+)")
SPLIT = re.compile(r"(?<=[.!?])\s+")


def body(text):
    """프론트매터를 걷어낸 본문."""
    m = common.FRONTMATTER.match(text)
    return text[m.end():] if m else text


def blocks(text):
    """줄을 블록으로 묶는다.

    빈 줄, 목록 항목, 표 행에서 블록이 끊긴다. 그 밖의 줄은 앞 블록에 이어
    붙인다. 줄바꿈으로 갈린 한 문장을 조각으로 자르지 않기 위해서다.
    """
    lines = common.outside_fence(body(text)).splitlines()
    out = []
    current = []
    for i, line in enumerate(lines):
        nxt = lines[i + 1] if i + 1 < len(lines) else ""
        heading = ATX.match(line) or SETEXT.match(line)
        if line.strip() and SETEXT.match(nxt):
            heading = True
        if not line.strip() or heading:
            if current:
                out.append(" ".join(current))
                current = []
            continue
        stripped = BOLD.sub("", line)
        if MARKER.match(stripped) or stripped.lstrip().startswith("|"):
            if current:
                out.append(" ".join(current))
                current = []
            stripped = MARKER.sub("", stripped).replace("|", " ")
        current.append(stripped.strip())
    if current:
        out.append(" ".join(current))
    return out


def sentences(text):
    """코드블록 밖의 문장. 제목만 뺀다.

    목록과 표도 대상이다. 항목과 셀에도 함께 고쳐야 하는 사실이 들어간다.
    """
    for block in blocks(text):
        for part in SPLIT.split(block):
            part = " ".join(part.split()).strip(" -")
            if len(part) >= MIN_LENGTH:
                yield part


def check(root):
    seen = {}
    for path in common.repo_markdown(root):
        text = path.read_text(encoding="utf-8")
        for sentence in sentences(text):
            seen.setdefault(sentence, []).append(common.rel(root, path))
    out = []
    for sentence, places in sorted(seen.items()):
        if len(places) < 2:
            continue
        where = sorted(set(places))
        if len(where) == 1:
            out.append(
                "%s 안에 같은 문장이 %d번 있다: %s"
                % (where[0], len(places), sentence)
            )
        else:
            out.append(
                "같은 문장이 %s 에 있다: %s" % (", ".join(where), sentence)
            )
    return out
