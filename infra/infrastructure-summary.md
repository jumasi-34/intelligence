# infrastructure-summary.md (공용 인프라스트럭처 연합 요약서)

이 문서는 시스템 내에 구축된 5대 핵심 인프라 영역(API 계약, 인증/권한, 과금/비용, 다중 DB 커넥션, 하네스 보안)의 **핵심 규칙, 불변 조건, 민감 소스 코드 파일 정보 및 필수 테스트 시나리오**를 단일화하여 통합 영속 관리하는 공용 인프라 연합 요약서(SSOT)입니다.

---

## 1. API 계약 및 아키텍처 정합성 지침 (API Contract Summary)

UI(pages), 서비스(service), 쿼리(queries) 세 레이어 간의 유기적인 데이터 전달 정합성을 유지하고 하위 호환성 붕괴를 예방하기 위한 인터페이스 연동 규약입니다.

### ① 불변 조건 (Invariants)
* **3-Layer 경계 엄수**:
  * `pages/` (UI)는 직접 SQL을 컴파일하거나 DB 클라이언트를 조작할 수 없으며, 반드시 `service/` 모듈의 함수를 경유해 데이터를 수집해야 합니다.
  * `queries/` (Query)는 데이터베이스를 실행(execute)하는 능력이 없어야 하며, 오직 조립 완료된 순수 **`str` SQL 쿼리**만 반환해야 합니다.
* **파라미터 표준화**: 모든 서비스 및 쿼리용 공용 API는 파라미터를 개별 변수가 아닌 **`core/params/parameters.py`**에 기선언된 특정 `dataclass`(예: `BaseFilterParams` 등) 단일 인자 형태로 통일하여 전달받아야 합니다.
* **데이터프레임 스키마 계약 보존**: 서비스 전처리 함수가 최종 리턴하는 Pandas DataFrame의 **공식 연산 컬럼명 및 데이터 타입**은 함부로 변경할 수 없습니다. 컬럼명이 변경되면 이를 매핑하여 그리던 `*_plots.py` 내부의 Plotly 차트 렌더링이 즉시 무너집니다.

### ② 민감 소스 파일 (Sensitive Files)
* `core/params/parameters.py` (전사 공통 파라미터 dataclass 수집 명세서)
* `core/query/query_helper.py` (SQL 결합용 QueryFilter, SQLConverter 조립기 모듈)
* `core/preprocessing/dataframe_helper.py` (Pandas DataFrame 구조 및 타입 조율 모듈)

### ③ 필수 테스트 케이스 (Required Tests)
* **잘못된 파라미터 타입 유입 방어**: 기대하는 parameters 데이터클래스가 아닌 딕셔너리나 기형 객체 인입 시 명확히 오류 처리가 작동하는가?
* **리턴 데이터프레임 구조적 계약 검증**: 전처리 함수 리턴 DataFrame 내에 차트 렌더링에 꼭 필요한 필수 컬럼들(`PLANT`, `REG_DATE`, `OEQI` 등)이 올바른 타입으로 정확히 장착되어 있는가?
* **쿼리 헬퍼 조합 정합성**: `QueryFilter.where_in` 사용 시 올바른 IN 조건 구문(`'KP', 'DP'`)이 이스케이프와 함께 SQL 문자열 내에 정상 포맷팅되어 반환되는가?

---

## 2. 인증 및 사용자 권한 도메인 요약 (Authentication & Authorization Summary)

인사번호 인증, 사용자 권한 및 Streamlit 세션 타임아웃을 안전하게 제어하기 위한 보안 필수 불변 수칙과 가이드라인입니다.

### ① 불변 조건 (Invariants)
* **인사번호 형식**: 사용자 인사번호(`personnel_id`)는 반드시 **8자리 숫자 정규식 (`^\d{8}$`)** 형식을 완벽히 만족해야 합니다.
* **역할 범위 및 비밀번호**: 시스템 역할은 `Viewer`, `Contributor`, `Admin` 세 가지만 존재합니다. `Admin`(131209) 및 `Contributor`(December)는 지정된 고정 패스워드 검증을 필수로 통과해야 합니다.
* **계정 잠금 정책**: 로그인 연속 **3회 실패 시**, 해당 세션은 강제로 잠금 처리(`st.session_state["is_locked"] = True`)되어 접근이 영구 봉쇄됩니다.
* **세션 타임아웃**: 사용자의 마지막 활동 시간(`last_activity`)이 기입되며, **30분** 동안 아무런 활동이 감지되지 않으면 세션이 자동 만료되고 로그아웃 처리됩니다.
* **인증 로그 강제 적재**: 성공적으로 로그인이 처리된 경우, 반드시 SQLite `log.db` 내 `user_login` 테이블에 `INSERT` DML 기록을 유실 없이 남겨야 합니다.

### ② 민감 소스 파일 (Sensitive Files)
* `pages/_90_system/login_page.py` (사용자 인증, 잠금, UI 렌더링 코어 모듈)
* `app.py` (세션 상태 수명 주기 제어 및 30분 활동 추적 엔진)
* `core/page/config_pages.py` (역할별 페이지 네비게이션 접근 통제 설정)

### ③ 필수 테스트 케이스 (Required Tests)
* **정상 인사번호 유형 검증**: 8자리 유효 숫자 및 비정상 문자 포함 시 즉각 기각 처리 검증.
* **계정 잠금 복구 및 한계 검증**: 실패 카운터 3회째 도달 시 즉각 잠금 여부 및 복구 불가 검증.
* **SQLite DML 예외 방어**: 로그 DB 장애 시 로그인 런타임 Crash가 발생하지 않고 조용히 예외 로깅 처리되는지 검증.

---

## 3. 과금 통제 및 Databricks 비용 관리 요약 (Billing & Cost Control Summary)

이 시스템에서 'Billing'은 **Databricks 빅데이터 서버 조회 비용 관리**와 **제조 품질 핵심 지표 계산식의 불변 정합성**을 통제하는 영역입니다.

### ① 불변 조건 (Invariants)
* **Databricks 캐싱 강제화**: Databricks 쿼리는 비용이 매우 고가이므로, 이를 직접 호출하는 모든 전처리 함수는 반드시 **`@st.cache_data(ttl=3600)`(1시간 캐시)**를 준수해야 합니다.
* **분모가 0인 경우 예외 회피**: 납품량(`SUPP_QTY`) 또는 생산량(`PROD_QTY`)이 **0**인 데이터 인입 시, 지표 연산에서 `ZeroDivisionError`가 유발되지 않고 안전하게 **0**으로 가공되도록 예외 처리를 필수로 통과해야 합니다.
* **품질 지표 공식 엄수**:
  * **OEQI(고객불량수치)** = `(QI_CNT / SUPP_QTY) * 1,000,000` (백만 납품당 불량건수)
  * **NCF_RATE(불합격률)** = `(NCF_CNT / PROD_QTY) * 100` (%)
  * 어떠한 리팩토링이나 변경 도중에도 위 수식 상수를 임의 변형해서는 안 됩니다.

### ② 민감 소스 파일 (Sensitive Files)
* `service/cqms_df.py` (OEQI 계산 공식 및 Databricks 캐싱 핵심 전처리부)
* `service/gmes_df.py` (생산량, 불합격률, RR, 중량 데이터 전처리부)
* `service/iqm_df.py` (제품 통합 품질 지표 및 누적 캐시 처리부)

### ③ 필수 테스트 케이스 (Required Tests)
* **분모 0 (Zero-Value) 예외 회피**: 납품량이 0일 때 OEQI 연산이 뻗지 않고 0으로 정상 반환되는가?
* **캐싱 동작 및 성능 검증**: 동일 필터 파라미터 연속 유입 시 데이터베이스 `.execute()` 함수가 추가 호출되지 않고 캐시 데이터가 즉시 리턴되는가?
* **OEQI 수식 극한치 검증**: QI_CNT가 납품량보다 높은 기형 데이터 인입 시 공식 연산이 오버플로우 없이 정확히 실행되는가?

---

## 4. 다중 데이터베이스 커넥션 관리 요약 (Multi-Database Connection Summary)

Databricks(빅데이터 분석), Oracle(생산/품질), SQLite(메모리/운영) 간의 다중 DB 연결 안전성을 보장하고 커넥션 누수를 방지하기 위한 핵심 규격 지침입니다.

### ① 불변 조건 (Invariants)
* **DataFrame 반환 일원화**: 모든 데이터베이스 클라이언트는 `.execute(query)` 또는 `.execute_query(query)` 실행 시, 반드시 결과를 **Pandas DataFrame** 구조로 일치시켜 반환해야 합니다.
* **Oracle BI 연결 안전성**: Oracle BI DB 연결 누수 및 타임아웃을 예방하기 위해, SQLAlchemy create_engine 시 반드시 **`pool_pre_ping=True`** 및 **`pool_recycle=3600`** 옵션을 강제해야 합니다.
* **자원 정리 (Dispose)**: 모든 Oracle 커넥션 인스턴스는 쿼리 수행 직후 `try-finally` 구문 내에서 무조건 **`engine.dispose()`**를 기동해 DB 리소스 누수(Leak)를 원천 차단해야 합니다.
* **SQLite 격리**: SQLite 데이터베이스는 오직 **`log`**(세션), **`staging`**(중간 집계), **`ops`**(인사 정보) 세 도메인 파일로만 경로 및 권한이 고정 관리되어야 합니다.
* **Databricks OAuth**: Databricks SQL 쿼리 시, SDK 자동 감지 및 토큰 갱신 병목을 피하고자 **OAuth Service Principal (`client_id`, `client_secret`)** 전용 자격 증명만 허용합니다.

### ② 민감 소스 파일 (Sensitive Files)
* `core/db/client.py` (모든 데이터베이스 연결 및 쿼리 실행 추상화 모듈)
* `core/query/query_database.py` (Databricks 테이블 고정 카탈로그 경로 관리 상수)

### ③ 필수 테스트 케이스 (Required Tests)
* **자격 증명 미비 시 즉각 기각 검증**: 필수 환경변수 누락 시 `ValueError`가 정상적으로 발생하는가?
* **쿼리 실패 시 DB 자원 반환 검증**: 쿼리에 중대 오타가 있어 실행 예외가 나더라도, `engine.dispose()`가 보장되어 포트가 안전하게 닫히는가?
* **SQLite DML 동시 쓰기 락**: `log.db` 에 여러 세션이 동시 삽입할 때 `database is locked` 크래시 없이 조용히 재시도 처리되는가?

---

## 5. AI 하네스 보안 요약 (Harness Security Summary)

이 문서는 AI 에이전트가 코드, 로그, PR, run archive를 생성할 때 반드시 지켜야 하는 보안 기준입니다.

### ① 절대 금지 (Absolute Prohibitions)
* `.env`, 토큰, 비밀번호, DB 접속 문자열, 개인 인증 정보를 출력하거나 run artifact에 저장하지 않습니다.
* Databricks, Oracle, SQLite 운영 DB에 write, destructive query, 임의 마이그레이션을 실행하지 않습니다.
* 운영 데이터 샘플, 사용자 식별자, 세션 로그, 메일 주소를 마스킹 없이 PR 본문이나 로그에 남기지 않습니다.
* raw SQL string concatenation으로 사용자 입력을 직접 결합하지 않습니다.

### ② 필수 기준 (Mandatory Rules)
* DB 조회는 가능한 `service/` 레이어와 기존 파라미터 dataclass를 경유합니다.
* 운영 DB 참조, 인증/권한, `.env`, `client.py`, `login_page.py` 변경은 High risk로 분류합니다.
* High risk 변경은 `risk.md`에 사유를 남기고 PR 본문에서 사람 승인을 받아야 합니다.
* AI-assisted PR은 `ai/runs/run_*` 아카이브와 `risk.md`의 Risk Level을 연결해야 합니다.

### ③ 로그와 아티팩트 (Logs & Artifacts)
* `task.md`, `context-manifest.yaml`, `plan.md`, `diff.patch`, `test.log`, `review.md`, `risk.md`에는 재현에 필요한 정보만 남깁니다.
* 내부 추론 원문이나 민감 데이터 원문 대신, 실행 계획과 결정 근거를 요약합니다.
* 사고 대응용 traceback은 파일명과 함수명 중심으로 축약하고 credential-like 문자열은 제거합니다.
