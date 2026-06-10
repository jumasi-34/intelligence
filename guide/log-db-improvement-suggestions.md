# [보고서] 사용자 접속 로그 DB 운영 현황 및 보안/기능 보완 가이드

현재 운영 중인 SQLite 기반의 **사용자별 접속 로그 DB (`user_login`)**는 단순하면서도 Streamlit 화면과 SAP 인사 정보(`ops` DB)를 유연하게 결합하여 직관적인 방문자 분석 대시보드를 제공하고 있는 좋은 아키텍처입니다.

다만, 시스템의 실무 운영 안정성과 보안 감사(Audit Security), 그리고 비즈니스 분석 성능을 더욱 끌어올리기 위해 **보안 강화 및 설계 관점에서 보완할 수 있는 5가지 핵심 포인트**를 도출하였습니다.

---

## 1. 5대 핵심 보완 포인트

### 🔑 ① 역할(Role) 및 컨텍스트 정보의 누락 보완
* **현황**: `user_login` 테이블에는 `employee_id`(인사번호)와 `login_time`만 저장됩니다.
* **보완 이유**: 사용자가 로그인 시 선택한 역할(`Viewer`, `Contributor`, `Admin`) 정보가 DB에 남지 않아, 사후에 "누가 어떤 권한 권한으로 접속하여 어떤 데이터에 접근했는지" 세부 감사가 불가능합니다.
* **개선 제안**:
  - `user_login` 테이블에 `login_role` (TEXT) 컬럼을 추가합니다.
  - 로그인 성공 기록 시 `st.session_state`에 있는 `role` 값을 함께 저장합니다.

### 🔒 ② 로그인 실패(Failed Attempt) 로그 기록 (무차별 대입 공격 방어)
* **현황**: 로그인 실패 및 시도 횟수 관리는 오로지 Streamlit의 메모리 세션(`st.session_state`) 내에서만 처리되고 있습니다.
* **보완 이유**: 사용자가 브라우저를 새로고침하거나 창을 닫고 다시 열면 로그인 시도 횟수가 즉시 리셋되어, 해커나 악의적인 사용자의 **무차별 대입(Brute-force) 공격**을 차단할 수 없습니다.
* **개선 제안**:
  - `user_login_failed` 혹은 시도 이력을 관리하는 테이블을 구축합니다.
  - 로그인 실패 발생 시 "시도한 인사번호, 실패 시각, 접속 IP"를 DB에 기록하고, 특정 시간 내 실패가 누적되면 DB 레이어에서 자동으로 해당 IP 또는 인사번호를 일정 시간 차단(Lock)하도록 설계합니다.

### 🌐 ③ 접속 클라이언트 메타데이터 (IP & User-Agent) 기록
* **현황**: 어떤 기기, 어떤 브라우저, 어떤 네트워크 대역에서 접속했는지 기록이 전혀 없습니다.
* **보완 이유**: 계정 탈취나 다중 기기에서의 비정상 동시 접속을 식별하고 차단하기 어렵습니다.
* **개선 제안**:
  - Streamlit의 신규 기능인 `st.context.headers` 등을 활용해 클라이언트의 IP 주소와 `User-Agent` 브라우저 정보를 추출하여 `client_ip`, `user_agent` 컬럼에 함께 기록합니다.

### ⏱️ ④ 로그아웃(Logout) 및 세션 만료 시간 트래킹 부재
* **현황**: 로그인 시점만 기록될 뿐, 사용자가 언제 나갔는지(Logout) 알 수 없습니다.
* **보완 이유**: 실제 사용자가 시스템을 얼마나 사용했는지 **체류 시간(Usage Duration)** 분석이 불가능하고, 현재 **실시간 동시 접속 중인 Active 세션 수**를 파악하기 어렵습니다.
* **개선 제안**:
  - `user_login` 테이블에 `logout_time` (TEXT) 및 `last_activity_time` (TEXT) 컬럼을 추가합니다.
  - "로그아웃" 버튼 클릭 시 `logout_time`을 업데이트하고, 사용자가 화면을 이용하는 동안 주기적으로 `last_activity_time`을 갱신하도록 설계합니다.

### 🛡️ ⑤ 개인정보 보호 및 로그 보존 정책 (Compliance)
* **현황**: 관리자 화면(`Raw Data` 탭)에 인사번호와 이름이 완전 가공 없이 그대로 평문 노출되고 있습니다. 또한 SQLite 용량이 장기적으로 계속 누적됩니다.
* **보완 이유**: 사내 보안 컴플라이언스 및 개인정보 보호 규정을 충족하기 위해 불필요한 민감 정보의 광범위한 노출을 막아야 합니다.
* **개선 제안**:
  - **마스킹 처리**: 관리자 화면에 노출될 때 이름 중간 글자 및 인사번호 뒷자리를 마스킹 처리하는 옵션 적용 (예: `KIM * *`, `213***15`).
  - **로그 보존 정책(Retention Policy)**: 6개월 또는 1년이 지난 과거 접속 로그는 성능 저하를 방지하기 위해 정기적으로 백업 및 삭제(Log Purge)하는 유틸리티 작성.

---

## 2. 권장하는 개선 데이터베이스 스키마 설계 (DDL 예시)

현재 단일 테이블 구조를 아래와 같이 고도화하여 보완하는 것을 제안합니다.

### AS-IS (현재 구조)
```sql
CREATE TABLE user_login (
    employee_id INTEGER,
    login_time TEXT
);
```

### TO-BE (개선 구조)
```sql
-- 1. 성공 로그인 상세 감사 로그 테이블
CREATE TABLE user_login (
    login_id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_id INTEGER NOT NULL,
    login_role TEXT NOT NULL,         -- 로그인 시 부여된 권한 (Viewer, Contributor, Admin)
    login_time TEXT NOT NULL,         -- 로그인 일시
    logout_time TEXT,                 -- 로그아웃 일시 (또는 세션 만료 시간)
    last_activity_time TEXT,          -- 세션 만료 유추용 최종 활동 일시
    client_ip TEXT,                   -- 접속 IP 주소
    user_agent TEXT                   -- 브라우저 정보
);

-- 2. 보안 공격 모니터링용 로그인 실패 로그 테이블
CREATE TABLE user_login_failed (
    fail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    attempt_id TEXT,                  -- 시도한 ID
    fail_time TEXT NOT NULL,          -- 실패 일시
    client_ip TEXT,                   -- 시도한 IP 주소
    user_agent TEXT                   -- 브라우저 정보
);
```

---

## 3. 단계적 적용 로드맵 제안

1. **[보안 우선 - Immediate]**
   - **로그인 실패 이력 DB 기록**: Brute-force 공격 방어를 위해 실패 로그를 DB에 적재하는 기능을 최우선 적용합니다.
2. **[기능 고도화 - Short-term]**
   - **로그인 시 Role 및 IP, User-Agent 기록**: `user_login` 스키마에 해당 컬럼들을 추가하고 로그인 시 함께 인서트합니다.
3. **[분석 정교화 - Mid-term]**
   - **체류 시간(Logout) 추적 및 개인정보 마스킹**: 화면 로직 개선과 함께 마스킹 기법을 적용하여 사내 보안 규정을 완전히 충족시킵니다.
