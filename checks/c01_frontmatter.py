"""C1 프론트매터에 name 과 description 외의 키가 없다."""
import common

ID = "C1"
NAME = "프론트매터 키"
FULL_ONLY = False
ALLOWED = {"name", "description"}


def check(root):
    out = []
    for skill in common.skill_dirs(root):
        path = skill / "SKILL.md"
        if not path.is_file():
            continue
        keys, _ = common.frontmatter(path)
        if keys is None:
            out.append("%s -- 프론트매터가 없다" % common.rel(root, path))
            continue
        missing = [k for k in sorted(ALLOWED) if k not in keys]
        if missing:
            out.append(
                "%s -- 빠진 키: %s"
                % (common.rel(root, path), ", ".join(missing))
            )
        extra = [k for k in keys if k not in ALLOWED]
        if extra:
            out.append(
                "%s -- 허용되지 않은 키: %s"
                % (common.rel(root, path), ", ".join(extra))
            )
    return out
