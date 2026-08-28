---
id: M6
group: meta
title: 인덱스 정합
mode: script
check: checks/m6_index_sync.py
applies_to: ruleset
fixtures: fixtures/M6
severity: error
why: 목록을 손으로 쓰면 규칙이 늘 때마다 어긋나고, 어긋난 목록은 없는 규칙을 있다고 하거나 있는 규칙을 감춘다
---

## 판정 기준

결함: `README.md` 의 규칙 인덱스 블록이 `rules/` 실제 내용과 다르다.

인덱스 블록은 `<!-- rules-index:start -->` 와 `<!-- rules-index:end -->` 사이다.
비교 대상은 각 규칙의 id, title, mode, severity 다.

## 수정 지침

`engine/verify.py --fix` 나 `engine/gen_index.py <규칙 디렉토리>` 로 블록을 다시 생성한다.
블록 안을 손으로 고치지 않는다. 생성물이라 고칠 결과가 하나로 정해진다.

## 예시

통과 -- 생성 결과와 현재 블록이 문자열로 동일
결함 -- 규칙을 추가했는데 인덱스에 그 행이 없다
