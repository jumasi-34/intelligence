# app/queries 쿼리 레이어 정합성 감사 보고서 (Queries Audit Report)

이 보고서는 `app/queries/` 디렉터리 내에 정의된 데이터베이스 조회용 SQL 쿼리 선언부 코드들을 대상으로 프로젝트 아키텍처 규칙, 행동 제약 조건 및 코드 규정 등을 준수하는지 종합적으로 진단한 정합성 감사 보고서입니다.

---

## 1. 감사 개요 및 기준

- **감사 대상 경로**: `app/queries/` 내의 전체 파이썬 소스 코드 및 문서 파일
- **적용 규칙 가이드라인 (단일 진실 공급원, SSOT)**:
  1. **[GEMINI.md](file:///home/jumasi/workstation/GEMINI.md)**: 소스코드 변경 제한(Safety Lock), 이모지 전면 금지, 아티팩트 관리 및 보관 정책 등
  2. **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**: 3-레이어 아키텍처, 의존성 격벽 제약 조건, UI 종속 라이브러리 제거
  3. **[L3-query.md](file:///home/jumasi/workstation/intelligence/rules/L3-query.md)**: 쿼리 레이어 5대 작성 표준, 명명 규칙, 파라미터 바인딩 및 테이블 상수 바인딩 통일

---

## 2. 종합 평가 및 핵심 요약

> [!NOTE]
> **종합 평가 요약**
> 쿼리 레이어(`app/queries/`)는 데이터베이스에 전달할 SQL 문자열을 조립 및 생성하는 책임을 전반적으로 훌륭하게 수행하고 있으며, **직접 DB 연결을 생성하거나 쿼리를 강제 실행(`execute`)하는 아키텍처 치명적 위반은 단 한 건도 발견되지 않았습니다.**
> 
> 그러나 **테이블 경로 하드코딩**, **파라미터 데이터클래스 미적용**, **역방향 의존성(Streamlit 임포트 및 데코레이터 캐싱)**, **이모지 사용**, **민감 보안 정보 방치** 등의 세부 규칙 위반 사례 및 테스트 코드 버그가 여러 파일에서 발견되었습니다.

| 파일명 | 파일 크기 | 아키텍처 정합성 상태 | 주요 미준수 항목 / 특이사항 |
| :--- | :---: | :---: | :--- |
| `cqms_query.py` | 18 KB | **주의 (WARNING)** | DatabricksTables 상수가 정의되어 있음에도 실제 SQL 쿼리에는 테이블 경로를 하드코딩함. |
| `ctms_query.py` | 4.5 KB | **우수 (EXCELLENT)** | 3-레이어 구조 및 L3-query 작성 가이드라인을 완벽히 준수함. |
| `dbx_query.py` | 0.4 KB | **보통 (NORMAL)** | 시스템 권한 조회용 소형 모듈로 특이사항 없음. |
| `ev3_query.py` | 4.8 KB | **주의 (WARNING)** | 테이블명 하드코딩, 개별 변수 직접 수신, 파일명과 내부 함수 도메인 불일치. |
| `gmes_query.py` | 80 KB | **주의 (WARNING)** | 테이블 경로 하드코딩 다수 검출 (`hkt_dw...`), 거대 파일 내 복잡한 쿼리 중복 잔존. |
| `hgws_return_query.py` | 3.5 KB | **주의 (WARNING)** | 테이블명 하드코딩, 개별 변수 수신 및 정적 쿼리 반환. |
| `hope_query.py` | 4.1 KB | **주의 (WARNING)** | Oracle BI 뷰 하드코딩, 임시 목적의 미사용 함수 잔존. |
| `plm_query.py` | 2.4 KB | **치명적 위반 (CRITICAL)** | **역방향 UI 의존성 유발 (`import streamlit as st`) 및 `@st.cache_data` 부적절한 캐싱 적용**, 테이블 경로 하드코딩. |
| `q_iqm_plus.py` | 38 KB | **주의 (WARNING)** | 파라미터 데이터클래스를 사용하지 않고 개별 변수 수신, 독자 실행 목적의 시스템 경로 조작(`sys.path.append`). |
| `qrs_query.py` | 112 KB | **보안 위험 (SECURITY)** | **사번 및 패스워드로 추정되는 주석이 노출되어 방치됨**, 명명 규칙 위반(접두사 `get_` 누락 및 카멜 케이스), 파라미터 데이터클래스 미사용. |
| `sap_query.py` | 5 KB | **결함 검출 (BUG)** | **이모지 사용 규정 위반 (`✅`, `❌`)**, **독자 실행 시 단언문(AssertionError) 실패로 비정상 종료되는 내부 결함 검출.** |
| `sqlite_query.py` | 1.6 KB | **주의 (WARNING)** | 함수명 카멜 케이스 오용, 데이터클래스 대신 개별 변수 사용, 일부 테이블명 하드코딩. |
| `CATALOG.md` | 10 KB | **참조 문서** | 쿼리 모듈 카탈로그 문서. |
| `gmes_query_duplicates.md` | 1.4 KB | **배치 위반 (RULE)** | 개발 분석용 마크다운 아티팩트가 쿼리 소스코드 폴더 내에 방치되어 위치 규칙 위반. |

---

## 3. 세부 위반 및 결함 분석 (Key Findings)

### ① 치명적 아키텍처 규칙 위반 (Layer Isolation Breach)
- **대상 파일**: [plm_query.py](file:///home/jumasi/workstation/app/queries/plm_query.py#L6-L21)
- **위반 사항**: 
  - `import streamlit as st`를 통해 쿼리 레이어에서 UI 패키지를 임포트하였습니다.
  - `get_ctms_ctl_IqmAnalysis_general_rawdata` 함수에 `@st.cache_data(ttl=3600)` 캐시 데코레이터를 적용하였습니다.
- **원인 및 정합성 위배 이유**:
  - `L2-architecture.md`에 따르면 쿼리 레이어는 오직 순수한 SQL 문자열(`str`) 조립만 담당해야 하며, UI 라이브러리(`streamlit`, `plotly` 등)를 임포트하여 역방향 의존성을 형성해서는 안 됩니다.
  - 쿼리 레이어에서 조립 문자열을 캐싱하는 것은 무의미합니다. 실제 캐싱과 데이터 쿼리 처리는 서비스 레이어(`app/service/*_df.py`)에서 적용되어야 합니다.

---

### ② 민감 정보 노출 및 보안 위험 (Security Vulnerability)
- **대상 파일**: [qrs_query.py](file:///home/jumasi/workstation/app/queries/qrs_query.py#L8)
- **위반 사항**:
  - 코드 상단 라인 8에 사번 및 패스워드로 추정되는 정보인 `# 21400060 // dhdbstlr1#` 주석이 노출되어 있습니다.
- **원인 및 정합성 위배 이유**:
  - 보안 통제 규칙상 소스 코드 내부 주석에 개인 자격 증명 정보나 기밀 정보를 포함해서는 절대 안 되며, 개발 과정에서 남겨진 임시 주석은 즉시 영구 삭제 대상입니다.

---

### ③ 독자 실행 테스트 코드 단언문(AssertionError) 실패 결함 (Bug & Defect)
- **대상 파일**: [sap_query.py](file:///home/jumasi/workstation/app/queries/sap_query.py#L173-L180)
- **버그 현상**:
  - 로컬 환경이나 터미널에서 `sap_query.py`를 단독 실행(`PYTHONPATH=. python app/queries/sap_query.py`)할 경우, 아래와 같이 내부 단언 검증 단계에서 실패하여 비정상 종료됩니다.
    ```bash
    $ PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python app/queries/sap_query.py
    🧪 SAP 인사정보 쿼리 모듈 테스트 시작
       ✅ dispatch 함수 테스트 성공
    ❌ 테스트 실패: PERNR 컬럼이 없음
    ```
- **원인 분석**:
  - `_cte_sap_personnel()` 함수(라인 55~64)는 실제 SQLite 테이블인 `SQLiteTables.ref_hk_personnel_info`를 조회하는 SQL을 빌딩합니다. 이때 실제 조회하는 컬럼은 `pnl_no AS PNL_NO`, `ename AS ENAME`, `pnl_nm AS PNL_NM`입니다.
  - 하지만 모듈의 하단 테스트 코드 라인 176~177에서는 아래와 같이 단언 검증을 하고 있습니다.
    ```python
    assert "PERNR" in cte_query, "PERNR 컬럼이 없음"
    assert "NACHN" in cte_query, "NACHN 컬럼이 없음"
    ```
  - 생성된 쿼리 문자열에 실제 `PERNR`, `NACHN` 문자열이 존재하지 않으므로 무조건 `AssertionError`가 발생하여 예외 처리부(`except`)로 분기하고 테스트가 무조건 실패합니다.

---

### ④ 이모지 사용 전면 금지 규칙 위반 (Emoji Rule Violation)
- **대상 파일**: [sap_query.py](file:///home/jumasi/workstation/app/queries/sap_query.py#L158-L189)
- **위반 사항**:
  - `sap_query.py` 파일 내 하단 테스트 코드 및 콘솔 출력 로그 영역에 유니코드 이모지 `✅`, `❌`, `🧪` 등이 무분별하게 하드코딩되어 있습니다.
- **원인 및 정합성 위배 이유**:
  - `GEMINI.md` 및 `L2-architecture.md`는 Streamlit UI 화면뿐 아니라 마크다운 문서, 버튼, 콘솔 출력, 소스코드 주석 등을 포함한 **전체 소스코드 공간**에서 일반 유니코드 이모지 사용을 엄격히 금지하고 있습니다. 

---

### ⑤ 중앙화 테이블 상수 바인딩 미준수 (Hardcoded Table Paths)
- **대표적 대상 파일**: `cqms_query.py`, `gmes_query.py`, `ev3_query.py`, `hgws_return_query.py`, `plm_query.py`
- **위반 사항**:
  - 테이블 상수인 `DatabricksTables`를 임포트해 두고도, 실제 SQL 블록에서는 물리적 테이블 경로 문자열을 그대로 하드코딩하여 사용하였습니다.
  - *예시 (cqms_query.py 라인 112)*:
    ```python
    # AS-IS (하드코딩)
    FROM hkt_system_dw.eqms.cqms_quality_issue
    
    # TO-BE (중앙 상수 바인딩)
    FROM {DatabricksTables.cqms_quality_main}
    ```
  - *예시 (plm_query.py 라인 45, 65)*:
    - `hkt_rnd_dw.full_specification.tb_pl_dw_spec_pd_mast_rel_bas` 및 `tb_pl_dw_spec_pd_item_ctl_bas` 테이블 경로가 SQL에 직접 기재되어 있습니다. 이 두 테이블은 심지어 `DatabricksTables` 공통 모듈에 상수로 정의조차 되어 있지 않습니다.
- **원인 및 정합성 위배 이유**:
  - `L3-query.md` 3.3에 따라 Databricks 테이블 경로는 임의의 문자열로 직접 하드코딩할 수 없으며, 반드시 `query_database.py` 내의 `DatabricksTables` 클래스 상수를 바인딩하여 런타임 환경에 따라 상응하는 테이블명이 유연하게 주입될 수 있도록 제안되어야 합니다.

---

### ⑥ 파라미터 데이터클래스 바인딩 미준수 (Raw Parameter Usage)
- **대표적 대상 파일**: `qrs_query.py` (전체 18개 핵심 함수), `q_iqm_plus.py`, `sqlite_query.py`, `ev3_query.py`
- **위반 사항**:
  - 쿼리를 생성하기 위한 필터 조건을 개별 변수(예: `start_date: str, end_date: str`, `mfg_mcode_list`) 형태로 직접 전달받고 있습니다.
- **원인 및 정합성 위배 이유**:
  - `L3-query.md` 3.4 표준에 명시된 바와 같이, 쿼리 생성 인자는 개별 파라미터로 산만하게 쪼개서 받지 않고 반드시 `app/core/params/parameters.py`에 선언된 캡슐화된 파라미터 `dataclass`를 입력 인자로 통합 전달받아 처리해야 합니다.

---

### ⑦ 표준 함수 명명 규칙 및 스타일 미준수 (Naming & Convention Issues)
- **대표적 대상 파일**: `sqlite_query.py`, `plm_query.py`, `qrs_query.py`
- **위반 사항**:
  - **카멜 케이스 남용**: `sqlite_query.py` 내 함수들의 중간 단어가 카멜 케이스로 선언되어 있습니다. (`get_sqlite_SpecMaster_iqm_rawdata`, `get_sqlite_ProductionVolume_iqm_rawdata`, `get_sqlite_SellinMonthlyAgg_iqm_rawdata` 등)
  - **접두사 누락**: `qrs_query.py` 내 모든 함수에 `get_` 접두사가 누락되어 있습니다. (`qrs_cal_op`, `qrs_ext_tread_op` 등)
- **원인 및 정합성 위배 이유**:
  - `L3-query.md` 4번 표준 규칙에 의거하여, 원시 조회의 경우 반드시 `get_<도메인>_*_rawdata(...)` 구조의 **순수 스네이크 케이스(Snake Case)** 규칙을 완벽하게 적용해야 합니다.

---

### ⑧ 임시/보고용 아티팩트 보관 위치 위반 (Artifact Location Breach)
- **대상 파일**: [gmes_query_duplicates.md](file:///home/jumasi/workstation/app/queries/gmes_query_duplicates.md)
- **위반 사항**:
  - 쿼리 중복 통합 및 리팩토링 검토 보고서인 `gmes_query_duplicates.md`가 쿼리 소스코드 폴더인 `app/queries/`에 잘못 배치되어 있습니다.
- **원인 및 정합성 위배 이유**:
  - `GEMINI.md` 및 `L2-architecture.md`는 소스코드 하위 디렉터리 내에 독립적인 마크다운 아티팩트를 보관하는 것을 엄격히 차단하고 있습니다. 발견 즉시 `intelligence/` 서브 폴더(예: `intelligence/guide/` 또는 `intelligence/domain/`)로 이관하고 정리해야 합니다.

---

## 4. 구체적인 수정 및 리팩토링 개선안 (Proposed Refactoring Plan)

> [!IMPORTANT]
> **Safety Lock (변경 제한 수칙) 준수 고지**
> `GEMINI.md` 제3조 제1항에 따라, 프로덕션 소스 코드(`app/queries/` 및 `app/core/`)를 **사용자의 명시적 승인 전까지 임의로 수정, 생성, 가공하지 않습니다.**
> 아래의 변경안을 검토하신 후, **사용자님의 구체적인 동의/승인(예: "수정을 허가한다" 또는 "수정안대로 코드를 고쳐라")**을 남겨주시면 정해진 수칙에 의거하여 안전하게 수정 작업을 기동하겠습니다.

### ① `plm_query.py` 리팩토링 제안
- **조치 1**: `import streamlit as st` 제거 및 `@st.cache_data` 어노테이션 제거
- **조치 2**: `tb_pl_dw_spec_pd_mast_rel_bas` 및 `tb_pl_dw_spec_pd_item_ctl_bas` 테이블명을 `app/core/query/query_database.py` 내 `DatabricksTables` 클래스에 아래 상수로 신규 선언 등록 및 본 파일에서 상수 바인딩 적용.
  ```python
  plm_spec_pd_mast_rel_bas: str = "hkt_rnd_dw.full_specification.tb_pl_dw_spec_pd_mast_rel_bas"
  plm_spec_pd_item_ctl_bas: str = "hkt_rnd_dw.full_specification.tb_pl_dw_spec_pd_item_ctl_bas"
  ```
  *(수정본 코드 시안)*
  ```python
  from app.core.params.parameters import CTMSProcessingParams
  from app.core.query.query_database import DatabricksTables
  from app.core.query.query_helper import QueryFilter, SQLConverter
  from app.core.query.query_config import SPEC_CD_LIST, CTL_ITEM_CAT_DIC

  def get_plm_mfgspec_general_rawdata(mcode_list):
      mcode_condition = QueryFilter.where_in("GDS_CD", mcode_list)
      query = f"""--sql
          SELECT * FROM {DatabricksTables.plm_spec_full}
          WHERE 1=1
              AND {mcode_condition}
              AND substring(SPEC_CD, 12, 1) IN ('S', 'M', 'T')
          """
      return query

  def get_ctms_ctl_iqm_analysis_general_rawdata(
      params: CTMSProcessingParams, direction: str = "UPPER"
  ):
      mcode_condition = QueryFilter.where_like("SPEC_CD", params.mcode_list, "both_ends_with")
      spec_cd_condition = QueryFilter.where_in("SUBSTRING(ISPCM_SPEC_CD, 12, 1)", SPEC_CD_LIST)
      condition = [mcode_condition, spec_cd_condition]
      where_clause = QueryFilter.build_where(condition)

      query = f"""--sql
          WITH REL AS (
              SELECT
                  DATE_FORMAT(to_timestamp(RGSDTM, 'yyyyMMddHHmmss'), 'yyyy-MM-dd') AS REG_DATE,
                  STRING_AGG(DISTINCT SUBSTRING(ISPCM_SPEC_CD, 12, 1), ',') AS SPEC,
                  SUBSTRING(ISPCM_SPEC_CD, 13, 5) AS REV,
                  INDSPDC_OBJ_TBLK
              FROM {DatabricksTables.plm_spec_pd_mast_rel_bas}
              {where_clause}
              GROUP BY
                  DATE_FORMAT(to_timestamp(RGSDTM, 'yyyyMMddHHmmss'), 'yyyy-MM-dd'),
                  SUBSTRING(ISPCM_SPEC_CD, 13, 5),
                  INDSPDC_OBJ_TBLK
              )
          SELECT
              REL.REG_DATE,
              REL.SPEC,
              REL.REV,
              CTL.SFPRD_TPNM AS SEMI_PRDT,
              CTL.ITMNM AS ITEM,
              {"CTL.UPS_VAL AS UPPER," if direction == "UPPER" else ""}
              {"CTL.LWRSD_VAL AS LOWER," if direction == "LOWER" else ""}
              CTL.TLRNC_VAL AS TOL
          FROM REL
          LEFT JOIN {DatabricksTables.plm_spec_pd_item_ctl_bas} AS CTL
          ON REL.INDSPDC_OBJ_TBLK = CTL.INDSPDC_OBJ_TBLK
          WHERE 1=1
              AND CTL.ITMNM IN ({','.join([f"'{k}'" for k in CTL_ITEM_CAT_DIC.keys()])});
          """
      return query
  ```

---

### ② `sap_query.py` 결함 수정 및 이모지 제거 제안
- **조치 1**: 독자 실행 시 무조건 에러가 발생하는 테스트 코드 검증문 수정 (실제 반환되는 컬럼명인 `PNL_NO`, `PNL_NM`을 검증하도록 정정)
- **조치 2**: 파일 내 모든 콘솔 출력 로그에서 유니코드 이모지 제거 및 문자형 포맷으로 대체 수호
  *(수정본 테스트 블록 시안)*
  ```python
  if __name__ == "__main__":
      print("[TEST] SAP personnel query module test start")

      try:
          query = dispatch_sap_personnel_query()
          assert isinstance(query, str), "Query is not string"
          assert len(query) > 0, "Empty query generated"
          assert "SELECT" in query.upper(), "SELECT keyword missing"
          assert "PNL_NO" in query, "PNL_NO column missing"
          assert "PNL_NM" in query, "PNL_NM column missing"
          print("   [OK] dispatch function test success")

          cte_query = _cte_sap_personnel()
          assert isinstance(cte_query, str), "CTE Query is not string"
          assert "PNL_NO" in cte_query, "PNL_NO column missing"
          assert "PNL_NM" in cte_query, "PNL_NM column missing"
          print("   [OK] CTE function test success")

          legacy_query = direct_sap_personnel_query()
          assert isinstance(legacy_query, str), "Legacy compatibility function failed"
          print("   [OK] legacy function compatibility check")
          print("[SUCCESS] All tests passed")

      except Exception as e:
          print(f"[FAIL] Test failed: {e}")
  ```

---

### ③ `qrs_query.py` 보안 위험 노출 주석 삭제 제안
- **조치**: 라인 8의 `# 21400060 // dhdbstlr1#` 주석 라인을 영구 삭제하여 계정 정보 자격 증명 노출 위협 차단.

---

### ④ `app/queries/` 테이블명 하드코딩 일괄 교정 및 상수 바인딩 적용 제안
- **조치**: `cqms_query.py`, `ev3_query.py`, `gmes_query.py`, `hgws_return_query.py` 등의 파일 내부 SQL 쿼리 본문에 수동 기술된 물리 테이블명을 사전에 등록된 `DatabricksTables` 또는 `SQLiteTables` 변수 런타임 주입 바인딩으로 전면 수정 교정합니다.

---

### ⑤ `gmes_query_duplicates.md` 파일 올바른 경로 이관 제안
- **조치**: `app/queries/gmes_query_duplicates.md` 파일을 `intelligence/guide/gmes_query_duplicates.md`로 물리적으로 이동시킵니다.

---

### ⑥ 명명 규칙(카멜 케이스 -> 스네이크 케이스) 및 데이터클래스 파라미터 바인딩 교정 제안
- **조치**: `sqlite_query.py`, `qrs_query.py` 등 표준 명명 규칙 및 매개변수 데이터클래스를 위반하는 함수들에 대하여, 하위 호환성을 완벽히 수호하는 선에서 가이드라인과 100% 일치하도록 시그니처 및 명칭 교정 작업을 순차 적용합니다.

---

## 5. 결론 및 승인 요청

본 감사를 통해 쿼리 레이어 전반의 아키텍처 및 코딩 수칙 부합성을 정밀 확인하였으며, 사소한 이모지 위반부터 보안 위험 주석, 치명적 UI 라이브러리 임포트, 테스트 단언문 버그에 이르는 실질적인 품질 저하 요소들을 다량으로 발굴하는 성과를 거두었습니다.

상기 제안된 개선안들을 바탕으로 수정을 전격 적용하고자 하오니, **변경 작업을 허가하는 최종 명시적 승인**을 당부드립니다. 승인 직후 순차적이고도 매우 조심스럽게 코드베이스 정비 및 수정을 단행하겠습니다.
