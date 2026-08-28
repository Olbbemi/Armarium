---
id: R3
group: readability
title: 헤딩 레벨 건너뜀 금지
mode: script
check: checks/r3_heading_skip.py
applies_to: markdown
severity: error
why: 레벨을 건너뛰면 목차가 실제 포함 관계와 어긋나, 어느 절의 하위인지 읽는 쪽이 추측하게 된다
---

## 판정 기준

결함: 헤딩 레벨이 이전 헤딩보다 2단계 이상 깊어진다.

레벨이 얕아지는 방향은 몇 단계를 건너뛰어도 결함이 아니다.

## 수정 지침

건너뛴 레벨의 헤딩을 채우거나, 깊은 헤딩의 레벨을 한 단계만 내리도록 조정한다.

## 예시

<!-- case: pass -->
```
## 절
### 항목
# 다음 제목
```

<!-- case: fail -->
```
## 절
#### 세부
```
