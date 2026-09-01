"""C3 name 이 디렉토리 이름과 같다."""
import common

ID = "C3"
NAME = "name 과 디렉토리명 일치"
FULL_ONLY = False


def check(root):
    out = []
    for skill in common.skill_dirs(root):
        path = skill / "SKILL.md"
        if not path.is_file():
            continue
        _, values = common.frontmatter(path)
        name = values.get("name", "")
        if name != skill.name:
            out.append(
                "%s -- name 이 %r 인데 디렉토리는 %r 이다"
                % (common.rel(root, path), name, skill.name)
            )
    return out
