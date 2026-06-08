# \[CORE\] core/ — 공용 인프라 레이어 컨텍스트

> **LAYER:** `core/` · 공용 인프라 — DB 클라이언트·파라미터 dataclass·SQL 헬퍼·설정. 모든 레이어가 의존.

---

## 역할

프로젝트 전반에서 공유되는 기반 코드를 제공한다.
DB 클라이언트, 파라미터 dataclass, SQL 헬퍼, 차트 유틸리티, 전처리, 페이지 라우팅 등 모든 레이어가 의존한다.

## 구조

```
core/
├── boilerplate_column_config.py    # st.dataframe 컬럼 설정 보일러플레이트
├── quality_management_db.py        # 품질 관리 DB 유틸리티
├── params/                         # 파라미터 dataclass (실제 정의)
│   └── parameters.py
├── constants/                      # 전역 상수 (실제 정의)
│   ├── business.py                 # 비즈니스 도메인 상수 (공장 코드, OEQG 그룹, 날짜 등)
│   └── ui.py                       # UI 관련 상수
├── ui/                             # UI 컴포넌트·스타일
│   ├── components.py
│   └── styles.py
├── db/                             # DB 클라이언트·메일러·SQLite DML/DDL (실제 구현)
│   ├── client.py
│   ├── mailer.py
│   └── sqlite_utils.py             # SQLite DML(INSERT/UPDATE/DELETE) · DDL(CREATE/ALTER/DROP)
├── utils/                          # 범용 유틸리티
│   ├── datetime.py                 # 날짜 헬퍼 (get_year_start_end 등)
│   └── numbers.py                  # 숫자 포매팅·아웃라이어 제거
├── query/                          # SQL 조립 헬퍼
│   ├── query_helper.py
│   ├── query_database.py
│   └── query_config.py
├── page/                           # 페이지 라우팅
│   └── config_pages.py
├── plot/                           # 차트 유틸리티
│   ├── viz_config.py
│   ├── viz_helper.py
│   └── viz_plotly_design.py
└── preprocessing/                  # 데이터 전처리 유틸리티
    ├── dataframe_config.py
    └── dataframe_helper.py
```

---

## DB 클라이언트 (`db/client.py`)

모든 DB 연결의 진입점. `.execute(query) → pd.DataFrame`.

실제 구현은 `core/db/client.py`에 있으며, 기존의 하위 호환용 레거시 브릿지(`core/operate/db_client.py`)는 완전히 제거되었습니다.

```python
from app.core.db.client import get_client           # 단일 진실 공급원(SSOT) 임포트 경로

get_client("databricks")           # Databricks SQL (주 분석 데이터)
get_client("oracle_bi")            # Oracle BI DB
get_client("oracle_mes")           # Oracle MES DB
get_client("sqlite", "log")        # ~/database/log.db  (세션 로그)
get_client("sqlite", "staging")    # ~/database/staging.db (중간 집계)
get_client("sqlite", "ops")        # ~/database/ops.db  (운영 참조)
```

환경변수는 `.env`에서 자동 로드 (`load_dotenv`). `PYTHONPATH`를 프로젝트 루트로 지정해야 import가 동작한다.

---

## SQLite DML/DDL (`db/sqlite_utils.py`)

SQLite 데이터 변경(DML)·구조 관리(DDL)를 위한 유틸리티 클래스.
**SELECT는 `get_client().execute()`를 사용한다.** 이 모듈은 쓰기·구조 변경 전용이다.

```python
from core.db.sqlite_utils import SQLiteDML, SQLiteDDL
```

### SQLiteDML — 데이터 조작

```python
dml = SQLiteDML("log")   # "log" | "staging" | "ops"

# INSERT / UPDATE / DELETE 실행 (rowcount 반환)
dml.execute_dml("DELETE FROM user_login WHERE id = ?", (42,))

# INSERT 후 생성된 행의 id 반환
new_id = dml.execute_insert(
    "INSERT INTO user_login (employee_id, login_time) VALUES (?, ?)",
    (12345678, "2025-01-01 09:00:00"),
)

# 단일 행 삽입 (편의 메서드)
dml.insert_row("user_login", ["employee_id", "login_time"], (12345678, "2025-01-01 09:00:00"))

# 테이블 목록 조회
tables = dml.list_tables()
```

### SQLiteDDL — 구조 관리

```python
ddl = SQLiteDDL("ops")

# 테이블 생성 (이미 있으면 무시)
ddl.create_table("my_table", [("id", "INTEGER PRIMARY KEY"), ("name", "TEXT")])

# 여러 DDL 구문 한 번에 실행 (CREATE TABLE + INDEX + TRIGGER 등)
ddl.execute_script("""
    CREATE TABLE IF NOT EXISTS t1 (...);
    CREATE INDEX IF NOT EXISTS idx_t1 ON t1(col);
""")

# 컬럼 추가
ddl.alter_table_add_column("my_table", "score", "REAL")

# 컬럼 이름 변경 (임시 테이블 방식으로 처리)
ddl.alter_table_rename_column("my_table", "old_name", "new_name")

# 테이블 스키마 확인
schema_df = ddl.get_table_schema("my_table")   # cid, name, type, notnull, dflt_value, pk

# 테이블 삭제
ddl.drop_table("my_table")
```

### SQLite 작업 선택 기준

| 작업 | 사용 |
|------|------|
| 데이터 조회 (SELECT) | `get_client("sqlite", "ops").execute(query)` |
| 데이터 조회 — 파라미터 바인딩 | `get_client("sqlite", "ops").execute(query, params)` |
| DataFrame 일괄 저장 | `get_client("sqlite", "ops").insert_dataframe(df, table)` |
| INSERT / UPDATE / DELETE | `SQLiteDML("ops").execute_dml(query, params)` |
| INSERT + id 반환 필요 | `SQLiteDML("ops").execute_insert(query, params)` |
| 테이블 생성·변경·삭제 | `SQLiteDDL("ops").create_table / alter / drop` |

---

## params/parameters.py

쿼리·서비스 함수의 인수를 정의하는 dataclass 모음.
새 파라미터 클래스는 `core/params/parameters.py`에 추가한다.

```python
from core.params.parameters import NonconformityParams
```

### 계층 구조

```
BaseFilterParams        → plant_list, mcode_list (Optional)
  └─ DateFilterParams   → start_date, end_date
  └─ MonthFilterParams  → start_month, end_month

SpecTypeParams          → spec_fg_list, spec_type_list (mix-in)
```

### 주요 dataclass

| 클래스 | 용도 |
|--------|------|
| `NonconformityParams` | NCF(부적합) 조회. `view_mode`, `disposition_type`, `is_only_fm` |
| `ProductionParams` | 생산량 조회. `view_mode` |
| `RollingResistanceParams` | RR(구름저항) 조회. `view_mode`, `is_only_oe`, `test_fg` |
| `UniformityParams` | UF(균일성) 조회. `view_mode` |
| `GTWeightParams` | 중량 조회. `view_mode` |
| `GMESSpecMasterParams` | 규격 마스터 조회. `view_mode`, `spec_fg_list` |
| `QualityIssueTasksParams` | CQMS 품질 이슈. `is_only_hk_fault`, `stage_tag_list` 등 |
| `ChangeTaskParams` | 4M 변경 조회. `is_only_ongoing_status`, `remove_rejected` |
| `AuditTaskParams` | CQMS 고객사 감사. `status_list`, `audit_type_list` |
| `OEAppTasksParams` | HOPE OE App 조회. `is_only_supplying`, `is_only_ev` |
| `SellinTasksParams` | HOPE Sell-in 조회. `view_mode` (monthly/yearly) |
| `HGWSProcessingParams` | 반품 조회. `view_mode` |
| `CTMSProcessingParams` | CTMS 조회. `is_only_mass` |
| `IqmPlusParams` | IQM Plus 전체 파라미터 (다단계 UI 상태 포함) |

모든 구체 dataclass는 `frozen=True` 없이도 기본 사용 가능하나, `@st.cache_data` 키로 쓰려면 `frozen=True`가 필요하다.

---

## query/query_helper.py

WHERE 절 조립을 위한 유틸리티 클래스.

```python
from core.query.query_helper import QueryFilter, SQLConverter

where_clauses = [
    QueryFilter.where_in("PLANT", params.plant_list),            # IN 절
    QueryFilter.where_date_between(                               # BETWEEN 절
        params.start_date, params.end_date, "REG_DATE"
    ),
    QueryFilter.where_equal("DISP_TYPE", "scrap"),               # = 절
]
where_sql = SQLConverter.concat_where_clause(where_clauses)       # WHERE ... AND ...
```

`where_in`에 `None` 또는 빈 리스트가 전달되면 해당 조건을 자동으로 생략한다.

---

## query/query_database.py

Databricks 테이블 경로를 상수로 관리하는 dataclass.

```python
from core.query.query_database import DatabricksTables

tables = DatabricksTables()
# 예: tables.ncf_main, tables.production_main, tables.rr_main
```

쿼리 함수에서 테이블 경로를 하드코딩하지 말고 반드시 이 dataclass를 사용한다.

---

## page/config_pages.py

페이지 등록 및 역할(role) 기반 접근 제어.

```python
PAGE_CONFIGS = {
    "대시보드 메인": {
        "filename": "pages/_10_dashboard/iqm_plus_main_page.py",
        "icon": ":material/dashboard:",
        "category": "Dashboard",
        "roles": ["Viewer", "Contributor", "Admin"],
    },
}
```

`VALID_CATEGORIES`: `Dashboard`, `Analysis`, `Monitoring`, `Collaboration`, `Workplace`, `Admin`, `Settings`, `System`, `UserGuide`

---

## constants/business.py

프로젝트 전반에서 공유하는 비즈니스 상수.
실제 정의는 `core/constants/business.py`에 있으며, 직접 참조하도록 코드가 전환되었습니다.

```python
from core.constants.business import plant_codes, plant_oeqg_dict

# 공장 코드
plant_codes = ["DP", "KP", "JP", "HP", "CP", "MP", "IP", "TP", "OT"]

# OEQ 그룹 매핑
plant_oeqg_dict = {
    "KP": "G.OE Quality",   # 한국 공장 (KP, DP, IP)
    "JP": "China OE Quality",
    "MP": "Europe OE Quality",
    "TP": "NA OE Quality",
}

oeqg_codes = ["G.OE Quality", "China OE Quality", "Europe OE Quality", "NA OE Quality"]

# 날짜 상수 (런타임 계산)
today, today_str, this_year, one_year_ago, a_week_ago

# 시스템 설정 (SQLite 경로, DEV_MODE, DEBUG_MODE 등)
SQLITE_DB_LOG_PATH, SQLITE_DB_STAGING_PATH, SQLITE_DB_OPS_PATH
```

OEQI = `QI_CNT / SUPP_QTY × 1_000_000` (백만 납품당 불량건수).

---

## utils/

범용 유틸리티 함수.

```python
from core.utils.datetime import get_year_start_end
from core.utils.numbers import format_number, remove_outliers_by_column

get_year_start_end(2024)  # → ("20240101", "20241231")
format_number(1_500_000)  # → "1.5M"
remove_outliers_by_column(df, "VALUE", method="iqr")
```
