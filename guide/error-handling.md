# error-handling.md (UI 렌더링 예외 처리 및 SQLite 영구 로깅 설계 가이드)

이 문서는 파이썬 및 Streamlit의 실행 구조 내에서 컴포넌트 오류 발생 시, 사용자 정보, 발생 시각, 코드 위치를 추적하여 SQLite(log DB)에 영구 저장하는 예외 격리 및 감사 로깅(Audit Logging) 표준 설계 사양을 정의합니다.

사용자가 특정 기능에서 에러를 경험했을 때, 해당 기능 구역에서만 에러가 발생했음을 사용자에게 고지하고 전체 페이지가 중단(Crash)되지 않으며, 다른 기능 및 컴포넌트들은 계속해서 정상적으로 렌더링 및 작동되도록 보장하는 에러 격리(Error Boundary) 메커니즘을 규정합니다.

---

## 1. 전체 로깅 파이프라인 아키텍처 (Error & Audit Logging Flow)

특정 탭이나 차트 등에서 예외가 발생하면, 시스템은 화면 전체가 깨지는 것을 방지하는 동시에 다음과 같이 유기적으로 작동하여 장애 정보를 영구히 기록합니다.

```
[ UI 컴포넌트 예외 발생 ]
        │
        ▼ (try-except 격리 감지)
[ st_error_boundary / @error_safe_plot / @log_error ]
        │
        ├─▶ [1] 사용자 경험 보호: 우아한 Fallback UI & Empty Figure 출력 (화면 유지)
        │
        └─▶ [2] 장애 맥락 추출 (Error Context Extractor)
                    │  - 접속자 사번 (personnel_id), 이름 (user_name), 권한 (role)
                    │  - 에러 발생 시각 (YYYY-MM-DD HH:MM:SS)
                    │  - 에러 원인 코드 위치 (파일 경로, 라인 번호, 에러 타입/메시지)
                    │  - 상세 Stack Trace
                    ▼
            [ SQLite 영구 로깅 적재 ] ──▶ ~/database/log.db (app_error_logs 테이블)
```

---

## 2. SQLite 에러 로그 테이블 정의 (DDL)

에러 분석 및 개발진의 추후 신속한 디버깅을 지원하기 위해 SQLite `log` 데이터베이스에 적재할 에러 트랙용 `app_error_logs` 테이블 스펙입니다.

```sql
-- SQLite 'log.db' 내 생성될 에러 로그 이력 관리 테이블
CREATE TABLE IF NOT EXISTS app_error_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,             -- 에러 발생 일시 (YYYY-MM-DD HH:MM:SS)
    personnel_id TEXT,                  -- 로그인한 사용자의 사번 (8자리 숫자, 미로그인 시 'Guest')
    user_name TEXT,                     -- 로그인한 사용자의 한글명
    user_role TEXT,                     -- 로그인한 사용자의 권한 등급 (Admin, Contributor, Viewer)
    component_name TEXT NOT NULL,       -- 오류 발생한 화면 영역/컴포넌트 식별자
    error_type TEXT NOT NULL,           -- 파이썬 예외 클래스명 (e.g., KeyError, ZeroDivisionError)
    error_message TEXT,                 -- 상세 예외 메시지 내용
    stack_trace TEXT,                   -- 디버깅용 파이썬 full stack trace (traceback)
    file_path TEXT,                     -- 오류 유발 실제 소스 코드 파일명
    line_number INTEGER,                -- 오류가 발생한 라인 번호 (추적 가능 시)
    page_path TEXT                      -- 에러 발생 시 접속 중인 대시보드 화면 경로 (sys.argv)
);

-- 검색 속도 최적화를 위한 인덱스 설정
CREATE INDEX IF NOT EXISTS idx_err_logs_timestamp ON app_error_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_err_logs_personnel ON app_error_logs(personnel_id);
```

---

## 3. 에러 발생 정보 및 사용자 컨텍스트 추출 설계

### (1) Streamlit 세션 기반 사용자 정보 추출
로그인 세션 바인딩 방식에 의거하여, 에러가 포착되는 시점에 `st.session_state`를 조회하여 현재 활성화된 세션의 사용자 메타데이터를 안정적으로 확보합니다.

```python
import streamlit as st

def get_current_user_context():
    """현재 세션에서 접속자 정보를 조회하여 딕셔너리로 반환합니다."""
    try:
        personnel_id = st.session_state.get("personnel_id", "Guest")
        user_name = st.session_state.get("user_name", "Guest")
        role = st.session_state.get("role", "Guest")
    except Exception:
        personnel_id = "System/Background"
        user_name = "System"
        role = "System"
        
    return {
        "personnel_id": personnel_id,
        "user_name": user_name,
        "role": role
    }
```

### (2) 파이썬 traceback 분석을 통한 대상 코드 위치 역추적
예외 객체의 `__traceback__` 속성을 파싱하여, 공통 헬퍼의 위치가 아닌 실제로 에러를 촉발한 최종 비즈니스 소스 코드 파일(`file_path`) 및 라인 번호(`line_number`)를 분석해 냅니다.

```python
import traceback
import sys

def extract_error_location(exception: Exception):
    """예외 객체를 분석하여 실제 에러가 시작된 사용자 코드의 위치 정보를 반환합니다."""
    exc_type, exc_value, exc_tb = sys.exc_info()
    if not exc_tb:
        exc_tb = exception.__traceback__
        
    tb_list = traceback.extract_tb(exc_tb)
    if tb_list:
        last_frame = tb_list[-1]
        return {
            "file_path": last_frame.filename,
            "line_number": last_frame.lineno,
            "function_name": last_frame.name
        }
    return {
        "file_path": "Unknown",
        "line_number": 0,
        "function_name": "Unknown"
    }
```

---

## 4. SQLite 영구 로깅 프레임워크 구현 표준안 (Implementation Code)

해당 구현은 `app/core/ui/error_handler.py` 또는 `core/utils/error_boundary.py`에 구성되어 시스템 내부의 모든 렌더링 예외를 SQLite DB에 트랜잭션 단위로 안전하게 커밋합니다.

```python
import contextlib
import functools
import logging
import sqlite3
import traceback
import sys
from datetime import datetime
import streamlit as st

from app.core.db.client import get_client

logger = logging.getLogger("goeq_bi.ui_error")

def get_sqlite_log_conn():
    """SQLite log 클라이언트를 통해 실제 DB 연결 커넥션을 생성합니다."""
    try:
        sqlite_log_client = get_client("sqlite", "log")
        conn = sqlite3.connect(sqlite_log_client.db_path)
        return conn
    except Exception as e:
        logger.error(f"SQLite log.db 커넥션 생성 실패: {str(e)}")
        return None

def initialize_error_log_table():
    """로그 DB에 에러 로그 기록용 테이블이 존재하지 않을 시 자동 생성합니다."""
    conn = get_sqlite_log_conn()
    if not conn:
        return
    try:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS app_error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            personnel_id TEXT,
            user_name TEXT,
            user_role TEXT,
            component_name TEXT NOT NULL,
            error_type TEXT NOT NULL,
            error_message TEXT,
            stack_trace TEXT,
            file_path TEXT,
            line_number INTEGER,
            page_path TEXT
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_err_logs_timestamp ON app_error_logs(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_err_logs_personnel ON app_error_logs(personnel_id);")
        conn.commit()
    except Exception as e:
        logger.error(f"app_error_logs 테이블 초기화 실패: {str(e)}")
    finally:
        conn.close()

def log_error_to_sqlite(component_name: str, exception: Exception):
    """포착된 에러 컨텍스트와 세션 로그인 정보를 융합하여 SQLite log 데이터베이스에 영구 적재합니다."""
    initialize_error_log_table()
    
    conn = get_sqlite_log_conn()
    if not conn:
        return
        
    try:
        personnel_id = st.session_state.get("personnel_id", "Guest")
        user_name = st.session_state.get("user_name", "Guest")
        user_role = st.session_state.get("role", "Guest")
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        error_type = type(exception).__name__
        error_message = str(exception)
        stack_trace = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))
        
        loc_info = extract_error_location(exception)
        file_path = loc_info["file_path"]
        line_number = loc_info["line_number"]
        
        page_path = "Unknown"
        if len(sys.argv) > 0:
            page_path = sys.argv[-1]
            
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO app_error_logs (
                timestamp, personnel_id, user_name, user_role,
                component_name, error_type, error_message, stack_trace,
                file_path, line_number, page_path
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            timestamp, personnel_id, user_name, user_role,
            component_name, error_type, error_message, stack_trace,
            file_path, line_number, page_path
        ))
        conn.commit()
        logger.info(f"[DB_AUDIT_LOG_SUCCESS] {component_name} 에러 SQLite 적재 완료 (사용자: {user_name}/{personnel_id})")
        
    except Exception as e:
        logger.error(f"SQLite에 에러 로그 INSERT 중 예외 발생: {str(e)}", exc_info=True)
    finally:
        conn.close()
```

---

## 5. 로깅 모듈이 통합된 에러 격리 컴포넌트 설계

### (1) st_error_boundary 컨텍스트 매니저
에러 자동 영구 로깅(SQLite) 기능이 내장된 UI용 샌드박스 컨텍스트 매니저입니다.

```python
@contextlib.contextmanager
def st_error_boundary(component_name: str, fallback_type: str = "warning"):
    try:
        yield
    except Exception as e:
        log_error_to_sqlite(component_name, e)
        
        if fallback_type == "warning":
            st.warning(f"[경고] {component_name} 데이터를 시각화하는 중 오류가 발생하여 표시할 수 없습니다.")
        elif fallback_type == "info":
            st.info(f"정보: {component_name} 섹션은 현재 시스템 점검 또는 데이터 분석 준비 중입니다.")
        elif fallback_type == "empty":
            st.write("")
        else:
            st.error(f"오류: {component_name} 로딩 중 오류가 발생했습니다.")
```

### (2) error_safe_plot 데코레이터
차트 그리기 전용 데코레이터로, 예외가 발생할 경우 에러 정보를 SQLite에 자동 기록 후 빈 차트 피규어(Empty Figure)를 리턴합니다.

```python
def error_safe_plot(chart_title: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                if args and hasattr(args[0], "empty"):
                    df = args[0]
                    if df is None or df.empty:
                        return create_empty_figure(chart_title, "조회 조건에 해당하는 데이터가 없습니다.")
                
                return func(*args, **kwargs)
                
            except Exception as e:
                log_error_to_sqlite(f"Plot: {chart_title}", e)
                return create_empty_figure(chart_title, f"차트 렌더링 중 오류가 기록되었습니다. (오류 내용: {type(e).__name__})")
        return wrapper
    return decorator
```

### (3) log_error 데코레이터
일반 비즈니스 로직 및 서비스/전처리 함수에 전역 에러 경계를 형성하고, 실패 시 지정된 안전 기본값(Default Return)을 반환하는 데코레이터입니다.

```python
def log_error(feature_name: str, default_return=None):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                log_error_to_sqlite(feature_name, e)
                
                st.error(
                    f"주의: {feature_name} 기능 로딩 중 일시적인 오류가 발생했습니다.\n\n"
                    f"일부 데이터를 표시할 수 없으나, 다른 기능 및 차트는 계속해서 이용이 가능합니다.\n"
                    f"(상세 원인: {str(e)})"
                )
                return default_return
        return wrapper
    return decorator
```

---

## 6. 에러 로그 감사 및 확인 방법 (Audit Verification)

적재된 에러 로그는 SQLite 전용 관리자 화면이나, DB 클라이언트를 통해 아래 SQL로 정밀 추적 및 상태 점검을 진행할 수 있습니다.

```sql
-- 1. 가장 최근 발생한 에러 10건 정밀 조회 (접속 유저, 코드 위치 확인용)
SELECT timestamp, personnel_id, user_name, component_name, error_type, file_path, line_number 
FROM app_error_logs 
ORDER BY timestamp DESC 
LIMIT 10;

-- 2. 사용자별/권한별 에러 조우 횟수 집계
SELECT user_role, COUNT(*) as err_count 
FROM app_error_logs 
GROUP BY user_role;

-- 3. 특정 파일의 특정 라인에서 반복적으로 터진 버그 추적
SELECT file_path, line_number, COUNT(*) as occur_count, error_message 
FROM app_error_logs 
GROUP BY file_path, line_number 
ORDER BY occur_count DESC;
```
