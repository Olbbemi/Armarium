"""C11 검증 이력이 필수 대상마다 있고 현재 파일의 최신 해시와 일치한다."""
import hashlib
import re
from pathlib import PurePosixPath

import common

ID = "C11"
NAME = "검증 이력 일치"
FULL_ONLY = True


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def required(root):
    """저장소 구조에서 검증 단위를 산출한다.

    기록 파일에서 찾으면 기록을 안 만든 대상이 조용히 통과한다.
    """
    out = []
    for name in ("standards/skills", "checks"):
        if (root / name).is_dir():
            out.append(name)
    for skill in common.skill_dirs(root):
        out.append("skills/" + skill.name)
    return out


def normal(value):
    """저장소 안의 정규화된 상대 디렉토리면 그 값을, 아니면 None 을 준다.

    정규형과 글자까지 같아야 한다. `checks/` 처럼 뜻이 같아도 표기가 다르면
    기록마다 다른 문자열이 남아 겹침 판정이 흔들린다.
    """
    if not isinstance(value, str) or not value:
        return None
    if value.startswith("/") or "\\" in value:
        return None
    parts = PurePosixPath(value).parts
    if not parts or ".." in parts or "." in parts:
        return None
    canonical = "/".join(parts)
    return canonical if canonical == value else None


VERIFIER = ("claude", "codex")
DATE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def shaped_round(round_):
    """한 회차가 `CLAUDE.md` 검증 이력 절의 형식이면 None, 아니면 사유를 준다."""
    if not isinstance(round_, dict):
        return "회차가 객체가 아니다"
    for key in ("verifier", "at", "files", "items", "notes"):
        if key not in round_:
            return "회차에 %s 가 없다" % key
    if round_["verifier"] not in VERIFIER:
        return "verifier 가 claude 나 codex 가 아니다"
    if not isinstance(round_["at"], str) or not DATE.match(round_["at"]):
        return "at 이 YYYY-MM-DD 가 아니다"
    if not isinstance(round_["notes"], str):
        return "notes 가 문자열이 아니다"
    if not isinstance(round_["items"], dict):
        return "items 가 객체가 아니다"
    files = round_["files"]
    if not isinstance(files, dict):
        return "files 가 객체가 아니다"
    for name, value in files.items():
        if not isinstance(name, str) or not name:
            return "files 의 경로가 문자열이 아니다"
        if normal(name) is None:
            return "files 의 경로가 target 기준 상대 경로가 아니다: %s" % name
        if not isinstance(value, str) or not SHA256.match(value):
            return "files 의 해시가 sha256 이 아니다: %s" % name
    return None


def shaped(record):
    """기록이 정해진 형식이면 None, 아니면 사유를 준다."""
    if not isinstance(record, dict):
        return "최상위가 객체가 아니다"
    rounds = record.get("verifications")
    if rounds is None:
        return "verifications 가 없다"
    if not isinstance(rounds, list):
        return "verifications 가 배열이 아니다"
    for round_ in rounds:
        bad = shaped_round(round_)
        if bad is not None:
            return bad
    return None


def overlaps(a, b):
    return a == b or a.startswith(b + "/") or b.startswith(a + "/")


def records(root, need):
    """(대상 -> 기록) 과 문제 목록.

    `need` 는 저장소 구조에서 산출한 필수 단위다. 그 밖의 target 은 오타이거나
    지난 구조의 잔재이므로 위반으로 본다. 단위를 늘리려면 `required` 를 고친다.
    """
    out = {}
    problems = []
    base = root / "verifications"
    if not base.is_dir():
        return out, problems
    for path in sorted(base.glob("*.json")):
        name = common.rel(root, path)
        record = common.load_json(path)
        if record is None:
            problems.append("%s -- 읽을 수 없다" % name)
            continue
        bad = shaped(record)
        if bad is not None:
            problems.append("%s -- 기록 형식이 아니다: %s" % (name, bad))
            continue
        target = normal(record.get("target"))
        if target is None:
            problems.append("%s -- target 이 저장소 안의 상대 경로가 아니다" % name)
            continue
        if target in out:
            problems.append("%s -- target 이 다른 기록과 같다: %s" % (name, target))
            continue
        overlap = next((o for o in out if overlaps(target, o)), None)
        if overlap is not None:
            problems.append(
                "%s -- target 이 다른 기록과 겹친다: %s" % (name, overlap)
            )
            continue
        base_dir = root / target
        if not base_dir.is_dir():
            problems.append("%s -- target 이 디렉토리가 아니다: %s" % (name, target))
            continue
        if not common.inside(root, base_dir):
            problems.append("%s -- target 이 저장소 밖을 가리킨다: %s" % (name, target))
            continue
        if target not in need:
            problems.append("%s -- 검증 단위가 아닌 target 이다: %s" % (name, target))
            continue
        out[target] = record
    return out, problems


def latest(record, rel_path):
    value = None
    for round_ in record.get("verifications") or []:
        files = round_.get("files") or {}
        if rel_path in files:
            value = files[rel_path]
    return value


def files(base):
    return sorted(
        p
        for p in base.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
    )


def check(root):
    need = required(root)
    found, out = records(root, need)
    for target in need:
        record = found.get(target)
        if record is None:
            out.append("%s -- 검증 이력이 없다" % target)
            continue
        base = root / target
        for path in files(base):
            name = common.rel(root, path)
            if not common.inside(root, path):
                out.append("%s -- 저장소 밖을 가리킨다" % name)
                continue
            rel_path = str(path.relative_to(base))
            recorded = latest(record, rel_path)
            if recorded is None:
                out.append("%s -- 검증받은 적이 없다" % name)
            elif recorded != digest(path):
                out.append("%s -- 검증 후 내용이 바뀌었다" % name)
    return out
