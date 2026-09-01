"""검사기 자체를 픽스처로 검증한다."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import discovery

FIXTURES = HERE / "fixtures"


def run():
    failures = []
    for module in discovery.modules():
        base = FIXTURES / module.PREFIX
        fails = sorted(
            d for d in base.glob("fail*") if d.is_dir()
        ) if base.is_dir() else []
        samples = [("pass", base / "pass")] + [("fail", d) for d in fails]
        if not base.is_dir() or not (base / "pass").is_dir() or not fails:
            failures.append(
                "%s -- 픽스처가 모자라다: fixtures/%s 에 pass 와 fail 이 있어야 한다"
                % (module.ID, module.PREFIX)
            )
            continue
        for kind, sample in samples:
            result = module.check(sample)
            if kind == "pass" and result:
                failures.append(
                    "%s -- 통과해야 할 샘플이 실패했다: %s" % (module.ID, result)
                )
            if kind == "fail" and not result:
                failures.append(
                    "%s -- 실패해야 할 샘플이 통과했다: %s"
                    % (module.ID, sample.name)
                )
    return failures


if __name__ == "__main__":
    problems = run()
    for line in problems:
        print("FAIL  " + line)
    if problems:
        print("selftest FAIL  %d건" % len(problems))
        sys.exit(1)
    print("selftest OK")
