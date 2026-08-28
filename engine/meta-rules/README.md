# 메타 규칙

규칙 셋 자체와 코어 문서를 검사하는 규칙. 검사 대상이 밖이 아니라 안이라서 산출물 규칙과 갈라 둔다.

대상 규칙 디렉토리는 `verify.json` 의 `ruleset` 종류가 갖는다. 자기 자신도 대상이 된다.

## 그룹

| 그룹 | 없으면 무엇이 깨지는가 |
|---|---|
| `meta` | 규칙 자체를 아무도 검사하지 않아, 문서와 판정기가 어긋난 채로 통과한다 |

## 인덱스

이 표는 `engine/gen_index.py` 가 생성한다. 손으로 고치지 않는다.

<!-- rules-index:start -->
| id | 항목 | mode | 대상 | severity |
|---|---|---|---|---|
| M1 | 규칙 파일 프론트매터 | script | ruleset | error |
| M10 | 픽스처 필수 | script | ruleset | error |
| M2 | 규칙 본문 고정 섹션 | script | ruleset | error |
| M3 | mode 와 판정기 정합 | script | ruleset | error |
| M4 | 픽스처 왕복 검증 | script | ruleset | error |
| M5 | id 안정성 | script | ruleset | error |
| M6 | 인덱스 정합 | script | ruleset | error |
| M7 | generic 어댑터 완주 | hybrid | procedure | error |
| M8 | 대상 종류 정의 | script | ruleset | error |
| M9 | 코어 순수성 | script | neutral | error |
<!-- rules-index:end -->

## 실행

```
python3 engine/verify.py
```
