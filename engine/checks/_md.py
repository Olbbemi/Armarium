"""판정기 공용 헬퍼. 마크다운 줄을 훑어 코드블록 구간을 표시한다.

판정 공통 규약(core.md 소유)에 따라 판정기는 코드블록 안을 대상에서 뺀다.
픽스처는 코드블록 안에 두므로 이 한 가지 규칙으로 함께 걸러진다.
"""
import re

FENCE = re.compile(r"^\s*(```|~~~)")


def scan(text):
    """(lineno, line, in_code) 를 순서대로 낸다. 펜스 줄 자체도 in_code 로 본다."""
    in_code = False
    for i, line in enumerate(text.splitlines(), 1):
        if FENCE.match(line):
            in_code = not in_code
            yield i, line, True
            continue
        yield i, line, in_code


def body_lines(text, skip_code=True):
    """판정 대상이 되는 줄만 (lineno, line) 으로 낸다."""
    for i, line, in_code in scan(text):
        if skip_code and in_code:
            continue
        yield i, line


def headings(text):
    """(lineno, level, title) 을 낸다. 코드블록 안의 # 는 세지 않는다."""
    for i, line in body_lines(text):
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            yield i, len(m.group(1)), m.group(2).strip()
