"""C8 커스텀 태그가 없다."""
import re

import common

ID = "C8"
NAME = "커스텀 태그 금지"
FULL_ONLY = False
TAG = re.compile(r"</?[A-Z][A-Z0-9_-]*(?:\s[^>]*)?/?>")


def check(root):
    out = []
    for path in common.repo_markdown(root):
        text = common.outside_fence(path.read_text(encoding="utf-8"))
        for line_no, line in enumerate(text.splitlines(), 1):
            found = TAG.findall(line)
            if found:
                out.append(
                    "%s:%d -- 커스텀 태그: %s"
                    % (common.rel(root, path), line_no, " ".join(found))
                )
    return out
