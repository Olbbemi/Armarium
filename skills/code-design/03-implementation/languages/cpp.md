> **이름:** `cpp.md`
> **역할:** 3단계 구현에서 C++ 사용 시 참조하는 reference. 빌드 시스템 / 테스트 프레임워크 / 의존성 관리 명령과 C++ 관용 패턴을 모은다. 흐름 variant 파일의 사전 조사 / 작업 흐름에서 언어별 명령이 필요할 때 로드된다.

# C++ 언어 reference

---

## 표준 도구 (기본값)

| 영역 | 기본 | 대안 |
|------|------|------|
| 빌드 시스템 | CMake (3.20+) | Bazel |
| 패키지 / 의존성 | vcpkg | Conan, FetchContent |
| 테스트 프레임워크 | GoogleTest (gtest) | Catch2 |
| 포맷팅 | clang-format | - |
| 정적 분석 | clang-tidy | cppcheck |
| 표준 | C++20 | C++17 (필요 시) |

대안을 선택할 사유가 있으면 사용자에게 질문 (공통 원칙 1).

---

## 디렉토리 레이아웃

```
프로젝트 루트/
├── CMakeLists.txt
├── vcpkg.json              # vcpkg 사용 시
├── include/                # public 헤더
│   └── {project}/
├── src/                    # 구현
│   └── {module}.cpp
└── tests/                  # 테스트
    └── test_{module}.cpp
```

---

## 명령 매핑

### 초기화 (새 프로젝트 - 흐름 A)

```bash
# CMakeLists.txt 작성 후
cmake -B build -DCMAKE_BUILD_TYPE=Debug
```

### 의존성 추가 (vcpkg)

```bash
vcpkg add port {package_name}    # vcpkg.json 갱신
cmake -B build                    # 재구성
```

### 빌드

```bash
cmake --build build
```

### 테스트 실행

```bash
ctest --test-dir build --output-on-failure
```

### 포맷팅 / 린트

```bash
clang-format -i src/**/*.cpp include/**/*.hpp
clang-tidy src/**/*.cpp
```

---

## TDD 사이클 명령 매핑

| 사이클 단계 | 명령 |
|-----------|------|
| 테스트 작성 후 실패 확인 (Red) | `ctest --test-dir build -R {test_name}` |
| 구현 후 통과 확인 (Green) | `ctest --test-dir build -R {test_name}` |
| 전체 테스트 재실행 (Refactor) | `ctest --test-dir build --output-on-failure` |

---

## 관용 패턴 / 주의 사항

- **헤더 / 소스 분리:** public 인터페이스는 `include/` 의 `.hpp`, 구현은 `src/` 의 `.cpp`
- **헤더 가드:** `#pragma once` 권장 (또는 include guard 매크로)
- **RAII:** 자원 관리는 스마트 포인터 / RAII 객체로. raw `new` / `delete` 금지
- **표준 명시:** `CMakeLists.txt` 에 `set(CMAKE_CXX_STANDARD 20)` 명시
- **컴파일러 경고:** `-Wall -Wextra -Wpedantic` 활성화 권장
- **테스트 빌드 분리:** 테스트는 별도 타겟. production 빌드에 포함 X
- **lock 파일:** `vcpkg.json` 의 baseline / overrides 로 버전 고정. 커밋 권장
