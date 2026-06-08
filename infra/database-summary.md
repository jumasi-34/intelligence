# context-database-summary.md (다중 데이터베이스 커넥션 관리 요약)

Databricks(빅데이터 분석), Oracle(생산/품질), SQLite(메모리/운영) 간의 다중 DB 연결 안전성을 보장하고 커넥션 누수를 방지하기 위한 핵심 규격 지침입니다.

---

## 1. 불변 조건 (Invariants)
- **DataFrame 반환 일원화**: 모든 데이터베이스 클라이언트는 `.execute(query)` 또는 `.execute_query(query)` 실행 시, 반드시 결과를 **Pandas DataFrame** 구조로 일치시켜 반환해야 합니다.
- **Oracle BI 연결 안전성**: Oracle BI DB 연결 누수 및 타임아웃을 예방하기 위해, SQLAlchemy create_engine 시 반드시 **`pool_pre_ping=True`** 및 **`pool_recycle=3600`** 옵션을 강제해야 합니다.
- **자원 정리 (Dispose)**: 모든 Oracle 커넥션 인스턴스는 쿼리 수행 직후 `try-finally` 구문 내에서 무조건 **`engine.dispose()`**를 기동해 DB 리소스 누수(Leak)를 원천 차단해야 합니다.
- **SQLite 격리**: SQLite 데이터베이스는 오직 **`log`**(세션), **`staging`**(중간 집계), **`ops`**(인사 정보) 세 도메인 파일로만 경로 및 권한이 고정 관리되어야 합니다.
- **Databricks OAuth**: Databricks SQL 쿼리 시, SDK 자동 감지 및 토큰 갱신 병목을 피하고자 **OAuth Service Principal (`client_id`, `client_secret`)** 전용 자격 증명만 허용합니다.

---

## 2. 민감 소스 파일 (Sensitive files)
- `core/db/client.py` (모든 데이터베이스 연결 및 쿼리 실행 추상화 모듈)
- `core/query/query_database.py` (Databricks 테이블 고정 카탈로그 경로 관리 상수)

---

## 3. 필수 테스트 케이스 (Required tests)
- **자격 증명 미비 시 즉각 기각 검증**: 필수 환경변수 누락 시 `ValueError`가 정상적으로 발생하는가?
- **쿼리 실패 시 DB 자원 반환 검증**: 쿼리에 중대 오타가 있어 실행 예외가 나더라도, `engine.dispose()`가 보장되어 포트가 안전하게 닫히는가?
- **SQLite DML 동시 쓰기 락**: `log.db` 에 여러 세션이 동시 삽입할 때 `database is locked` 크래시 없이 조용히 재시도 처리되는가?
