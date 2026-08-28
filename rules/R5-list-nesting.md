---
id: R5
group: readability
title: 중첩 리스트 깊이 상한
mode: script
check: checks/r5_list_nesting.py
applies_to: markdown
severity: error
why: 3단계를 넘는 중첩은 목록이 아니라 표나 별도 절이어야 할 것을 목록으로 눌러 담은 상태다
---

## 판정 기준

결함: 리스트 중첩 깊이가 3 을 넘는다.

최상위 항목이 깊이 1 이다. 들여쓰기 2칸 또는 4칸을 한 단계로 센다.

## 수정 지침

깊이 3 이하로 평탄화한다. 항목마다 속성이 여럿이라 중첩이 필요했다면 표로 바꾼다.

## 예시

<!-- case: pass -->
```
- 1단계
  - 2단계
    - 3단계
```

<!-- case: fail -->
```
- 1단계
  - 2단계
    - 3단계
      - 4단계
```
