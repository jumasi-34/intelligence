# intelligence/ (인텔리전스 및 에이전트 확장 레이어)

이 디렉터리는 본 제조 품질 모니터링 시스템의 데이터를 지능적으로 분석하고 자율적인 품질 의사결정을 자동화하기 위해 설계된 인텔리전스 확장 및 AI 에이전트 구동 공간입니다.

최근 바이브코딩 이후 산재되어 있던 소형 컨텍스트 문서들을 핵심 연합 원장 문서(SSOT)로 전면 통합하여, 시스템 부하와 토큰 오버헤드를 최적화하고 에이전트의 상황 인지(Context) 정밀도를 극대화하였습니다.

---

## 1. 핵심 아키텍처 및 폴더 구조

```
intelligence/
├── README.md                  # 본 인텔리전스 레이어 종합 안내서
├── agent/                     # 자율 작업 및 의사결정을 수행하는 에이전트 설계 공간
│   ├── GEMINI.md              # 에이전트 협업 관계 및 역할 매니페스트 통합 원장 (SSOT)
│   └── agents_registry.json   # 에이전트 명세 단일 진실 공급원 (JSON)
│
├── domain/                    # 비즈니스 도메인 지식 베이스
│   └── domain-knowledge.md    # 6대 품질 도메인 지표 및 규칙 연합 지식 원장 (SSOT)
│
├── infra/                     # 공용 인프라스트럭처 사양 및 데이터베이스 메타데이터
│   ├── infrastructure-summary.md # 5대 핵심 인프라 영역 공용 연합 요약서 (SSOT)
│   └── (기타 스키마 검증 및 메타데이터 관리 스크립트)
│
├── guide/                     # 애플리케이션 개발 프로세스 및 핵심 가이드라인
│   ├── 3layer-development-process.md # 3-Layer 물리 격리 및 최초 보안 규정
│   ├── error-handling.md             # 에러 격리(Error Boundary) 및 SQLite 로깅 가이드
│   ├── testing-verification.md       # 테스트 격리 원칙, Golden Schema 및 정적 검증 가이드
│   └── (기타 템플릿 및 양식 문서)
│
├── hook/                      # 시스템 이벤트 훅 및 트리거 로직 공간
│   ├── hooks-specification.md # 3단계 품질 게이트 및 릴리즈 훅 규격서 (SSOT)
│   └── (훅 감지기 및 모니터링용 파이썬 스크립트)
│
├── rules/                     # 에이전트 행동 및 설계 규정 저장소
│   ├── L1-git.md              # 한국어 기반 커밋 및 Dual Push 규정 표준 (SSOT)
│   └── L2-architecture.md     # L2 아키텍처 및 코딩 규칙 단일 진실 공급원 (SSOT)
│
├── runs/                      # 에이전트 자율 작업 이력(Runs) 보관 공간
│   └── run_*/                 # 고유 RUN_ID별 7대 아티팩트 자동 저장소
│
└── note/                      # AI 읽기 금지 구역 (Private User Space)
```

---

## 2. 레이어별 주요 역할 및 SSOT 연합 문서

### (1) agent/ (자율 에이전트 레이어)
* **역할**: Planner, Builder, Analyst, Evaluator 등 구체적인 역할을 지닌 지능형 서브에이전트가 배치되어 역할을 수행합니다.
* **동기화**: 에이전트들의 역할이나 협업 관계가 변경될 때 마크다운 가이드를 직접 수정하지 않고, `agents_registry.json`을 수정한 뒤 `python skill/skill_sync_agents.py` 스크립트를 기동하여 모든 상세 가이드와 `agent/GEMINI.md` 표/다이어그램을 자동 동기화합니다.

### (2) domain/ (도메인 지식 베이스)
* **SSOT 문서**: `domain/domain-knowledge.md`
* **내용**: CQMS, GMES, IQM, QRS, 알림 메일, 운영 DB 등의 6대 핵심 비즈니스 도메인의 지표 수식과 데이터 집계 룰을 하나의 마크다운 파일로 완결성 있게 통합 관리합니다.

### (3) infra/ (공용 인프라 사양)
* **SSOT 문서**: `infra/infrastructure-summary.md`
* **내용**: API 계약, 인사 정보 및 권한 인증, Databricks 과금 비용 통제, SQLAlchemy 다중 DB 커넥션 자원 관리, AI 하네스 보안 등 5대 기술 인프라 규칙과 필수 테스트 시나리오를 집대성한 사양 요약서입니다.

### (4) guide/ (개발 및 운영 지침)
* **핵심 가이드**:
  * `guide/error-handling.md`: 특정 차트나 컴포넌트 에러 시 전체 페이지 중단 없이 격리 렌더링을 보장하는 에러 격리(Error Boundary) 기술과 SQLite `app_error_logs` 테이블 영구 적재 사양을 가이드합니다.
  * `guide/testing-verification.md`: 원천 데이터베이스를 오염시키지 않는 인메모리 테스트 기법(Mocking), 골든 스키마 준수 및 `verify_code.py` 정적 코드 컴파일 검증 기동 방법을 다룹니다.

### (5) hook/ (이벤트 훅 레이어)
* **SSOT 문서**: `hook/hooks-specification.md`
* **내용**: 커밋과 푸시 시 문법 오류를 잡는 3단계 로컬 품질 게이트 사양부터, 에이전트 실행 시 7대 아티팩트를 보존하는 Runs Observer, 장애 상황을 분석하고 롤백 대책을 수동으로 수립하는 4대 릴리즈 운영 훅까지 아우릅니다.

### (6) rules/ (규정 및 가이드라인)
* **핵심 규칙**:
  * `rules/L2-architecture.md`: SQL 5대 불변 규칙, Pandas 메서드 체이닝 표준, UI 6대 정합성 수칙 등 코딩과 아키텍처적 경계를 분리하는 정밀한 규칙들을 정의합니다.

---

## 3. 에이전트 작동 시 주의 및 제한 사항

* **Safety Lock (기존 소스 변경 금지)**: 사용자의 명시적인 수정 승인 없이는 프로덕션 영역(`app/` 하위 및 `app.py`)의 소스 코드를 임의로 수정하는 행위가 완전히 금지되어 있습니다.
* **AI 읽기 금지 구역 (Exclusion Zone)**: `intelligence/note/` 및 그 하위 디렉터리는 사용자의 개인 기록 보관 영역이므로 AI가 `list_dir`, `view_file`, `grep_search` 등으로 어떠한 경우에도 조회 또는 참조하지 않아야 합니다.
* **이모지 사용 전면 금지**: UI 상은 물론이고 `intelligence/` 내에 작성되는 모든 문서와 주석 내에서 유니코드 이모지(Emoji) 사용을 금지합니다.
