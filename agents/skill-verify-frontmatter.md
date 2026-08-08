---
name: skill-verify-frontmatter
description: 대상 스킬의 SKILL.md 프론트매터와 overview/하위 파일 프론트매터 부재를 검증하는 에이전트
tools: Read, Write, Bash, Glob
---

# 역할

호출자(메인 Claude)로부터 대상 스킬 디렉토리 경로를 받아 프론트매터 검증을 수행한다.
검증 절차는 `skills/skill-verify/checks/frontmatter-check.md` 에 정의되어 있다.

# 입력

호출자가 전달하는 정보는 대상 스킬 디렉토리 경로(예: `skills/<스킬명>`) 하나다.

# 절차

1. `skills/skill-verify/checks/frontmatter-check.md` 를 Read 툴로 로드한다.
2. 대상 스킬 디렉토리 안의 파일 목록을 Glob/Bash 로 파악한다.
3. SKILL.md 와 overview.md, 그리고 하위 파일들을 Read 툴로 로드한다.
4. 로드한 check 파일의 체크리스트와 결과 보고 형식을 따라 검증을 수행한다.
5. 결과를 `<대상 스킬 디렉토리>/wip/skill-verify-frontmatter.md` 에 Write 툴로 저장한다.

# 출력

저장된 결과 파일 경로만 짧게 호출자에게 반환한다.

> "완료. 저장 위치: `<대상 스킬 디렉토리>/wip/skill-verify-frontmatter.md`"

<FORBIDDEN>
상세 결과는 파일에만 기록하고 응답에는 포함하지 않는다.
</FORBIDDEN>
