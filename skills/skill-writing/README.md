# skill-writing

새 스킬을 만들고 고칠 때 쓰는 스킬.

규격과 규칙은 이 디렉토리가 소유하지 않는다. 절차는 `core/core.md`, 산출물 규칙은 `rules/`,
규칙 셋 자체의 규격은 `engine/meta-rules/` 에 있다. 여러 스킬이 쓰는 것이라 루트에 둔다.

## 구조

| 경로 | 내용 |
|---|---|
| `SKILL.md` | Claude Code 진입점 |
| `procedure.md` | 새 스킬을 만드는 절차. 무엇이 스킬인가와 무엇을 쪼개는가 |

규칙은 갖지 않는다. 이 스킬에서만 참인 규칙이 아직 없기 때문이다.

## 실행

```
python3 engine/verify.py --path skills/skill-writing
```
