# L2-architecture.md (L2 3-레이어 파일 아키텍처 및 모듈 격리 규칙)

이 문서는 프로젝트의 지속 가능한 확장성과 일관된 품질을 수호하기 위해 코드베이스 전반의 **파일 구조(File Structure), 레이어별 격리 수준(Layer Isolation), 명명 규칙(Naming Convention), 그리고 의존성 제약 조건**을 정의하는 **단일 진실 공급원(SSOT, Single Source of Truth) 아키텍처 표준 가이드라인**입니다.

---

## 1. 3-레이어 아키텍처 파일 배치 및 역할 (Standard Layout & Roles)

본 프로젝트는 UI, 비즈니스 서비스, 데이터베이스 쿼리를 완전히 물리적으로 격리하는 **3-레이어 아키텍처(3-Layer Architecture)**를 엄격히 준수합니다. 모든 신규 파일 작성 및 기존 파일 수정 시 지정된 위치 외의 경로에 파일을 배치하는 행위는 엄격히 규제됩니다.

```
workstation/
└── app/
    ├── core/                # [인프라 & 유틸] 공통 UI, 공통 쿼리 헬퍼, 파라미터, DB 클라이언트
    ├── pages/               # [UI 레이어] Streamlit 화면 배치 및 Plotly 시각화 드로잉
    ├── service/             # [서비스 레이어] Pandas 데이터 전처리, 통계 집계, 메모리 캐싱
    └── queries/             # [쿼리 레이어] Pure SQL 쿼리 텍스트 조립 및 빌딩
```

### ① UI 레이어 (`app/pages/`)
* **목적**: 사용자의 필터 입력을 제어하고, 레이아웃을 구성하며, 최종 차트와 지표 카드를 화면에 렌더링합니다.
* **하위 디렉터리 구성**: 도메인/메뉴 카테고리에 따라 접두사 번호가 붙은 폴더로 격리됩니다.
  * `_10_dashboard/`, `_20_analysis/`, `_30_monitoring/`, `_40_collaboration/` 등
* **핵심 배치 규칙**: 모든 화면은 **화면 컨트롤러(`*_page.py`)**와 **시각화 드로잉(`*_plots.py`)** 파일이 **1:1 대칭 매핑** 구조로 구성되어야 합니다.
  * [안티패턴] `*_page.py` 내부에 수백 줄의 Plotly 차트 드로잉 코드를 인라인으로 작성하는 것을 금지합니다.
  * [안티패턴] `*_plots.py` 내부에서 Streamlit 레이아웃 요소(`st.write`, `st.columns` 등)를 호출하는 것을 금지합니다.

### ② 서비스 레이어 (`app/service/`)
* **목적**: DB 클라이언트를 통해 수집된 원시 데이터(Raw DataFrame)를 결측값 대체, 데이터 타입 복구, 비즈니스 공식 적용, 통계 집계 연산 등을 거쳐 정제된 Pandas DataFrame으로 가공합니다.
* **핵심 배치 규칙**: 모든 비즈니스 로직 함수는 이 레이어 내의 `*_df.py` 파일에만 존재해야 합니다.
  * [안티패턴] UI 레이어(`app/pages/`) 또는 쿼리 레이어(`app/queries/`) 내부에 비즈니스 통계 수식이나 전처리 루틴을 혼용하지 마십시오.

### ③ 쿼리 레이어 (`app/queries/`)
* **목적**: 데이터베이스(Databricks, Oracle 등)에 전송할 SQL 쿼리 문자열을 조립하고 생성합니다.
* **핵심 배치 규칙**: 모든 SQL 조립 모듈은 `*_query.py` 또는 `q_*.py` 파일 형식을 지키며 이 레이어 아래에 위치합니다.
  * [안티패턴] 쿼리 파일 내에서 직접 데이터베이스 커넥터를 import하여 쿼리를 실행(`execute`)하지 마십시오. 오직 순수 문자열(`str`)인 SQL을 반환하는 함수만 포함되어야 합니다.

---

## 2. 물리적 폴더 구조 및 파일 명명 규칙 (Directory & Naming Standards)

프로젝트 내 파일, 클래스, 변수, 데이터베이스 객체 등의 상세 명명 기준은 **[L2-naming-convention.md](intelligence/rules/L2-naming-convention.md)**에서 단일 진실 공급원(SSOT)으로 전담하여 관리합니다.

* **레이어별 파일 명명 규칙**: `*_page.py`, `*_plots.py`, `*_df.py`, `*_query.py`/`q_*.py` 등 상세 템플릿과 예시는 [L2-naming-convention.md](intelligence/rules/L2-naming-convention.md)를 참조하십시오.
* **공통 코어 폴더 구조 (`app/core/`)**:
  - `app/core/constants/`: 비즈니스 코드 사전 및 맵핑 상수 정의 (`business_constants.json`, `business.py`)
  - `app/core/params/`: 필터 매개변수를 캡슐화한 파라미터 데이터클래스 정의 (`parameters.py`)
  - `app/core/db/`: DB 클라이언트 및 커넥터 인터페이스 (`client.py`, `sqlite_utils.py` 등) [레거시 브릿지 `app/core/operate/db_client.py`는 완전히 제거됨]
  - `app/core/query/`: 공통 SQL 빌더, SQLConverter, 테이블 상수 정의 (`query_helper.py`, `query_database.py`)
  - `app/core/ui/`: 공통 UI 컴포넌트, 공통 CSS 스타일 및 테마 정의 (`components.py`, `styles.py`)

---

## 3. 레이어간 결리 및 격벽 제약 조건 (Strict Layer Isolation Rules)

안정적인 3-레이어 아키텍처 유지를 위해 아래와 같이 **레이어 간 참조 및 의존성 격벽 제약 조건**을 반드시 적용합니다.

```mermaid
flowchart TD
    UI_Page["app/pages/*_page.py (UI Control)"]
    UI_Plots["app/pages/*_plots.py (Visual plots)"]
    Service["app/service/*_df.py (Data Processing)"]
    Query["app/queries/*_query.py (SQL assembly)"]
    DB_Client["app/core/db/client.py"]

    UI_Page -->|Import & Call| Service
    UI_Page -->|Import & Pass DF| UI_Plots
    Service -->|Import & Call| Query
    Service -->|Import & Run| DB_Client
    
    %% 금지 참조 관계 표시
    UI_Page -.-x|[금지] DIRECT DB RUN BLOCK| DB_Client
    UI_Plots -.-x|[금지] NO PLOTLY IMPORT IN SERVICE| Service
    Query -.-x|[금지] NO DB EXECUTE IN QUERY| DB_Client
    
    style UI_Page fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style UI_Plots fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style Service fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style Query fill:#f3f4f6,stroke:#94a3b8,stroke-width:2px
    style DB_Client fill:#fee2e2,stroke:#ef4444,stroke-width:2px
```

### ① 역방향 의존성 금지 (No Reverse Dependencies)
의존성 방향은 반드시 **[UI -> Service -> Query]**로 흘러야 합니다.
* **규제 사항**:
  - `queries/`는 `service/`나 `pages/`에 속한 모듈을 절대 임포트(import)할 수 없습니다.
  - `service/`는 `pages/`에 속한 UI 컴포넌트나 Plotly 차트 드로잉 파일(`*_plots.py`)을 절대 임포트할 수 없습니다.

### ② UI 레이어의 데이터베이스 직접 통신 차단 (No Direct DB Access in UI)
* **규제 사항**: 
  - `app/pages/*_page.py` 또는 `*_plots.py` 내부에서 `get_client()`를 임포트하여 직접 DB를 쿼리하거나, `queries/`의 SQL 빌더 함수를 직접 호출해 결과를 수집하는 행위를 엄격히 차단합니다.
  - UI는 무조건 서비스 레이어(`app/service/*_df.py`)의 함수를 게이트웨이로 삼아서만 데이터를 수집할 수 있습니다.

### ③ 서비스 레이어의 UI 종속성 제거 (No UI Library in Service)
* **규제 사항**:
  - 서비스 레이어(`app/service/*_df.py`) 내부에 `plotly`, `matplotlib`, `streamlit` 등의 시각화/UI 패키지를 임포트하여 차트 객체(`go.Figure`, `plt.Figure` 등)를 생성하거나 반환하는 행위는 불허합니다.
  - 서비스 함수는 오직 순수한 원시 데이터 타입(주로 `pd.DataFrame`, `dict`, `list`, `int`, `float`)만을 반환하여 독립적으로 단위 테스트가 가능한 순수 연산 구조를 가져야 합니다.

### ④ 쿼리 레이어의 실행 책임 제거 (No DB Execute in Queries)
* **규제 사항**:
  - 쿼리 레이어(`app/queries/q_*.py`) 내부의 어떤 함수도 데이터베이스 클라이언트를 사용하여 쿼리를 직접 수행하지 않습니다.
  - 이 레이어의 함수의 리턴 타입은 예외 없이 오직 **순수 SQL 문자열(`str`)**이어야 합니다.

---

## 4. 아키텍처 정합성 수호 수칙 (Architectural Integrity Standards)

### ① 공개 인터페이스 영속성 보장 (No Public Interface Modification)
타 레이어에 예기치 못한 사이드 이펙트가 전파되는 것을 원천 차단하기 위해 공개 API를 안전하게 보존합니다.
1. **파라미터 데이터클래스 보존**: `core/params/parameters.py`에 선언된 파라미터 `dataclass`의 인자 구성, 타입 힌트, 디폴트값을 임의로 수정하거나 누락시켜서는 안 됩니다.
2. **함수 호출 명세(Signature) 유지**: `service/` 및 `queries/` 공용 API 함수의 이름, 파라미터 타입, 리턴 타입을 그대로 수호해야 합니다.
3. **결과 데이터프레임 스키마 무결성**: 서비스 모듈이 반환하는 Pandas DataFrame의 핵심 컬럼명 및 데이터 타입은 수정이 절대 불가합니다. 컬럼명 파괴는 UI 시각화 렌더링 에러로 즉각 직결됩니다.

### ② 성능 캐싱 메커니즘 보증 (Caching Preservation)
Databricks 등 클라우드 쿼리 비용 폭증과 성능 저하를 방지하기 위한 캐싱을 필수로 유지합니다.
* **`@st.cache_data` 준수**: 데이터 수집 및 연산을 가공하는 서비스 레이어 함수에는 무조건 캐싱 데코레이터와 만료 시간(배치형 대용량 분석: `ttl=3600`(1시간), 실시간 모니터링: 30분 등)을 부여해야 합니다.

### ③ Streamlit UI 개발 및 시각화 일관성 표준 (6대 정합성 수칙)
1. **3-레이어 아키텍처 철저 준수**: UI 내부의 DB 직접 접근 및 무단 SQL 실행을 차단하고, 서비스 레이어로의 호출 창구를 일원화합니다.
2. **공통 UI 모듈 (`app/core/ui/`) 활용 극대화**: 페이지 내에서 인라인 HTML 스타일을 작성하지 않고, `components.py` 및 `styles.py`에서 제공하는 공통 컴포넌트(ShadCN 스타일, 카드형 지표, mini_header 등)를 참조합니다.
3. **도메인별 파라미터 데이터클래스 필수 통일**: 입력 필터를 전달할 때 개별 변수로 흩뿌려 넘기지 않고, `app/core/params/parameters.py`의 전용 데이터클래스로 조립하여 넘깁니다.
4. **캐싱 규칙 일관성 준수**: 무거운 쿼리가 발생하는 서비스 기능에는 캐싱 및 적절한 만료 시간을 부여합니다.
5. **시각화(Plots) 컬러 코드의 중앙화**: 차트 마커 및 라인 색상 지정 시 임의의 헥사 코드를 쓰지 않고, `app/core/common_design_parameter.py` 또는 `viz_plotly_design` 테마 컬러 변수를 바인딩합니다.
6. **세션 상태 네임스페이스 통제**: 임의 변수명을 키로 쓰지 말고 `core/constants/` 또는 `core/page/` 아래에 정의된 표준 세션 상태 키 목록을 바인딩합니다.

### ④ 데이터 전처리 vs 시각화 전처리 경계 표준 (Preprocessing Boundary)
1. **비즈니스 가공은 서비스 레이어에서만**: 데이터 조건 필터링, 통계 공식 적용, 결측값 처리 등은 반드시 서비스 레이어 내에서 연산되어 순수 DataFrame으로 보관/캐싱되어야 합니다.
2. **시각화 전처리는 플롯 레이어에서만**: 마우스 호버 텍스트 조립, 차트 디자인을 고려한 Top-N 자르기 및 `Others` 그룹화, 그래프 축 포맷팅(Tickformat) 등 비주얼 종속 가공은 플롯 레이어(`*_plots.py`) 내에서만 수행합니다.
3. **세부 판정 가이드**: 상세 시나리오는 [preprocessing-boundary.md](intelligence/guide/preprocessing-boundary.md) 문서를 기준 삼아 준수합니다.

---

## 5. 무단 접근 금지 구역 (Strict No-Touch Zones)

시스템의 근간을 지탱하는 아래 영역들은 에이전트의 임의 수정 범위에서 영구히 제외됩니다.
1. **사용자 세션 및 로그인 보안 제어 구역**: `pages/_90_system/login_page.py` 및 SQLite 인증 연동 로직
2. **데이터베이스 물리적 커넥터 구역**: `core/db/client.py` 및 관련 커넥터 인터페이스
3. **SQLite 스키마 마이그레이션 및 DML 구역**: `ops.db`/`staging.db` 등을 조작하거나 핸들링하는 로직

---

## 6. 안전 정책 연동 (No-Mutation Policy Safety Sync)

이 규칙 역시 `GEMINI.md` 및 `guide/agent-common.md`에 명시된 **[CRITICAL] 기존 소스 코드 변경 금지 및 차단 장치 (Safety Lock)**의 통제를 받습니다.

* 신규 파일 배치 및 파일 분리 리팩토링 작업을 설계할 때, 기존 프로덕션 코드를 분리하거나 이동시키는 행위는 **임의로 수행되어서는 절대 안 됩니다.**
* 반드시 변경 계획(구조 및 리팩토링안)을 사용자에게 구체적으로 리포트하여 **명시적 승인**을 받은 직후에만 승인된 규칙에 의거하여 조심스럽게 작업을 적용해야 합니다.
