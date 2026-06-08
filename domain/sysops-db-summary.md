# sysops-db-summary.md (SQLite 세션 및 운영 로그 도메인 요약)

이 시스템에서 'SysOps & SQLite'는 사용자 세션 검증, 유저 권한 매핑, 오퍼레이션 로깅, 그리고 일회성 배치 연산 결과를 일시 홀딩하는 **시스템 중앙 제어 및 로컬 영속화 허브**입니다. 메인 DB 데이터 유출 방지와 로컬 로그 무결성이 극도로 보존되어야 하는 인프라스트럭처 보안 영역입니다.

---

## 1. 도메인 규칙 및 불변 조건 (Invariants)
- **로컬 데이터의 독립성 및 동시성 보호**:
  - 로컬 SQLite 데이터베이스 파일(`database/log.db`, `database/ops.db`)은 다중 유저가 접속하는 Streamlit 특성상 무거운 트랜잭션 충돌로 인해 Lock이 걸리지 않도록 동시성 제어 장치(timeout, WAL mode)가 불변하게 동작해야 합니다.
- **인증 자격 증명의 철저한 격리**:
  - 암호화되지 않은 유저 비밀번호나 식별 키를 SQLite 데이터베이스에 그대로 평문 저장하는 행위는 엄격히 금지됩니다.

---

## 2. 민감 소스 파일 (Sensitive Files)
- `core/db/sqlite_utils.py` (SQLite 커넥션 풀 구축, 트랜잭션 오퍼레이션 래퍼 및 WAL 모드 활성화부)
- `pages/_80_admin/sqlite_management_page.py` (시스템 데이터 관리 및 SQLite 다이렉트 컨트롤 어드민 화면)
- `pages/_90_system/login_page.py` (사용자 권한 검증 및 로그 테이블 동기화부)

---

## 3. 절대 금지 행동 (Prohibited Actions)
- 유저 세션 가로채기를 방해할 수 있는 하이재킹 취약점을 유발하는 방식으로 SQLite 쿠키/세션 홀더에 평문 자격 증명을 평문 보관하는 행동.
- 어드민 권한 체크(`st.session_state.user_role == 'Admin'`) 우회 처리를 삽입하여 비인가 사용자에게 SQLite 다이렉트 조작 패널을 개방하는 백도어 개발 행위.

---

## 4. 필수 테스트 시나리오 (Required Test Scenarios)
- **다중 쓰기 동시성 Lock 테스트**: 10명의 가상 모킹 사용자가 동시에 SQLite에 접속하여 개별 오퍼레이션 로그 쓰기 연산을 난타 호출할 때, `sqlite3.OperationalError: database is locked` 예외 없이 WAL 모드 및 타임아웃 기능에 의해 부드럽게 큐잉되어 안전 완료되는가?
- **비인가 권한 접근 차단 검증**: 비Admin 권한(`Contributor` 또는 `Viewer`)의 세션을 부여하고 `sqlite_management_page.py`를 다이렉트 임포트 호출할 때, 에러 및 즉시 차단 화면이 올바로 렌더링되는가?
- **로그 위변조 차단 테스트**: 로그 저장 함수 호출 시, 생성 일시(`LOG_DT`)를 사용자가 입력하는 임의 값이 아닌 서버 시스템 표준시(`datetime.now()`)가 원천 고정 기입되도록 로직이 설계되어 있는가?
