"""표본 판정기. 표본이라는 말이 있으면 검출한다."""


def check(path, text):
    return [{"line": i, "snippet": line.strip(), "message": "표본이다"}
            for i, line in enumerate(text.splitlines(), 1) if "표본" in line]
