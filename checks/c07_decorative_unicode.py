"""C7 코드블록 밖에 장식용 유니코드가 없다."""
import common

ID = "C7"
NAME = "장식용 유니코드 금지"
FULL_ONLY = False

RANGES = (
    (0x2013, 0x2014, "en 대시와 em 대시"),
    (0x2018, 0x2019, "곡선 작은따옴표"),
    (0x201C, 0x201D, "곡선 큰따옴표"),
    (0x2022, 0x2022, "장식 불릿"),
    (0x2026, 0x2026, "말줄임표"),
    (0x00B7, 0x00B7, "가운뎃점"),
    (0x2190, 0x21FF, "화살표"),
    (0x2500, 0x257F, "박스드로잉"),
    (0x2713, 0x2718, "체크와 엑스"),
    (0x2600, 0x27BF, "기호와 장식"),
    (0x2B00, 0x2BFF, "화살표와 도형"),
    (0xFE0F, 0xFE0F, "이모지 변형 선택자"),
    (0x1F300, 0x1FAFF, "이모지"),
)


def classify(ch):
    code = ord(ch)
    for lo, hi, label in RANGES:
        if lo <= code <= hi:
            return label
    return None


def check(root):
    out = []
    for path in common.repo_markdown(root):
        text = common.outside_fence(path.read_text(encoding="utf-8"))
        for line_no, line in enumerate(text.splitlines(), 1):
            for ch in line:
                label = classify(ch)
                if label:
                    out.append(
                        "%s:%d -- %s (U+%04X)"
                        % (common.rel(root, path), line_no, label, ord(ch))
                    )
                    break
    return out
