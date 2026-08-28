#!/usr/bin/env python3
"""규칙 데이터를 읽어 판정기를 실행하고 결과를 JSON 으로 낸다.

사용:
  verify.py [--manifest verify.json] [--path <접두사>]
            [--checks <dir>] [--json <out>] [--out-dir <dir>] [--verdicts <json>]

무엇을 검사할지는 사람이 짝지어 주지 않는다. 규칙은 `applies_to` 로 대상의 종류만 선언하고,
그 종류가 어느 경로인지는 매니페스트가 갖는다. 규칙이 경로를 모르므로 다른 저장소에서
같은 규칙을 매니페스트만 바꿔 쓴다.

--out-dir 를 주면 회차를 보관하고 직전 회차와 비교한다. 비교 결과가 루프의 진행 판정이다.
--verdicts 는 hybrid 규칙의 후보에 대한 실행 모델의 확정을 받는다.

종료 코드: 0 통과, 1 결함 있음, 2 헛돎(진전 없는 회차가 두 번 연속), 3 미확정 후보 있음.

판정 기준은 이 파일이 갖지 않는다. rules/ 가 유일한 원본이고 여기는 실행 엔진이다.
"""
import argparse, hashlib, importlib.util, json, pathlib, re, sys

ENGINE_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ENGINE_DIR))
sys.path.insert(0, str(ENGINE_DIR / "checks"))
from _call import DEFAULT_TIMEOUT, call_check, has_timeout  # noqa: E402
import render  # noqa: E402
SKIP_FILES = {"README.md"}

FIELDS_REQUIRED = ("id", "group", "title", "mode", "applies_to", "severity", "why")
OPTIONAL_FIELDS = ("fixtures",)
MODES = ("script", "hybrid")
SEVERITIES = ("error", "warn")


def parse_frontmatter(text):
    """--- 로 감싼 앞머리를 key: value 로 읽는다. YAML 서브셋만 지원한다."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    meta = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            continue
        k, v = line.split(":", 1)
        meta[k.strip()] = v.strip()
    return meta, text[end + 5:]


def split_sections(body):
    """## 헤딩 단위로 본문을 자른다. 코드블록 안의 ## 는 헤딩이 아니다."""
    out, cur, buf, in_code = [], None, [], False
    for line in body.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            in_code = not in_code
        if line.startswith("## ") and not in_code:
            if cur is not None:
                out.append((cur, "\n".join(buf).strip()))
            cur, buf = line[3:].strip(), []
        else:
            buf.append(line)
    if cur is not None:
        out.append((cur, "\n".join(buf).strip()))
    return out


FIXTURE_RE = re.compile(r"<!--\s*case:\s*(fail|pass)\s*-->")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


def parse_fixtures(example_text):
    """예시 섹션에서 <!-- case: fail|pass --> 바로 뒤 코드블록 본문을 뽑는다.

    픽스처를 코드블록에 두는 이유는 본문이 마크다운이기 때문이다. 감싸지 않으면
    픽스처 안의 헤딩이 이 파일의 헤딩으로 세어져 규칙이 자기 예시에 걸린다.
    """
    lines = example_text.splitlines()
    fixtures, i = [], 0
    while i < len(lines):
        m = FIXTURE_RE.search(lines[i])
        if not m:
            i += 1
            continue
        kind, i = m.group(1), i + 1
        while i < len(lines) and not lines[i].strip():
            i += 1
        if i >= len(lines) or not FENCE_RE.match(lines[i]):
            i += 1
            continue
        i += 1
        buf = []
        while i < len(lines) and not FENCE_RE.match(lines[i]):
            buf.append(lines[i])
            i += 1
        i += 1
        if buf:
            fixtures.append((kind, "\n".join(buf)))
    return fixtures


def load_rules(rules_dir, kinds=None, checks_base=None):
    """규칙 디렉토리를 구조화해 읽는다.

    kinds 를 주면 각 규칙에 granularity 를 붙인다. 판정기가 매니페스트를 직접 읽지 않고도
    대상 단위를 알게 하려는 것이다. 붙지 않으면 그 규칙의 applies_to 가 매니페스트에 없다.

    checks_base 는 그 규칙 셋의 판정기가 놓인 자리다. 공용 규칙은 엔진 아래, 스킬 고유 규칙은
    그 스킬 아래에 둔다. 규칙마다 달고 다녀야 판정기를 부르는 쪽이 셋을 구분하지 않아도 된다.
    """
    rules = []
    for path in sorted(pathlib.Path(rules_dir).glob("*.md")):
        if path.name in SKIP_FILES:
            continue
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        sections = split_sections(body)
        sec = dict(sections)
        gran = (kinds or {}).get(meta.get("applies_to"), {}).get("granularity")
        rules.append({
            "path": path,
            "meta": meta,
            "granularity": gran,
            "checks_base": str(checks_base or ENGINE_DIR),
            "sections": sections,
            "criteria": sec.get("판정 기준", ""),
            "fix": sec.get("수정 지침", ""),
            "example": sec.get("예시", ""),
            "fixtures": parse_fixtures(sec.get("예시", "")),
        })
    return rules


_loaded = {}


def load_checker(base_dir, rel):
    """check 필드가 가리키는 판정기 모듈을 불러온다."""
    p = pathlib.Path(base_dir) / rel
    if not p.exists():
        return None
    key = str(p)
    if key in _loaded:
        return _loaded[key]
    if str(p.parent) not in sys.path:
        sys.path.insert(0, str(p.parent))
    spec = importlib.util.spec_from_file_location(p.stem, p)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    _loaded[key] = mod
    return mod


def section_of(text, line_no):
    """그 줄이 속한 가장 가까운 헤딩 제목을 찾는다."""
    cur = ""
    for i, line in enumerate(text.splitlines(), 1):
        if i > line_no:
            break
        if line.startswith("#"):
            cur = line.lstrip("#").strip()
    return cur or "(root)"


def slug(s):
    s = re.sub(r"[^\w가-힣]+", "-", s).strip("-").lower()
    return s[:40] or "root"


def finding_id(rule_id, path, section, snippet):
    """회차 사이에 같은 결함을 같은 것으로 알아보게 하는 id.

    파일 경로를 해시에 넣는다. 같은 문장이 두 파일에 있으면 서로 다른 결함이고,
    빼면 한쪽 확정이 다른 쪽까지 덮는다.
    """
    key = "%s|%s" % (path or "", snippet.strip())
    h = hashlib.sha256(key.encode("utf-8")).hexdigest()[:8]
    return "%s:%s:%s" % (rule_id, slug(section), h)


def first_sentence(text):
    """여러 줄에 걸친 지침에서 첫 문장을 뽑는다. 줄에서 자르면 문장이 중간에 끊긴다."""
    flat = " ".join(l.strip() for l in text.splitlines() if l.strip())
    head = flat.split(". ")[0]
    return head if head.endswith(".") or not flat else head + "."


def make_finding(rule, path, raw):
    line = raw.get("line", 0)
    snippet = raw.get("snippet", "")
    section = raw.get("section") or (section_of(path.read_text(encoding="utf-8"), line)
                                     if path and path.exists() else "(root)")
    return {
        "id": finding_id(rule["meta"]["id"], str(path) if path else "",
                         section, snippet or str(line)),
        "rule": rule["meta"]["id"],
        "severity": rule["meta"].get("severity", "warn"),
        "detected_by": "script",
        "location": {"file": str(path) if path else None, "section": section,
                     "line": line, "snippet": snippet[:200]},
        "message": raw.get("message", ""),
        "fix": {"suggestion": first_sentence(rule["fix"]) if rule["fix"] else "",
                "autofixable": raw.get("autofixable", False)},
    }


def load_verdicts(path):
    """hybrid 후보에 대한 확정을 읽는다. {finding_id: {verdict, evidence}} 형식."""
    if not path:
        return {}
    p = pathlib.Path(path)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def apply_verdict(finding, verdicts):
    """후보 하나에 확정을 적용한다. ('drop'|'defect'|'pending', finding) 을 낸다.

    근거가 비면 확정으로 세지 않는다. 판정했다는 표시만으로 통과시키면
    후보를 훑기만 하고 넘어간 것과 구분되지 않는다.
    """
    v = verdicts.get(finding["id"]) or {}
    verdict = v.get("verdict")
    evidence = (v.get("evidence") or "").strip()
    finding["detected_by"] = "hybrid"
    if not evidence or verdict not in ("ok", "defect"):
        finding["pending"] = True
        return "pending", finding
    finding["evidence"] = evidence
    return ("drop" if verdict == "ok" else "defect"), finding


def stale_verdicts(verdicts, seen_ids):
    """확정은 있는데 이번에 후보로 나오지 않은 id 를 찾는다.

    미확정을 통과로 세지 않는 것과 같은 이유로, 대상이 사라진 확정도 남겨두지 않는다.
    남겨두면 무엇을 위한 확정인지 알 수 없게 되고 그 파일을 아무도 못 믿는다.
    """
    return sorted(set(verdicts) - set(seen_ids))


def drop_verdicts(path, ids):
    """낡은 확정을 지운다. 무엇을 지울지는 판단이 아니라 대조로 정해진다."""
    p = pathlib.Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    for k in ids:
        data.pop(k, None)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return "낡은 확정 %d건 지움: %s" % (len(ids), p)


def load_previous(out_dir):
    """직전 회차 보고서를 읽는다. 없으면 None."""
    runs = pathlib.Path(out_dir) / "runs"
    if not runs.exists():
        return None
    files = sorted(runs.glob("*.json"))
    if not files:
        return None
    return json.loads(files[-1].read_text(encoding="utf-8"))


def compute_delta(prev, findings):
    """직전 회차와 비교해 resolved / persisted / new 로 가른다."""
    cur_ids = {f["id"] for f in findings}
    if prev is None:
        return {"first_run": True, "resolved": [], "persisted": [], "new": sorted(cur_ids)}
    prev_ids = {f["id"] for f in prev.get("findings", [])}
    return {"first_run": False,
            "resolved": sorted(prev_ids - cur_ids),
            "persisted": sorted(prev_ids & cur_ids),
            "new": sorted(cur_ids - prev_ids)}


def stall_streak(prev, delta):
    """진전 없는 회차가 몇 번 연속인지 센다.

    한 회차 헛짚는 것은 흔하므로 즉시 멈추지 않는다. 두 회차 연속이면 멈춘다.
    """
    if prev is None or delta["first_run"] or not delta["persisted"]:
        return 0
    no_progress = not delta["resolved"] and not delta["new"]
    if not no_progress:
        return 0
    return prev.get("stall_streak", 0) + 1


STALL_LIMIT = 2


def next_run_seq(out_dir):
    runs = pathlib.Path(out_dir) / "runs"
    runs.mkdir(parents=True, exist_ok=True)
    return len(list(runs.glob("*.json"))) + 1


def save_run(out_dir, report):
    """보고서를 현재본과 회차 이력으로 저장한다. 회차 번호는 이미 report 에 있다."""
    out = pathlib.Path(out_dir)
    blob = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    (out / "runs" / ("%03d.json" % report["run"])).write_text(blob, encoding="utf-8")
    (out / "report.json").write_text(blob, encoding="utf-8")


def normalize_rulesets(man):
    """규칙 셋 항목을 {path, checks} 로 고른다. 문자열이면 판정기는 엔진 아래에 있다."""
    out = []
    for item in man.get("rulesets", []):
        if isinstance(item, str):
            out.append({"path": item, "checks": str(ENGINE_DIR)})
        else:
            out.append({"path": item["path"],
                        "checks": item.get("checks", str(ENGINE_DIR))})
    return out


def resolve_kinds(man):
    """종류별 경로를 확정한다. `from_rulesets` 인 종류는 규칙 셋 목록에서 채운다.

    같은 목록을 두 곳에 적으면 한쪽만 늘어난다. 실제로 새 규칙 셋이 검사 대상에서 빠진
    적이 있다 -- 등록은 했는데 대상 목록에 안 넣어서 메타 규칙이 그 셋을 안 봤다.
    """
    kinds = dict(man.get("kinds", {}))
    paths = [r["path"] for r in normalize_rulesets(man)]
    for name, kind in kinds.items():
        if kind.get("from_rulesets"):
            kinds[name] = dict(kind, paths=paths)
    return kinds


def load_manifest(path):
    p = pathlib.Path(path)
    if not p.exists():
        raise SystemExit("매니페스트가 없다: %s" % path)
    return json.loads(p.read_text(encoding="utf-8"))


def build_names(man):
    """매니페스트가 가리킨 디렉토리에서 이름 목록을 만든다.

    이름을 손으로 나열하지 않는 이유는 그 목록이 실제와 어긋나도 드러나지 않기 때문이다.
    디렉토리에서 뽑으면 어긋날 자리가 없다.
    """
    out = {}
    for key, spec in (man.get("names") or {}).items():
        src = spec.get("from_dirs")
        p = pathlib.Path(src) if src else None
        out[key] = sorted(d.name for d in p.iterdir() if d.is_dir()) if p and p.is_dir() else []
    return out


def filter_paths(paths, prefix):
    if not prefix:
        return list(paths)
    return [p for p in paths if p.startswith(prefix) or prefix.startswith(p)]


def collect_files(paths):
    out = []
    for entry in paths:
        p = pathlib.Path(entry)
        if p.is_file():
            out.append(p)
        elif p.is_dir():
            out += [q for q in p.rglob("*.md") if q.is_file()]
    return sorted(set(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default="verify.json",
                    help="규칙 셋과 대상 종류를 담은 매니페스트")
    ap.add_argument("--path", default=None,
                    help="이 경로에 걸리는 대상만 검사한다")
    ap.add_argument("--json", default=None, help="산출물 JSON 을 이 파일에 쓴다")
    ap.add_argument("--format", choices=("text", "json"), default="text",
                    help="화면 출력 형식")
    ap.add_argument("--warn", action="store_true", help="warn 도 목록에 낸다")
    ap.add_argument("--fix", action="store_true",
                    help="autofixable 인 결함을 고친다. 생성물인 것만 대상이다")
    ap.add_argument("--out-dir", default=None,
                    help="회차를 보관하고 직전 회차와 비교한다")
    ap.add_argument("--verdicts", default=None,
                    help="hybrid 후보에 대한 실행 모델의 확정 JSON")
    args = ap.parse_args()

    if args.path and args.out_dir:
        # 회차를 쌓는 것은 루프의 진행 판정이다. 부분만 본 회차는 안 본 결함을 사라진 것으로
        # 세어 resolved 에 넣고, 그러면 헛돎 판정이 리셋돼 루프가 거짓 진전으로 끝난다.
        print("--path 와 --out-dir 는 함께 쓸 수 없다. 부분만 본 회차는 "
              "안 본 결함을 해결로 센다.", file=sys.stderr)
        return 2

    man = load_manifest(args.manifest)
    kinds = resolve_kinds(man)
    verdicts = load_verdicts(args.verdicts or man.get("verdicts"))
    timeout = man.get("timeout", DEFAULT_TIMEOUT)

    ctx = {"names": build_names(man), "kinds": kinds, "manifest": args.manifest}

    rules = []
    base_by_path = {}
    for rs in normalize_rulesets(man):
        base_by_path[rs["path"]] = rs["checks"]
        rules += load_rules(rs["path"], kinds, rs["checks"])

    findings, pending, evaluated, skipped, fixed = [], [], [], [], []
    seen_verdict_ids = []
    if timeout and not has_timeout():
        skipped.append({"rule": "(엔진)",
                        "reason": "이 플랫폼에는 판정기 제한 시간을 걸 수 없다"})
    for rule in rules:
        m = rule["meta"]
        rid, kind_name = m.get("id", "?"), m.get("applies_to")
        kind = kinds.get(kind_name)
        if kind is None:
            skipped.append({"rule": rid,
                            "reason": "applies_to:%s -- 매니페스트에 없는 종류" % kind_name})
            continue
        paths = filter_paths(kind.get("paths", []), args.path)
        if not paths:
            skipped.append({"rule": rid, "reason": "--path 로 걸러져 대상이 없다"})
            continue
        mod = load_checker(rule["checks_base"], m.get("check", ""))
        if mod is None or not hasattr(mod, "check"):
            skipped.append({"rule": rid, "reason": "판정기 없음"})
            continue
        evaluated.append(rid)

        def emit(rule, path, raw):
            f = make_finding(rule, path, raw)
            if raw.get("question"):
                f["question"] = raw["question"]
            if rule["meta"].get("mode") != "hybrid":
                findings.append(f)
                return
            seen_verdict_ids.append(f["id"])
            verdict_kind, f = apply_verdict(f, verdicts)
            if verdict_kind == "defect":
                findings.append(f)
            elif verdict_kind == "pending":
                pending.append(f)


        def run_one(target, args_):
            """대상 하나를 판정한다. 여기서 죽어도 나머지 대상은 계속 돈다."""
            try:
                raws = call_check(mod.check, *args_, ctx=ctx, timeout=timeout)
                if (args.fix and hasattr(mod, "fix")
                        and any(r.get("autofixable") for r in raws)):
                    fixed.extend(call_check(mod.fix, *args_, ctx=ctx,
                                            timeout=timeout) or [])
                    raws = call_check(mod.check, *args_, ctx=ctx, timeout=timeout)
                for raw in raws:
                    emit(rule, target, raw)
            except Exception as e:  # 판정기가 죽으면 그 사실 자체가 결함이다
                f = make_finding(rule, target, {
                    "line": 0, "snippet": "%s %s" % (rid, target or ""),
                    "section": "(checker)",
                    "message": "판정기 실행 실패: %s: %s" % (type(e).__name__, e)})
                f["severity"] = "error"  # 규칙이 warn 이어도 판정기가 죽은 것은 error 다
                f["fix"] = {"suggestion": "판정기를 고친다. 이 대상은 검사되지 않았다.",
                            "autofixable": False}
                findings.append(f)

        if kind.get("granularity") == "dir":
            for d in paths:
                # 대상 규칙 셋의 판정기 자리는 그 셋의 것이다. 검사하는 규칙의 것이 아니다.
                target_rules = load_rules(d, kinds, base_by_path.get(d, str(ENGINE_DIR)))
                run_one(pathlib.Path(d), (d, target_rules))
        else:
            for target in collect_files(paths):
                run_one(target, (str(target), target.read_text(encoding="utf-8")))

    verdicts_path = args.verdicts or man.get("verdicts")
    stale = [] if args.path else stale_verdicts(verdicts, seen_verdict_ids)
    if stale and args.fix and verdicts_path:
        fixed.append(drop_verdicts(verdicts_path, stale))
        stale = []
    for vid in stale:
        findings.append({
            "id": "verdicts:%s" % vid, "rule": "(확정)", "severity": "error",
            "detected_by": "engine",
            "location": {"file": verdicts_path, "section": "(verdicts)",
                         "line": 0, "snippet": vid},
            "message": "확정은 있는데 그 대상이 이번 검사에 없다: %s" % vid,
            "fix": {"suggestion": "--fix 로 지운다. 대상이 돌아오면 다시 판정한다.",
                    "autofixable": True}})

    summary = {"error": sum(1 for f in findings if f["severity"] == "error"),
               "warn": sum(1 for f in findings if f["severity"] == "warn"),
               "pending": len(pending)}

    prev = load_previous(args.out_dir) if args.out_dir else None
    errs = [f for f in findings if f["severity"] == "error"] + pending
    delta = compute_delta(prev, errs)
    streak = stall_streak(prev, delta)
    stalled = streak >= STALL_LIMIT

    report = {"schema": 1, "manifest": args.manifest, "path_filter": args.path,
              "timeout": timeout,
              "rulesets": [r["path"] for r in normalize_rulesets(man)],
              "summary": summary, "rules_evaluated": evaluated,
              "rules_skipped": skipped, "delta": delta,
              "stall_streak": streak, "stalled": stalled,
              "fixed": fixed, "stale_verdicts": stale,
              "findings": findings, "pending": pending}

    if args.out_dir:
        report["run"] = next_run_seq(args.out_dir)
        save_run(args.out_dir, report)
    blob = json.dumps(report, ensure_ascii=False, indent=2)
    if args.json:
        pathlib.Path(args.json).write_text(blob + "\n", encoding="utf-8")
    print(blob if args.format == "json" else render.to_text(report, args.warn))

    if stalled:
        return 2
    if summary["error"]:
        return 1
    return 3 if pending else 0


if __name__ == "__main__":
    sys.exit(main())
