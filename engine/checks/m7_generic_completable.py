"""M7 -- generic 어댑터 완주. 어댑터 기능에 기대는 단계를 후보로 뽑는다."""
import pathlib

from _md import body_lines

ENGINE = pathlib.Path(__file__).resolve().parent.parent
GENERIC = ENGINE.parent / "adapters" / "generic.md"
SECTION = "제공하지 않는"


def features():
    """generic 어댑터가 제공하지 않는다고 선언한 기능 이름을 읽는다."""
    if not GENERIC.exists():
        return []
    out, inside = [], False
    for line in GENERIC.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            inside = SECTION in line
            continue
        if not inside or not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] == "기능" or set(cells[0]) <= set("-: "):
            continue
        out.append(cells[0])
    return out


def check(path, text):
    feats = features()
    out = []
    for i, line in body_lines(text):
        for f in feats:
            if f in line:
                out.append({
                    "line": i, "snippet": line.strip(),
                    "message": "'%s' 에 기대는 단계인지 확정이 필요하다" % f,
                    "question": "'%s' 없이 이 단계를 넘어갈 수 있는가" % f,
                })
                break
    return out
