"""아르마리움 스킬 규격 검사 진입점."""
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent

# 바이트코드 무효화는 소스의 (mtime, size) 로 판단하고 헤더의 mtime 은 초 단위다.
# 검사기를 고치고 같은 초에 돌리면서 크기가 같으면 옛 바이트코드가 그대로 실행된다.
# 위 설정은 새로 만드는 것만 막으므로 남은 것을 지운다.
for cache in HERE.rglob("__pycache__"):
    if cache.is_symlink() or not cache.is_dir():
        continue
    if cache.resolve().parts[: len(HERE.parts)] != HERE.parts:
        continue
    for item in cache.glob("*.pyc"):
        if item.is_symlink() or not item.is_file():
            continue
        item.unlink()
    try:
        cache.rmdir()
    except OSError:
        pass
sys.path.insert(0, str(HERE))

import discovery
import selftest

ROOT = HERE.parent


def main(argv):
    full = "--full" in argv

    problems = selftest.run()
    for line in problems:
        print("FAIL  selftest  " + line)
    if problems:
        print()
        print("selftest 실패 %d건. 검사기를 먼저 고친다." % len(problems))
        return 1

    print("selftest OK")

    failures = 0
    for module in discovery.modules():
        if module.FULL_ONLY and not full:
            print("SKIP  %-4s %s  (--full 에서만 돈다)" % (module.ID, module.NAME))
            continue
        result = module.check(ROOT)
        if result:
            failures += len(result)
            print("FAIL  %-4s %s" % (module.ID, module.NAME))
            for line in result:
                print("        " + line)
        else:
            print("OK    %-4s %s" % (module.ID, module.NAME))

    print()
    if failures:
        print("실패 %d건" % failures)
        return 1
    print("전부 통과")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
