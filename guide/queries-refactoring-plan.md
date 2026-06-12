# app/queries 대규모 리팩토링 작업 계획서 (보완본 v2)

이 문서는 `app/queries/` 폴더 내 SQL 쿼리 빌더 모듈들의 가독성을 향상시키고, 작성 일관성을 확보하며, 유지보수성을 극대화하기 위한 대규모 리팩토링 작업 계획을 정의합니다.

추가적인 설계 요건(JSON 메타데이터 관리, 상수 역할 분리, CTE 분할 금지, 작성 스타일 다변화)과 **종합 네이밍 컨벤션 표준(테이블, 모듈, 함수, 공통 상수, 디코드 및 추가 로컬 변수 일체)**을 반영하여 철저히 정비된 마스터 계획서입니다.

---

## 1. 리팩토링의 목적 및 기대효과
- **가독성 극대화**: SQL 조립 구조와 파이썬 로직을 격리하여 코드 판독 시간을 단축합니다.
- **유지보수 용이성**: 데이터베이스 스키마나 공통 코드 맵핑 변경 시 파이썬 코드 수정 없이 공통 마스터 JSON 파일만 업데이트하여 반영합니다.
- **안정성 강화**: 테스트 하네스(Harness Sandbox)를 사전에 구축하여, 리팩토링 전후의 SQL 문자열 논리적 일치 여부를 완벽히 자동 검증합니다.

---

## 2. 5대 핵심 영역별 보완 설계안

### ① 테이블 메타데이터의 `query_database.py` 중앙 정적 관리
* **현황**: 테이블명이 코드 곳곳에 산재해 가독성과 자동완성이 다소 파편화되어 있습니다.
* **보완 설계 및 결합 원칙**:
  - **정적 중앙 집중화**: 모든 데이터베이스 테이블명은 `.json` 파일에 기술하지 않고, 오직 `app/core/query/query_database.py` 내부의 정적 테이블 데이터 클래스(예: `DatabricksTables`, `SQLiteTables`)에서만 직접 정적으로 변수를 정의하고 유지 관리합니다.
  - **IDE Intellisense & 타입 안정성 극대화**: 파이썬 정적 클래스 변수로 유지함으로써 개발 단계에서 IDE의 자동완성(Intellisense), 타입 힌트 추적, 정적 코드 분석을 완벽하게 이용할 수 있도록 보장합니다.
  - **네이밍 규칙 엄수**: 정적 클래스 내의 변수명은 새롭게 정비된 `{시스템}_{도메인}_{세부내용}` 명명 규정(소문자 스네이크 케이스)을 준수하도록 관리합니다.
  - **테이블 데이터 클래스 설계 구조 예시**:
    ```python
    @dataclass
    class DatabricksTables:
        """
        Databricks 테이블 경로 관리 정적 데이터 클래스
        """
        # CQMS
        cqms_qi_main: str = "hkt_system_dw.eqms.cqms_quality_issue"
        cqms_qi_mcode: str = "hkt_system_dw.eqms.cqms_quality_issue_material"
        
        # GMES / Specification
        gmes_spec_product_master: str = "hkt_dw.specification.mas_d_lmastr101"
        
        # CTMS
        ctms_ctl_result_raw: str = "hkt_system_dw.ctms.ctms_result_data"
    ```

### ❶ SQL 조립 및 DECODE 제어용 `query_metadata.json` 설계
물리적인 테이블 경로명은 파이썬 정적 클래스(`query_database.py`)에서 전담하여 가독성과 Intellisense를 책임지는 한편, 데이터의 규칙적인 맵핑 변환(DECODE)이나 쿼리 런타임 제어 설정 등은 `app/core/query/query_metadata.json` 파일에서 동적으로 유연하게 관리하여 결합도를 최소화합니다.

#### 1) `query_metadata.json` 스키마 및 메타데이터 정의
- **`decodes`**: SQL 쿼리 조립 시 `CASE WHEN` 또는 `DECODE` 절에 사용될 핵심 업무 매핑 상수로, 파이썬 코드 변경 없이 맵핑 정보만 손쉽게 원격 제어할 수 있도록 보장합니다.
- **`settings`**: 데이터베이스 쿼리 실행의 디폴트 조회 제한수(`default_row_limit`), 타임아웃, 캐시 타임아웃 시간 등 런타임 상수 설정을 다룹니다.
- **`dimension_mappings` (차원 매핑)**: 시스템마다 날짜 컬럼명(`REG_DATE` vs `MRM_DATE`)이나 공장 컬럼명이 제각기 다를 때, 공통 필터 클래스에서 해당 도메인별 표준 컬럼을 인식하고 주입할 수 있도록 돕는 메타 사전입니다.

#### 2) `query_metadata.json` 구성 예시 (Specification)
```json
{
  "decodes": {
    "plant_to_oeqg": {
      "P1": "OEQG_A",
      "P2": "OEQG_B",
      "P3": "OEQG_C"
    },
    "defect_code_map": {
      "D01": "Tread Cut",
      "D02": "Sidewall Crack",
      "D03": "Bead Damage"
    }
  },
  "settings": {
    "databricks": {
      "default_row_limit": 100000,
      "query_timeout_seconds": 180,
      "cache_ttl_seconds": 3600
    }
  },
  "dimension_mappings": {
    "cqms_qi": {
      "date_column": "QI.REG_DATE",
      "plant_column": "QI.PLANT",
      "mcode_column": "M.M_CODE"
    },
    "ctms_ctl": {
      "date_column": "MRM_DATE",
      "plant_column": "PLANT",
      "mcode_column": "MFG_CD"
    }
  }
}
```

#### 3) 파이썬 런타임 연계 바인딩 가이드
- **DECODE 쿼리 주입**: `SQLConverter.dict_to_decode_sql(...)` 헬퍼 함수를 통해 JSON 내의 특정 디코드 변환 딕셔너리를 자동으로 SQL 문자열로 조립하여 주입합니다.
- **차원 매핑 필터**: `QueryFilter` 내에서 `dimension_mappings` 구조를 인지하여, 도메인 정보만 주면 알맞은 컬럼명으로 AND 조건절을 동적으로 조립해 주도록 설계하여 중복 코드를 제거합니다.

---
* **규칙**: 상수가 중복되어 스파게티화되는 현상을 근절하기 위해, 기존 공통 상수 파일(`app/core/constants/business.py` 등)과 테이블 관리 파일(`query_database.py`) 간의 책임을 분명히 단일화합니다.
* **역할 매핑 격리표**:

| 구분 | SQL용 테이블 경로 상수 (`query_database.py`) | 서비스/UI 비즈니스 상수 데이터 (`constants/business.py`) |
| :--- | :--- | :--- |
| **성격** | SQL 문법 내부 조립을 위한 물리적 테이블 경로 자원 | 서비스 비즈니스 규칙, 전처리 공식, UI 필터용 정적 자원 |
| **대상 예시** | DB 테이블 전체 경로 주소 문자열 (`DatabricksTables.*` 등) | 통계 수식 계수, 공장 도메인 매핑 상수, UI 탭 라벨 리스트 등 |
| **상호 참조** | 서비스 비즈니스 상수가 테이블 경로 바인딩을 침범하지 않음 | 테이블 상수 경로 정보를 서비스/UI 로직이 임의로 직접 재정의하지 않음 |

### ③ CTE 함수의 별도 모듈 관리 및 쪼개기 절대 금지
* **핵심 제약**: SQL의 가독성을 높인다는 명목으로 CTE(Common Table Expressions) 구문이나 부분 쿼리들을 파이썬 함수/모듈 단위로 잘게 쪼개어 동적 결합하는 행위를 **엄격히 금지**합니다.
* **사유**: CTE 구문이 잘게 쪼개지면 전체 SQL 구문을 조감하고 쿼리 실행 계획(Execution Plan)을 디버깅하기가 극도로 어려워집니다.
* **수칙**: 반드시 하나의 쿼리 함수 내에서 **완성된 형태의 단일 Full Query 대형 문자열**로 일목요연하게 조립되어 가독성을 확보하도록 제어해야 합니다.

### ④ SQL 유형별 표준 작성 스타일 (2~3개 관리)
모든 쿼리 함수를 획일화된 하나의 포맷에 끼워 맞추지 않고, SQL의 구조와 동적 조건의 복잡성에 따라 **3가지 표준 스타일**로 분류하여 정형화합니다.

#### Style A: 단순 조회 및 단일 테이블형 (Simple Table Target)
* **적용**: 별도의 JOIN이 없거나 조건문이 1~2개 수준으로 극히 정적인 기준 정보 및 마스터 조회용 쿼리.
* **포맷**: 동적 WHERE 배열 조립 없이 즉시 `QueryFilter` 인라인 바인딩을 이용해 단순하게 반환.
```python
def get_gmes_spec_product_master(params: GMESSpecMasterParams) -> str:
    cond_mcode = QueryFilter.where_in("M_CODE", params.mcode_list)
    where_clause = QueryFilter.build_where([cond_mcode])
    
    return f"""--sql
    SELECT * 
    FROM {DatabricksTables.product_master}
    {where_clause}
    """
```

#### Style B: 다중 조인 및 동적 필터링형 (Dynamic Multi-Join Target)
* **적용**: 2개 이상의 테이블 조인이 들어가고, 사용자 필터 입력값 유무에 따라 WHERE 조건절이 동적으로 가변 탑재되어야 하는 일반 트랜잭션 데이터 쿼리.
* **포맷**: 가변 조건들을 파이썬 리스트(`conditions`)로 캡슐화한 뒤 `QueryFilter.build_where`로 취합하여 쿼리에 바인딩.
```python
def get_cqms_qi_mttc_rawdata(params: QualityIssueTasksParams) -> str:
    conditions = [
        QueryFilter.where_in("QI.PLANT", params.plant_list),
        QueryFilter.where_date_between(params.start_date, params.end_date, "QI.REG_DATE"),
        # 조건이 참일 때만 동적으로 생성
        QueryFilter.where_in("QI.STATUS", ["On-going"]) if params.status_filter else None
    ]
    where_clause = QueryFilter.build_where(conditions)
    
    return f"""--sql
    SELECT QI.*, M.M_CODE
    FROM {DatabricksTables.cqms_quality_main} QI
    INNER JOIN {DatabricksTables.cqms_quality_mcode} M ON QI.SEQ = M.CQMS_QUALITY_ISSUE_SEQ
    {where_clause}
    """
```

#### Style C: 대규모 CTE 구조화형 (Complex CTE-Structured Target)
* **적용**: 대규모 다단계 데이터 정제, LATERAL VIEW STACK 등의 가공 및 윈도우 함수가 수반되는 초복잡 분석용 쿼리.
* **포맷**: 서브 쿼리를 모듈로 쪼개지 않는 대신, SQL 소스 최상단에 명시적인 CTE(`WITH ... AS (...)`) 블록을 계층적으로 정비하여 가독성을 극대화하는 형태.
```python
def get_ctms_ctl_general_rawdata(params: CTMSProcessingParams) -> str:
    where_clause = QueryFilter.build_where([
        QueryFilter.where_in("SUBSTRING(MFG_CD, 5, 7)", params.mcode_list),
        QueryFilter.where_date_between(params.start_date, params.end_date, "MRM_DATE")
    ])
    
    return f"""--sql
    WITH base AS (
        SELECT DOC_NO, PLANT, TO_DATE(MRM_DATE, 'yyyyMMdd') AS MRM_DATE
        FROM {DatabricksTables.ctms_result_data}
        {where_clause}
    ),
    exploded AS (
        SELECT DOC_NO, PLANT, MRM_DATE, side, actual
        FROM base
        LATERAL VIEW STACK(2, 'UPPER', U_AVG, 'LOWER', L_AVG) s AS side, actual
    )
    SELECT * FROM exploded
    ORDER BY MRM_DATE DESC;
    """
```

### ⑤ 네이밍 컨벤션 표준화 (Comprehensive Naming Standards)
쿼리 레이어 전반의 일관성 향상과 파편화 방지를 위해 6가지 영역에 대한 명명 표준을 엄밀히 선언합니다.

#### 1) 테이블 변수명 데이터 클래스 및 변수명 (Table Data Classes & Variables)
- **테이블 데이터 클래스명 (Table Data Class Names)**:
  - **공식**: `{데이터베이스/소스 시스템명}Tables` (파스칼 케이스, `PascalCase` 적용)
  - **예시**: `DatabricksTables`, `OracleTables`, `SqliteTables`
- **JSON 메타데이터 내 Key 및 클래스 내부 변수명 (Internal Table Variables)**:
  - **공식**: `{시스템}_{도메인}_{세부내용}` (소문자 스네이크 케이스, `snake_case` 적용)
  - **설명**: 파이썬 테이블 데이터 클래스의 속성명과 JSON Key를 완전히 일치(1:1 매핑)시키며, 시스템명, 도메인명, 세부내용 순으로 정갈하게 결합하여 출처와 쓰임새를 명확히 나타냅니다.
  - **예시**: `cqms_qi_main`, `gmes_spec_product_master`, `ctms_ctl_result_raw`
  - **안티패턴**: `DBTables` (클래스명 모호), `QUALITY_MAIN` (대문자 및 출처/도메인 표기 누락), `tb_cqms_quality` (불필요한 'tb_' 접두사 기입 및 세부내용 구분 모호)

#### 2) 모듈명 (Module Files)
- **위치**: `app/queries/` 아래 배치.
- **규칙**: 소문자 스네이크 케이스(`snake_case`)를 사용하며, 반드시 접미사 `_query.py` 또는 접두사 `q_`를 부착합니다.
  - 올바른 예시: `cqms_query.py`, `ctms_query.py`, `q_iqm_plus.py`
  - 잘못된 예시: `cqmsSQL.py` (대소문자 혼용), `cqms_assembly.py` (접미사 규칙 불일치)

#### 3) 함수명 (Functions)
- **공개 API 함수**: 반드시 소문자 스네이크 케이스를 준수하고, 아래의 대통합 표준 공식과 접미사/접두사 체계를 적용합니다. (가장 중요)
  - **대통합 함수 명명 공식**: `get_{system}_{domain}_{조건/설명/특별한 내용이 없으면 general}_{agg/rawdata}`
  - **세부 분류 및 예시**:
    - **원시 데이터 조회 및 일반 조회**: `get_{system}_{domain}_general_rawdata`
      - 예: `get_cqms_qi_general_rawdata(...)`, `get_ctms_ctl_general_rawdata(...)`
    - **조건/설명형 조회**: `get_{system}_{domain}_{조건/설명}_rawdata`
      - 예: `get_cqms_qi_mttc_rawdata(...)` (여기서 system=cqms, domain=qi, 조건/설명=mttc, rawdata 타입)
    - **집계 데이터 조회**: `get_{system}_{domain}_{조건/설명}_agg`
      - 예: `get_gmes_production_plant_agg(...)` (system=gmes, domain=production, 조건/설명=plant, agg 타입)
    - **기준 정보 및 마스터 조회**: `get_{system}_{domain}_{조건/설명}_master` 또는 `_standard`
      - 예: `get_gmes_spec_product_master(...)`, `get_gmes_rr_standard(...)`
- **모듈 내부 비공개 헬퍼 함수**: 로컬에서 보조 조립(문자열 가공 등)을 담당하는 함수는 외부 노출을 완벽히 격리하기 위해 반드시 싱글 언더바(`_`) 접두사로 시작합니다.
  - 예: `_format_mcode_list(...)`, `_normalize_query_whitespace(...)`

#### 4) 공통상수명 (Global Constants)
- **규칙**: 대문자 스네이크 케이스(`UPPER_SNAKE_CASE`)를 필수 사용합니다.
- **예시**: `PLANT_TO_OEQG`, `STAGE_DICT`, `INCLUDED_TYPE_LIST`
- **안내**: 기존 공통상수 관리 파일(`constants/business.py`) 내부 상수는 기존 설계를 전적으로 수호하며 동일 스타일로 일관성을 유지합니다.

#### 5) 디코드 상수명 (Decode Constants)
- **JSON 메타데이터 내 Key**: 소문자 스네이크 케이스(`snake_case`)를 필수 적용합니다.
  - 예: `"plant_to_oeqg"`, `"stage_dict"`
- **파이썬 런타임 바인딩 변수**: JSON에서 읽어온 뒤 `SQLConverter`를 통해 쿼리 주입 전용 완성형 SQL 디코드 문자열로 보관되는 변수는 반드시 대문자 스네이크 케이스 및 `DECODE_` 접두사를 지정해 가시성을 높입니다.
  - 예: `DECODE_PLANT_TO_OEQG = SQLConverter.dict_to_decode_sql(...)`
  - 예: `DECODE_STAGE = SQLConverter.dict_to_decode_sql(...)`

#### 6) 기타 추가 가이딩 로컬 변수명 (Additional Local Variables)
- **파라미터 입력 변수**: 쿼리 함수의 표준 필터 데이터클래스를 받는 매개변수명은 항상 단수형인 `params`로 백퍼센트 통일합니다.
  - 예: `def get_cqms_qi_mttc_rawdata(params: QualityIssueTasksParams)`
- **동적 조건 리스트**: 여러 가변 `QueryFilter` 조건식을 수집하는 중간 리스트 변수명은 항상 복수형 명사인 `conditions`로 단일화합니다. (안티패턴: `conds`, `where_list` 방지)
  - 예: `conditions = [cond_a, cond_b]`
- **최종 SQL 조립 변수**: 쿼리 텍스트를 담아 리턴하는 로컬 변수명은 예외 없이 오직 `query`로만 선언 및 통일합니다.
  - 예: `query = f"""--sql SELECT ..."""` ➔ `return query` (안티패턴: `sql`, `sql_str`, `qry` 방지)
- **로깅 데코레이터명**: 쿼리 조립 시작 및 요약을 Trace 하는 데코레이터 함수 식별자는 `@log_query_assembly`로 정적으로 명명합니다.

---

## 3. 리팩토링 단계별 실행 로드맵 (Action Plan)

### 1단계: 영향도 분석 및 의존성 맵 설계 (Impact Analysis)
- `app/queries/` 내 함수들을 호출하는 `app/service/` 내 비즈니스 모듈(`*_df.py`)의 참조 리스트를 전수 매핑하여 영향도 맵을 작성합니다.

### 2단계: 테스트 하네스(Sandbox) 구축 (Harnessing Setup)
- 리팩토링 과정에서 SQL 문법이나 논리 구조가 변경되지 않음을 담보하기 위해, `tests/refactoring_harness_test.py` 검증 장치를 신규 설계합니다.
- 공백/줄바꿈 정규화 비교 및 SQL 주석 제거를 병행하여, 전후 SQL의 순수 기계적 의미 동등성을 완벽히 검증합니다.

### 3단계: JSON 메타데이터 아키텍처 수립 및 런타임 바인딩 구현
- `app/core/query/query_metadata.json` 설계를 착수하고, 테이블 상수와 DECODE 매핑 상수를 격리하여 기술합니다.
- `app/core/query/query_database.py`에서 JSON 파일을 싱글턴 패턴 혹은 모듈 임포트 시점에 동적으로 캐싱 로드하여 기존 `DatabricksTables` 및 `SQLiteTables` 구조에 바인딩하는 로직을 수립합니다.
- DECODE 전용 SQL 구문 조립 헬퍼를 `query_helper.py`에 마련하여 파이썬 런타임 변수 의존성을 해소합니다.

### 4단계: 모듈별 점진적 리팩토링 수행 (Iterative Refactoring)
- 스타일별 및 규모별 점진적 교정을 수행합니다.
- 쪼개져 있는 서브 CTE 쿼리들을 발견 시, 메인 쿼리 함수 본문 내부의 단일 CTE 문자열로 강제 수렴·병합합니다.

### 5단계: 하네스 테스트 검증 및 이관 (Validation & Merge)
- 작성한 모든 테스트 하네스를 기동하여, 전수 "GREEN (Pass)" 사인이 뜨는지 확인합니다.
- 형상관리 규정([L1-git.md](file:///home/jumasi/workstation/intelligence/rules/L1-git.md))에 의거하여 한글 커밋 및 동시 푸시(Dual Push)를 수행합니다.

---

## 4. 리팩토링 수행 시 안전 수칙 (Safety Guardrails)

> [!CAUTION]
> 1. **무단 수정 금지(Safety Lock)**: 본 계획서를 사용자가 정독하고 **"리팩토링을 승인한다"**고 동의하기 전까지는 어떠한 프로덕션 소스 코드(`app/queries/`, `app/service/` 등)도 수정하지 않습니다.
> 2. **인메모리 모킹 검증**: 하네스 테스트를 기동할 때 DB 물리적 커넥션이나 쓰기 작업이 유발되지 않도록 완벽한 Pure-String 레벨에서만 검증합니다.
> 3. **이모지 사용 절대 금지**: 소스 내 주석 및 로깅 메시지, 텍스트 등에 유니코드 이모지 사용을 금지합니다.
