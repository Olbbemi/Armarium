---
id: R2
group: readability
title: 헤딩 깊이 상한
mode: script
check: checks/r2_heading_depth.py
applies_to: markdown
severity: error
why: 4단계 헤딩이 필요하다는 것은 그 절이 이미 파일 하나 분량의 구조를 갖고 있다는 뜻이다
---

## 판정 기준

결함: `####` 이상 깊이의 헤딩이 있다.

허용 깊이는 `#`, `##`, `###` 까지다.

## 수정 지침

`####` 을 쓰려는 절을 별도 파일로 옮기고, 그 파일 안에서 헤딩 깊이를 한 단계씩 올린다.

## 예시

<!-- case: pass -->
```
# 제목
## 절
### 항목
```

<!-- case: fail -->
```
# 제목
## 절
### 항목
#### 세부
```
