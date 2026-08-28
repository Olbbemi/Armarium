---
id: M8
group: meta
title: 대상 종류 정의
mode: script
check: checks/m8_kind_defined.py
applies_to: ruleset
fixtures: fixtures/M8
severity: error
why: 정의되지 않은 종류를 가리키는 규칙은 대상을 못 찾아 조용히 건너뛰어지고, 검사되지 않은 채로 통과로 보고된다
---

## 판정 기준

결함: 규칙의 `applies_to` 가 매니페스트에 정의되지 않은 종류를 가리킨다.

종류 이름과 그 경로는 매니페스트가 갖는다. 규칙은 이름만 선언하므로, 이름이 어긋나도
규칙 파일만 봐서는 드러나지 않는다.

## 수정 지침

이름의 오타면 규칙을 고치고, 정말 새로운 종류면 매니페스트에 그 종류와 경로를 더한다.
어느 쪽인지는 그 규칙이 무엇을 검사하려던 것인지로 정한다.

## 예시

매니페스트에 `markdown` 과 `ruleset` 만 정의돼 있을 때다.

```
통과 -- applies_to: markdown
결함 -- applies_to: markdwon
```
