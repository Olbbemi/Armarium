"""C10 매니페스트가 가리키는 경로가 실제로 존재한다."""
import common

ID = "C10"
NAME = "매니페스트 경로 존재"
FULL_ONLY = False


def targets(root):
    out = []
    codex = common.load_json(root / ".codex-plugin/plugin.json")
    if isinstance(codex, dict) and isinstance(codex.get("skills"), str):
        out.append((".codex-plugin/plugin.json", "skills", codex["skills"]))
    market = common.load_json(root / ".claude-plugin/marketplace.json")
    if isinstance(market, dict):
        for plugin in market.get("plugins") or []:
            source = plugin.get("source")
            if isinstance(source, str):
                out.append((".claude-plugin/marketplace.json", "source", source))
    return out


def check(root):
    out = []
    for where, field, value in targets(root):
        if not (root / value).exists():
            out.append("%s -- %s 가 가리키는 %s 가 없다" % (where, field, value))
    return out
