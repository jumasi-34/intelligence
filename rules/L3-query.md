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

---

## 3. SQL 작성 및 조립 5대 표준
1. **Full Query 지향 (CTE 비분리)**:
   - CTE(Common Table Expressions)를 불필요하게 잘게 쪼개어 부분 쿼리로 나누지 말고, 가급적 하나로 완성된 구조화된 쿼리 형태로 반환합니다.
2. **쿼리 헬퍼 (`QueryFilter`, `SQLConverter`) 필수 활용**:
   - `app/core/query/query_helper.py`의 헬퍼 클래스를 사용해 동적 `WHERE`, `IN`, `DECODE` 조건문 등을 조립합니다.
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

## 4. 표준 명명 규칙 (Naming Standard)
* **원시 데이터 조회**: `get_<도메인>_*_rawdata(...)`
  - 예: `get_cqms_qi_mttc_rawdata(...)`
* **조건별 데이터 조회**: `get_<도메인>_*_by_<조건>(...)`
  - 예: `get_gmes_production_by_plant(...)`
* **기준 정보 및 마스터 조회**: `get_<도메인>_*_master(...)` 또는 `_standard(...)`
  - 예: `get_gmes_spec_product_master(...)`

---

## 5. Databricks 과금 방지 및 무분별한 쿼리 요청 차단 수칙 (Cost Control Guardrails)
1. **개발 중 실서버 쿼리 원천 금지**: 단순 UI 배치 변경, 변환 비즈니스 로직 수정 시 실제 Databricks에 접속하지 말고 `local.data/` 하위의 Parquet/CSV 덤프 데이터를 활용하여 Mocking 테스트를 진행하십시오.
2. **개발용 LIMIT 강제 바인딩**: 검증용으로 작성하는 쿼리 및 테스트 쿼리에는 데이터 풀 스캔을 막기 위해 반드시 `LIMIT 100` ~ `LIMIT 1000`을 강제 주입하여 샘플 데이터만 조회하도록 제한하십시오.
3. **Streamlit 캐시 무결성 유지**: 데이터 수집 서비스 함수는 무조건 `@st.cache_data`를 적용하고, 캐시 키 매개변수에 매번 바뀌는 변수(예: `datetime.now()`)를 바인딩하여 캐시가 깨지는 현상을 완벽히 방지하십시오.

