# Claude Plugins

> Claude Code CLI 에서 /plugin 명령어로 설치/관리하는 플러그인 목록.
> 외부 설치가 필요한 툴은 references/tools.md 참고.
> 모두 "이런게 있다" 수준의 참고 목록이며, 실제 도입 여부는 별도 검토 필요.

---

## 코드 설계 / 생성

### superpowers
- 설계 -> 계획 -> TDD 구현 -> 코드리뷰 -> 머지까지 전체 개발 사이클 자동화
- 슬래시 커맨드 + 서브에이전트 조합
- 링크: https://github.com/obra/superpowers
- 쓰면 좋을 때: 새 기능을 처음부터 설계하고 구현할 때

### gstack
- CEO, 디자이너, 엔지니어, QA 등 23개 역할의 슬래시 커맨드 스킬 묶음
- 링크: https://github.com/garrytan/gstack
- 쓰면 좋을 때: 역할별로 나눠서 설계/검토가 필요할 때

### backend-architect
- 백엔드 아키텍처 패턴, API 설계, DB 스키마, 시스템 설계 특화
- 쓰면 좋을 때: 새 서비스 아키텍처 설계 초기 단계

---

## 코드 분석 / 수정

### AgentLint
- AI 에이전트 호환성 검사. 5개 차원 33개 체크 항목
- 쓰면 좋을 때: 코드베이스를 Claude와 함께 쓰기 위한 구조 점검 시

### debugger
- 복잡한 버그 추적 및 수정 특화 어시스턴트
- 쓰면 좋을 때: 원인 파악이 어려운 버그 디버깅 시

### security-sweep
- OWASP Top 10 (2025), LLM Top 10 기반 보안 취약점 스캔
- 하드코딩 secrets, 인젝션, 인증 이슈, AI 특화 취약점 포함
- PreToolUse 훅으로 코드 생성 전에 먼저 잡아냄
- 쓰면 좋을 때: 보안 검토가 필요한 코드 작성/수정 시

---

## 문서화

### documentation-generator
- 코드를 분석해서 README, API 문서, 가이드 문서 자동 생성
- 주석 없이도 코드 구조를 이해해서 작성. 예시 코드, 설명, 주의사항 포함 가능
- 생성 결과는 md 포맷 -> VSCode에서 바로 확인, 필요 시 docusaurus로 웹 문서화
- tools.md의 pdoc/doxygen/cargo doc과 차이: 정형화된 API 문서가 아닌 사람이 읽기 좋은 가이드 문서 생성에 특화
- 쓰면 좋을 때: 코드 작성 후 유저 친화적인 문서가 필요할 때

---

## 코드 리뷰 / 피드백

> 멀티 에이전트 리뷰 파이프라인 (여러 에이전트 병렬 실행 -> 결과 취합 -> 교차 검증 -> 수정)은
> pipeline-analyze.md 참고. (TBD)

### pr-review-toolkit
- PR 리뷰 특화. 주석, 테스트, 에러 처리, 타입, 코드 품질, 단순화 등 6개 에이전트 병렬 실행
- 커맨드: `/pr-review-toolkit:review-pr`
- 쓰면 좋을 때: PR 머지 전 종합 리뷰 시

### code-review
- 베스트 프랙티스, 패턴, 개선 제안 중심 코드 리뷰
- 쓰면 좋을 때: 일반적인 코드 품질 리뷰 시

### security-guidance
- OWASP 가이드라인 기반 보안 베스트 프랙티스 및 취약점 탐지
- 쓰면 좋을 때: 보안 관점 코드 리뷰 시

---

## 테스트

### test-writer-fixer
- 유닛 테스트 자동 작성 및 수정. pytest, Jest, Vitest 지원
- 쓰면 좋을 때: 테스트 커버리지 확보 또는 실패한 테스트 수정 시

### ralph
- Claude Code를 완료 신호가 올 때까지 반복 실행하는 자율 루프
- 무한루프 방지, rate limiting, 진행 감지 포함
- 링크: https://github.com/frankbria/ralph-claude-code
- 쓰면 좋을 때: 테스트 통과까지 자동으로 반복 수정이 필요할 때

---

## 지식 관리

### qmd (사용 중)
- 로컬 md 파일 기반 하이브리드 검색 엔진
- BM25 + vector + LLM 리랭킹. 완전 로컬 실행 (클라우드 불필요)
- MCP 서버 포함 -> Claude Code에서 직접 연결 가능
- raw/wiki 디렉토리 구조와 연동해서 세션 간 산출물 조회에 사용
- 링크: https://github.com/tobi/qmd
- 쓰면 좋을 때: 세션 간 프로젝트 산출물 조회 시

### gbrain (도입 후보)
- 세션 간 지식 축적을 위한 Postgres 기반 지식베이스
- 하이브리드 검색 (vector + keyword + 그래프) 지원
- gstack과 연동 가능
- 링크: https://github.com/garrytan/gbrain
- 쓰면 좋을 때: 대규모 지식베이스가 필요하거나 의미 기반 횡단 검색이 필요할 때
