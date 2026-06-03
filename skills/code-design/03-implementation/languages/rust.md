> **이름:** `rust.md`
> **역할:** 3단계 구현에서 Rust 사용 시 참조하는 reference. 빌드 / 테스트 / 의존성 명령과 Rust 관용 패턴을 모은다. 흐름 variant 파일의 사전 조사 / 작업 흐름에서 언어별 명령이 필요할 때 로드된다.

# Rust 언어 reference

---

## 표준 도구 (기본값)

| 영역 | 기본 | 대안 |
|------|------|------|
| 빌드 / 패키지 / 의존성 | cargo (표준) | - |
| 테스트 프레임워크 | `cargo test` (내장) | cargo-nextest |
| 포맷팅 | rustfmt | - |
| 정적 분석 | clippy | - |
| 에디션 | 2021 | 2024 (필요 시) |

대안을 선택할 사유가 있으면 사용자에게 질문 (공통 원칙 1).

---

## 디렉토리 레이아웃

### 라이브러리 + 바이너리 혼합 (권장 패턴)

```
프로젝트 루트/
├── Cargo.toml
├── Cargo.lock
├── src/
│   ├── lib.rs               # 라이브러리 진입점
│   ├── main.rs              # 바이너리 진입점 (있는 경우)
│   └── {module}.rs          # 또는 {module}/mod.rs
└── tests/                   # 통합 테스트
    └── {test}.rs
```

단위 테스트는 같은 파일 안 `#[cfg(test)] mod tests` 안에 작성.

---

## 명령 매핑

### 초기화 (새 프로젝트 - 흐름 A)

```bash
cargo init --lib              # 라이브러리
cargo init --bin              # 바이너리
```

### 의존성 추가

```bash
cargo add {crate}
cargo add --dev {crate}       # 개발 의존성
```

### 빌드

```bash
cargo build                    # debug
cargo build --release          # 최적화
```

### 테스트 실행

```bash
cargo test
cargo test {test_name}         # 특정 테스트만
cargo test -- --nocapture      # println! 출력 보기
```

### 포맷팅 / 린트

```bash
cargo fmt
cargo clippy -- -D warnings    # 경고를 에러로 처리
```

---

## TDD 사이클 명령 매핑

| 사이클 단계 | 명령 |
|-----------|------|
| 테스트 작성 후 실패 확인 (Red) | `cargo test {test_name}` |
| 구현 후 통과 확인 (Green) | 동일 |
| 전체 테스트 재실행 (Refactor) | `cargo test` |

---

## 관용 패턴 / 주의 사항

- **lib.rs vs main.rs:** 재사용 가능한 로직은 `lib.rs` 로 분리. `main.rs` 는 entry point 만
- **mod 구조:** `mod {name};` 으로 모듈 선언. 파일은 `{name}.rs` 또는 `{name}/mod.rs`
- **Result / Option 우선:** `panic!` / `unwrap()` 은 정말 불변량이 깨졌을 때만
- **ownership:** `Clone` 남발 X. 가능하면 borrow (`&`) 우선
- **`?` 연산자:** 에러 전파는 `?` 로. `match` 남발 X
- **clippy 경고:** CI 에서 `cargo clippy -- -D warnings` 로 강제
- **edition:** `Cargo.toml` 에 `edition = "2021"` 명시
- **lock 파일:** 바이너리 프로젝트는 `Cargo.lock` 커밋, 라이브러리는 커밋 안 함이 일반적
