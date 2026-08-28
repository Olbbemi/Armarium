# 산출물 규칙

스킬이 만드는 마크다운 문서에 적용하는 규칙. 규칙 하나 = 파일 하나이고, 여기가 유일한 원본이다.

검사 대상은 문서 자체다. 규칙 파일 자신의 규격을 보는 것은 `engine/meta-rules/` 다.

## 그룹

| 그룹 | 없으면 무엇이 깨지는가 |
|---|---|
| `readability` | 관심사가 한 파일에 쌓여, 필요한 규칙 하나를 보려고 문서 전체를 훑게 된다 |

## 인덱스

이 표는 `engine/gen_index.py` 가 생성한다. 손으로 고치지 않는다.

<!-- rules-index:start -->
| id | 항목 | mode | 대상 | severity |
|---|---|---|---|---|
| R1 | 파일 줄 수 상한 | script | markdown | error |
| R2 | 헤딩 깊이 상한 | script | markdown | error |
| R3 | 헤딩 레벨 건너뜀 금지 | script | markdown | error |
| R4 | 형제 헤딩 번호 일관성 | script | markdown | error |
| R5 | 중첩 리스트 깊이 상한 | script | markdown | error |
| R6 | 문장 길이 | script | markdown | warn |
| R7 | 문단 문장 수 | script | markdown | warn |
| R8 | 표 열 수 | script | markdown | warn |
| R9 | 링크 대상 존재 | script | markdown | error |
<!-- rules-index:end -->

## 실행

```
python3 engine/verify.py --path rules
```

대상 경로는 `verify.json` 의 `markdown` 종류가 갖는다.
