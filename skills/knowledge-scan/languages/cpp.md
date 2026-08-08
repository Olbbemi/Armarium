> 역할: `knowledge-scan` 스킬(`skills/knowledge-scan/overview.md`)에서 대상이 C++ 일 때, `knowledge-code-scanner` 에이전트가
>        로드해 코드베이스와 대조하는 "정리할 만한 비자명 문법/기능" 카탈로그.
>        스캐너는 이 목록에 오른 기능이 코드에 실제로 쓰였는지 탐지하고, 각 항목의 정식 topic 명칭을
>        dedup 파일명·wip topic 으로 그대로 쓴다. 언어를 추가하려면 이 디렉토리에 `<lang>.md` 를 더한다.

# C++ 비자명 문법 카탈로그

## 제외 기준 (카탈로그에 넣지 않는 것)

언어의 기본기는 후보로 뽑지 않는다 -- 어차피 아는 것을 다시 정리하는 낭비다.

- 기본 제어흐름: `if` / `for` / `while` / `switch`
- 기본 타입·연산·함수 정의, 기본 클래스/구조체 선언, 단순 상속
- 표준 컨테이너의 단순 사용(`vector`/`map` 에 넣고 빼는 정도)

아래 목록에 오른 기능이 **코드에 실제로 쓰였을 때만** 후보가 된다. 목록에 없는데 비자명해 보이는 기능을 발견하면 후보 반환 시 별도로 표시해 사람이 카탈로그 보강 여부를 판단하게 한다.

## 카탈로그

각 항목: `정식 topic 명칭` -- 코드에서 알아볼 신호(키워드/토큰) / 무엇을 정리할지 한 줄.

신호는 그 토픽을 확실히 대표하는 **강앵커**로 적는다. 이 스킬은 사용처를 전수 조사하는 게 아니라 "이 토픽이 이 코드베이스에 쓰였나" 를 한 번 감지하는 것이라, 토픽마다 강앵커 하나만 걸리면 충분하다. 그래서 `&&`(논리 AND 와 구분 불가) · `|`(비트 OR) · 맨 `auto` 처럼 흔하고 모호한 토큰은 오탐만 늘리므로 신호로 쓰지 않는다. 같은 토픽을 대표하는 더 고유한 토큰(`std::move`, `std::ranges::`, `auto [` 등)이 있으면 그것만 신호로 둔다. 고유 강앵커가 없는 소수 항목(`ctad`, `raii-idioms`, `rule-of-zero-three-five`, `lambda-advanced`)은 문맥 확증에 기대며 recall 이 제한적임을 감수하고, 아래에서 항목별로 신호를 따로 명시한다.

### 템플릿 · 제네릭

- `templates-metaprogramming` -- `template<...>`, 부분·명시 특수화, `std::enable_if`, 태그 디스패치. 컴파일 타임 분기·특성 추론.
- `concepts` -- `concept`, `requires`, 제약된 `auto`/템플릿 인자. 템플릿 제약과 오류 메시지 개선.
- `variadic-templates` -- `template<typename... Ts>`, 파라미터 팩 `Ts...`, 팩 확장. 가변 인자 제네릭.
- `fold-expressions` -- `(... op pack)`, `(pack op ...)`. 파라미터 팩 접기.
- `ctad` -- 고유 강앵커 없음. 사용자 정의 추론 가이드(`-> 클래스명`)와 명시 인자 없는 클래스 템플릿 생성(`std::pair{...}` 등)을 문맥으로 확증. recall 제한적.

### 값 · 자원 · 수명

- `move-semantics` -- 강앵커 `std::move(`. 맨 `&&` 우변참조는 논리 AND 와 안 갈려 신호에서 뺀다 -- `std::move` 하나로 토픽이 잡힌다. 소유권 이전과 복사 회피.
- `perfect-forwarding` -- 강앵커 `std::forward`. 맨 `T&&` 포워딩 참조는 신호에서 뺀다. 인자 완전 전달.
- `smart-pointers` -- `unique_ptr` / `shared_ptr` / `weak_ptr`, `make_unique`/`make_shared`. 소유권 표현과 수명 관리.
- `raii-idioms` -- 고유 토큰 없음. 소멸자에서 자원을 해제하는 사용자 래퍼·스코프 가드를 문맥으로 확증. recall 제한적. 예외 안전한 자원 해제.
- `rule-of-zero-three-five` -- 특수 멤버(복사/이동 생성·대입, 소멸자)의 `=default`/`=delete` 조합. 값 시맨틱 설계.

### 컴파일 타임

- `constexpr-consteval` -- `constexpr` / `consteval` / `constinit`, 컴파일 타임 계산. 런타임 비용 제거·상수 보장.
- `if-constexpr` -- `if constexpr (...)`. 컴파일 타임 분기로 미선택 분기 인스턴스화 제거.
- `type-traits` -- `<type_traits>` 의 `std::is_*`, `std::decay_t` 등. 타입 특성 질의·변환.

### 함수 · 호출

- `lambda-advanced` -- 고유 강앵커 약함. 초기화 캡처(`[x = ...]`) · `mutable` 람다 · 제네릭 람다(`auto` 인자)를 신호로 보되, 단순 인라인 콜백(`[](){}`)은 제외한다. 맨 `[]`/`[&]` 만으로 잡지 않는다. recall 제한적.
- `std-function-bind` -- `std::function`, `std::bind`, 호출 가능 객체 추상화.
- `structured-bindings` -- `auto [a, b] = ...`. 튜플/구조체/맵 원소 분해.

### 라이브러리 · 관용구

- `ranges` -- 강앵커 `std::ranges::` / `views::`(`views::filter`/`transform` 등). 파이프 `|` 는 비트 OR 와 안 갈려 신호에서 뺀다. 지연 평가 시퀀스 변환.
- `coroutines` -- `co_await` / `co_yield` / `co_return`, `promise_type`. 중단 가능 함수.
- `optional-variant-any` -- `std::optional` / `std::variant` / `std::any`, `std::visit`. 합타입·부재 표현.
- `three-way-comparison` -- `operator<=>`, `std::strong_ordering`. 비교 연산 자동 생성.
- `span-string-view` -- `std::span` / `std::string_view`. 비소유 뷰로 복사 없이 참조.
- `concurrency-primitives` -- `std::thread`/`jthread`, `mutex`/`lock_guard`/`scoped_lock`, `atomic`, `condition_variable`, `future`/`promise`. 동시성 기본 도구.
