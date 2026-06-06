# 커스텀 태그

이 플러그인(armarium)의 스킬 파일에서 절대 규칙을 표시할 때 쓰는 태그.

- `<PENETRATE>` — 반드시 실행한다. 어떤 상황에서도 예외 없음.
- `<RICOCHET>` — 절대 실행하지 않는다. 맥락과 무관하게 차단한다.

한 태그 블록 안에 "수행"과 "금지"를 섞지 않는다. 수행 규칙은 `<PENETRATE>`, 금지 규칙은 `<RICOCHET>` 로 분리해 표기한다.

# 버전 규칙

플러그인 버전을 올릴 때 `.claude-plugin/plugin.json` 과 `.claude-plugin/marketplace.json` 의 `version` 을 **항상 같은 값으로 함께** 올린다. 둘 중 하나만 올리면 `/plugin marketplace update` 시 카탈로그 버전이 어긋나 업데이트가 제대로 반영되지 않는다.

# 커밋 규칙

커밋 로그(커밋 메시지)는 영어로 작성한다.
