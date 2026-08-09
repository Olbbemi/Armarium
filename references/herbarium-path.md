# Herbarium 경로 검증

`knowledge-capture` · `knowledge-scan` · `knowledge-study` · `knowledge-promote` 네 스킬이 공유하는 경로 판정 규약.

wip 를 비롯한 지식 파일은 Herbarium 저장소에만 둔다. 스킬이 사용자에게 디렉토리 경로를 입력받을 때마다 아래 절차로 검증한다.

경로를 코드에 고정하지 않으며, 세션마다 새로 입력받는다. 어느 시점에 입력받을지는 호출한 스킬이 정한다. 검증은 git origin remote 조회로 한다.

---

## 절차

1. 입력 경로에서 origin remote 를 조회한다.
   `git -C <입력경로> remote get-url origin`
2. 결과가 아래 기대 remote URL 과 정확히 일치하면 채택한다.
3. 일치하지 않거나 조회에 실패하면(존재하지 않는 경로 포함) 사유를 한 줄로 알리고 경로를 다시 입력받는다. 일치할 때까지 반복한다.

## 기대 remote URL

이 값이 경로 검증의 단일 기준이다.

```
git@github.com:Olbbemi/Herbarium.git
```

## 무슨 경로를 몇 개 받을지는 호출한 스킬이 정한다

이 파일은 경로 하나를 어떻게 검증하는지만 정의한다. 어떤 용도의 경로를 몇 개 받을지, 받은 경로에서 하위 디렉토리를 도출할지는 각 스킬이 자기 overview 에서 정한다. 받은 경로마다 위 절차를 각각 적용한다.

이 검증이 보는 것은 그 경로가 Herbarium 저장소 안이라는 사실 하나다. 하위 디렉토리 이름이 실재하는지는 보지 않으므로, 존재하지 않는 이름도 그대로 통과한다. 그 경로를 실제로 훑는 단계에서 결과가 비었을 때 어떻게 할지는 호출한 스킬이 정한다.

채택한 경로는 메인 LLM 컨텍스트에만 유지한다(세션 휘발).

<FORBIDDEN>
origin remote 가 기대 remote URL 과 일치하지 않는 경로를 채택하지 않는다.
</FORBIDDEN>

<FORBIDDEN>
채택한 경로를 별도 파일이나 인덱스에 저장하지 않는다.
</FORBIDDEN>
