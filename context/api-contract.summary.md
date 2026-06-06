# API Contract Context Summary

UI(pages), 서비스(service), 쿼리(queries) 세 레이어 간의 유기적인 데이터 전달 정합성을 유지하고 하위 호환성 붕괴를 예방하기 위한 인터페이스 연동 규약입니다.

---

## 1. 불변 조건 (Invariants)
- **3-Layer 경계 엄수**:
  - `pages/` (UI)는 직접 SQL을 컴파일하거나 DB 클라이언트를 조작할 수 없으며, 반드시 `service/` 모듈의 함수를 경유해 데이터를 수집해야 합니다.
  - `queries/` (Query)는 데이터베이스를 실행(execute)하는 능력이 없어야 하며, 오직 조립 완료된 순수 **`str` SQL 쿼리**만 반환해야 합니다.
- **파라미터 표준화**: 모든 서비스 및 쿼리용 공용 API는 파라미터를 개별 변수가 아닌 **`core/params/parameters.py`**에 기선언된 특정 `dataclass`(예: `BaseFilterParams` 등) 단일 인자 형태로 통일하여 전달받아야 합니다.
- **데이터프레임 스키마 계약 보존**: 서비스 전처리 함수가 최종 리턴하는 Pandas DataFrame의 **공식 연산 컬럼명 및 데이터 타입**은 함부로 변경할 수 없습니다. 컬럼명이 변경되면 이를 매핑하여 그리던 `*_plots.py` 내부의 Plotly 차트 렌더링이 즉시 무너집니다.

---

## 2. 민감 소스 파일 (Sensitive files)
- `core/params/parameters.py` (전사 공통 파라미터 dataclass 수집 명세서)
- `core/query/query_helper.py` (SQL 결합용 QueryFilter, SQLConverter 조립기 모듈)
- `core/preprocessing/dataframe_helper.py` (Pandas DataFrame 구조 및 타입 조율 모듈)

---

## 3. 필수 테스트 케이스 (Required tests)
- **잘못된 파라미터 타입 유입 방어**: 기대하는 parameters 데이터클래스가 아닌 딕셔너리나 기형 객체 인입 시 명확히 오류 처리가 작동하는가?
- **리턴 데이터프레임 구조적 계약 검증**: 전처리 함수 리턴 DataFrame 내에 차트 렌더링에 꼭 필요한 필수 컬럼들(`PLANT`, `REG_DATE`, `OEQI` 등)이 올바른 타입으로 정확히 장착되어 있는가?
- **쿼리 헬퍼 조합 정합성**: `QueryFilter.where_in` 사용 시 올바른 IN 조건 구문(`'KP', 'DP'`)이 이스케이프와 함께 SQL 문자열 내에 정상 포맷팅되어 반환되는가?
