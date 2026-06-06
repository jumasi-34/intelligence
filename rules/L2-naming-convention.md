# L2-naming-convention.md (L2 코드베이스 명명 규칙 표준)

이 문서는 프로젝트의 지속 가능성과 가독성, 그리고 아키텍처적 일관성을 유지하기 위해 소스 코드 파일, 클래스, 함수, 변수, 데이터베이스 객체 등의 **명명 규칙(Naming Convention)**을 정의하는 **단일 진실 공급원(SSOT) 명명 표준 가이드라인**입니다.

---

## 1. 물리적 파일 및 디렉터리 명명 규칙 (File & Directory Naming)

모든 파일과 폴더의 이름은 소문자 스네이크 케이스(`snake_case`)를 원칙으로 하며, 역할에 맞는 접미사(Suffix) 또는 접두사(Prefix)를 반드시 부여해야 합니다.

### ① 3-레이어 핵심 파일 명명

| 레이어 | 역할 | 파일명 규칙 | 올바른 예시 | 잘못된 예시 |
| :--- | :--- | :--- | :--- | :--- |
| **UI 메인** | Streamlit 화면 구성 및 입력 필터 제어 | `*_page.py` | `cqms_dashboard_page.py` | `cqms_dashboard.py` (접미사 누락) |
| **UI 시각화** | Plotly 차트 드로잉 및 Hover 포맷팅 | `*_plots.py` | `cqms_dashboard_plots.py` | `cqms_chart.py` (일관성 없음) |
| **Service** | Pandas 전처리, 비즈니스 계산 및 캐싱 | `*_df.py` 또는 `df_*.py` | `cqms_df.py` | `cqms_service.py` (접미사 불일치) |
| **Query** | SQL 문자열 조립 및 반환 | `*_query.py` 또는 `q_*.py` | `cqms_query.py`, `q_iqm_plus.py`| `cqms_sql.py` (접미사 불일치) |

### ② 공통 코어 및 유틸 파일 (`app/core/`)
* **파라미터 정의**: `parameters.py` 등의 완전 명사형 명명
* **테마 및 디자인**: `styles.py`, `components.py` 등 역할 기반 명사 명명
* **유틸리티**: `*_helper.py` 또는 `*_utils.py` (예: `query_helper.py`, `common_helper.py`)

### ③ 인텔리전스 및 규칙 파일 (`intelligence/`)
* **규칙 문서 (`intelligence/rules/`)**: 룰 계층화 관리를 위해 반드시 최상위 분류 접두사(`L1-`, `L2-`, `L3-`)를 부여합니다.
  * L1 (기본 및 안전): `L1-git.md`
  * L2 (설계 및 표준): `L2-architecture.md`, `L2-naming-convention.md`, `L2-business-constants.md`, `L2-context-readability.md`
  * L3 (구현 및 레이어): `L3-query.md`, `L3-service.md`, `L3-dashboard.md`, `L3-plot.md`
* **맥락/컨텍스트 문서 (`intelligence/context/`)**: 반드시 `context-` 접두사를 붙여 에이전트 전용 컨텍스트 파일임을 명시합니다.
  * 예: `context-queries.md`, `context-service.md`, `context-preprocessing-boundary.md`
  * [안티패턴] `app/` 실 소스 디렉터리 내부에 독립적인 `CONTEXT.md`를 단독 생성 및 방치하는 행위는 엄격히 금지됩니다.

### ④ Streamlit 페이지 폴더 (`app/pages/`)
* **메뉴 순서 제어**: 폴더 정렬 및 메뉴 구성을 위해 반드시 언더바와 번호 접두사를 붙여 정의합니다.
  * 형식: `_<번호>_<카테고리명>/`
  * 예: `_10_dashboard/`, `_20_analysis/`, `_30_monitoring/`

---

## 2. 소스 코드 요소 명명 규칙 (Code Level Naming)

파이썬 PEP 8 스타일 가이드를 기본으로 준수하며, 프로젝트의 아키텍처 패턴에 맞추어 아래 규칙을 강제합니다.

### ① 클래스 명명 (Classes)
* **표준 규칙**: 파스칼 케이스(`PascalCase`)를 사용하며, 역할에 맞는 명확한 명사형 이름을 지정합니다.
* **파라미터 데이터클래스 (`core/params/`)**: 필터 데이터를 담는 클래스는 반드시 `*Params` 접미사로 통일합니다.
  * 예: `BaseFilterParams`, `DateFilterParams`, `OeQualityIssueParams`
* **쿼리 헬퍼**: `QueryFilter`, `SQLConverter` 등 객체 지향적 책임을 명시합니다.

### ② 함수 명명 (Functions & Methods)
* **표준 규칙**: 소문자 스네이크 케이스(`snake_case`)를 사용하며, 역할(Query, Preprocessing, Transformation 등)과 도메인(gmes, cqms, ctms 등)을 결합하여 가시성이 극대화된 구조로 일관성 있게 정의합니다.

#### 1) 쿼리 레이어 함수 명명 규칙 (`app/queries/`)
쿼리 레이어 함수는 SQL 쿼리 문자열을 조립 및 생성하여 반환합니다. 데이터베이스 커넥터를 직접 다루지 않고 오직 텍스트 조립에만 관여함을 표현합니다.

* **원시 데이터 조회 (`get_<도메인>_*_rawdata`)**:
  - 필터링 전 원시 데이터(Raw data)를 조회하는 메인 쿼리 함수는 반드시 `get_` 접두사와 `_rawdata` 접미사를 지정합니다.
  - 예: `get_cqms_qi_mttc_rawdata(...)`, `get_ctms_ctl_general_rawdata(...)`, `get_hope_oeapp_general_rawdata(...)`
* **조건별 조회 (`get_<도메인>_*_by_<조건>`)**:
  - 특정 축(공장, 제품 코드, 기간, 설비 등)에 맞춰 데이터를 그룹핑 또는 필터링하여 가져오는 쿼리 함수는 `_by_<조건>` 접미사를 활용합니다.
  - 예: `get_gmes_production_by_plant(...)`, `get_gmes_production_by_mcode(...)`, `get_gmes_ncf_by_dft_cd(...)`, `get_gmes_gt_wt_by_period(...)`
* **기준 정보 및 마스터 조회 (`get_<도메인>_*_master` / `_standard`)**:
  - 시스템 기준 정보, 스펙 마스터, 불량 코드 사전 등을 쿼리하는 용도는 마스터 혹은 스펙임을 나타내는 접미사로 귀결됩니다.
  - 예: `get_gmes_spec_product_master(...)`, `get_gmes_rr_standard(...)`

#### 2) 서비스 레이어 함수 명명 규칙 (`app/service/`)
서비스 레이어 함수는 데이터베이스를 조회(execute)하여 결과 데이터프레임(`pd.DataFrame`)을 수집하고, Pandas를 통한 비즈니스 연산 및 집계를 거쳐 뷰 레이어에 적합한 데이터 형태로 반환합니다.

* **원시 데이터 수집 및 1차 전처리 (`preprocessing_<도메인>_*_rawdata`)**:
  - 쿼리를 호출해 데이터프레임을 받아오고 결측치 및 타입 교정을 하는 1차 함수는 `preprocessing_` 접두사와 `_rawdata` 접미사를 결합합니다. (주로 비용 최적화를 위한 `@st.cache_data` 데코레이터를 적용합니다.)
  - 예: `preprocessing_qi_general_rawdata(...)`, `preprocessing_ctms_general_rawdata(...)`
* **데이터 형태 변환 및 2차 가공 (`transform_<업무/차트>_df`)**:
  - 1차 전처리 완료된 데이터프레임을 넘겨받아 대시보드 구조에 맞춰 피벗 및 다차원 가공을 수행하는 2차 함수는 `transform_` 접두사와 `_df` 접미사를 사용합니다.
  - 예: `transform_qi_dashboard_df(...)`, `transform_qi_kpi_trend_df(...)`, `transform_gmes_scrap_general_rawdata(...)`
* **통계 및 그룹 집계 (`preprocessing_<업무>_*_agg`)**:
  - 일별, 주별, 월별, 연별, 공장별 등의 특정 디멘션 기준으로 그룹 연산(`groupby`)을 수행해 데이터프레임을 축소/가공하여 반환하는 집계 함수는 `_agg` 접미사를 붙여 선언합니다.
  - 예: `preprocessing_ncf_daily_agg(...)`, `preprocessing_ncf_plant_agg(...)`, `preprocessing_production_mcode_agg(...)`
* **모듈 내부 전용 비공개 헬퍼 함수 (`_fetch_*`, `_apply_*`)**:
  - 서비스 모듈 내부의 재사용 보조 및 필터 적용을 담당하는 로컬 프라이빗 함수는 반드시 언더바(`_`) 접두사를 지정하여 외부에 무분별하게 노출되지 않도록 제어합니다.
  - 예: `_fetch_ncf_base_df(...)`, `_apply_production_quality_filters(...)`

### ③ 변수 명명 (Variables)
* **표준 규칙**: 소문자 스네이크 케이스(`snake_case`)를 사용하여 데이터의 성격을 직관적으로 표현합니다.
* **Pandas DataFrame 변수**: 명확히 DataFrame 타입임을 인지할 수 있도록 `_df` 접미사를 적극 적용합니다.
  * 예: `raw_df`, `filtered_df`, `summary_df`
  * [안티패턴] `data`, `df` 등 너무 축약되거나 의미를 알 수 없는 광범위한 명명은 권장하지 않습니다.
* **데이터프레임 내 컬럼명**:
  * 데이터베이스로부터 기인한 컬럼은 대문자 스네이크 케이스(`UPPER_SNAKE_CASE`)를 사용합니다. (예: `PLANT`, `OEQI`, `NCF_RATE`, `ISSUE_DATE`)
  * 임시 가공용 파이썬 루프 내 인덱스나 로컬 변수는 소문자 스네이크 케이스를 준수합니다.

### ④ 상수 명명 (Constants)
* **표준 규칙**: 대문자 스네이크 케이스(`UPPER_SNAKE_CASE`)를 강제 준수합니다.
* **비즈니스 상수 (`core/constants/`)**: JSON 맵핑 상수를 파이썬으로 바인딩할 때 무조건 대문자를 적용합니다.
  * 예: `PLANT_TO_OEQG`, `NEW_BUSINESS_DICT`, `ISSUE_AREA`
* **테이블 경로 상수 (`core/query/query_database.py`)**: Databricks 및 Oracle 테이블 명세 상수를 정의할 때 대문자를 사용합니다.
  * 예: `DatabricksTables.CQMS_MAIN_TABLE`

---

## 3. 데이터베이스 객체 명명 규칙 (Database Naming)

데이터베이스 쿼리 작성 및 스키마 참조 시의 일관성을 위한 규칙입니다.

* **테이블명 및 뷰(View)명**: 대문자 스네이크 케이스(`UPPER_SNAKE_CASE`)를 사용하며, 업무 도메인 단위의 접두사를 포함합니다.
  * 예: `TB_CQMS_QUALITY_ISSUE`, `VW_GMES_DEFECT_RATE`
* **컬럼명**: 대문자 스네이크 케이스를 활용하여 명사형으로 명명합니다. (예: `REG_USER_ID`, `CREATE_DT`)

---

## 4. 안전 정책 연동 (No-Mutation Policy Safety Sync)

이 명명 규칙 역시 `GEMINI.md`에 명시된 **[CRITICAL] 기존 소스 코드 변경 금지 및 차단 장치 (Safety Lock)**의 통제를 받습니다.

* 이미 존재하는 클래스명, 함수 서명(Signature), 파일명 등은 공개 인터페이스 영속성과 깊게 연결되어 있으므로, 가독성 향상만을 목표로 **기존 프로덕션 명칭을 임의 리팩토링하는 행위는 엄격히 금지**됩니다.
* 만약 명명 오류로 인해 중대한 에러가 예상되거나 신규 파일 명명이 필요한 경우, 반드시 사전에 제안서를 사용자에게 리포트하고 **명시적 승인**을 받은 뒤 규칙에 부합하게 명명해야 합니다.
