---
id: R7
group: readability
title: 문단 문장 수
mode: script
check: checks/r7_paragraph_sentences.py
applies_to: markdown
severity: warn
why: 한 문단에 문장이 쌓이면 여러 주장이 한 덩어리가 되어, 그중 하나만 고치려 할 때 어디를 손댈지 정하기 어렵다
---

## 판정 기준

결함: 한 문단의 문장 수가 5 를 넘는다.

문단은 빈 줄로 구분한다. 리스트 항목, 표, 코드블록은 문단으로 세지 않는다.

## 수정 지침

주장 단위로 문단을 나눈다. 나열이 이어지는 문단이면 리스트로 바꾼다.

## 예시

<!-- case: pass -->
```
주장이다. 근거 하나다. 근거 둘이다.
```

<!-- case: fail -->
```
정의다. 근거다. 예외다. 반례다. 보충이다. 결론이다.
```
