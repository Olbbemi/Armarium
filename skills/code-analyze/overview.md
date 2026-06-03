# code-analyze

코드의 4가지 측면 분석: 구조, 품질, 변경 영향도, 로직 요약.

## 하위 스킬

| 분석 | 파일 | 역할 |
|------|------|------|
| 구조/아키텍처 | `skills/code-analyze/agents/structure.md` | 디렉토리·모듈·의존성·진입점·데이터 흐름 |
| 품질 | `skills/code-analyze/agents/quality.md` | 복잡도·중복·데드코드·안티패턴 |
| 변경 영향도 | `skills/code-analyze/agents/impact.md` | 지정 대상 수정 시 영향 받는 범위 |
| 로직 요약 | `skills/code-analyze/agents/summary.md` | 코드 동작을 사람 말로 서술 |

## 실행 순서

### 1. 디스패처 호출

bash 디스패처를 호출해 실행 모드와 에이전트 경로를 결정한다.

```
bash "${CLAUDE_PLUGIN_ROOT}/skills/code-analyze/code-analyze.sh" [<analysis>...]
```

인자: `structure`, `quality`, `impact`, `summary` 중 하나 이상. 또는 인자 없음.

### 2. 디스패처 출력 해석

디스패처는 `KEY=VALUE` 형태로 stdout에 출력한다.

- `MODE=ASK` — 선택이 비어있다. 사용자에게 어떤 분석을 원하는지 묻고, 응답을 받아 1단계 재실행
- `MODE=INLINE` — 단일 분석. `AGENT=<path>` 한 줄. 해당 에이전트 파일을 Read 툴로 로드하고 본문대로 인라인 실행
- `MODE=PARALLEL` — 2개 이상 분석. `AGENT=<path>` 여러 줄. 각 경로를 Task 도구로 병렬 호출

### 3. 분석 선택 판단

사용자가 호출 시 분석 종류를 명시하지 않으면 Claude는 대화 맥락을 보고 적절한 분석을 자동 선택한다. 맥락이 모호하면 디스패처를 인자 없이 호출해 `MODE=ASK` 신호를 받은 뒤 사용자에게 선택지를 제시한다.

### 4. 병렬 에이전트 실행 (PARALLEL 모드)

디스패처가 출력한 모든 에이전트 경로를 동시에 실행한다.

- [ ] 각 에이전트 파일 경로를 Task 도구에 전달
- [ ] 각 에이전트에 분석 대상 경로를 입력으로 명시
- [ ] 모든 에이전트는 마크다운 리포트를 출력

### 5. 결과 취합

모든 에이전트 완료 후 결과를 통합해 사용자에게 제시한다. 섹션 헤더(`## 구조`, `## 품질` 등)로 각 분석 결과를 구분한다.

## 분석 대상

대상 경로는 디스패처 인자로 받지 않는다. Claude가 대화 맥락에서 결정하며, 명확하지 않으면 사용자에게 묻는다. 결정된 경로를 각 에이전트 입력으로 전달한다.
