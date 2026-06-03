#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AGENTS_DIR="$SCRIPT_DIR/agents"

VALID=(structure quality impact summary)

is_valid() {
    local arg="$1"
    for v in "${VALID[@]}"; do
        if [[ "$v" == "$arg" ]]; then
            return 0
        fi
    done
    return 1
}

for arg in "$@"; do
    if ! is_valid "$arg"; then
        echo "ERROR: unknown analysis '$arg'. Valid: ${VALID[*]}" >&2
        exit 1
    fi
done

selected=()
for a in "$@"; do
    dup=0
    if [[ ${#selected[@]} -gt 0 ]]; then
        for s in "${selected[@]}"; do
            if [[ "$s" == "$a" ]]; then
                dup=1
                break
            fi
        done
    fi
    if [[ $dup -eq 0 ]]; then
        selected+=("$a")
    fi
done

count=${#selected[@]}

if [[ $count -eq 0 ]]; then
    echo "MODE=ASK"
    echo "AVAILABLE=${VALID[*]}"
elif [[ $count -eq 1 ]]; then
    echo "MODE=INLINE"
    echo "AGENT=$AGENTS_DIR/${selected[0]}.md"
else
    echo "MODE=PARALLEL"
    for s in "${selected[@]}"; do
        echo "AGENT=$AGENTS_DIR/$s.md"
    done
fi
