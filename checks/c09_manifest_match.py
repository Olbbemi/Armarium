"""C9 매니페스트 세 곳의 name 과 version 이 일치한다."""
import common

ID = "C9"
NAME = "매니페스트 일치"
FULL_ONLY = False


def filled(value):
    """값이 문자열이고 공백만 있지 않으면 True."""
    return isinstance(value, str) and value.strip() != ""


def entry(root, rel_path):
    data = common.load_json(root / rel_path)
    if data is None:
        return None
    if "plugins" in data:
        plugins = data.get("plugins") or []
        if not plugins:
            return None
        first = plugins[0]
        return first.get("name"), first.get("version")
    return data.get("name"), data.get("version")


def check(root):
    out = []
    found = {}
    for rel_path in common.MANIFESTS:
        if not (root / rel_path).is_file():
            out.append("%s -- 매니페스트가 없다" % rel_path)
            continue
        value = entry(root, rel_path)
        if value is None:
            out.append("%s -- name 과 version 을 읽을 수 없다" % rel_path)
            continue
        if not filled(value[0]):
            out.append("%s -- name 이 비었다" % rel_path)
            continue
        if not filled(value[1]):
            out.append("%s -- version 이 비었다" % rel_path)
            continue
        found[rel_path] = value
    if len(found) > 1:
        names = {v[0] for v in found.values()}
        versions = {v[1] for v in found.values()}
        if len(names) > 1:
            out.append("name 이 서로 다르다: %s" % sorted(names))
        if len(versions) > 1:
            out.append("version 이 서로 다르다: %s" % sorted(versions))
    return out
