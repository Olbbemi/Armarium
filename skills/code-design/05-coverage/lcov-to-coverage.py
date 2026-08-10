#!/usr/bin/env python3
"""lcov 트레이스를 05-coverage 의 정규화 데이터(coverage.js)로 변환한다.

스키마는 `skills/code-design/05-coverage.md` 의 "데이터 스키마" 절이 단일 출처다.
이 스크립트는 그 스키마를 그대로 산출하며, 판정이나 임계치 비교는 하지 않는다.

여러 lcov 파일을 받으면 같은 소스 파일의 레코드를 합산한다. 테스트 바이너리가
여럿이거나 계측 실행이 여러 번인 경우가 그렇다.

사용:
    lcov-to-coverage.py --root <프로젝트 루트> --target <대상 경로> \
        --branch <브랜치 슬러그> --tool <도구 이름> \
        --out <출력 경로> [--exclude <glob>]... <lcov 파일>...
"""

import argparse
import fnmatch
import json
import os
import sys
from datetime import datetime, timezone

EXT_LANGUAGE = {
    ".c": "c",
    ".h": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".cxx": "cpp",
    ".hh": "cpp",
    ".hpp": "cpp",
    ".hxx": "cpp",
    ".rs": "rust",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".js": "javascript",
    ".jsx": "javascript",
    ".py": "python",
}


class FileRecord:
    """한 소스 파일에 대해 여러 lcov 레코드를 합산한 것."""

    def __init__(self, path):
        self.path = path
        self.line_hits = {}          # 라인번호(int) -> 실행 횟수
        self.function_hits = {}      # (이름, 라인) -> 실행 횟수
        self.branch_hits = {}        # (라인, 블록, 브랜치) -> taken
        self.saw_branch_data = False
        self.saw_function_data = False

    def add_line(self, line, count):
        self.line_hits[line] = self.line_hits.get(line, 0) + count

    def add_function(self, name, line):
        self.saw_function_data = True
        self.function_hits.setdefault((name, line), 0)

    def add_function_hit(self, name, count):
        self.saw_function_data = True
        for key in self.function_hits:
            if key[0] == name:
                self.function_hits[key] += count
                return
        self.function_hits[(name, 0)] = count

    def add_branch(self, line, block, branch, taken):
        self.saw_branch_data = True
        key = (line, block, branch)
        self.branch_hits[key] = self.branch_hits.get(key, 0) + taken

    def to_dict(self):
        lines = {
            "found": len(self.line_hits),
            "hit": sum(1 for count in self.line_hits.values() if count > 0),
        }

        if self.saw_branch_data:
            branches = {
                "found": len(self.branch_hits),
                "hit": sum(1 for taken in self.branch_hits.values() if taken > 0),
            }
            branch_list = [
                {"line": line, "block": block, "branch": branch, "taken": taken}
                for (line, block, branch), taken in sorted(self.branch_hits.items())
            ]
        else:
            branches = None
            branch_list = []

        if self.saw_function_data:
            functions = {
                "found": len(self.function_hits),
                "hit": sum(1 for count in self.function_hits.values() if count > 0),
            }
            function_list = [
                {"name": name, "line": line, "hit": count}
                for (name, line), count in sorted(
                    self.function_hits.items(), key=lambda item: (item[0][1], item[0][0])
                )
            ]
        else:
            functions = None
            function_list = []

        return {
            "path": self.path,
            "language": language_of(self.path),
            "lines": lines,
            "branches": branches,
            "functions": functions,
            "lineHits": {str(line): count for line, count in sorted(self.line_hits.items())},
            "branchHits": branch_list,
            "functionHits": function_list,
        }


def language_of(path):
    return EXT_LANGUAGE.get(os.path.splitext(path)[1].lower(), "unknown")


def parse_taken(raw):
    """BRDA 의 taken 필드. '-' 는 블록 자체가 실행되지 않아 평가되지 않은 브랜치다."""
    return 0 if raw == "-" else int(raw)


def normalize(source_path, root):
    """프로젝트 루트 기준 상대경로로 정규화한다. 루트 밖이면 None (제외 대상)."""
    absolute = os.path.realpath(
        source_path if os.path.isabs(source_path) else os.path.join(root, source_path)
    )
    relative = os.path.relpath(absolute, root)
    return None if relative.startswith(os.pardir) else relative.replace(os.sep, "/")


def excluded(path, patterns):
    return any(fnmatch.fnmatch(path, pattern) for pattern in patterns)


def parse_lcov(stream, root, patterns, records):
    """lcov 트레이스 한 벌을 읽어 records 에 합산한다."""
    current = None

    for raw_line in stream:
        line = raw_line.strip()
        if not line:
            continue

        if line == "end_of_record":
            current = None
            continue

        prefix, _, payload = line.partition(":")

        if prefix == "SF":
            path = normalize(payload, root)
            current = None if path is None or excluded(path, patterns) else records.setdefault(
                path, FileRecord(path)
            )
            continue

        if current is None:
            continue

        fields = payload.split(",")
        if prefix == "DA":
            current.add_line(int(fields[0]), int(fields[1]))
        elif prefix == "FN":
            current.add_function(",".join(fields[1:]), int(fields[0]))
        elif prefix == "FNDA":
            current.add_function_hit(",".join(fields[1:]), int(fields[0]))
        elif prefix in ("FNF", "FNH"):
            current.saw_function_data = True
        elif prefix == "BRDA":
            current.add_branch(
                int(fields[0]), int(fields[1]), fields[2], parse_taken(fields[3])
            )
        elif prefix in ("BRF", "BRH"):
            current.saw_branch_data = True


def summarize(files):
    """files 를 합산한다. 어느 파일도 그 계측을 안 냈으면 null 이다."""
    summary = {}
    for key in ("lines", "branches", "functions"):
        present = [entry[key] for entry in files if entry[key] is not None]
        summary[key] = (
            {
                "found": sum(item["found"] for item in present),
                "hit": sum(item["hit"] for item in present),
            }
            if present
            else None
        )
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("traces", nargs="+", help="lcov 트레이스 파일")
    parser.add_argument("--root", required=True, help="프로젝트 루트. 경로 정규화 기준")
    parser.add_argument("--target", required=True, help="대상 경로 (루트 기준)")
    parser.add_argument("--branch", required=True, help="브랜치 슬러그")
    parser.add_argument("--tool", required=True, help="커버리지를 뽑은 도구 이름")
    parser.add_argument("--out", required=True, help="출력할 coverage.js 경로")
    parser.add_argument(
        "--exclude",
        action="append",
        default=[],
        metavar="GLOB",
        help="제외할 경로 패턴 (루트 기준 상대경로에 매칭). 여러 번 지정 가능",
    )
    parser.add_argument(
        "--generated-at",
        default=None,
        help="추출 시각 (ISO 8601). 생략하면 현재 시각",
    )
    args = parser.parse_args()

    root = os.path.realpath(args.root)
    records = {}

    for trace in args.traces:
        with open(trace, encoding="utf-8", errors="replace") as stream:
            parse_lcov(stream, root, args.exclude, records)

    if not records:
        print(
            "변환할 레코드가 없습니다. 경로 정규화(--root)나 제외 패턴(--exclude)을 확인하세요.",
            file=sys.stderr,
        )
        return 1

    files = [records[path].to_dict() for path in sorted(records)]
    languages = sorted({entry["language"] for entry in files})

    payload = {
        "meta": {
            "target": args.target,
            "branch": args.branch,
            "languages": languages,
            "tool": args.tool,
            "generatedAt": args.generated_at
            or datetime.now(timezone.utc).isoformat(timespec="seconds"),
        },
        "summary": summarize(files),
        "files": files,
    }

    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as stream:
        stream.write("window.COVERAGE = ")
        json.dump(payload, stream, ensure_ascii=False, separators=(",", ":"))
        stream.write(";\n")

    summary = payload["summary"]["lines"]
    print(
        f"{len(files)}개 파일, 라인 {summary['hit']}/{summary['found']} -> {args.out}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
