#!/usr/bin/env python3
"""스킬과 규칙의 뼈대를 만든다.

만든 직후에는 검증을 통과하지 않는다. 판정 기준과 판정기와 픽스처가 비어 있기 때문이고,
그 상태가 결함으로 보이는 것이 맞다 -- 통과하는 빈 규칙은 검사되는 척만 한다.

사용:
  scaffold.py skill <이름> [--with-rules]
  scaffold.py rule <규칙셋 경로> <ID> <slug> --applies-to <종류> [--fixtures]
"""
import argparse, datetime, json, pathlib, subprocess, sys

HERE = pathlib.Path(__file__).resolve().parent
MANIFEST = pathlib.Path("verify.json")


def load_manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def save_manifest(man):
    MANIFEST.write_text(json.dumps(man, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")


def write(path, text):
    if path.exists():
        print("이미 있다: %s" % path)
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    print("만듦: %s" % path)
    return True


SKILL_MD = '''---
name: %(name)s
description: |
  (언제 이 스킬을 부르는지 한 줄씩)
created: %(now)s
---

`skills/%(name)s/procedure.md` 를 Read 툴로 로드하고 그 내용을 따른다.

이 파일은 Claude Code 어댑터의 진입점이다. 툴별 실행 차이는
`adapters/claude-code.md` 에 있다.
'''

RULES_README = '''# %(name)s 규칙

(이 규칙 셋이 무엇을 검사하는지 한 줄)

## 그룹

| 그룹 | 없으면 무엇이 깨지는가 |
|---|---|
| %(group)s | (한 줄) |

## 인덱스

이 표는 `engine/gen_index.py` 가 생성한다. 손으로 고치지 않는다.

<!-- rules-index:start -->
<!-- rules-index:end -->
'''

PROCEDURE_MD = '''# %(name)s

(이 스킬이 무엇을 하는지 한 문단)

## 절차

1. (첫 단계)
2. (다음 단계)
'''

RULE_MD = '''---
id: %(id)s
group: %(group)s
title: (한 줄 제목)
mode: script
check: checks/%(mod)s.py
applies_to: %(kind)s
%(fixtures)sseverity: error
why: (이 규칙이 없으면 무엇이 깨지는지 한 문장)
---

## 판정 기준

결함: (무엇이 결함인지 검출형으로. "적절한가" 가 아니라 "무엇이 결함인가")

## 수정 지침

(무엇으로 바꾸는지. 방향이 하나로 정해져야 error 다)

## 예시

<!-- case: fail -->
```
(이 입력에서 결함이 하나 이상 나와야 한다)
```

<!-- case: pass -->
```
(이 입력에서 아무것도 안 나와야 한다)
```
'''

CHECK_PY = '''"""%(id)s -- (한 줄 제목)."""
from _md import body_lines


def check(path, text):
    out = []
    for i, line in body_lines(text):
        pass  # 여기에 판정을 쓴다
    return out
'''


def cmd_skill(args):
    name = args.name
    root = pathlib.Path("skills") / name
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    write(root / "SKILL.md", SKILL_MD % {"name": name, "now": now})
    write(root / "procedure.md", PROCEDURE_MD % {"name": name})
    if not args.with_rules:
        print("규칙 없이 만들었다. 필요해지면 --with-rules 로 다시 부르거나 손으로 더한다.")
        return 0
    (root / "checks").mkdir(parents=True, exist_ok=True)
    write(root / "rules" / "README.md",
          RULES_README % {"name": name, "group": name})
    man = load_manifest()
    entry = {"path": "skills/%s/rules" % name, "checks": "skills/%s" % name}
    if entry not in man.get("rulesets", []):
        man.setdefault("rulesets", []).append(entry)
        save_manifest(man)
        print("매니페스트 rulesets 에 더함: %s" % entry["path"])
    print("규칙이 볼 대상 종류를 verify.json 의 kinds 에 더한 뒤 rule 명령을 쓴다.")
    return 0


def cmd_rule(args):
    man = load_manifest()
    kinds = man.get("kinds", {})
    if args.applies_to not in kinds:
        print("매니페스트에 없는 종류다: %s (있는 것: %s)"
              % (args.applies_to, ", ".join(sorted(kinds))), file=sys.stderr)
        return 1

    ruleset = pathlib.Path(args.ruleset)
    base = HERE
    for item in man.get("rulesets", []):
        path = item if isinstance(item, str) else item["path"]
        if pathlib.Path(path) == ruleset:
            base = pathlib.Path(item["checks"]) if isinstance(item, dict) else HERE
            break
    else:
        print("매니페스트 rulesets 에 없는 규칙 셋이다: %s" % ruleset, file=sys.stderr)
        return 1

    mod = "%s_%s" % (args.id.lower(), args.slug.replace("-", "_"))
    fixtures = ""
    if args.fixtures:
        fixtures = "fixtures: fixtures/%s\n" % args.id
        for kind in ("fail", "pass"):
            d = base / "fixtures" / args.id / kind
            d.mkdir(parents=True, exist_ok=True)
            print("만듦: %s/" % d)

    write(ruleset / ("%s-%s.md" % (args.id, args.slug)),
          RULE_MD % {"id": args.id, "group": args.group, "mod": mod,
                     "kind": args.applies_to, "fixtures": fixtures})
    write(base / "checks" / ("%s.py" % mod), CHECK_PY % {"id": args.id})
    subprocess.run([sys.executable, str(HERE / "gen_index.py"), str(ruleset)])
    print("판정 기준과 판정기와 픽스처를 채운다. 채우기 전에는 검증이 통과하지 않는다.")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("skill", help="스킬 뼈대")
    s.add_argument("name")
    s.add_argument("--with-rules", action="store_true", help="그 스킬 고유 규칙 셋까지 만든다")
    s.set_defaults(fn=cmd_skill)

    r = sub.add_parser("rule", help="규칙 뼈대")
    r.add_argument("ruleset", help="규칙 디렉토리. 매니페스트에 등록돼 있어야 한다")
    r.add_argument("id")
    r.add_argument("slug")
    r.add_argument("--applies-to", required=True)
    r.add_argument("--group", default="")
    r.add_argument("--fixtures", action="store_true", help="픽스처 디렉토리까지 만든다")
    r.set_defaults(fn=cmd_rule)

    args = ap.parse_args()
    if args.cmd == "rule" and not args.group:
        args.group = "meta" if "meta" in args.ruleset else "readability"
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
