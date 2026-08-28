#!/usr/bin/env python3
"""규칙 디렉토리의 README 인덱스 블록을 생성한다. 손으로 쓰지 않는다.

사용: gen_index.py <rules_dir> [<rules_dir> ...]
"""
import pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "checks"))
from verify import load_rules      # noqa: E402
from m6_index_sync import fix      # noqa: E402


def main():
    if len(sys.argv) < 2:
        print(__doc__.strip())
        return 1
    for d in sys.argv[1:]:
        rules_dir = pathlib.Path(d)
        for note in fix(rules_dir, load_rules(rules_dir)):
            print(note)
    return 0


if __name__ == "__main__":
    sys.exit(main())
