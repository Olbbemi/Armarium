# Armarium

**현재 버전: `0.32.0`**

개인 커스텀 스킬을 담아 **여러 프로젝트에서 공통으로 쓰는 비공개 Claude Code 플러그인**.

라틴어로 도구/책을 넣어두는 보관장(캐비닛)을 뜻한다. Hortus 네이밍 패밀리의 한 구역.

```
Hortus (정원 — 상위 우산)
├── Terrarium   작업 본체
├── Herbarium   지식 보존 아카이브 (확정지식 저장소)
└── Armarium    스킬·도구 보관장   <- 이 repo
```

---

## 이 repo의 역할

커스텀 스킬을 한 곳에서 버전관리하고, 플러그인으로 설치해 **어느 프로젝트에서나** 쓰기 위한 저장소.

- 프로젝트별 `.claude/skills/` 에 흩어두면 다른 프로젝트에서 못 쓴다 -> 플러그인으로 묶어 해결.
- **공개 마켓플레이스에 게시하지 않는다.** `marketplace.json` 은 repo 안 파일일 뿐이고, 사용자가 이 repo 를 직접 마켓플레이스로 add 해야 쓸 수 있다. (git repo 가 public 이어도 그건 일반 repo 노출이지 공개 마켓플레이스 등재가 아니다.)
- 플러그인이라 스킬뿐 아니라 **에이전트·규약(CLAUDE.md)·훅까지 묶어** 배포되어, 다른 프로젝트에서도 의존성 없이 자기완결로 동작한다.

---

## 구조

```
Armarium/
├── .claude-plugin/
│   ├── marketplace.json   # 이 repo 를 마켓플레이스로 선언 (name: hortus)
│   └── plugin.json        # 플러그인 정의 (name: armarium)
├── CLAUDE.md              # 커스텀 태그 등 규약 (자기완결)
├── agents/                # 스킬이 호출하는 서브에이전트 정의 (플러그인 루트)
│   ├── knowledge-writer.md
│   └── skill-verify-*.md
├── hooks/                 # 세션 시작 등 훅 스크립트 (플러그인 루트)
│   ├── hooks.json
│   └── session-skill-list.sh
├── references/            # 여러 스킬이 공유하는 참조 문서
│   └── knowledge-wip-protocol.md
└── skills/                # 스킬 본체 (각 디렉토리 = 스킬 1개, 각자 README.md 포함)
    ├── code-design/
    ├── code-analyze/
    ├── skill-writing/
    ├── skill-verify/
    ├── knowledge-capture/
    ├── knowledge-scan/
    ├── knowledge-study/
    └── knowledge-promote/
```

- `skills/<스킬>/SKILL.md` — 진입점. 보통 같은 디렉토리의 `overview.md` 를 로드해 따른다.
- `agents/` — 플러그인 루트에 두어야 `subagent_type` 으로 디스패치된다. 스킬 본문에서는 bare 이름(예: `knowledge-writer`)으로 부르고, 외부 노출 시 `armarium:` 네임스페이스가 붙는다.
- 스킬 본문의 파일 경로는 **플러그인 루트 상대**(`skills/...`, `agents/...`)로 쓴다. `.claude/skills/...` 같은 프로젝트 절대경로를 쓰지 않는다.

---

## 설치

`/plugin` 은 슬래시 명령이라 세션에서 직접 입력한다. 평생 1회면 된다.

```
/plugin marketplace add Olbbemi/Armarium
/plugin install armarium@hortus
/reload-plugins
```

- GitHub `owner/repo` 로 add 하면 Claude Code 가 자동으로 clone·캐시한다 (`~/.claude/plugins/`). 직접 clone 할 필요 없다.
- **user scope** 설치라 1회만 하면 어느 프로젝트에서 켜든 `armarium:<스킬>` 으로 노출된다.
- 등록이 바로 안 보이면 `/reload-plugins` 또는 새 세션.

---

## 세션 시작 배너

설치해 두면 새 세션 시작 시 화면 배너에 스킬 목록(이름 + 한 줄 설명)이 자동 표시된다.

- SessionStart 훅(`hooks/session-skill-list.sh`)이 `skills/*/SKILL.md` 를 훑어 목록을 만든다.
- 기존 대화를 잇는 맥락(resume·compact)에서는 배너를 안 띄운다.

같은 훅이 `knowledge-capture` 를 매 세션 자동 활성한다. 그 스킬의 `overview.md` 전문을 `additionalContext` 로 실어 보내므로, 슬래시 명령 없이도 활성 상태로 시작한다.

- 이 스킬만 예외다. 논의 중 지식 부재는 사용자가 스킬을 부를 생각을 못 하는 순간에 드러나므로, 명시 호출에만 의존하면 잡을 시점을 놓친다.
- 나머지 스킬은 목록만 노출하고 발동은 `description` 판단에 맡긴다.
- wip 저장 경로는 활성 시점이 아니라 첫 캡처가 확정될 때 묻는다. 캡처가 없는 세션은 아예 묻지 않는다.
- overview 를 런타임에 읽으므로 스킬을 고치면 다음 세션부터 자동 반영된다.

배너와 컨텍스트 주입은 별개 필드(`systemMessage` / `additionalContext`)라 따로 논다.

| source | 배너 | overview 주입 |
|--------|------|--------------|
| `startup` · `clear` | 띄움 | 함 |
| `resume` · `compact` | 안 띄움 | 함 |

`compact` 에서도 주입하는 것이 중요하다. 자동 압축은 앞서 넣은 overview 를 컨텍스트에서 날려버리므로, 여기서 다시 넣지 않으면 압축 이후 감시가 조용히 멈춘다.

---

## 수록 스킬

각 스킬의 상세는 해당 디렉토리의 README 참조.

| 스킬 | 요약 | 호출 |
|------|------|------|
| [`code-design`](skills/code-design/README.md) | 설계→구현→문서화 9단계 개발 파이프라인 지도. 현재 단계 판단·전환 규칙 | `/code-design`, "어디서부터 시작?" |
| [`code-analyze`](skills/code-analyze/README.md) | 코드를 구조·품질·변경 영향도·로직 요약 네 측면으로 분석 | `/code-analyze` (명시 호출) |
| [`skill-writing`](skills/skill-writing/README.md) | armarium 스킬 작성 규격 가이드 (구조·태그·프론트매터·에이전트) | `/skill-writing`, "스킬 만들어줘" |
| [`skill-verify`](skills/skill-verify/README.md) | 스킬이 `skill-writing` 규격·동작대로인지 7항목 검증 후 보고서 | `/skill-verify`, "스킬 검증해줘" |
| [`claude-md-verify`](skills/claude-md-verify/README.md) | 프로젝트 CLAUDE.md 품질을 16항목으로 검증 후 고침 제안 보고 | `/claude-md-verify`, "CLAUDE.md 검증해줘" |
| [`knowledge-capture`](skills/knowledge-capture/README.md) | 논의 중 전제 지식 부재를 감지해 wip 초안으로 누적 | 매 세션 자동 활성 (훅) |
| [`knowledge-scan`](skills/knowledge-scan/README.md) | 코드베이스를 훑어 쓰인 비자명 문법을 wip 초안으로 누적 | `/knowledge-scan` (명시 활성) |
| [`knowledge-study`](skills/knowledge-study/README.md) | CS 로드맵에서 미착수 주제를 골라 wip 초안으로 누적 | `/knowledge-study` (명시 활성) |
| [`knowledge-promote`](skills/knowledge-promote/README.md) | wip 초안을 정제해 확정지식으로 승급 | `/knowledge-promote` |

### knowledge 계열 4개의 관계

앞 3개가 wip 를 만들고 `knowledge-promote` 가 그것을 확정지식으로 올린다. 만드는 3개는 진입 경로만 다르고 산출물 형식이 같아서, 승급은 누가 만들었는지 따지지 않는다.

| 스킬 | 진입 | 앵커 | 수명주기 |
|------|------|------|---------|
| `knowledge-capture` | 대화 중 감지 또는 명시 요청 | 대화 발췌 | 활성 후 상시 |
| `knowledge-scan` | 코드베이스 스캔 명령 | 코드 발췌 | 단발 |
| `knowledge-study` | CS 로드맵에서 주제 선택 | 카탈로그 항목 | 단발 |

저장 경로 검증 · `knowledge-writer` 호출 · 반환 본문 저장은 만드는 3개가 [`references/knowledge-wip-protocol.md`](references/knowledge-wip-protocol.md) 를 공유한다. 스킬끼리는 서로를 참조하지 않는다.

네 스킬 모두 지식 저장소(**Herbarium**)의 `wip/` 와 `knowledge/` 를 읽고 쓴다. 경로는 스킬 본문에 박지 않고 사용자에게 입력받으며, 그 경로의 git origin remote 가 Herbarium 인지 검증한 뒤에만 채택한다. `knowledge-study` 는 로드맵 카탈로그가 있는 `roadmap/` 경로도 함께 받는다.

경로를 묻는 시점은 활성 방식에 따라 다르다. 사용자가 직접 부르는 `knowledge-scan` · `knowledge-study` · `knowledge-promote` 는 활성 직후에 묻고, 자동 활성되는 `knowledge-capture` 는 첫 캡처가 확정될 때까지 미룬다. 캡처 없이 끝나는 세션에 경로 질문을 띄우지 않기 위해서다.

---

## 새 스킬 추가

1. `skills/<새스킬>/SKILL.md` 작성 (frontmatter `name`, `description` 필수).
2. 같은 디렉토리에 `README.md` 작성 후 위 "수록 스킬" 표에 링크 추가.
3. 서브에이전트가 필요하면 `agents/<에이전트>.md` 에 정의.
4. 내부 경로는 플러그인 루트 상대(`skills/...`, `agents/...`)로 작성.
5. 커밋·푸시 후 아래 "업데이트" 흐름으로 반영.

---

## 버전 규칙

`.claude-plugin/plugin.json` 의 `version` 은 SemVer(`major.minor.patch`)를 따른다. **plugin payload**(`skills/`, `agents/`, `CLAUDE.md` 등 배포물)가 바뀔 때만 올리며, `.claude/`(dev 설정·push 훅)·`.planning/` 같은 비배포 파일은 버전과 무관하다.

| 등급 | 기준 | 예 |
|------|------|----|
| MAJOR `X.0.0` | 부르는 법·연동 규약이 깨짐 | 스킬/슬래시 명령 이름 변경·삭제, 호출·경로·등록 규약 변경, 필수 입력 추가, 명시한 보장 제거 |
| MINOR `0.X.0` | 사용자가 새로 할 수 있는 일이 생김 | 새 스킬·에이전트 추가, 새 옵션·입력 필드·트리거·지식 종류 노출 |
| PATCH `0.0.X` | 새 능력 없이 기존 것을 고치거나 다듬음 | 버그 수정, 문구·오타·README, 내부 리팩터링, 군더더기 제거·단순화, 스펙대로 동작 복원, 기존 규칙의 명확화·강화 |

등급은 위에서부터 질문 사다리로 판정한다.

1. **부르는 법·연동 규약이 바뀌어 기존 방식이 안 통하나?** -> MAJOR. 같은 이름·같은 입력이면 내부 동작을 근본적으로 갈아엎어도 MAJOR 가 아니다.
2. **이 변경으로 사용자가 *새로* 할 수 있게 된 일이 있나?** -> MINOR. 검증을 더 빡세게 거는 등 기존 동작을 조이는 것은 새 능력이 아니다.
3. 둘 다 아니다 -> PATCH. 스킬 문서를 고쳤다는 사실만으로 MINOR 가 되지 않는다. 명확화·교정·단순화·동작 정합 복원은 PATCH 다.

- **0.x 단계:** 스킬 셋과 호출 규약이 안정될 때까지는 1.0 전이며, 이 동안엔 큰 변경도 0.x 안에서 MINOR로 흡수해도 된다. 안정되면 `1.0.0` 으로 올린다.
- 버전을 안 올리고 push 하면 `/plugin marketplace update` 가 변경을 받아오지 않는다. push 직전 확인 훅이 이를 잡아준다.

### 버전 올릴 때 고치는 곳 (3군데, 같은 값으로)

버전을 올릴 때 아래 **세 파일을 모두 같은 값으로** 바꾼다. 하나라도 빠지면 카탈로그 버전이 어긋나거나 README 표기가 실제와 달라진다.

| # | 파일 | 위치 | 자동 검사 |
|---|------|------|----------|
| 1 | `.claude-plugin/plugin.json` | `"version"` 필드 | push 훅이 직전 푸시 대비 상승 여부 검사 |
| 2 | `.claude-plugin/marketplace.json` | 해당 플러그인의 `"version"` 필드 | push 훅이 plugin.json 과 parity 검사 |
| 3 | `README.md` | 상단 `**현재 버전: ...**` 줄 | push 훅이 plugin.json 과 parity 검사 |

`check-version-bump.sh` 훅은 1·2·3 세 곳을 모두 잡는다 — plugin.json 의 직전 푸시 대비 상승, marketplace.json parity, README 상단 표기 parity 를 검사한다. 그래도 버전을 올릴 때 세 곳을 같은 값으로 함께 바꾼다.

---

## 업데이트

소스 저장소(`/home/olbbemi/Project/Armarium`)를 고쳐 GitHub 에 올리고 설치처(캐시)를 갱신하는 흐름이다. 설치된 플러그인은 `~/.claude/plugins/cache/...` 의 읽기전용 사본이라 직접 고치지 않는다.

1. 소스 저장소에서 수정 -> commit -> push
2. 의미 있는 변경이면 `.claude-plugin/plugin.json` 의 `version` 을 올린다 (안 올리면 update 가 변경을 받아오지 않는다).
3. `/plugin marketplace update hortus` -> `/reload-plugins`

> push 시 `version` 미변경을 잡아주는 확인 훅이 `.claude/settings.json` 에 있다 (armarium 저장소에서 작업할 때만 동작).
