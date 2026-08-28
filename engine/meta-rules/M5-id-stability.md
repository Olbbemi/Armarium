---
id: M5
group: meta
title: id 안정성
mode: script
check: checks/m5_id_stability.py
applies_to: ruleset
fixtures: fixtures/M5
severity: error
why: 폐기한 번호를 다시 쓰면 지난 회차 보고서의 그 id 와 이번 id 가 다른 규칙을 가리켜, 회차 비교가 조용히 틀린 답을 낸다
---

## 판정 기준

결함: 아래 중 하나에 해당한다.

- 같은 `id` 를 가진 규칙 파일이 둘 이상이다
- `retired.txt` 에 적힌 id 를 현재 규칙이 쓰고 있다
- 파일명의 id 부분이 프론트매터의 `id` 와 다르다

## 수정 지침

새 id 를 부여한다. 규칙을 폐기할 때는 파일을 지우고 그 id 를 `rules/retired.txt` 에 한 줄로 적는다.

## 예시

통과 -- R1 이 한 파일에만 있고 `retired.txt` 에 없다
결함 -- R6 을 폐기한 뒤 새 규칙에 R6 을 다시 부여
