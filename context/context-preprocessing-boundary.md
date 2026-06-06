# IQM+ 데이터 전처리 및 시각화 전처리 경계 정의 가이드라인
> **Data Preprocessing & Plot-Specific Preprocessing Boundary Specification**

이 명세서는 IQM+ 프로젝트 내에서 데이터가 가공되는 흐름을 투명하게 규격화하고, **비즈니스 로직 전처리(Service-Level Preprocessing)**와 **시각화 전처리(Plot-Level Preprocessing)** 간의 엄격한 경계(Boundary)를 설계하기 위한 아키텍처 가이드입니다. 

두 영역의 명확한 관심사 분리(Separation of Concerns)를 통해, 코드의 단위 테스트 용이성을 극대화하고 데이터 파이프라인의 유지보수 비용을 획기적으로 낮추는 것을 목적으로 합니다.

---

## 1. 전처리 파이프라인 아키텍처 (Data Flow Diagram)

IQM+ 프로젝트의 데이터 전처리는 데이터베이스 수집부터 최종 Streamlit UI 렌더링까지 총 3단계의 샌드박스로 격리되어 흐릅니다.

```mermaid
flowchart TD
    subgraph Layer1 ["1. 데이터 수집 & 쿼리 레이어 (queries/)"]
        RAW_DB[(Raw Databases)] -->|q_*.py| SQL_QUERY["SQL 쿼리 빌딩<br>(필터링/조인/기본 Agg)"]
    end

    subgraph Layer2 ["2. 서비스 전처리 레이어 (service/df_*.py)"]
        SQL_QUERY -->|DB Client 실행| RAW_DF["Raw pd.DataFrame"]
        RAW_DF -->|df_*.py| SVC_PROCESS["비즈니스 전처리<br>(통계 연산/비즈니스 룰/결측 정제)"]
        SVC_PROCESS -->|@st.cache_data| CACHED_DF["Clean pd.DataFrame<br>(순수 정형 데이터)"]
    end

    subgraph Layer3 ["3. 시각화 전처리 & 렌더링 레이어 (pages/*_plots.py)"]
        CACHED_DF -->|전달| PLOT_PRE["시각화 전용 전처리<br>(포맷팅/호버 조립/Top-N)"]
        PLOT_PRE -->|Trace/Layout 조립| FIG["go.Figure 렌더링"]
    end

    style Layer1 fill:#f3f4f6,stroke:#94a3b8,stroke-width:1px
    style Layer2 fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style Layer3 fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style CACHED_DF fill:#fef3c7,stroke:#f59e0b,stroke-width:2px
```

---

## 2. 영역별 역할 및 경계 표준 정의 (The Boundary Standard)

| 비교 항목 | ❶ 서비스 전처리 레이어 (`service/df_*.py`) | ❷ 시각화 전처리 레이어 (`pages/*_plots.py`) |
| :--- | :--- | :--- |
| **핵심 목적** | **비즈니스 정합성 확보 및 순수 통계 산출** | **인간 중심의 데이터 가독성 극대화** |
| **반환 데이터** | 순수한 정형 데이터프레임 (`pd.DataFrame`) | Plotly Figure (`go.Figure`) |
| **수행 주체** | 비즈니스 서비스 가공 함수 (예: `get_cqms_statistics_df`) | 플롯 드로잉 함수 (예: `draw_defect_trend_chart`) |
| **수정 빈도** | 비즈니스 정책 변경, 통계 공식 변경 시 수정 | 디자이너 요구사항, UI 레이아웃, 화면 해상도 튜닝 시 수정 |
| **단위 테스트**| **필수 대상** (인메모리 데이터 검증 완벽 가능) | 차트 구성 객체 검증 (상대적으로 비주얼 의존적) |

---

## 3. 핵심 판정 기준 및 실제 시나리오 5선

개발 도중 특정 전처리 코드를 어느 레이어에 배치할지 모호할 경우, 다음 **판정 기준(Decision Rule)**을 따릅니다.

> **[참고] 핵심 질문**: *"만약 차트 라이브러리를 Plotly에서 Matplotlib나 다른 UI 컴포넌트(예: AgGrid 테이블)로 전면 교체한다면 이 전처리 코드를 수정해야 하는가?"*
> * **Yes** -> **시각화 전처리 (Plot-Level)**
> * **No** -> **서비스 전처리 (Service-Level)**

---

### 시나리오별 상세 배치 가이드

#### Case A. 수치 단위 변환 및 반올림
* **서비스 레이어 (Service)**: 수치의 절대값 정밀도 유지를 위해 원시 Float 상태 그대로 유지하거나 통계 연산상 필요한 정밀도(예: `round(4)`)만 적용.
* **시각화 레이어 (Plot)**: 텍스트 가독성을 위해 축에 천단위 콤마(`,`)를 추가하거나, Y축 단위를 만원/억원/M$로 축소 변환하는 행위, 소수점 첫째 자리 표기(`format=".1f"`) 등은 **시각화 레이어**에서 수행.

#### Case B. 데이터 정렬 (Sorting)
* **서비스 레이어 (Service)**: 날짜순, 공장 코드순 등 비즈니스 논리에 부합하는 정렬 적용.
* **시각화 레이어 (Plot)**: "누적 바 차트에서 시각적 대비를 위해 내림차순 정렬", "상위 결함 항목순으로 시각적으로 정렬" 등 차트의 흐름을 지배하는 비주얼 정렬은 **시각화 레이어**에서 수행.

#### Case C. 결측치 (Null / NaN) 처리
* **서비스 레이어 (Service)**: 결측치가 있을 때 비즈니스 룰에 따라 "이전 값으로 채우기(FFill)", "평균값 대체", 또는 "비즈니스 오류 로깅 후 누락" 처리.
* **시각화 레이어 (Plot)**: 차트 선이 끊기지 않고 부드럽게 이어지도록 강제로 `0`으로 표시하기, 또는 범주형 축에서 누락된 날짜 슬롯에 더미 데이터를 임시로 주입하여 차트가 깨지지 않게 보장하는 행위.

#### Case D. 다중 컬럼 결합 및 텍스트 포합 (호버용)
* **서비스 레이어 (Service)**: `MCODE`와 `MNAME`을 개별 데이터 필드로 분리 유지.
* **시각화 레이어 (Plot)**: 마우스 호버 시 툴팁에 `"[자재코드] 자재명 (결함수)"` 형식으로 화려하게 표현하기 위해 컬럼을 합치는 가공 행위 (`df['hover_text'] = ...`).

#### Case E. 대용량 범주 필터링 (Top-N / Others 묶기)
* **서비스 레이어 (Service)**: 모든 범주의 전체 통계 테이블 데이터 유지.
* **시각화 레이어 (Plot)**: 차트에 50개의 범주를 모두 그리면 가독성이 떨어지므로, 상위 10개만 드로잉하고 나머지 40개는 즉석에서 `Others` 범주로 묶어 연산하는 행위.

---

## 4. 실제 코드 구현 예시 (Before vs After)

### Before (안티패턴: 시각화 함수 내부에서 복잡한 비즈니스 룰과 시각화 가공이 엉켜있음)
```python
# pages/_20_analysis/defect_plots.py
import pandas as pd
import plotly.graph_objects as go

def draw_defect_chart(df: pd.DataFrame):
    #  비즈니스 로직 전처리: 결함률 연산 공식을 시각화 함수 내에 직접 하드코딩
    df["defect_rate"] = (df["defect_qty"] / df["total_qty"]) * 100
    df["defect_rate"] = df["defect_rate"].fillna(0)
    
    #  비즈니스 룰 필터링: 특정 공정 코드 제외 필터가 시각화 안에 박혀있음
    df = df[df["process_code"] != "TEMP_99"]
    
    #  시각화 가공: 차트 툴팁을 위한 HTML 결합
    df["hover_text"] = df.apply(
        lambda r: f"공정: {r['process_name']}<br>결함률: {r['defect_rate']:.2f}%", axis=1
    )
    
    # Trace 조립
    trace = go.Scatter(
        x=df["date"],
        y=df["defect_rate"],
        text=df["hover_text"],
        hoverinfo="text"
    )
    return go.Figure(data=[trace])
```

---

### After (디자인 시스템 적용: 서비스 레이어와 시각화 레이어의 전처리 역할 분리)

#### ❶ 서비스 레이어 (`service/df_defect.py`)에서 순수 통계 및 비즈니스 룰 전처리 수행
```python
# service/df_defect.py
import pandas as pd
import streamlit as st

@st.cache_data(ttl=3600)
def get_clean_defect_data(params: BaseFilterParams) -> pd.DataFrame:
    # 1. DB 쿼리 실행 결과 취득
    df = execute_defect_query(params)
    
    # 2. 비즈니스 필터링 수행 (관심사 분리: 임시 공정 배제)
    df = df[df["process_code"] != "TEMP_99"]
    
    # 3. 비즈니스 통계 연산 및 결측 처리 공식 일괄 적용 (Single Source of Truth)
    df["defect_rate"] = (df["defect_qty"] / df["total_qty"]) * 100
    df["defect_rate"] = df["defect_rate"].fillna(0.0)
    
    # 4. 순수 통계 데이터프레임만 정형 상태로 캐싱 후 반환
    return df[["date", "process_name", "defect_qty", "defect_rate"]]
```

#### ❷ 시각화 레이어 (`pages/*_plots.py`)에서는 오직 비주얼 렌더링에 특화된 포맷팅만 수행
```python
# pages/_20_analysis/defect_plots.py
import pandas as pd
import plotly.graph_objects as go
from core.plot.viz_plotly_design import get_default_layout_config

def draw_defect_chart(df: pd.DataFrame) -> go.Figure:
    # 1. 차트 전용 전처리: 마우스 호버(Tooltip) 텍스트 데이터의 비주얼 조립
    df_plot = df.copy()
    df_plot["hover_text"] = df_plot.apply(
        lambda r: f"<b>공정</b>: {r['process_name']}<br><b>결함률</b>: {r['defect_rate']:.2f}%", 
        axis=1
    )
    
    # 2. Rule 1에 따른 정적 조립 (Trace 선언)
    trace = go.Scatter(
        x=df_plot["date"],
        y=df_plot["defect_rate"],
        text=df_plot["hover_text"],
        hovertemplate="%{text}<extra></extra>",
        marker=dict(color=colors.iqm_primary_500),
        mode="lines+markers"
    )
    
    # Y축 포맷팅 등의 시각화 전처리는 레이아웃 레벨에서 처리
    layout = get_default_layout_config(
        chart_type="scatter",
        title="공정별 결함율 추이",
        yaxis=dict(tickformat=".1f") # 소수점 첫째짜리 축 표기 지정
    )
    
    return go.Figure(data=[trace], layout=layout)
```

---

## 5. 전처리 구조 품질 검증 체크리스트 (Review Checklist)

코드 리뷰어 및 작업자는 소스 코드를 반영하기 전에 아래 4가지 항목을 필히 점검해야 합니다:

- [ ] **Q1. 서비스(`service/`) 모듈의 함수가 Pandas DataFrame 이외의 UI 라이브러리(Plotly, Streamlit 등) 종속적인 컴포넌트를 반환하고 있지 않은가?**
- [ ] **Q2. 시각화(`*_plots.py`) 함수 내에 특정 데이터 조건(예: `df[df['code'] != 'X']`)을 배제하는 하드코딩 필터가 존재하지 않는가?**
- [ ] **Q3. 차트 레이아웃의 축 포맷(Y-axis Tickformat)이나 호버 템플릿(Hover Template) 조립 기능이 서비스 레이어에서 연산되어 전달되고 있지는 않은가?**
- [ ] **Q4. 서비스 전처리 함수에 대해 Streamlit의 `@st.cache_data`가 올바르게 설정되어 비용이 큰 DB 쿼리를 무한 반복하지 않도록 보장하였는가?**
