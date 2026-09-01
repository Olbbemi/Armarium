"""검사가 공유하는 도우미."""
import json
import re

FENCE = re.compile(r"```.*?```|~~~.*?~~~", re.S)
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
REF_DEF = re.compile(r"^\s*\[[^\]]+\]:\s*\S.*$", re.M)
FENCE_LINE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
FRONTMATTER = re.compile(r"\A---\n(.*?)\n---\n", re.S)
KEY = re.compile(r"^([A-Za-z][\w-]*):\s*(.*)$", re.M)

MANIFESTS = (
    ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
)


def is_fixture(root, path):
    """검사 대상 루트를 기준으로 픽스처 경로인지 본다.

    절대 경로로 보면 픽스처를 루트로 준 selftest 에서 모든 파일이
    걸러지므로 상대 경로로 판정한다.
    """
    try:
        parts = path.relative_to(root).parts
    except ValueError:
        parts = path.parts
    return "fixtures" in parts


def skill_dirs(root):
    base = root / "skills"
    if not base.is_dir():
        return []
    return sorted(d for d in base.iterdir() if d.is_dir())


def skill_markdown(root, skill_dir):
    return sorted(
        p for p in skill_dir.rglob("*.md") if not is_fixture(root, p)
    )


def skill_files(root, skill_dir):
    """검증 대상 파일. 생성물만 뺀다. 픽스처도 검증 대상이다."""
    return sorted(
        p
        for p in skill_dir.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )


def documents(root):
    """링크를 판정하는 문서. 스킬 안과 `standards/` 아래의 마크다운이다."""
    out = []
    for skill in skill_dirs(root):
        out.extend(skill_markdown(root, skill))
    base = root / "standards"
    if base.is_dir():
        out.extend(
            p for p in sorted(base.rglob("*.md")) if not is_fixture(root, p)
        )
    return out


def inside(root, path):
    """해석한 경로가 저장소 루트 안이면 True. 심볼릭 링크도 따라간다."""
    try:
        path.resolve().relative_to(root.resolve())
    except (ValueError, OSError, RuntimeError):
        return False
    return True


def repo_markdown(root):
    out = []
    for p in sorted(root.rglob("*.md")):
        if is_fixture(root, p) or ".git" in p.parts or p.is_symlink():
            continue
        out.append(p)
    return out


def frontmatter(path):
    """(키 목록, 값 사전) 을 돌려준다. 프론트매터가 없으면 (None, {})."""
    m = FRONTMATTER.match(path.read_text(encoding="utf-8"))
    if not m:
        return None, {}
    keys = []
    values = {}
    for k, v in KEY.findall(m.group(1)):
        keys.append(k)
        values[k] = v.strip()
    return keys, values


def outside_fence(text):
    return FENCE.sub("", text)


def inline_code(text):
    """인라인 코드를 걷어낸다.

    여는 백틱 런과 같은 길이의 런에서 닫는다. 닫히지 않으면 코드가 아니므로
    그대로 둔다.
    """
    out = []
    i = 0
    n = len(text)
    while i < n:
        if text[i] != "`":
            out.append(text[i])
            i += 1
            continue
        j = i
        while j < n and text[j] == "`":
            j += 1
        run = j - i
        close = -1
        k = j
        while k < n:
            if text[k] != "`":
                k += 1
                continue
            end = k
            while end < n and text[end] == "`":
                end += 1
            if end - k == run:
                close = end
                break
            k = end
        if close == -1:
            out.append(text[i:j])
            i = j
        else:
            i = close
    return "".join(out)


def outside_code(text):
    """코드 펜스와 인라인 코드를 걷어낸 본문.

    규격 문서는 표기 자체를 예시로 적는다. 코드로 감싼 예시를 실제 링크로 보면
    문서가 자기 규칙을 설명하지 못한다.

    펜스는 여는 구분자와 같은 문자이면서 길이가 같거나 긴 줄에서 닫는다. 들여쓰기
    코드는 목록의 이어지는 줄과 형식이 같아 처리하지 않는다. 저장소 문서는 코드를
    펜스나 인라인 백틱으로만 적는다.
    """
    out = []
    fence = None
    for line in text.splitlines():
        m = FENCE_LINE.match(line)
        if fence is None:
            if m:
                fence = m.group(1)
                continue
            out.append(line)
        elif (
            m
            and m.group(1)[0] == fence[0]
            and len(m.group(1)) >= len(fence)
            and not m.group(2).strip()
        ):
            fence = None
    return inline_code("\n".join(out))


def external(target):
    """저장소 상대 링크가 아닌 대상이면 True."""
    return target.strip("<>").startswith(
        ("http://", "https://", "#", "mailto:")
    )


def links(text):
    """상대 링크의 경로 부분. 앵커와 쿼리는 잘라 낸다."""
    out = []
    for target in LINK.findall(outside_code(text)):
        if external(target):
            continue
        path = target.split("#")[0].split("?")[0]
        if path:
            out.append(path)
    return out


def link_syntax(text):
    """허용하지 않는 링크 표기. 사유 문자열의 목록이다.

    표기를 인라인 하나로 고정하고 나머지는 위반으로 본다. 마크다운 문법을 넓게
    해석하면 경계가 끝없이 늘어난다. 저장소 상대 링크에만 적용한다.
    """
    body = outside_code(text)
    out = []
    for line in REF_DEF.findall(body):
        out.append("참조형 링크 정의: %s" % line.strip())
    for target in LINK.findall(body):
        if external(target):
            continue
        if target.startswith("<") or target.endswith(">"):
            out.append("꺾쇠 표기: %s" % target)
        elif "%" in target:
            out.append("퍼센트 인코딩: %s" % target)
    return out


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def rel(root, path):
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
