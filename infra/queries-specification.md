# \[QUERIES\] queries/ — 레포지토리 레이어 컨텍스트

> **LAYER:** `queries/` · 레포지토리 레이어 — SQL 문자열 생성 전용. DB 실행 없음.

---

## 역할

SQL 문자열을 생성해 반환하는 레이어. DB 실행은 하지 않는다.
모든 함수는 `str`을 반환하며, 실행은 `service/` 레이어의 `get_client().execute()`가 담당한다.

## 설계 철학

- **동적 WHERE 절 구성** → `QueryFilter` 사용, 문자열 하드코딩 금지
- **코드값 → 의미값 변환** → `DECODE` + `convert_dict_to_decode` 활용
- **CTE 기반 쿼리 구조** → 역할별로 CTE를 분리해 가독성 확보
- **Params 객체 기반 입력** → dataclass 인수로 일관된 인터페이스 유지
- **SQL 생성과 비즈니스 로직 분리** → query 함수는 조립(Orchestration) 역할만 수행

## 네이밍 컨벤션

### 모듈

```
{system}_query.py
```

### 함수

```
get_{system}_{domain}_{description}(params: SomeParams) -> str
```

| 세그먼트 | 예시 |
|----------|------|
| `{system}` | `gmes`, `cqms`, `hope`, `hgws`, `qrs`, `sap`, `ctms`, `plm`, `sqlite`, `dbx` |
| `{domain}` | `ncf`, `production`, `rr`, `uf`, `qi`, `oeapp`, `sellin` |
| `{description}` | `rawdata`, `by_plant`, `by_mcode`, `by_period`, `by_dft_cd`, `standard` |

예: `get_gmes_ncf_by_plant`, `get_cqms_qi_general_rawdata`, `get_hope_oeapp_general_rawdata`

Private 헬퍼(내부 subquery 조립용)는 언더스코어 접두어: `_spec_master_subquery()`.

## 규칙

- **SQL만 반환한다**: 비즈니스 로직, DataFrame 조작, DB 실행 코드 없음.
- **`dispatch_*` 함수 없음**: view_mode 분기는 `service/` 레이어가 담당.
- **파라미터 dataclass 사용**: `core/params/parameters.py`의 dataclass를 인수로 받는다.
- **QueryFilter / SQLConverter 사용**: WHERE 절 조립은 헬퍼 클래스를 활용한다.
- **DatabricksTables 사용**: 테이블 경로는 상수(`DatabricksTables` dataclass)로 관리한다.
- **서브패키지·파일 세분화 금지**: 도메인이나 함수가 늘어도 `{system}_query.py` 단일 파일 구조를 유지한다. 도메인별 서브폴더·파일 분리는 허용하지 않는다.

## 핵심 유틸리티 (`core/query/`)

### QueryFilter

WHERE 절 조건을 동적으로 생성하는 Stateless static method 구조.
`None` 또는 빈 리스트가 전달되면 해당 조건을 자동으로 생략한다.

```python
from core.query.query_helper import QueryFilter, SQLConverter

where_clauses = [
    QueryFilter.where_in("PLANT", params.plant_list),
    QueryFilter.where_date_between(params.start_date, params.end_date, "REG_DATE"),
    QueryFilter.where_equal("DISP_TYPE", "scrap"),
]
where_sql = SQLConverter.concat_where_clause(where_clauses)  # WHERE ... AND ...
```

주요 메서드:
- `where_in(col, values)` — IN 절. `None`/빈 리스트이면 생략
- `where_date_between(start, end, col)` — BETWEEN 날짜 조건
- `where_equal(col, value)` — = 조건
- `where_like(col, value)` — LIKE 조건

### SQLConverter

WHERE 절 리스트를 최종 SQL 문자열로 결합한다.

- `concat_where_clause(clauses)` — 유효 조건을 `WHERE ... AND ...` 형태로 결합

### DatabricksTables

Databricks 테이블 경로를 dataclass 상수로 중앙 관리. 하드코딩 금지.

```python
from core.query.query_database import DatabricksTables

_tables = DatabricksTables()
# _tables.ncf_main, _tables.production_main, _tables.rr_main 등
```

## 쿼리 작성 보일러플레이트

```python
from core.query.query_database import DatabricksTables
from core.query.query_helper import QueryFilter, SQLConverter, convert_dict_to_decode
from core.params.parameters import SomeParams

_tables = DatabricksTables()

_MAPPING_DICT = {"A": "Value A", "B": "Value B"}
_DECODE_FIELD = convert_dict_to_decode(_MAPPING_DICT)


def get_{system}_{domain}_rawdata(params: SomeParams) -> str:
    where_clauses = [
        QueryFilter.where_in("T.PLANT", params.plant_list),
        QueryFilter.where_date_between(
            params.start_date, params.end_date, "DATE_FORMAT(T.REG_DATE, 'yyyyMMdd')"
        ),
    ]
    where_sql = SQLConverter.concat_where_clause(where_clauses)

    return f"""
        WITH
            MAIN AS (
                SELECT
                    KEY      AS DOC_NO,
                    DECODE(CODE, {_DECODE_FIELD}) AS CODE_NAME,
                    COL1,
                    COL2,
                    SEQ
                FROM {_tables.some_table}
            ),
            SUB AS (
                SELECT SEQ, REF_COL
                FROM {_tables.some_sub_table}
            )
        SELECT
            MAIN.DOC_NO,
            MAIN.CODE_NAME,
            MAIN.COL1,
            MAIN.COL2,
            SUB.REF_COL
        FROM MAIN
        LEFT JOIN SUB ON MAIN.SEQ = SUB.SEQ
        {where_sql}
        ORDER BY MAIN.DOC_NO DESC
    """
```

## 구현 가이드

### Best Practices

- WHERE 조건은 `QueryFilter`를 통해 조립한다 — 직접 문자열 조합 금지
- DECODE 변환은 dict 기반 상수(`_DECODE_FIELD`)로 모듈 상단에 정의한다
- 날짜 컬럼의 문자열/DATE 타입 혼용에 주의한다 (`DATE_FORMAT` 사용 통일)
- CTE 단위로 역할을 분리해 SELECT 절은 최종 소비 데이터 기준으로 구성한다
- JOIN 대상은 필요한 경우 DISTINCT로 중복을 제어한다

### Known Caveats

- Databricks SQL과 Oracle 스타일 함수가 혼재되어 있다 (`TO_CHAR` vs `DATE_FORMAT`)
- 일부 쿼리에 하드코딩된 업무 조건이 남아 있다
- 날짜 필터가 주석 처리된 쿼리가 존재한다

## 모듈 목록

| 파일 | 시스템 | 주요 도메인 |
|------|--------|------------|
| `gmes_query.py` | GMES | 생산량, NCF, RR, UF, Weight, 규격 마스터 |
| `cqms_query.py` | CQMS | 품질 이슈, 4M 변경, 고객 감사 |
| `hope_query.py` | HOPE | OE App, Sell-in |
| `hgws_query.py` | HGWS | 반품 |
| `qrs_query.py` | QRS | 워크시트 |
| `ctms_query.py` | CTMS | CTMS 데이터 |
| `sap_query.py` | SAP | SAP 데이터 |
| `plm_query.py` | PLM | UF Balance |
| `sqlite_query.py` | SQLite | 로그, 스테이징, 운영 참조 |
| `q_iqm_plus.py` | IQM Plus | IQM Plus 집계 쿼리 |
| `dbx_query.py` | Databricks | 시스템 메타데이터 (테이블 권한 조회 등) |

## 함수 카탈로그

→ 각 모듈 파일(`app/queries/{system}_query.py`) 내 소스코드 및 Docstring 참조
