# context-coding-standards.md (프로젝트 전역 코딩 스타일 및 표준 가이드라인)

이 문서는 CQ-BI 프로젝트에서 개발자 및 모든 AI 에이전트(개발, 품질, 운영)가 신규 코드를 작성하거나 리팩토링할 때 반드시 준수해야 하는 **공통 코딩 스타일 및 코드 정합성 표준**을 정의합니다. 본 가이드라인은 코드의 일관성을 확보하여 가독성을 높이고 유지보수 비용을 낮추며 결함을 예방하는 데 목적이 있습니다.

---

## 1. 기본 Python 코딩 스타일 (General Python Standards)

모든 파이썬 소스 코드는 PEP 8 스타일 가이드를 기본으로 준수하며, 정적 컴파일 무결성을 최우선으로 합니다.

### 1) 명명 규칙 (Naming Conventions)
- **클래스 (Classes)**: 파스칼 케이스 (`PascalCase`)를 사용합니다. (예: `QueryFilter`, `SQLiteConnector`)
- **함수 및 변수 (Functions & Variables)**: 스네이크 케이스 (`snake_case`)를 사용합니다. (예: `get_processed_data()`, `defect_rate`)
- **상수 (Constants)**: 대문자 스네이크 케이스 (`UPPER_SNAKE_CASE`)를 사용합니다. (예: `DEFAULT_CACHE_TTL`, `MAX_LOCKOUT_STRIKES`)
- **모듈/파일 이름**: 스네이크 케이스를 준수하며, 역할별 명확한 접미사(`_page.py`, `_plots.py`, `_df.py`, `_query.py`)를 부착합니다.

### 2) 타입 힌팅 (Type Hinting)
- 함수 정의 시 모든 입력 파라미터와 반환 값(Return Type)에 대해 명시적인 **Type Hint**를 지정합니다.
  ```python
  import pandas as pd
  from core.params.parameters import DateFilterParams

  def calculate_yield_rate(df: pd.DataFrame, params: DateFilterParams) -> pd.DataFrame:
      # 로직 구현
      return df
  ```

### 3) Google 스타일 Docstring (한국어 필수)
- **모든 파일/모듈 상단 설명, 클래스 및 함수의 Docstring과 설명 주석은 영어 대신 반드시 한국어로 작성해야 합니다.**
- 모든 공용(Public) 함수 및 클래스에는 구체적인 역할, 파라미터 정보, 반환형 및 예외 처리를 명시한 Google 스타일 Docstring을 한국어로 의무 작성합니다.
  ```python
  def execute_sqlite_query(query: str, db_name: str = "log") -> pd.DataFrame:
      """SQLite 데이터베이스에 쿼리를 실행하여 결과를 DataFrame으로 반환합니다.

      Args:
          query (str): 실행할 SQL 쿼리 문자열.
          db_name (str, optional): 대상 DB 식별자 ('log' 또는 'ops'). Defaults to 'log'.

      Returns:
          pd.DataFrame: 조회 결과 데이터프레임 (실패 시 빈 데이터프레임 반환).

      Raises:
          ValueError: 허용되지 않는 db_name이 입력되었을 때 발생.
      """
  ```

---

## 2. 3-Layer 아키텍처 레이어별 표준 (3-Layer Coding Standards)

우리 시스템은 3-Layer 아키텍처를 엄격히 고수합니다. 각 레이어는 자신에게 부여된 역할만 전담해야 합니다.

```
  ┌────────────────────────────────────────────────────────┐
  │                        1. UI 레이어                    │
  │   - pages/*_page.py  : 입력 제어 및 레이아웃 (Streamlit) │
  │   - pages/*_plots.py : 순수 Plotly 차트 렌더링          │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │                     2. 서비스 레이어                    │
  │   - service/*_df.py  : 원시 데이터 전처리, 연산, 캐싱    │
  └───────────────────────────┬────────────────────────────┘
                              │
  ┌───────────────────────────▼────────────────────────────┐
  │                     3. 쿼리 레이어                      │
  │   - queries/*_query.py : 안전한 SQL 문자열 조립          │
  └────────────────────────────────────────────────────────┘
```

### 1) 쿼리 레이어 (`queries/*_query.py`)
- **String 조립 전용**: 쿼리 레이어 함수는 오직 SQL `str`을 리턴하는 빌더 역할만 수행하며, DB 커넥터를 임포트하거나 실행해서는 안 됩니다.
- **예약어 대문자화**: `SELECT`, `FROM`, `WHERE`, `JOIN` 등 모든 SQL 예약어는 **대문자**로 일관되게 작성합니다.
- **SQL Injection 방어**: 문자열 포맷팅(`f"..."`)을 통한 원시 변수 직접 대입을 배제하고, 반드시 `QueryFilter` 헬퍼 클래스를 경유하여 WHERE 조건을 동적 결합합니다.
- **테이블 경로 상수화**: 데이터베이스 테이블 경로는 하드코딩하지 않고 `core.query.query_database`의 `DatabricksTables` 상수를 참조합니다.

### 2) 서비스 레이어 (`service/*_df.py`)
- **단일 파라미터 데이터클래스**: 입력 필터 인자는 개별 변수로 쪼개 받지 않고, 반드시 `core/params/parameters.py`에 선언된 데이터클래스(`BaseFilterParams`, `DateFilterParams` 등) 단일 객체로 수령합니다.
- **Streamlit 캐싱 의무화**: DB 네트워크 조회 비용을 제어하기 위해 데이터프레임 수집기 함수 최상단에 반드시 `@st.cache_data(ttl=3600)` 캐시 장치를 부착합니다.
- **Pandas 방어적 코딩 (Defensive Pandas)**:
  - 날짜 컬럼은 명시적으로 `pd.to_datetime` 처리를 진행합니다.
  - 사칙연산(특히 백분율 비율 연산) 시 분모가 0이 되어 `inf` 혹은 `NaN` 오류가 나지 않도록 `np.where(denominator == 0, 0, numerator / denominator)`와 같은 안전장치를 부여합니다.
  - 조회 결과가 없거나 DB 오류 발생 시 크래시를 방지하기 위해 빈 데이터프레임(`pd.DataFrame()`)을 리턴하는 예외 처리를 반드시 수행합니다.

### 3) UI 및 시각화 레이어 (`pages/`)
- **화면(Page)과 차트(Plot)의 1:1 격리**:
  - `*_page.py`: Streamlit 컴포넌트, 사이드바 필터 바인딩, 멀티 탭, 그리드 데이터프레임 레이아웃 배치 전담.
  - `*_plots.py`: 오직 `plotly.graph_objects.Figure` 객체를 생성하고 디자인 스타일 토큰을 부여하는 렌더링 연산만 전담 (`st.*` 컴포넌트 호출 엄격 금지).

---

## 3. 프리미엄 시각화 & UI 스타일 가이드 (Visual Aesthetics)

사용자가 시스템을 마주할 때 최고의 고급감을 느끼도록(WOW Factor), 미적 완성도와 UI 세련미를 보존하기 위한 필수 장치들입니다.

### 1) 프리미엄 컬러 팔레트 준수 (Aesthetic Palette)
- 자극적이고 투박한 원색(순수 빨강 `#FF0000`, 파랑 `#0000FF`)의 사용을 금지합니다.
- 은은하고 깊이 있는 HSL 계열의 컬러 테마 및 Sleek Dark Mode를 기본 지원하도록 스타일링합니다.
- 면적 차트 및 분포도 렌더링 시 투명도(Opacity)가 들어간 그라데이션 채우기(`rgba(37, 99, 235, 0.08)`)를 사용해 눈의 피로를 최소화합니다.

### 2) 타이포그래피 및 레이아웃 마진 최적화
- 모든 차트의 `font_family` 설정에는 브라우저 디폴트 서체 대신 세련된 산세리프 글꼴인 `Inter, Roboto, sans-serif` 세트를 명시합니다.
- 모바일 및 대시보드 다단 격자 배치 시 차트 테두리가 찌그러지거나 잘리는 현상을 방지하도록 차트 마진을 타이트하게 조율합니다.
  ```python
  # 마진 및 배경 최적화 표준 템플릿 (선언형)
  layout = go.Layout(
      font_family="Inter, Roboto, sans-serif",
      margin=dict(l=15, r=15, t=40, b=15),
      paper_bgcolor=colors.transparent, # 중앙화된 투명 상수 활용 (대시보드 카드 밀착)
      plot_bgcolor=colors.transparent
  )
  ```

### 3) 맞춤형 호버 툴팁 (Interactive Tooltips)
- 기본 Plotly 호버 서식 대신, 정보 구조가 구조적으로 가시화될 수 있도록 `<br>`, `<b>` 등의 HTML 서식을 결합한 커스텀 호버 템플릿(`hovertemplate`)을 반드시 정의하여 뛰어난 사용성을 제공합니다.

---

## 4. 데이터베이스 및 세션 처리 보안 (Security & Session Standards)

안정적인 리소스 관리와 세션 제어를 위한 운영 표준입니다.

### 1) DB 클라이언트 안전 수명 주기
- 데이터베이스 클라이언트는 직접 커넥션을 열지 않고, 검증된 게이트웨이인 `core.operate.db_client.get_client()` 브릿지를 호출하여 사용합니다.
- 세션 누수 및 커넥션 오버플로우를 막기 위해 데이터 취득 완료 시 커넥션 리소스가 안정적으로 닫힐 수 있도록 프레임워크가 보증하는 실행 라이프사이클을 준수합니다.

### 2) UI 상태 영속성 (Session State Persistence)
- Streamlit의 고유 특성인 재실행(Re-run) 시 입력값 초기화 현상을 예방하기 위해, 사용자가 선택한 공장 코드, 자재 번호, 날짜 값 등 핵심 필터 변수는 무조건 `st.session_state` 객체에 바인딩하여 보존합니다.

### 3) 하드코딩 원천 차단 (No Hardcoded Secrets)
- 데이터베이스 비밀번호, API 토큰, 메일 서버 포트 등의 민감 자격 증명(Credential) 정보는 소스 코드 내에 문자열로 직접 기록하는 것을 절대 금지합니다.
- 반드시 루트 경로의 `.env` 파일에 환경변수를 기술하고, 소스 코드 내부에서는 `os.getenv` 또는 `dotenv` 모듈을 경유하여 동적으로 안전하게 읽어 들이도록 개발합니다.

## 5. 검증 가이드 (Harness Verification)

새롭게 코드를 추가했거나 수정을 진행한 이후에는, 시스템의 무결성을 기밀하게 자체 보증하기 위해 아래의 테스트 절차를 필수로 수행해야 합니다.

- **파이썬 정적 및 컴파일 검증**:
  - 로컬 커밋 및 푸시 전, 터미널에서 `make verify` 명령어를 구동하여 전체 파이썬 소스 코드의 AST 문법에 이상이 없는지 전수 스캔합니다.
  ```bash
  make verify
  ```
- **독립 격리 테스트**:
  - 기존 비즈니스 로직을 검증해야 하는 경우 실제 파일을 수정하여 print를 찍지 말고, `tests/` 폴더 아래 별도의 독립 테스트 파일(예: `tests/feature_logic_test.py`)을 개설하여 `PYTHONPATH`를 지정한 후 실행 검증을 완료합니다.

---

## 6. 구조적 코드 리전 및 섹션 표준 (Structural Code Region & Section Standards)

모든 파이썬 소스 파일은 코드 가독성을 극대화하고 IDE(예: VS Code, Cursor 등)에서의 폴딩(Folding) 및 구조 파악을 원활히 하기 위해 **리전(Region)과 섹션(Section) 주석 구조**를 기본 틀로 준수하여 논리 영역을 명확히 구분해야 합니다.

### 1) 기본 리전 및 섹션 틀 (Basic Framework)
모든 주요 논리적 단위는 다음 형식을 기본으로 감싸야 합니다. 구분선의 폭은 통일성 유지를 위해 45자(`─────────────────────────────────────────────`)로 고정합니다.

```python
# region Title
# Section: Title
# ─────────────────────────────────────────────
# endregion
```

필요시 세부 구조 파악과 가이드라인을 위해 다음 보조 주석 태그를 자유롭게 사용하십시오.
* **`# Subsection: Title`** : 섹션 내부의 하위 상세 기능을 분리할 때 사용합니다.
* **`# Note: Description`** : 비즈니스 공식, 예외 처리 사유, 혹은 중요한 개발 맥락을 기술할 때 사용합니다.

---

### 2) 3-Layer 및 레이어별 특화 프레임 규격 (Layer-Specific Code Frames)

우리의 3-Layer 레이어 아키텍처에 정의되는 모든 파이썬 파일은 아래의 고유 레이아웃 프레임에 맞춰 논리적 단계를 구분해야 합니다.

#### A. 쿼리 프레임 (`queries/*_query.py`)
쿼리 조립 및 SQL 스트링 생성 모듈은 CTE 및 풀 쿼리 구조를 한눈에 볼 수 있도록 주석 영역이 명확해야 합니다.

```python
"""
<도메인명> 쿼리 조립 모듈
"""
# region Imports
# Section: Imports
# ─────────────────────────────────────────────
import os
from core.query.query_helper import QueryFilter
# endregion

# region Helper Functions
# Section: Helper Functions
# ─────────────────────────────────────────────
# Note: 쿼리 바인딩 및 상수화에 쓰이는 소형 도우미 정의
# endregion

# region Core Queries
# Section: Core Queries
# ─────────────────────────────────────────────
def get_example_query(params) -> str:
    """공장 및 기간별 수율 분석을 위한 메인 SQL 스트링을 조립합니다."""
    # Subsection: CTE Definitions
    # Note: CTE 구문은 절대로 파이썬 함수로 쪼개지 않고 명시적으로 노출합니다.
    cte_sql = """
    WITH base_yield AS (
        SELECT ...
    )
    """
    
    # Subsection: Main Select Query
    main_sql = f"""
    {cte_sql}
    SELECT * FROM base_yield
    WHERE 1=1
    """
    return main_sql
# endregion
```

#### B. 서비스 프레임 (`service/*_df.py`)
원시 데이터를 취득하고 수치 분석 공식 및 비즈니스 전처리(Pandas Method Chaining)를 다루는 서비스 레이어의 표준 구조입니다.

```python
"""
<도메인명> 비즈니스 전처리 및 데이터 수집 서비스
"""
# region Imports
# Section: Imports
# ─────────────────────────────────────────────
import pandas as pd
import streamlit as st
from core.operate.db_client import get_client
from core.params.parameters import DateFilterParams
# endregion

# region Helper Functions
# Section: Helper Functions
# ─────────────────────────────────────────────
# Note: 순수 산술 통계 공식 및 보조 전처리 유틸리티 배치
# endregion

# region Core Service Logic
# Section: Core Service Logic
# ─────────────────────────────────────────────
@st.cache_data(ttl=3600)
def get_example_statistics_df(params: DateFilterParams) -> pd.DataFrame:
    """DB를 조회하고 비즈니스 공식을 적용하여 완결된 데이터프레임을 생성합니다."""
    # Subsection: Data Retrieval
    # Note: DB 클라이언트는 core.operate.db_client를 통해서만 안전히 취득합니다.
    try:
        client = get_client("databricks")
        ...
    except Exception as e:
        # Note: 서비스 레이어 오류 복구(Service Recovery) 장치 필수 동작
        return pd.DataFrame()
        
    # Subsection: Pandas Method Chaining
    # Note: setting-with-copy-warning 방지를 위해 가변 조작 대신 체이닝을 활용합니다.
    df_clean = (
        df.dropna(subset=["MCODE"])
          .assign(YIELD_RATE=lambda d: d["GOOD_QTY"] / d["PROD_QTY"])
    )
    return df_clean
# endregion
```

#### C. 페이지 프레임 (`pages/*_page.py`)
사용자 입력 위젯, 레이아웃 배치, 멀티 탭 및 사이드바 제어를 지휘하는 Streamlit UI 레이어의 기본 뼈대입니다.

```python
"""
<화면명> Streamlit 대시보드 화면
"""
# region Imports
# Section: Imports
# ─────────────────────────────────────────────
import streamlit as st
from core.ui.styles import mini_header_panel
from core.params.parameters import DateFilterParams
from service.example_df import get_example_statistics_df
from pages._10_dashboard.example_plots import draw_example_chart
# endregion

# region Page State & Setup
# Section: Page State & Setup
# ─────────────────────────────────────────────
# Note: 페이지 최초 진입 시 세션 상태 초기화 및 물리 페이지 레이아웃 세팅
st.set_page_config(layout="wide")
# endregion

# region UI Components
# Section: UI Components
# ─────────────────────────────────────────────

# Subsection: Sidebar Filter Panel
def render_filter_panel():
    """사이드바 필터 영역을 렌더링하고 파라미터를 조립합니다."""
    # Note: 사용자의 입력값은 st.session_state에 영속화하여 Re-run 초기화를 방어합니다.
    pass

# Subsection: Main Dashboard Tab Layout
def render_main_dashboard():
    """종합 대시보드 및 지표 그리드 메인 영역을 구축합니다."""
    tab1, tab2 = st.tabs(["종합 통계", "세부 동향"])
    
    with tab1:
        # Note: st_error_boundary를 적용해 수직 실행 마비를 완벽히 차단합니다.
        with st_error_boundary("수율 분석 그래프"):
            fig = draw_example_chart(df)
            st.plotly_chart(fig, use_container_width=True)
# endregion
```

#### D. 플롯 프레임 (`pages/*_plots.py`)
오직 순수 시각화 피규어(Figure) 생성 및 디자인 속성 주입에만 집중하며, `st.*` 호출이 엄격하게 금지되는 시각화 전용 레이아웃입니다.
또한, **`plotly.express as px` 임포트 및 사용을 엄격히 금지**합니다. 오직 `plotly.graph_objects as go`를 사용하여, trace와 layout을 각각 개별 독립 변수로 정의한 다음 `go.Figure(data=[trace], layout=layout)` 형태로 한 번에 조립하여 반환하는 **"선언형(Declarative) 조립 구조"**를 강제합니다.

```python
"""
<화면명> 대화형 Plotly 시각화 플롯 모듈
"""
# region Imports
# Section: Imports
# ─────────────────────────────────────────────
import plotly.graph_objects as go
import pandas as pd
from core.plot.viz_plotly_design import get_default_layout_config
from core.common_design_parameter import colors
from core.utils.error_boundary import error_safe_plot
# endregion

# region Plotting Helper Functions
# Section: Plotting Helper Functions
# ─────────────────────────────────────────────
# Note: 그라데이션 채우기 계산, hover text 조립 전용 보조 함수
# endregion

# region Figure Generation Core
# Section: Figure Generation Core
# ─────────────────────────────────────────────
@error_safe_plot("예시 트렌드 분석")
def draw_example_chart(df: pd.DataFrame) -> go.Figure:
    """완성형 대화형 수율 차트를 생성합니다."""
    # Note: 입구 방어(Defensive Guard)는 데코레이터에서 자동 지원하나, 필요시 조기 리턴 수행
    
    # Subsection: Trace Definition
    # Note: trace 변수를 명확히 정의합니다.
    trace = go.Scatter(
        x=df["DATE"], y=df["YIELD_RATE"],
        # Note: 사용자 경험 극대화(Hover-First)를 위해 가독성 높은 툴팁 구조 필수 조립
        hovertemplate="일자: %{x}<br>수율: <b>%{y:.2f}%</b><extra></extra>",
        line=dict(color=colors.BLUE_PRIMARY)
    )
    
    # Subsection: Layout Definition
    # Note: layout을 단독 go.Layout 객체로 정의합니다. (또는 딕셔너리로 조립 후 go.Layout으로 넘김)
    layout_config = get_default_layout_config("line")
    layout = go.Layout(**layout_config)
    
    # Subsection: Declarative Figure Assembly
    # Note: trace와 layout을 생성자에 주입하여 한 번에 Figure를 조립하고 반환합니다.
    return go.Figure(data=[trace], layout=layout)
# endregion
```
