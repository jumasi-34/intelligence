# L3-query.md (L3 쿼리 레이어 개발 규칙)

이 문서는 프로젝트의 데이터베이스 조회 SQL을 정의하는 **쿼리 레이어(`app/queries/`)**의 핵심 개발 표준 및 안전 규칙을 정의합니다.

---

## 1. 쿼리 레이어의 핵심 역할 및 위치
- **위치**: `app/queries/` 아래에 배치
- **파일명**: `*_query.py` 또는 `q_*.py` 명명 규칙 준수
- **책임**: 오직 데이터베이스(Databricks, Oracle 등)에 전달할 **순수 SQL 문자열(`str`)**을 동적으로 조립하고 반환하는 것만 담당합니다.

---

## 2. 금지 규칙 (Strict Guardrails)
> [!IMPORTANT]
> 레이어 간 상호 작용 및 고수준 의존성 격벽 제약 조건은 단일 진실 공급원(SSOT)인 **[L2-architecture.md](intelligence/rules/L2-architecture.md)**의 규칙을 엄격히 준수합니다.

1. **SQL 실행 권한 제거**:
   - 쿼리 레이어 내부에서 어떠한 형태든 직접 DB 연결을 성립하거나 실행 메서드를 가동해서는 안 됩니다.
2. **인라인 하드코딩 금지**:
   - WHERE 조건절이나 테이블 경로 등을 하드코딩하지 않고, 공통 헬퍼와 중앙 상수를 통해 동적으로 바인딩해야 합니다.
3. **무의미한 일라인 구역/디코드 설명 주석 금지 및 필수 함수 식별 주석 준수**:
   - `# -- Query`, `# -- Decode Mapping`, `# ======== [도메인 명] ========` 같은 단순하고 관습적인 주석은 코드 청결도를 해치고 중복을 야기하므로 완전히 금지합니다. 쿼리 설계 사양이나 CTE 단계 등에 대한 설명은 표준화된 NumPy 스타일의 함수 Docstring 내 상세 가이드로 완벽하게 일원화하여 표현해야 합니다.
   - **단, 각 쿼리 함수 선언부 바로 위(데코레이터 위)에는 개발자가 함수를 직관적으로 파악할 수 있도록 대괄호 형태의 한글 기능명 주석(예: `# [도메인 - 한글 기능명]`)을 1줄로 반드시 기재해 두어야 합니다.** 이는 단순 구분 목적의 주석과 다른 필수 식별 가이드입니다.

---

## 3. SQL 작성 및 조립 5대 표준
1. **복잡 쿼리 CTE(Common Table Expressions) 지향**:
   - 단순한 단일 테이블 조회나 단순 조인은 CTE 없이 일반 SELECT 구문으로 간결하게 작성합니다.
   - 단, 2단계 이상의 집계 결합, 대용량 가공, LATERAL VIEW 등의 복잡한 단계적 로직이 수반될 때는 반드시 CTE(`WITH` 구문)를 설계하여 흐름을 위에서 아래로 논리적으로 나열해야 합니다.
2. **쿼리 헬퍼 및 변수 미사용 인라인 조립 필수**:
   - `app/core/query/query_helper.py`의 `QueryFilter`와 `SQLConverter`를 활용하여 동적 조건을 결합합니다.
   - 이때 가독성을 고도화하기 위해, 개별 조건에 대한 임시 지역 변수를 선언하지 않고 `QueryFilter.build_where` 리스트 매개변수 안에 헬퍼 함수를 직접 인라인으로 호출해 선언적 구성을 취하도록 합니다.
   - **AS-IS (불필요한 변수 선언)**:
     ```python
     plant_cond = QueryFilter.where_in("PLT_CD", params.plant_list)
     mcode_cond = QueryFilter.where_in("PRD_CD", params.mcode_list)
     where_clause = QueryFilter.build_where([plant_cond, mcode_cond])
     ```
   - **TO-BE (선언형 인라인 조립 - 가독성 극대화)**:
     ```python
     where_clause = QueryFilter.build_where([
         QueryFilter.where_in("PLT_CD", params.plant_list),
         QueryFilter.where_in("PRD_CD", params.mcode_list)
     ])
     ```
3. **중앙화 테이블 상수 바인딩**:
   - Databricks 테이블 경로는 임의의 문자열로 적지 않고, 반드시 `app/core/query/query_database.py` 내의 `DatabricksTables` 클래스 상수를 참조하여 바인딩합니다.
4. **파라미터 바인딩 통일**:
   - 쿼리 함수는 `app/core/params/parameters.py`에 선언된 파라미터 `dataclass`를 입력 인자로 전달받아 일관되게 처리합니다.
5. **한글 AS Alias(별칭) 사용 금지 및 물리 컬럼명 보존 수칙**:
   - SQL 쿼리 내에서 디스플레이용 한글 `AS "별칭"` 선언을 엄격히 금지합니다. 오직 영문 물리 컬럼명(예: `PLANT_CODE`, `MTTC_VAL`)을 그대로 반환하도록 설계하여, 컬럼명 강제 하드코딩으로 인한 관리 공수 폭증과 인코딩 오류, AI 컬럼 매핑 실수를 예방합니다. 한글 매핑 및 출력 포맷 제어는 오직 UI 단에서 메타데이터 헬퍼를 통해 연동합니다.
   - **AS-IS (안티패턴)**:
     ```sql
     SELECT plant_cd AS "공장코드", mttc_val AS "MTTC(시간)" FROM ...
     ```
   - **TO-BE (표준 준수)**:
     ```sql
     SELECT plant_cd, mttc_val FROM ...
     ```

---

## 4. 표준 쿼리 레퍼런스 및 모범 사례 (sample_query.py)
AI 에이전트 및 동료 개발자가 실시간으로 참조하고 복제할 수 있는 모범 사례 파이썬 모듈이 `app/queries/sample_query.py`에 위치하고 있습니다. 새로운 쿼리 모듈 작성 시 반드시 해당 구조를 참고하십시오.

---

## 5. 표준 명명 규칙 (Naming Standard)
* **원시 데이터 조회**: `get_<도메인>_*_rawdata(...)`
  - 예: `get_cqms_qi_mttc_rawdata(...)`
* **조건별 데이터 조회**: `get_<도메인>_*_by_<조건>(...)`
  - 예: `get_gmes_production_by_plant(...)`
* **기준 정보 및 마스터 조회**: `get_<도메인>_*_master(...)` 또는 `_standard(...)`
  - 예: `get_gmes_spec_product_master(...)`

---

## 6. Databricks 과금 방지 및 무분별한 쿼리 요청 차단 수칙 (Cost Control Guardrails)
1. **개발 중 실서버 쿼리 원천 금지**: 단순 UI 배치 변경, 변환 비즈니스 로직 수정 시 실제 Databricks에 접속하지 말고 `local.data/` 하위의 Parquet/CSV 덤프 데이터를 활용하여 Mocking 테스트를 진행하십시오.
2. **개발용 LIMIT 강제 바인딩**: 검증용으로 작성하는 쿼리 및 테스트 쿼리에는 데이터 풀 스캔을 막기 위해 반드시 `LIMIT 100` ~ `LIMIT 1000`을 강제 주입하여 샘플 데이터만 조회하도록 제한하십시오.
3. **Streamlit 캐시 무결성 유지**: 데이터 수집 서비스 함수는 무조건 `@st.cache_data`를 적용하고, 캐시 키 매개변수에 매번 바뀌는 변수(예: `datetime.now()`)를 바인딩하여 캐시가 깨지는 현상을 완벽히 방지하십시오.

---

## 7. 쿼리 함수 표준 독스트링(Docstring) 템플릿
모든 신규 및 기존 쿼리 함수는 아래의 NumPy 스타일 표준 독스트링 양식을 필수로 준수해야 합니다. 이 포맷은 데이터 구조 및 조인 흐름, 그리고 사용되는 파라미터 규격을 명시하여 에이전트와 휴먼 개발자 간의 가독성을 보증합니다.

```python
def get_<도메인>_<기능>_rawdata(params: <파라미터_클래스>) -> str:
    """
    [한 줄 요약] 대상 테이블에서 필요한 데이터를 조회하는 순수 SQL 쿼리를 생성합니다.

    [상세 설명]
    이 쿼리는 비즈니스 로직에 의거하여 다음과 같은 단계로 데이터를 가공/조립합니다.
    1. Base: <테이블_A상수>에서 지정된 필터 조건에 부합하는 대상 로우 추출
    2. Transformed/Joined: <테이블_B상수>와 LEFT JOIN하여 필요 부가 속성 바인딩
    3. Final: 영문 물리 컬럼명 보존을 유지하며 출력 최종 선택 및 정렬

    Parameters
    ----------
    params : <파라미터_클래스> (예: QualityIssueTasksParams)
        쿼리 조회 및 동적 조건 바인딩에 필요한 입력 파라미터 데이터클래스
        - plant_list : 조회 대상 공장 코드 리스트 (예: ['KP', 'DP'])
        - mcode_list : 조회 대상 자재 코드 리스트
        - start_date / end_date : 조회 기간 범위 (YYYYMMDD 형식 문자열)

    Returns
    -------
    str
        Databricks SQL 또는 SQLite SQL용 순수 동적 쿼리 문자열

    Examples
    --------
    >>> from app.core.params.parameters import QualityIssueTasksParams
    >>> params = QualityIssueTasksParams(plant_list=['KP'], start_date='20240101', end_date='20240131')
    >>> query = get_<도메인>_<기능>_rawdata(params)
    >>> print(query)
    """
```

