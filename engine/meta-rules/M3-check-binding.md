---
id: M3
group: meta
title: mode 와 판정기 정합
mode: script
check: checks/m3_check_binding.py
applies_to: ruleset
fixtures: fixtures/M3
severity: error
why: mode 가 script 인데 판정기가 없으면 그 규칙은 아무도 검사하지 않는 채로 검사되고 있다고 표시된다
---

## 판정 기준

결함: 아래 중 하나에 해당한다.

- `check` 가 가리키는 판정기 파일이 없다
- `check` 파일이 있는데 어느 규칙도 그 파일을 가리키지 않는다

## 수정 지침

판정기를 만든다. 만들 수 없으면 그것은 규칙이 아니므로 규칙 자리에서 내려 권고로 적는다.
어느 규칙도 안 쓰는 판정기는 지운다.

## 예시

통과 -- `mode: script` 이고 `check: checks/r1_file_lines.py` 가 실재
결함 -- `mode: script` 인데 `check` 경로에 파일 없음
