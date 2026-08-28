---
id: M10
group: meta
title: 픽스처 필수
mode: script
check: checks/m10_fixture_required.py
applies_to: ruleset
fixtures: fixtures/M10
severity: error
why: 픽스처가 없으면 그 규칙의 판정기가 죽어도 검출 0 이 통과와 구분되지 않아, 검사되지 않는 규칙이 검사된 것처럼 보고된다
---

## 판정 기준

결함: 규칙에 픽스처가 한 자리에도 없다.

`예시` 섹션의 마커 뒤 코드블록이거나 `fixtures` 가 가리키는 디렉토리다. 둘 중 하나면 된다.

## 수정 지침

그 규칙이 무엇을 잡는지 보여주는 최소 입력을 만들어 `fail` 로, 잡지 않아야 하는 입력을
`pass` 로 넣는다. 코드블록에 담기면 규칙 파일 안에, 안 담기면 픽스처 디렉토리에 둔다.

## 예시

```
통과 -- 예시 섹션에 case 마커와 코드블록이 있다
통과 -- fixtures 필드가 fail/ 과 pass/ 를 가진 디렉토리를 가리킨다
결함 -- 둘 다 없다
```
