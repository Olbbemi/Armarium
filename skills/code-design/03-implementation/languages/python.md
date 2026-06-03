> **이름:** `python.md`
> **역할:** 3단계 구현에서 Python 사용 시 참조하는 reference. 빌드 / 테스트 / 의존성 명령과 Python 관용 패턴을 모은다. 흐름 variant 파일의 사전 조사 / 작업 흐름에서 언어별 명령이 필요할 때 로드된다.

# Python 언어 reference

---

## 표준 도구 (기본값)

| 영역 | 기본 | 대안 |
|------|------|------|
| 패키지 / 가상환경 | poetry | pip + venv, uv |
| 테스트 프레임워크 | pytest | unittest (표준 라이브러리) |
| 포맷팅 | ruff format | black |
| 정적 분석 | ruff | flake8, pylint |
| 타입 체크 | mypy | pyright |
| 버전 명세 | pyproject.toml | - |

대안을 선택할 사유가 있으면 사용자에게 질문 (공통 원칙 1).

---

## 디렉토리 레이아웃 (src layout 권장)

```
프로젝트 루트/
├── pyproject.toml
├── poetry.lock              # poetry 사용 시
├── src/
│   └── {package}/
│       ├── __init__.py
│       └── {module}.py
└── tests/
    └── test_{module}.py
```

src layout 대신 flat layout 을 쓸 사유가 있으면 사용자에게 질문.

---

## 명령 매핑

### 초기화 (새 프로젝트 - 흐름 A)

```bash
poetry init                       # 또는 직접 pyproject.toml 작성
poetry install
```

### 의존성 추가

```bash
poetry add {package}              # 런타임 의존성
poetry add --group dev {package}  # 개발 의존성
```

### 빌드 / 실행

```bash
poetry run python -m {package}    # 모듈 실행
poetry build                       # 배포 패키지 생성
```

### 테스트 실행

```bash
poetry run pytest
poetry run pytest -k {pattern}    # 특정 테스트만
```

### 포맷팅 / 린트 / 타입 체크

```bash
poetry run ruff format src tests
poetry run ruff check src tests
poetry run mypy src
```

---

## TDD 사이클 명령 매핑

| 사이클 단계 | 명령 |
|-----------|------|
| 테스트 작성 후 실패 확인 (Red) | `poetry run pytest tests/test_{module}.py::{test_name}` |
| 구현 후 통과 확인 (Green) | 동일 |
| 전체 테스트 재실행 (Refactor) | `poetry run pytest` |

---

## 관용 패턴 / 주의 사항

- **type hint:** 모든 public 함수에 type hint 작성. `from __future__ import annotations` 권장
- **`__init__.py`:** 패키지 디렉토리에는 빈 `__init__.py` 라도 작성
- **가상환경 분리:** 시스템 Python 에 직접 설치 금지 (poetry / venv 사용)
- **import 순서:** 표준 라이브러리 -> 외부 라이브러리 -> 로컬 (ruff 가 자동 정렬)
- **pytest fixture:** 공용 픽스처는 `tests/conftest.py` 에
- **pyproject.toml:** 모든 도구 설정 (ruff, mypy, pytest) 을 한 파일에 모음
- **lock 파일:** `poetry.lock` 커밋 권장 (재현성)
