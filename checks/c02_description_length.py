"""C2 description 이 1024자 이하다."""
import common

ID = "C2"
NAME = "description 길이"
FULL_ONLY = False
LIMIT = 1024


def check(root):
    out = []
    for skill in common.skill_dirs(root):
        path = skill / "SKILL.md"
        if not path.is_file():
            continue
        _, values = common.frontmatter(path)
        text = values.get("description", "")
        if len(text) > LIMIT:
            out.append(
                "%s -- description 이 %d자로 %d자를 넘는다"
                % (common.rel(root, path), len(text), LIMIT)
            )
    return out
