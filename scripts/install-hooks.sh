#!/usr/bin/env bash
# 저장소 안 .githooks/ 를 git 훅 경로로 설정한다. 클론한 자리마다 한 번 실행한다.
#
# .git/hooks/ 는 커밋되지 않아 클론에 따라오지 않는다. core.hooksPath 로 저장소 안
# 디렉토리를 가리켜야 훅이 버전관리된다.
set -eu
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath .githooks
echo "core.hooksPath = $(git config core.hooksPath)"
