# [개발 설계 및 변경 계획] HGWS 리턴 현황 및 생산기반 PPM 대시보드

이 문서는 **HGWS 특정 리턴코드 기반 생산 PPM 모니터링 대시보드** 추가 개발을 위해 신규 생성 및 수정할 모든 파일의 상세 설계와 소스코드를 명시하는 변경 계획서(Implementation Plan)입니다.

---

## 1. 개요 및 설계 방향
* **목적**: 3-레이어 아키텍처 규칙과 프로젝트 명명 규정, 이모지 금지 규칙을 엄수하여 화면 및 로직을 완전 격리 설계합니다.
* **설계 사상**: 
  * UI(`*_page.py`)는 레이아웃과 필터 컨트롤만 담당하며 DB를 직접 호출하지 않습니다.
  * 시각화(`*_plots.py`)는 오직 Plotly 객체(`go.Figure`)만을 생성/반환하며 Streamlit 코드를 내포하지 않습니다.
  * 서비스(`*_df.py`)는 Databricks SQL을 활용해 1차 전처리된 캐시 데이터프레임을 생성하고, Pandas를 통해 PPM 가공을 완료하여 UI에 전달합니다.

---

## 2. 파일 변경 및 생성 목록 (File Manifest)

### ① `app/core/params/parameters.py` (수정 제안)
신규 파라미터 클래스 `HgwsReturnPpmParams`를 추가합니다.

```python
# ======== [ HGWS Return PPM Params ] ========
@dataclass
class HgwsReturnPpmParams(BaseFilterParams, DateFilterParams):
    """HGWS 특정 리턴코드 분석 및 생산기반 PPM 계산용 파라미터 클래스"""
    m_codes: list[str] = field(default_factory=list)      # 자재코드 멀티 필터
    claim_codes: list[str] = field(default_factory=list)  # 리턴코드 멀티 필터
    plants: list[str] = field(default_factory=list)       # 공장코드 멀티 필터
    view_mode: Literal["monthly", "weekly"] = "monthly"   # 시계열 분석 단위
```

---

### ② `app/core/page/config_pages.py` (수정 제안)
대시보드 화면을 `Monitoring` 카테고리 메뉴에 라우팅 등록합니다.

```python
    "HGWS Return Monitor": {
        "filename": "app/pages/_30_monitoring/hgws_return_dashboard_page.py",
        "icon": ":material/analytics:",
        "category": "Monitoring",
        "roles": ["Viewer", "Contributor", "Admin"],
    },
```

---

### ③ `app/queries/hgws_return_query.py` (신규 생성)
순수 SQL 텍스트 조립을 담당하는 쿼리 모듈을 생성합니다.

```python
# -*- coding: utf-8 -*-
"""
queries/hgws_return_query.py - HGWS 리턴 및 생산 실적 SQL 생성 모듈
"""

from app.core.query.query_helper import SQLConverter
from app.core.params.parameters import HgwsReturnPpmParams

SQL_CONVERTER = SQLConverter()

def get_hgws_return_rawdata_query(params: HgwsReturnPpmParams) -> str:
    """Databricks에서 필터 조건에 부합하는 HGWS 리턴 원시 데이터를 조회하는 SQL을 생성합니다."""
    
    # 동적 필터 조립
    m_code_filter = ""
    if params.m_codes:
        m_code_sql = SQL_CONVERTER.list_to_sql_in(params.m_codes)
        m_code_filter = f"AND MATNR IN ({m_code_sql})"
        
    claim_filter = ""
    if params.claim_codes:
        claim_sql = SQL_CONVERTER.list_to_sql_in(params.claim_codes)
        claim_filter = f"AND ZREASON IN ({claim_sql})"
        
    plant_filter = ""
    if params.plants:
        plant_sql = SQL_CONVERTER.list_to_sql_in(params.plants)
        # sap_zsrt10000 테이블 내 공장코드 컬럼(WERKS) 적용
        plant_filter = f"AND WERKS IN ({plant_sql})"
        
    date_filter = ""
    if params.start_date and params.end_date:
        date_filter = f"AND AUDAT BETWEEN '{params.start_date}' AND '{params.end_date}'"

    return f"""--sql
    SELECT
        WERKS AS PLANT,
        MATNR AS M_CODE,
        AUDAT AS RETURN_DATE,
        1 AS RETURN_QTY,       -- 바코드 레코드 1본당 수량 1개 매핑
        ZREASON AS CLAIM_CD,
        BELNR AS VIN,
        ZBARCODE AS BARCD_NO
    FROM hkt_system_dw.tableau.sap_zsrt10000
    WHERE 1=1
      AND ZRULT NOT IN ('R') -- Reject 제외
      {m_code_filter}
      {claim_filter}
      {plant_filter}
      {date_filter}
    """

def get_production_volume_rawdata_query(params: HgwsReturnPpmParams) -> str:
    """Databricks에서 필터 조건에 부합하는 실 생산량 실적 데이터를 조회하는 SQL을 생성합니다."""
    
    m_code_filter = ""
    if params.m_codes:
        m_code_sql = SQL_CONVERTER.list_to_sql_in(params.m_codes)
        m_code_filter = f"AND M_CODE IN ({m_code_sql})"
        
    plant_filter = ""
    if params.plants:
        plant_sql = SQL_CONVERTER.list_to_sql_in(params.plants)
        plant_filter = f"AND PLANT IN ({plant_sql})"
        
    date_filter = ""
    if params.start_date and params.end_date:
        # 생산실적 날짜 형식 보정 (YYYY-MM-DD)
        date_filter = f"AND WORK_DATE BETWEEN '{params.start_date}' AND '{params.end_date}'"

    return f"""--sql
    SELECT
        PLANT,
        M_CODE,
        WORK_DATE,
        PRDT_QTY
    FROM hkt_dw.production.wrk_f_lwrkts118
    WHERE 1=1
      {m_code_filter}
      {plant_filter}
      {date_filter}
    """
```

---

### ④ `app/service/hgws_return_df.py` (신규 생성)
데이터 수집, Pandas를 이용한 PPM 계산 및 캐싱 처리를 전담합니다.

```python
# -*- coding: utf-8 -*-
"""
service/hgws_return_df.py - HGWS 특정 리턴 분석 및 PPM 전처리 서비스 모듈
"""

import pandas as pd
import streamlit as st
from app.core.db.client import get_client
from app.core.params.parameters import HgwsReturnPpmParams
from app.queries import hgws_return_query

dbx_client = get_client("databricks")

@st.cache_data(ttl=1800)
def preprocessing_hgws_return_rawdata(params: HgwsReturnPpmParams) -> pd.DataFrame:
    """Databricks HGWS 테이블로부터 원시 리턴 데이터를 가져와 1차 정제 및 타입 변환을 수행하고 캐싱합니다."""
    query = hgws_return_query.get_hgws_return_rawdata_query(params)
    df = dbx_client.execute(query)
    
    if df is None or df.empty:
        return pd.DataFrame(columns=["PLANT", "M_CODE", "RETURN_DATE", "RETURN_QTY", "CLAIM_CD", "VIN", "BARCD_NO"])
        
    df.columns = df.columns.str.upper()
    df["RETURN_DATE"] = pd.to_datetime(df["RETURN_DATE"], errors="coerce")
    df["RETURN_QTY"] = pd.to_numeric(df["RETURN_QTY"], errors="coerce").fillna(0).astype(int)
    return df

@st.cache_data(ttl=1800)
def preprocessing_production_volume_rawdata(params: HgwsReturnPpmParams) -> pd.DataFrame:
    """Databricks 생산 테이블로부터 원시 생산량 데이터를 가져와 1차 정제를 거치고 캐싱합니다."""
    query = hgws_return_query.get_production_volume_rawdata_query(params)
    df = dbx_client.execute(query)
    
    if df is None or df.empty:
        return pd.DataFrame(columns=["PLANT", "M_CODE", "WORK_DATE", "PRDT_QTY"])
        
    df.columns = df.columns.str.upper()
    df["WORK_DATE"] = pd.to_datetime(df["WORK_DATE"], errors="coerce")
    df["PRDT_QTY"] = pd.to_numeric(df["PRDT_QTY"], errors="coerce").fillna(0).astype(float)
    return df

def transform_hgws_ppm_trend_df(params: HgwsReturnPpmParams) -> pd.DataFrame:
    """리턴 데이터와 생산량 데이터를 결합하여 기간별/공장별/자재별 종합 PPM 가공 데이터프레임을 생성합니다."""
    df_return = preprocessing_hgws_return_rawdata(params)
    df_prod = preprocessing_production_volume_rawdata(params)
    
    if df_return.empty or df_prod.empty:
        return pd.DataFrame(columns=["PERIOD", "PLANT", "M_CODE", "RETURN_QTY", "PRDT_QTY", "PPM"])
        
    # 시간 단위 그룹 지정을 위한 컬럼 생성 (월별 / 주간별)
    if params.view_mode == "weekly":
        df_return["PERIOD"] = df_return["RETURN_DATE"].dt.to_period("W").astype(str)
        df_prod["PERIOD"] = df_prod["WORK_DATE"].dt.to_period("W").astype(str)
    else:
        df_return["PERIOD"] = df_return["RETURN_DATE"].dt.to_period("M").astype(str)
        df_prod["PERIOD"] = df_prod["WORK_DATE"].dt.to_period("M").astype(str)
        
    # 1. 리턴 집계
    df_rtn_agg = (
        df_return.groupby(["PERIOD", "PLANT", "M_CODE"], as_index=False)["RETURN_QTY"]
        .sum()
    )
    
    # 2. 생산량 집계
    df_prod_agg = (
        df_prod.groupby(["PERIOD", "PLANT", "M_CODE"], as_index=False)["PRDT_QTY"]
        .sum()
    )
    
    # 3. Outer Join 병합
    merged_df = pd.merge(
        df_rtn_agg, 
        df_prod_agg, 
        on=["PERIOD", "PLANT", "M_CODE"], 
        how="outer"
    ).fillna(0)
    
    # 4. PPM 지표 산출
    merged_df["PPM"] = merged_df.apply(
        lambda row: (row["RETURN_QTY"] / row["PRDT_QTY"] * 1000000) if row["PRDT_QTY"] > 0 else 0.0,
        axis=1
    )
    
    return merged_df.sort_values(by="PERIOD")
```

---

### ⑤ `app/pages/_30_monitoring/hgws_return_dashboard_plots.py` (신규 생성)
Plotly 차트 생성을 담당하는 시각화 모듈을 생성합니다.

```python
# -*- coding: utf-8 -*-
"""
pages/_30_monitoring/hgws_return_dashboard_plots.py - 시각화 렌더링 모듈
"""

import pandas as pd
import plotly.graph_objects as go
from app.core.common_design_parameter import viz_plotly_design as design

# 테마 컬러 연동
COLOR_PRIMARY = design.colors.orange_500
COLOR_SECONDARY = design.colors.gray_500
COLOR_LIGHT = design.colors.light_gray

def draw_hgws_ppm_trend_chart(df: pd.DataFrame) -> go.Figure:
    """월간/주차별 리턴수량(Bar) 및 PPM 추이(Line) 이중 축 하이브리드 트렌드 차트를 생성합니다."""
    fig = go.Figure()
    
    if df.empty:
        return fig
        
    # 기간별 단순 1차원 집계
    agg = df.groupby("PERIOD", as_index=False).agg({"RETURN_QTY": "sum", "PRDT_QTY": "sum"})
    agg["PPM"] = agg.apply(
        lambda r: (r["RETURN_QTY"] / r["PRDT_QTY"] * 1000000) if r["PRDT_QTY"] > 0 else 0,
        axis=1
    )
    
    # 1. 리턴수량 막대 그래프 (Y1)
    fig.add_trace(go.Bar(
        x=agg["PERIOD"],
        y=agg["RETURN_QTY"],
        name="Return Qty",
        marker_color=COLOR_LIGHT,
        yaxis="y1",
        hovertemplate="<b>기간</b>: %{x}<br><b>리턴수량</b>: %{y:,.0f} ea<extra></extra>"
    ))
    
    # 2. PPM 결함률 선 그래프 (Y2)
    fig.add_trace(go.Scatter(
        x=agg["PERIOD"],
        y=agg["PPM"],
        name="PPM",
        mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=3),
        marker=dict(size=8),
        yaxis="y2",
        hovertemplate="<b>기간</b>: %{x}<br><b>결함률</b>: %{y:,.1f} PPM<extra></extra>"
    ))
    
    fig.update_layout(
        height=350,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Return Qty (ea)", showgrid=True),
        yaxis2=dict(title="PPM", overlaying="y", side="right", showgrid=False),
        xaxis=dict(type="category")
    )
    return fig

def draw_plant_ppm_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """공장별 리턴 수량 및 PPM을 분석하는 이중 축 차트를 생성합니다."""
    fig = go.Figure()
    
    if df.empty:
        return fig
        
    agg = df.groupby("PLANT", as_index=False).agg({"RETURN_QTY": "sum", "PRDT_QTY": "sum"})
    agg["PPM"] = agg.apply(
        lambda r: (r["RETURN_QTY"] / r["PRDT_QTY"] * 1000000) if r["PRDT_QTY"] > 0 else 0,
        axis=1
    ).sort_values(by="PPM", ascending=False)
    
    # 공장별 리턴 막대 (Y1)
    fig.add_trace(go.Bar(
        x=agg["PLANT"],
        y=agg["RETURN_QTY"],
        name="Return Qty",
        marker_color=COLOR_SECONDARY,
        yaxis="y1",
        hovertemplate="<b>공장</b>: %{x}<br><b>리턴수량</b>: %{y:,.0f} ea<extra></extra>"
    ))
    
    # 공장별 PPM 선 (Y2)
    fig.add_trace(go.Scatter(
        x=agg["PLANT"],
        y=agg["PPM"],
        name="PPM",
        mode="lines+markers",
        line=dict(color=COLOR_PRIMARY, width=2, dash="dash"),
        marker=dict(size=7),
        yaxis="y2",
        hovertemplate="<b>공장</b>: %{x}<br><b>PPM</b>: %{y:,.1f} PPM<extra></extra>"
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=40, r=40, t=30, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(title="Return Qty (ea)", showgrid=True),
        yaxis2=dict(title="PPM", overlaying="y", side="right", showgrid=False),
        xaxis=dict(type="category")
    )
    return fig

def draw_mcode_ppm_comparison_chart(df: pd.DataFrame) -> go.Figure:
    """자재코드별 PPM 비교 분석용 수평 막대 차트를 생성합니다. Top-N 자르기 및 Others 처리를 수행합니다."""
    fig = go.Figure()
    
    if df.empty:
        return fig
        
    agg = df.groupby("M_CODE", as_index=False).agg({"RETURN_QTY": "sum", "PRDT_QTY": "sum"})
    agg["PPM"] = agg.apply(
        lambda r: (r["RETURN_QTY"] / r["PRDT_QTY"] * 1000000) if r["PRDT_QTY"] > 0 else 0,
        axis=1
    ).sort_values(by="PPM", ascending=True) # 수평 차트이므로 하단에서 위로 정렬되도록 오름차순
    
    # 가드로직: 자재코드가 10개 초과 시 상위 9개 외 Others 처리
    if len(agg) > 10:
        top_9 = agg.iloc[-9:]
        others = agg.iloc[:-9]
        others_row = pd.DataFrame([{
            "M_CODE": "Others",
            "RETURN_QTY": others["RETURN_QTY"].sum(),
            "PRDT_QTY": others["PRDT_QTY"].sum(),
            "PPM": (others["RETURN_QTY"].sum() / others["PRDT_QTY"].sum() * 1000000) if others["PRDT_QTY"].sum() > 0 else 0
        }])
        agg = pd.concat([others_row, top_9])
        
    fig.add_trace(go.Bar(
        y=agg["M_CODE"],
        x=agg["PPM"],
        orientation="h",
        marker_color=COLOR_PRIMARY,
        hovertemplate="<b>자재코드</b>: %{y}<br><b>PPM</b>: %{x:,.1f} PPM<extra></extra>"
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=50, r=30, t=30, b=30),
        xaxis=dict(title="PPM", showgrid=True),
        yaxis=dict(type="category")
    )
    return fig

def draw_claim_code_donut_chart(df: pd.DataFrame) -> go.Figure:
    """리턴 사유(Claim Code)별 비중을 보여주는 프리미엄 도넛 차트를 생성합니다."""
    fig = go.Figure()
    
    # Claim Code는 원시 HGWS 데이터(df_return)에 직접 존재하므로
    # 서비스로부터 전달된 가공전 데이터프레임 혹은 추가 필드 연동이 유용합니다.
    # 여기서는 안전하게 예시 가이드 제공
    if df.empty or "CLAIM_CD" not in df.columns:
        return fig
        
    claim_agg = df.groupby("CLAIM_CD", as_index=False)["RETURN_QTY"].sum().sort_values(by="RETURN_QTY", ascending=False)
    
    fig.add_trace(go.Pie(
        labels=claim_agg["CLAIM_CD"],
        values=claim_agg["RETURN_QTY"],
        hole=0.4,
        textinfo="percent+label",
        hovertemplate="<b>코드</b>: %{label}<br><b>수량</b>: %{value:,.0f} ea<br><b>비율</b>: %{percent}<extra></extra>"
    ))
    
    fig.update_layout(
        height=300,
        margin=dict(l=30, r=30, t=30, b=30),
    )
    return fig
```

---

### ⑥ `app/pages/_30_monitoring/hgws_return_dashboard_page.py` (신규 생성)
Streamlit 레이아웃과 컨트롤러 로직을 전담 구현합니다.

```python
# -*- coding: utf-8 -*-
"""
pages/_30_monitoring/hgws_return_dashboard_page.py - HGWS 리턴 및 PPM 모니터링 화면
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from app.core.params.parameters import HgwsReturnPpmParams
from app.service import hgws_return_df
from app.pages._30_monitoring import hgws_return_dashboard_plots as plots
from app.core.ui.components import mini_header

# 1. 페이지 레이아웃 선언 및 디자인 적용 (이모지 전면 사용 금지)
st.title("HGWS Return Monitor")
mini_header("HGWS 특정 리턴코드 추적 및 생산 기반 PPM 정밀 모니터링 시스템", icon=":material/analytics:")

# 2. 사이드바 검색 필터 구성
st.sidebar.subheader("필터 검색 설정", icon=":material/filter_alt:")

# 조회기간
today = datetime.today()
one_year_ago = today - timedelta(days=365)
date_range = st.sidebar.date_input(
    "조회 기간 설정",
    value=(one_year_ago, today),
    max_value=today,
    icon=":material/calendar_today:"
)

start_dt = date_range[0].strftime("%Y-%m-%d") if len(date_range) >= 1 else None
end_dt = date_range[1].strftime("%Y-%m-%d") if len(date_range) == 2 else None

# 임시 분석 대상 기본값 연동 및 멀티셀렉트
plants_list = st.sidebar.multiselect("공장 선택", options=["KP", "KA", "KT"], default=["KP"], icon=":material/factory:")
claim_list = st.sidebar.multiselect("Claim 리턴코드", options=["P5SP", "W1SA", "W2SB"], default=["P5SP"], icon=":material/rule:")
mcode_list = st.sidebar.multiselect("자재코드 (선택)", options=["1032967", "1032966", "1032965"], default=[], icon=":material/view_in_ar:")

view_unit = st.sidebar.selectbox("시계열 분석 단위", options=["monthly", "weekly"], index=0, icon=":material/schedule:")

# 3. 파라미터 조립 (parameters.py 데이터클래스 통합 수칙 준수)
params = HgwsReturnPpmParams(
    plant_list=plants_list,
    mcode_list=mcode_list,
    start_date=start_dt,
    end_date=end_dt,
    m_codes=mcode_list,
    claim_codes=claim_list,
    plants=plants_list,
    view_mode=view_unit
)

# 4. 데이터 취득 및 병합
with st.spinner("데이터 로드 및 PPM 지표 연산 중..."):
    merged_df = hgws_return_df.transform_hgws_ppm_trend_df(params)
    raw_return_df = hgws_return_df.preprocessing_hgws_return_rawdata(params)

# 5. 화면 메인 레이아웃 탭 구성 (Material 아이콘 적용)
tab_dash, tab_det = st.tabs([
    "PPM 모니터링 대쉬보드", 
    "상세 이력 목록"
], icons=[":material/dashboard:", ":material/list_alt:"])

# ---- [ TAB 1: 대쉬보드 ] ----
with tab_dash:
    if merged_df.empty:
        st.warning("선택하신 조건에 부합하는 데이터가 존재하지 않습니다. 필터 설정을 확인하십시오.", icon=":material/warning:")
    else:
        # 1행: KPI 요약 지표 카드
        tot_rtn = merged_df["RETURN_QTY"].sum()
        tot_prd = merged_df["PRDT_QTY"].sum()
        overall_ppm = (tot_rtn / tot_prd * 1000000) if tot_prd > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("총 리턴 수량", f"{tot_rtn:,.0f} ea", delta=None, help="선택 기간 동안 발생한 불량 리턴 건수")
        col2.metric("총 생산 수량", f"{tot_prd:,.0f} ea", delta=None, help="선택 자재/공장의 실 총 생산량")
        col3.metric("종합 PPM 지표", f"{overall_ppm:,.1f} PPM", delta=None, help="백만본당 결함률")
        col4.metric("분석 대상 리턴코드 수", f"{len(claim_list)} 건", delta=None)
        
        st.markdown("---")
        
        # 2행: PPM 및 리턴 수량 시계열 트렌드
        st.subheader("리턴 추이 및 PPM 시계열 트렌드 분석", icon=":material/trending_up:")
        fig_trend = plots.draw_hgws_ppm_trend_chart(merged_df)
        st.plotly_chart(fig_trend, use_container_width=True, key="hgws_return_trend_chart")
        
        st.markdown("---")
        
        # 3행: 1행 2열 배치 (공장별 및 자재별 비교)
        col_left, col_right = st.columns(2)
        with col_left:
            st.subheader("공장별 품질 리턴 및 PPM 비교", icon=":material/factory:")
            fig_plant = plots.draw_plant_ppm_comparison_chart(merged_df)
            st.plotly_chart(fig_plant, use_container_width=True, key="hgws_plant_comparison_chart")
            
        with col_right:
            st.subheader("자재코드별 PPM 상위 분포", icon=":material/grid_view:")
            fig_mcode = plots.draw_mcode_ppm_comparison_chart(merged_df)
            st.plotly_chart(fig_mcode, use_container_width=True, key="hgws_mcode_comparison_chart")
            
        # 4행: 원인 분석
        st.subheader("원인 코드별 발생 비중 분석", icon=":material/pie_chart:")
        fig_donut = plots.draw_claim_code_donut_chart(raw_return_df)
        st.plotly_chart(fig_donut, use_container_width=True, key="hgws_claim_donut_chart")

# ---- [ TAB 2: 상세 이력 조회 ] ----
with tab_det:
    if merged_df.empty:
        st.warning("조회 데이터가 존재하지 않습니다.", icon=":material/warning:")
    else:
        st.subheader("HGWS 리턴 & 생산 실적 정밀 매핑 집계 데이터", icon=":material/table_rows:")
        
        # 테이블 컬럼 뷰 개선 및 다운로드
        st.dataframe(
            merged_df,
            column_config={
                "PERIOD": st.column_config.TextColumn("분석 기간", width="medium"),
                "PLANT": st.column_config.TextColumn("공장", width="small"),
                "M_CODE": st.column_config.TextColumn("자재코드", width="medium"),
                "RETURN_QTY": st.column_config.NumberColumn("리턴 수량 (ea)", format="%d ea"),
                "PRDT_QTY": st.column_config.NumberColumn("생산 수량 (ea)", format="%d ea"),
                "PPM": st.column_config.NumberColumn("계산된 PPM 결함률", format="%.1f PPM")
            },
            use_container_width=True,
            hide_index=True
        )
        
        csv_data = merged_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Excel(CSV) 데이터 다운로드",
            data=csv_data,
            file_name="hgws_return_ppm_details.csv",
            mime="text/csv",
            icon=":material/download:"
        )
```

---

## 3. 검증 및 수동 테스트 방안 (Testing Plan)
1. **단위 및 통합 검증 (`tests/hgws_return_test.py`)**
   * 기존 시스템에 부하를 전혀 유발하지 않는 블랙박스 테스트용 스크립트를 독립적으로 생성합니다.
   * `HgwsReturnPpmParams` 생성 및 `hgws_return_df.transform_hgws_ppm_trend_df()` 연산 무결성을 쉘에서 즉시 검증합니다.
2. **명시적 승인 하에 코드 적용**
   * 본 계획서에 대한 사용자의 승인 텍스트가 확인된 후, 순차적으로 파일을 작성 및 수정하도록 안전 통제를 수호합니다.
