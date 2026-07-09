# window.DATA 스키마 (뷰어 <-> render-data 계약)

code-analyze 의 HTML 산출은 고정 뷰어 + 생성 데이터로 나뉜다. 이 파일은 그 둘이 공유하는 **유일 계약**이다 -- 뷰어(`app.js`)는 이 구조를 읽어 렌더하고, `code-analyze-render-data` 에이전트는 facet 를 이 구조의 조각으로 변환한다. 양쪽이 이 파일을 단일 출처로 삼는다.

이 스키마는 **v1** 이다. SPA 운용 경험이 쌓이면 갱신하되, facet 가 지속되는 단일 출처라 재분석 없이 갱신할 수 있다(새 스키마로 facet -> data.js 만 다시 뽑고 뷰어는 내용 해시 비교로 교체).

<PENETRATE>
뷰어와 render-data 는 window.DATA 구조를 이 파일 단일 출처로 삼아 서로 맞춘다.
</PENETRATE>

---

## 로딩 형태

산출 데이터는 `<브랜치>/data.js` 한 파일이며 내용은 전역 대입 한 줄이다.

```js
window.DATA = { ...아래 구조... };
```

`fetch` 가 아니라 `<script src>` 로 주입하므로(`file://` 에서 fetch 는 CORS 로 막힘) 반드시 `window.DATA` 전역 대입 형태여야 한다. 뷰어의 `manifest.js` 도 같은 이유로 `window.MANIFEST = [ ... ]` 전역 대입이다.

<RICOCHET>
data.js 를 fetch 로 읽는 별도 JSON 파일로 두지 않는다(file:// 에서 막힌다). window.DATA 전역 대입 스크립트로 둔다.
</RICOCHET>

---

## 최상위 구조

```js
window.DATA = {
  meta,          // 객체. 항상.
  modules,       // 배열. 항상.
  nodes,         // 배열. 항상.
  architecture,  // 객체. 항상.
  flows,         // 배열. 항상(비면 []).
  invariants,    // 배열. 항상(비면 []).
  tests,         // 배열. 항상(비면 []).
  externals,     // 배열. 항상(비면 []).
  dataContracts, // 배열. 조건부 -- 없으면 키 자체 생략.
  callgraph      // 객체. 조건부 -- 없으면 키 자체 생략.
}
```

조건부 섹션(`dataContracts`, `callgraph`)은 데이터가 없으면 **키를 생략**한다. 뷰어는 키 부재/빈 배열을 보고 해당 탭을 숨긴다.

<PENETRATE>
조건부 섹션은 데이터가 없으면 키를 생략하고, 뷰어는 그 부재로 탭을 숨긴다.
</PENETRATE>

---

## 각 섹션

### meta
```js
meta: {
  target,       // 분석 대상 디렉토리 이름
  branch,       // 브랜치 슬러그
  language,     // 예: "cpp"
  nodeCount,    // 정수
  moduleCount   // 정수
}
```

### modules
```js
modules: [
  { id, name, layer, role }    // id 는 모듈 유일 식별자(레이어/디렉토리 단위)
]
```

### nodes
구조 트리의 파일노드. `id` 는 **스켈레톤이 정한 노드 이름**(단일 출처)이며 교차참조의 키다.
```js
nodes: [
  {
    id,        // 스켈레톤 노드 이름 = 교차참조 키
    path,      // 소스 미러 경로
    module,    // 소속 module.id
    kind,      // "class" | "free-functions" | ...
    role,      // 한 줄 역할
    types: [
      { name, kind, role, bases: [], members: [ { sig, kind } ],
        invariants: [invariantId], exceptions: [] }
    ],
    functions: [ { signature, role, exceptions: [] } ],
    related: [ { targetId, relation } ]   // relation: "delegates"|"dispatches"|"maps"|"consumes"
  }
]
```

### architecture
```js
architecture: {
  entryPoints: [ { id, surface } ],
  entrySurfaceMap: [ { surface, handlerId } ],   // handlerId = node.id
  ports: [ { port, implIds: [nodeId] } ],
  edges: [ { from, to, kind } ],                 // from/to = module.id 또는 node.id
  mermaid                                         // 의존 그래프 소스(엣지에서 생성)
}
```

### flows
```js
flows: [
  { id, trigger, lifecycle, steps: [ ... ],
    relatedNodes: [nodeId],
    mermaid }                                     // 시퀀스 다이어그램 소스(있으면). 사소 경로는 생략 가능.
]
```

### invariants / tests
```js
invariants: [ { id, statement, scope, coveredBy: [testId] } ],
tests:      [ { id, name, target, covers: [invariantId] } ]
```

### externals
```js
externals: [ { name, version, adapter, vendored, port } ]
```

### dataContracts (조건부)
```js
dataContracts: [ { name, kind, fields: [ { name, type, constraints } ] } ]
```

### callgraph (조건부)
호출 그래프는 그래프가 여럿이다. 각 그래프는 mermaid 소스를 갖는다.
```js
callgraph: {
  graphs: [ { id, label, mermaid, defaultCollapsed } ]
  // id: "overview-modules" | "drilldown-<진입점>" | "full-clustered"
  // defaultCollapsed: 부피 큰 그래프(드릴다운/full)는 true 로 두어 뷰어가 접어 시작
}
```

SVG 는 쓰지 않는다 -- 모든 그래프는 mermaid 소스다(뷰어가 클라이언트 렌더).

<RICOCHET>
callgraph 를 렌더된 SVG 로 담지 않는다(mermaid 소스로 담는다).
</RICOCHET>

---

## 교차참조 = 노드 ID

파일 상대경로가 아니라 **노드 ID**(`nodes[].id`, 스켈레톤 단일 출처)로 가리킨다. 위임/디스패치/매핑/소비 관계는 `related.targetId` 로, 진입표면->핸들러는 `entrySurfaceMap.handlerId` 로, 포트 구현은 `ports.implIds` 로, 플로우 관여 노드는 `flows.relatedNodes` 로, 테스트/불변식 조인은 `covers`/`coveredBy` 로 잇는다.

**매달린(dangling) ID 금지** -- 아래 참조 필드가 가리키는 ID 는 실제 존재하는 대상이어야 한다. verify 가 이를 검사한다.

| 참조 필드 | 가리키는 대상 |
|-----------|---------------|
| `nodes[].related.targetId` | `nodes[].id` |
| `architecture.entrySurfaceMap.handlerId` | `nodes[].id` |
| `architecture.ports.implIds` | `nodes[].id` |
| `flows[].relatedNodes` | `nodes[].id` |
| `tests[].covers` | `invariants[].id` |
| `invariants[].coveredBy` | `tests[].id` |

<PENETRATE>
교차참조는 파일 경로가 아니라 노드/불변식/테스트 ID 로 하고, 그 ID 는 실제 존재하는 대상을 가리킨다.
</PENETRATE>

---

## 조각(fragment) 형태 (render-data -> 메인 합침)

render-data 는 위 구조를 통째로 만들지 않고 **슬라이스별 조각**을 `<브랜치>/.dataparts/` 에 JSON 파일로 Write 한다. 메인이 조각들을 기계적으로 합쳐 `data.js` 를 만든다.

| 조각 파일 | 내용(JSON) | 만드는 주체 |
|-----------|-----------|-------------|
| `.dataparts/base.json` | `{ meta, modules }` | 메인(skeleton 에서 직접) |
| `.dataparts/nodes-<서브트리>.json` | `nodes` 배열의 일부(그 서브트리 노드들) | render-data(구조 서브트리) |
| `.dataparts/crosscutting.json` | `{ architecture, flows, invariants, tests, externals, dataContracts?, callgraph? }` | render-data(가로지르는) |

합침(메인, Bash -- 부피가 메인 컨텍스트를 안 거침):
```
{ printf 'window.DATA = ';
  jq -s '.[0] + .[1] + {nodes: (.[2:] | add)}' \
     .dataparts/base.json .dataparts/crosscutting.json .dataparts/nodes-*.json;
  printf ';\n'; } > <브랜치>/data.js
```

- `.[0]` = base, `.[1]` = crosscutting, `.[2:]` = 노드 조각들(배열)로 `add` 해 이어붙임.
- `jq` 가 없으면 python 의 json 으로 동일 병합.
- 합침 후 `.dataparts/` 삭제. 이 디렉토리는 순수 중간물이라 삭제가 정상이다(렌더 입력이 아니라 출력 조립용 -- 다이어그램 등 렌더 입력은 facet 에 지속한다).

<PENETRATE>
render-data 는 슬라이스별 JSON 조각을 .dataparts/ 에 Write 하고, 메인이 jq 로 조각들을 하나의 window.DATA 객체로 합쳐 data.js 를 만든다(부피가 메인 컨텍스트를 거치지 않게).
</PENETRATE>

<RICOCHET>
완성 data.js 전체를 에이전트가 한 본문으로 반환하지 않는다(큰 산출은 단일 응답 토큰 한도에서 잘린다).
</RICOCHET>
