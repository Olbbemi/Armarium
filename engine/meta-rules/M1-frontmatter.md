---
id: M1
group: meta
title: 규칙 파일 프론트매터
mode: script
check: checks/m1_frontmatter.py
applies_to: ruleset
fixtures: fixtures/M1
severity: error
why: 판정기가 규칙을 실행하려면 어느 필드를 읽을지 고정돼 있어야 하고, 하나라도 비면 그 규칙은 실행 대상에서 조용히 빠진다
---

## 판정 기준

결함: 규칙 파일이 아래 필드를 하나라도 빠뜨리거나, 값이 허용 목록 밖이다.

| 필드 | 허용 값 |
|---|---|
| `id` | 대문자 한 글자 + 숫자 |
| `group` | 파일이 속한 그룹 이름 |
| `title` | 비어 있지 않은 문자열 |
| `mode` | `script`, `hybrid` |
| `applies_to` | 매니페스트에 정의된 대상 종류 이름 |
| `severity` | `error`, `warn` |
| `why` | 비어 있지 않은 한 문장 |

`check` 는 어느 `mode` 에서도 필수다. 판정기가 없는 규칙은 규칙 자리에 두지 않는다.

`fixtures` 는 선택이다. 코드블록으로 못 담는 픽스처를 쓸 때만 디렉토리를 가리킨다.

`applies_to` 는 어떤 종류의 대상에 적용하는지다. 그 종류가 어느 경로인지는 규칙이 갖지 않고
매니페스트가 갖는다. 이름이 매니페스트에 실제로 정의돼 있는지는 M8 이 본다.

## 수정 지침

빠진 필드를 채운다. `why` 를 못 쓰겠으면 그 규칙이 무엇을 막는지가 아직 정해지지 않은 것이므로,
필드를 채우는 대신 규칙 자체를 다시 정의한다.

## 예시

필수 필드를 다 갖춘 앞머리와, 셋을 빠뜨린 앞머리다.

```
id: X1
group: sample
title: 무언가
mode: script
check: checks/x1_sample.py
applies_to: markdown
severity: warn
why: 없으면 무엇이 깨지는지 한 문장
```

```
id: X1
title: 무언가
```
