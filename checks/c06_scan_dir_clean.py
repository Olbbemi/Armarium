"""C6 스캔 디렉토리에 비등록물이 섞이지 않았다."""
import common

ID = "C6"
NAME = "스캔 디렉토리 정결"
FULL_ONLY = False


def check(root):
    out = []
    base = root / "skills"
    if not base.is_dir():
        return out
    for entry in sorted(base.iterdir()):
        if entry.is_file():
            out.append(
                "%s -- skills 바로 아래에 파일이 있다" % common.rel(root, entry)
            )
        elif entry.is_dir() and not (entry / "SKILL.md").is_file():
            out.append(
                "%s -- SKILL.md 가 없다" % common.rel(root, entry)
            )
    return out
