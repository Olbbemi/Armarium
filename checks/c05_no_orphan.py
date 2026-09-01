"""C5 진입점에서 도달할 수 없는 마크다운 파일이 없다."""
import common

ID = "C5"
NAME = "고아 파일 없음"
FULL_ONLY = False


def entries(root):
    """도달 판정의 시작점. 각 스킬의 `SKILL.md` 다."""
    out = []
    for skill in common.skill_dirs(root):
        path = skill / "SKILL.md"
        if path.is_file():
            out.append(path)
    return out


def reachable(root, starts):
    """상대 링크를 따라가며 닿은 경로를 모은다.

    방문한 경로를 기억하므로 링크가 순환해도 끝난다. 저장소 밖으로 나가는 링크는
    따라가지 않는다. 그 링크 자체는 검사 C4 가 판정한다.
    """
    seen = set()
    queue = list(starts)
    while queue:
        path = queue.pop()
        key = path.resolve()
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            continue
        for target in common.links(path.read_text(encoding="utf-8")):
            if not target.endswith(".md"):
                continue
            nxt = path.parent / target
            if common.inside(root, nxt):
                queue.append(nxt)
    return seen


def targets(root):
    """도달해야 하는 파일. 진입점 자신은 뺀다."""
    starts = {p.resolve() for p in entries(root)}
    return [p for p in common.documents(root) if p.resolve() not in starts]


def check(root):
    seen = reachable(root, entries(root))
    out = []
    for path in targets(root):
        if path.resolve() not in seen:
            out.append(
                "%s -- 진입점에서 도달할 수 없다" % common.rel(root, path)
            )
    return out
