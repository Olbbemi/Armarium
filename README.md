# Armarium

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
- **공개 마켓플레이스에 게시하지 않는다.** `marketplace.json` 은 repo 안 파일일 뿐이고, 로컬 경로로 등록한다. (git repo 자체가 public 이어도 그건 일반 repo 노출이지 마켓플레이스 공개가 아니다.)
- 플러그인이라 스킬뿐 아니라 **에이전트·규약(CLAUDE.md)·훅까지 묶어** 배포되어, 다른 프로젝트에서도 의존성 없이 자기완결로 동작한다.

---

## 구조

```
Armarium/
├── .claude-plugin/
│   ├── marketplace.json   # 이 repo 를 마켓플레이스로 선언 (name: hortus)
│   └── plugin.json        # 플러그인 정의 (name: armarium)
├── CLAUDE.md              # 커스텀 태그 등 규약 (자기완결)
├── agents/                # 스킬이 호출하는 서브에이전트 정의
│   └── knowledge-writer.md
└── skills/                # 스킬 본체 (각 디렉토리 = 스킬 1개)
    ├── knowledge-capture/
    └── knowledge-promote/
```

- `skills/<스킬>/SKILL.md` — 진입점. 보통 같은 디렉토리의 `overview.md` 를 로드해 따른다.
- `agents/` — 플러그인 루트에 두어야 `subagent_type` 으로 디스패치된다. 스킬 본문에서는 bare 이름(예: `knowledge-writer`)으로 부르고, 외부 노출 시 `armarium:` 네임스페이스가 붙는다.
- 스킬 본문의 파일 경로는 **플러그인 루트 상대**(`skills/...`, `agents/...`)로 쓴다. `.claude/skills/...` 같은 프로젝트 절대경로를 쓰지 않는다.

---

## 설치

`/plugin` 은 슬래시 명령이라 세션에서 직접 입력한다.

```
/plugin marketplace add /home/olbbemi/Project/Armarium
/plugin install armarium@hortus
```

- 경로는 **로컬 경로**로 등록한다. 작성 중에는 편집이 바로 반영되어 편하다.
- 다른 머신에서는 이 repo 를 clone 한 뒤 그 경로를 add 하거나, git URL 로 add 한다.
- 설치 후 스킬은 `armarium:knowledge-capture` 식으로 노출된다. 등록이 바로 안 보이면 새 세션을 시작한다.

---

## 수록 스킬

| 스킬 | 역할 |
|------|------|
| `knowledge-capture` | 논의 중 전제 지식 부재를 감지해 wip 초안으로 누적. `knowledge-writer` 에이전트에 작성 위임 |
| `knowledge-promote` | wip 초안을 정제해 확정지식으로 승급 |

두 스킬은 지식 저장소(**Herbarium**)의 `wip/` 와 `knowledge/` 를 읽고 쓴다. 기본 경로는 `/home/olbbemi/Project/Herbarium` 이며, 스킬 본문에 박혀 있다.

> 나머지 커스텀 스킬(code-design, skill-writing, skill-verify, code-analyze 등)은 순차 이관 예정.

---

## 새 스킬 추가

1. `skills/<새스킬>/SKILL.md` 작성 (frontmatter `name`, `description` 필수).
2. 서브에이전트가 필요하면 `agents/<에이전트>.md` 에 정의.
3. 내부 경로는 플러그인 루트 상대(`skills/...`, `agents/...`)로 작성.
4. 로컬 경로 설치 상태면 편집 즉시 반영, 안 되면 `/plugin marketplace update` 후 새 세션.

---

## 업데이트

- **이 머신(로컬 경로 설치)**: 파일 편집 -> 바로 반영 (필요 시 새 세션).
- **다른 머신(git 설치)**: `git pull` 후 `/plugin marketplace update`.
