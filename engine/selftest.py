#!/usr/bin/env python3
"""엔진 최하층 자기검사.

M4(픽스처 왕복)는 다른 규칙의 판정기가 죽었는지 알려준다. 그러나 자기가 죽으면 그 사실을
스스로 낼 수 없다 -- 아무것도 검출하지 않는 것이 곧 통과로 보이기 때문이다.
여기서는 M4 를 검증 엔진 밖에서 직접 불러 살아 있는지 본다.

이 파일보다 아래층은 없다. 그래서 짧게 유지하고 사람이 읽어 확인한다.

종료 코드: 0 살아 있음, 1 죽었음.
"""
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "checks"))
from verify import build_names, load_checker, load_manifest, load_rules  # noqa: E402

TARGET = "checks/m4_fixture_roundtrip.py"


def main():
    man = load_manifest(sys.argv[1] if len(sys.argv) > 1 else "verify.json")
    kinds = man.get("kinds", {})
    ctx = {"names": build_names(man), "kinds": kinds, "manifest": "selftest"}
    m4 = load_checker(HERE, TARGET)
    if m4 is None or not hasattr(m4, "check"):
        print("M4 판정기를 부를 수 없다: %s" % TARGET)
        return 1

    bad = []
    for kind, want_hits in (("fail", True), ("pass", False)):
        d = HERE / "fixtures" / "M4" / kind
        hits = m4.check(str(d), load_rules(d, kinds), ctx)
        if bool(hits) != want_hits:
            bad.append("%s 픽스처에서 %d건 -- M4 가 제 일을 하지 않는다" % (kind, len(hits)))

    for line in bad:
        print(line)
    print("엔진 자기검사: %s" % ("실패" if bad else "통과"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
