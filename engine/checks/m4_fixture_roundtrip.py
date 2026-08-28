"""M4 -- 픽스처 왕복 검증. 규칙의 픽스처를 그 규칙의 판정기에 먹여 본다.

픽스처는 두 자리에 있다. 코드블록에 담기는 것은 규칙 파일 안에 두고, 규칙 셋 하나나
아주 긴 파일처럼 코드블록으로 못 담는 것은 픽스처 디렉토리에 둔다. 둘 다 왕복한다.
"""
import importlib.util, pathlib, sys

from _call import call_check

ENGINE = pathlib.Path(__file__).resolve().parent.parent
if str(ENGINE) not in sys.path:
    sys.path.insert(0, str(ENGINE))
from verify import load_rules  # noqa: E402

_cache = {}


def _load(path):
    key = str(path)
    if key in _cache:
        return _cache[key]
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _cache[key] = mod
    return mod


def _flag(f, snippet, message):
    return {"file": f, "line": 1, "snippet": snippet,
            "section": "(fixture)", "message": message}


def _run(rule, mod, target, ctx):
    """픽스처 하나를 판정기에 먹인다. 대상 단위는 그 규칙의 것을 따른다."""
    if rule.get("granularity") == "dir":
        kinds = (ctx or {}).get("kinds", {})
        sub = load_rules(target, kinds, rule.get("checks_base"))
        return call_check(mod.check, str(target), sub, ctx=ctx)
    hits = []
    for f in sorted(pathlib.Path(target).rglob("*.md")):
        hits += call_check(mod.check, str(f), f.read_text(encoding="utf-8"), ctx=ctx)
    return hits


def _inline(rule, mod, f, ctx):
    out = []
    for kind, block in rule["fixtures"]:
        try:
            hits = call_check(mod.check, "<fixture>", block + "\n", ctx=ctx)
        except Exception as e:
            out.append(_flag(f, kind, "픽스처 실행 실패: %s" % e))
            continue
        if kind == "fail" and not hits:
            out.append(_flag(f, block[:60], "fail 픽스처인데 판정기가 아무것도 검출하지 못했다"))
        if kind == "pass" and hits:
            out.append(_flag(f, block[:60],
                             "pass 픽스처인데 판정기가 %d건을 검출했다" % len(hits)))
    return out


def _from_dir(rule, mod, f, root, ctx):
    out = []
    for kind in ("fail", "pass"):
        d = root / kind
        if not d.is_dir():
            out.append(_flag(f, str(d), "%s 픽스처 디렉토리가 없다" % kind))
            continue
        try:
            hits = _run(rule, mod, d, ctx)
        except Exception as e:
            out.append(_flag(f, str(d), "픽스처 실행 실패: %s: %s" % (type(e).__name__, e)))
            continue
        if kind == "fail" and not hits:
            out.append(_flag(f, str(d), "fail 픽스처인데 판정기가 아무것도 검출하지 못했다"))
        if kind == "pass" and hits:
            out.append(_flag(f, str(d),
                             "pass 픽스처인데 판정기가 %d건을 검출했다" % len(hits)))
    return out


def check(rules_dir, rules, ctx=None):
    out = []
    for r in rules:
        m, f = r["meta"], str(r["path"])
        inline = r["fixtures"] and r.get("granularity") == "file"
        fx = m.get("fixtures")
        if not inline and not fx:
            continue
        p = pathlib.Path(r.get("checks_base") or ENGINE) / m.get("check", "")
        if not p.exists():
            continue
        try:
            mod = _load(p)
        except Exception as e:
            out.append(_flag(f, m.get("check", ""), "판정기 로드 실패: %s" % e))
            continue
        if inline:
            out += _inline(r, mod, f, ctx)
        if fx:
            out += _from_dir(r, mod, f, pathlib.Path(r.get("checks_base") or ENGINE) / fx, ctx)
    return out
