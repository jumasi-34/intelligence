# L3-query.md (L3 쿼리 레이어 개발 규칙)

이 문서는 프로젝트의 데이터베이스 조회 SQL을 정의하는 **쿼리 레이어(`app/queries/`)**의 핵심 개발 표준 및 안전 규칙을 정의합니다.

---

## 1. 쿼리 레이어의 핵심 역할 및 위치
- **위치**: `app/queries/` 아래에 배치
- **파일명**: `*_query.py` 또는 `q_*.py` 명명 규칙 준수
- **책임**: 오직 데이터베이스(Databricks, Oracle 등)에 전달할 **순수 SQL 문자열(`str`)**을 동적으로 조립하고 반환하는 것만 담당합니다.

---

## 2. 쿼리 레이어의 3대 금지 규칙 (Strict Guardrails)
1. **DB 직접 실행 금지 (No DB Execute)**:
   - 쿼리 파일 내에서 직접 데이터베이스 클라이언트를 임포트하여 `execute()`를 수행하지 않습니다.
   - [안티패턴] `from app.core.operate.db_client import get_client`
2. **타 레이어 임포트 금지 (No Reverse Dependencies)**:
   - 쿼리 레이어는 UI 레이어(`app/pages/`)나 서비스 레이어(`app/service/`)의 모듈을 절대 임포트할 수 없습니다.
3. **인라인 하드코딩 금지**:
   - `WHERE` 조건절이나 테이블 경로 등을 하드코딩하지 않고, 공통 헬퍼와 중앙 상수를 통해 동적으로 바인딩해야 합니다.

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

---

## 4. 표준 명명 규칙 (Naming Standard)
* **원시 데이터 조회**: `get_<도메인>_*_rawdata(...)`
  - 예: `get_cqms_qi_mttc_rawdata(...)`
* **조건별 데이터 조회**: `get_<도메인>_*_by_<조건>(...)`
  - 예: `get_gmes_production_by_plant(...)`
* **기준 정보 및 마스터 조회**: `get_<도메인>_*_master(...)` 또는 `_standard(...)`
  - 예: `get_gmes_spec_product_master(...)`
