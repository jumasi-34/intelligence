# GEMINI.md (hook/ 로컬 가이드라인 및 인덱스)

이 문서는 `intelligence/hook/` (다차원 라이프사이클 이벤트 인터셉터 레이어) 고유의 로컬 규칙과 파일 정보를 신속히 인지하기 위한 마이크로 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **이벤트 라우팅 책임 (Single Responsibility)**: 인터셉터는 특정 이벤트(Git Commit, 세션 상태 변경, DB 변경, API 호출 등)를 캡처하고, 해당 상황에 정합하는 `guardrail/` 검증기 또는 `skill/` 도구를 구동하는 **라우팅 및 흐름 제어**에 집중해야 합니다. 복잡한 무결성 검증 규칙이나 도메인 산식을 인터셉터 내부에 직접 하드코딩하지 마십시오.
* **이벤트 불변성 (Event Immutability)**: 인터셉터는 감지된 원본 이벤트를 임의로 변경하거나 훼손해서는 안 됩니다. 읽기 전용으로 가이드라인을 기동하거나, 위반 시 단호하게 예외를 던져 실행 트랜잭션을 차단(Abort)하는 품질 게이트 역할에 한정되어야 합니다.
* **다차원 확장성 (Multi-dimensional Hooks)**:
  - **Git Hook**: 코드 커밋(`pre-commit`) 및 병합(`post-merge`) 시점의 정적 정합성 검증 트리거.
  - **UI/Session Hook**: Streamlit UI 라이프사이클 상에서 세션 상태 초기화, 세션 변수 변동 및 특정 렌더링 라이프사이클 인터셉트 트리거.
  - **Data/DB Hook**: 데이터 이관, 동기화 및 SQLite 등 운영 참조 DB의 CRUD 트랜잭션 발생 시점에 연동하는 정합성 검증 트리거.
  - **Agent Run Hook**: 에이전트 자율 가동(Agent Run)의 실행 시작, 종료, 비정상 중단 상태를 관측 및 모니터링하여 로그 분석을 기동하는 라이프사이클 인터셉트 트리거.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `hooks-specification.md` | 다차원 라이프사이클 이벤트 인터셉터 아키텍처 및 인터페이스 규격 정의서 |
| `agent_runs_observer.py` | 에이전트 자율 작업(Agent Run)의 라이프사이클 이벤트를 관측하고 후속 조치를 트리거하는 분석 인터셉터 |
| `agent_runs_analyzer.py` | 누적된 에이전트 실행 로그(runs) 이벤트를 수집하여 이상 동작 유무를 판별하는 훅 모듈 |
| `release_ops_hooks.py` | 코드 릴리즈 및 인프라 프로덕션 배포 단계의 품질 게이트 승인 이벤트를 가로채 가드레일을 구동하는 훅 |
| `reverse_sync.py` | 로컬(WSL)과 원격(Ubuntu) 간의 자산 및 데이터 동기화 이벤트를 트리거하고 로그를 제어하는 동기화 훅 |

---

## 3. 변경 이력 (Changelog)

* **2026-06-14**:
  * [REFACTOR] `hook/` 레이어를 단순 Git Hook에서 '다차원 라이프사이클 이벤트 인터셉터 (Multi-dimensional Interceptor)'로 격상. Git, UI 세션, DB CRUD, 에이전트 실행 상태 전반을 관장하도록 로컬 제약 수립.
  * [Feat] 인터셉터 폴더 전용 `GEMINI.md` 최초 비치.
