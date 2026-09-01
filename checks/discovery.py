"""검사 모듈을 자동으로 찾는다. 손으로 등록하지 않는다."""
import importlib.util
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATTERN = re.compile(r"^c(\d+)_[a-z0-9_]+\.py$")


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.PREFIX = path.stem.split("_")[0]
    return module


def modules():
    found = []
    for path in sorted(HERE.iterdir()):
        m = PATTERN.match(path.name)
        if m:
            found.append((int(m.group(1)), path))
    return [load(path) for _, path in sorted(found)]
