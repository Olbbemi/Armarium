"""C4 상대 링크의 대상 파일이 저장소 안에 존재한다."""
import common

ID = "C4"
NAME = "링크 대상 존재"
FULL_ONLY = False


def check(root):
    out = []
    for path in common.documents(root):
        name = common.rel(root, path)
        text = path.read_text(encoding="utf-8")
        bad = common.link_syntax(text)
        if bad:
            for reason in bad:
                out.append("%s -- 허용하지 않는 링크 표기다. %s" % (name, reason))
            continue
        for target in common.links(text):
            resolved = path.parent / target
            if not common.inside(root, resolved):
                out.append(
                    "%s -- 링크 대상이 저장소 밖이다: %s" % (name, target)
                )
            elif not resolved.exists():
                out.append("%s -- 링크 대상이 없다: %s" % (name, target))
            elif not resolved.is_file():
                out.append(
                    "%s -- 링크 대상이 파일이 아니다: %s" % (name, target)
                )
    return out
