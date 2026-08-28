---
id: R8
group: readability
title: 표 열 수
mode: script
check: checks/r8_table_columns.py
applies_to: markdown
severity: warn
why: 열이 많은 표는 터미널 폭에서 줄바꿈되어 행 경계가 무너지고, 그러면 어느 값이 어느 열인지 읽히지 않는다
---

## 판정 기준

결함: 마크다운 표의 열 수가 5 를 넘는다.

구분선(`|---|`) 이 있는 표만 대상으로 한다.

## 수정 지침

열을 나눠 표 둘로 만들거나, 부가 속성 열을 본문 서술로 내린다.

## 예시

<!-- case: pass -->
```
| 항목 | 판정 | 근거 |
|---|---|---|
| a | b | c |
```

<!-- case: fail -->
```
| 항목 | 그룹 | 판정 | 심각도 | 근거 | 예외 |
|---|---|---|---|---|---|
| a | b | c | d | e | f |
```
