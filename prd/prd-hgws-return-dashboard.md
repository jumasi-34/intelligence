# [PRD] HGWS 리턴 현황 및 생산기반 PPM 대시보드 개발 명세서 (Draft)

> **[필독] AI 에이전트 수호 수칙**: 본 작업은 [L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)에 정의된 3-레이어 아키텍처 규칙과 프로젝트 명명 표준을 엄격히 따릅니다. 임의로 기존 프로덕션 코드를 수정해서는 안 되며, 신규 개발 파일 배치는 지정된 경로에 한정해야 합니다. UI 페이지 내 모든 이모지 사용은 금지되며, 대신 Google Material Symbols (`:material/icon_name:`) 가이드라인을 준수합니다.

---

## 1. 제품 요구사항 및 배경 (Objective & Scope)
* **목적 (Why)**: 
  * 내수 실시간 리턴 시스템(HGWS)의 특정 품질 리턴코드(Claim Code) 데이터를 추적하고, 이에 대응하는 생산 실적(Production Volume) 데이터를 동일 분모로 매핑하여 **생산기반 PPM(Parts Per Million) 결함 지표**를 실시간 산출합니다.
  * 기간별, 공장별, 자재코드(M_CODE)별 품질 결함 트렌드를 다각도로 시각화하여 대량 품질 이슈의 전조 증상을 조기에 감지하고 선제적 예방 품질 활동을 지원합니다.
* **범위 (Scope)**:
  * **특정 리턴코드 기반 분석**: 전체 리턴 중 분석 대상 리턴코드(예: `P5SP` 등 특정 불량 사유)를 필터링하여 선별 분석하는 기능.
  * **생산 실적 동적 연계**: 동일 기간, 동일 자재코드(`M_CODE`)의 실 생산량(`PRDT_QTY`) 정보를 분모로 결합.
  * **생산기반 PPM 산출 및 게시**: 
    $$\text{PPM} = \left( \frac{\text{HGWS 리턴 수량}}{\text{실 생산 수량}} \right) \times 1,000,000$$
  * **핵심 시각화 및 테이블**:
    * 핵심 품질 지표 카드 (총 리턴량, 총 생산량, 종합 PPM 지표 및 전월 대비 증감율).
    * 리턴 추이 및 PPM 트렌드 시계열 분석 차트 (이중 축 적용).
    * **공장별 리턴 및 PPM 비교 차트** (공장별 품질 편차 가시화).
    * 자재코드(`M_CODE`)별 PPM 분포 비교 및 리턴사유별 도넛 차트.
    * 리턴 데이터와 생산 실적이 매핑된 상세 집계 그리드 테이블 및 Excel 내보내기 지원.

---

## 2. 타겟 디렉터리 및 대상 파일 (Target Layers & Files)

본 화면 및 기능 개발은 아래 3-레이어 아키텍처 구조를 엄격히 준수하여 독립적으로 배치되어야 합니다.

| 레이어 (Layer) | 대상 파일 경로 (File Path) | 역할 및 구현 내용 (Role) |
| :--- | :--- | :--- |
| **UI 레이어** | `app/pages/_30_monitoring/hgws_return_dashboard_page.py` | 화면 레이아웃 및 탭 구성, 사이드바 필터 바인딩 및 렌더링 제어 |
| **시각화 레이어** | `app/pages/_30_monitoring/hgws_return_dashboard_plots.py` | Plotly 시각화 드로잉 전담 함수 선언 (Streamlit 컴포넌트 호출 격리) |
| **서비스 레이어** | `app/service/hgws_return_df.py` | HGWS 데이터 및 생산 실적 데이터 취득, 결합, PPM 연산 및 캐싱 (`@st.cache_data`) |
| **쿼리 레이어** | `app/queries/hgws_return_query.py` | HGWS 리턴 테이블 및 생산 실적 테이블 조회 SQL 문자열 조립 전담 |
| **파라미터 정의** | `app/core/params/parameters.py` | 신규 파라미터 데이터클래스 `HgwsReturnPpmParams` 정의 및 추가 |

---

## 3. 데이터 흐름 및 데이터클래스 스펙 (Data Flow & Parameters)

```mermaid
flowchart LR
    Page["app/pages/..._page.py<br>(UI / Layout Control)"]
    Plots["app/pages/..._plots.py<br>(Plotly Drawings)"]
    Service["app/service/hgws_return_df.py<br>(Pandas Merge & PPM Calculation)"]
    Query["app/queries/hgws_return_query.py<br>(Pure SQL Assembly)"]
    DB["Databricks SQL<br>(Database Execution)"]

    Page -->|1. Call with params| Service
    Service -->|2. Build SQL with params| Query
    Service -->|3. Query & Cache| DB
    Service -->|4. Return Merged pd.DataFrame| Page
    Page -->|5. Pass DataFrames| Plots
    Plots -->|6. Return go.Figure| Page
    Page -->|7. Render st.plotly_chart| Page

    %% 격리 규칙 표시
    Page -.x|[금지] DIRECT DB ACCESS BLOCK| DB
    Service -.x|[금지] NO STREAMLIT/PLOTLY IMPORT| Page
```

### ① 파라미터 정의 (`app/core/params/parameters.py`)
기존 공통 데이터클래스를 계승하되, 본 화면 분석에 특화된 신규 파라미터 데이터클래스를 추가 선언합니다.
```python
@dataclass
class HgwsReturnPpmParams(BaseFilterParams, DateFilterParams):
    """HGWS 리턴현황 및 PPM 계산을 위한 필터 파라미터 데이터클래스"""
    m_codes: list[str] = field(default_factory=list)      # 자재코드 필터 (Multi)
    claim_codes: list[str] = field(default_factory=list)  # 리턴사유코드 필터 (Multi)
    plants: list[str] = field(default_factory=list)       # 공장코드 필터 (Multi)
```

### ② 서비스 레이어 인터페이스 명세 (`app/service/hgws_return_df.py`)
* **`preprocessing_hgws_return_rawdata(params: HgwsReturnPpmParams) -> pd.DataFrame`**:
  * Databricks `hgws` 테이블 (`hkt_system_dw.tableau.sap_zsrt10000`) 쿼리 수행 후 타입 및 결측치 보정 (1차 전처리).
  * 쿼리 성능 보존을 위해 `@st.cache_data(ttl=1800)` 캐싱 지정.
* **`preprocessing_production_volume_rawdata(params: HgwsReturnPpmParams) -> pd.DataFrame`**:
  * Databricks `production_volume` 테이블 (`hkt_dw.production.wrk_f_lwrkts118`) 쿼리 수행 후 1차 전처리 및 캐싱 적용.
* **`transform_hgws_ppm_trend_df(params: HgwsReturnPpmParams) -> pd.DataFrame`**:
  * 전처리된 HGWS 리턴 데이터와 생산량 데이터를 자재코드(`M_CODE`), 공장(`PLANT`), 기간(연월 또는 주) 기준으로 병합.
  * 병합된 데이터셋 기반으로 기간별 PPM 지표 계산 연산 수행.

---

## 4. 사용자 화면 및 레이아웃 스펙 (UI / UX Layout)

### ① 사이드바 입력 필터 (Sidebar Filters)
* **조회 기간 (Date Range)**: `st.date_input` 활용, 최근 1년이 기본값으로 지정됨.
* **공장 선택 (Plant Multi-Select)**: `st.multiselect` 활용, `PLANT` 목록 연동.
* **자재코드 (Material Code Multi-Select)**: 자재코드 리스트 검색/선택 지원.
* **리턴코드 선택 (Claim Code Multi-Select)**: 특정 리턴코드(예: `P5SP` 등) 멀티 선택 지원.

### ② 메인 레이아웃 및 탭 구성 (Tab Structure)

#### Tab 1: Dashboard (PPM 모니터링 대시보드)
1. **PPM KPI Summary Cards (1행 4열 메트릭 카드)**
   * `총 리턴 수량 (Return Qty)`: 선택 기간 내 총 결함 리턴 개수
   * `총 생산 수량 (Production Qty)`: 선택 기간 내 매핑 자재 총 생산 수량
   * `종합 PPM 지표 (Overall PPM)`: (총 리턴 / 총 생산) * 1,000,000
   * `전월 대비 증감율 (PPM Delta)`: 전월 대비 PPM 증감율 정보 및 인디케이터 시각화
2. **Return Qty & PPM 시계열 트렌드 (1행 1열 대형 차트)**
   * `[차트 1]` 월간/주간별 리턴 수량(막대)과 PPM 지표(꺾은선)를 한눈에 볼 수 있는 이중 축 하이브리드 트렌드 차트.
3. **공장 및 자재별 품질 비교 (1행 2열 레이아웃)**
   * `[차트 2 (좌)]` **공장(`PLANT`)별 리턴 수량 및 PPM 비교 분석 차트** (공장 간 품질 산포 가시화)
   * `[차트 3 (우)]` 자재코드(`M_CODE`)별 PPM 비교 차트 (PPM이 높은 순서대로 Top-N 정렬, 그 외는 `Others` 그룹화 가드 지원)
4. **원인 코드 비중 분석 (1행 1열 배치)**
   * `[차트 4]` 발생한 Claim Code별 리턴수량 비중 분석 도넛 차트

#### Tab 2: Details (상세 이력 조회)
1. **HGWS-생산 매핑 상세 데이터프레임**
   * 자재코드별, 공장별, 주차별(또는 일별)로 리턴 수량과 생산 수량이 조인되어 PPM이 행단위로 계산된 정밀 집계 그리드 테이블.
   * `st.dataframe`을 활용하여 정렬/필터링을 제공하며, `st.download_button`을 통한 Excel 다운로드 기능 기본 탑재.

---

## 5. 시각화 개별 스펙 (Chart Specifications)

### ① `draw_hgws_ppm_trend_chart(df: pd.DataFrame) -> go.Figure`
* **차트 타입**: 이중 축 하이브리드 차트 (Y1: Bar - 리턴 수량, Y2: Line - PPM 지표)
* **높이 스펙**: `STANDARD_HEIGHT (350)`
* **컬러 시스템**: 리턴 수량(`colors.gray` 또는 `colors.light_gray`), PPM 지표(`colors.orange_500` 또는 `colors.red_500`를 활용하여 경고성 하이라이트 부여)
* **호버 명세**: 
  `hovertemplate="<b>기간</b>: %{x}<br><b>리턴수량</b>: %{y:,.0f} ea<extra></extra>"` (Bar)
  `hovertemplate="<b>기간</b>: %{x}<br><b>PPM 지표</b>: %{y:,.1f} PPM<extra></extra>"` (Line)
* **예외 가드**: `viz_helper.validate_chart_data` 미통과 시 안전한 공백 차트 컴포넌트 반환.

### ② `draw_plant_ppm_comparison_chart(df: pd.DataFrame) -> go.Figure`
* **차트 타입**: 이중 축 또는 그룹형 막대 차트 (Y1: Bar - 공장별 리턴 수량, Y2: Line - 공장별 PPM)
* **높이 스펙**: `STANDARD_HEIGHT (300)`
* **컬러 시스템**: 공장별 구분 컬러 제공 (`colors` 테마 팔레트 적용)
* **호버 명세**: 
  `hovertemplate="<b>공장</b>: %{x}<br><b>리턴수량</b>: %{y:,.0f} ea<br><b>PPM</b>: %{customdata:.1f} PPM<extra></extra>"`
* **예외 가드**: `viz_helper.validate_chart_data` 미통과 시 안전한 공백 차트 컴포넌트 반환.

### ③ `draw_mcode_ppm_comparison_chart(df: pd.DataFrame) -> go.Figure`
* **차트 타입**: 수평 또는 수직 막대 차트
* **높이 스펙**: `STANDARD_HEIGHT (300)`
* **가드 로직**: 표시 대상 자재코드가 10개 초과 시 상위 9개만 단독 표시하고, 나머지는 `Others`로 자동 병합 및 전처리하여 시각화 복잡도 제어.
* **호버 명세**: 자재코드명과 계산된 정확한 PPM 수치를 시각화.

### ④ `draw_claim_code_donut_chart(df: pd.DataFrame) -> go.Figure`
* **차트 타입**: 도넛 파이 차트 (`hole=0.4` 설정)
* **높이 스펙**: `STANDARD_HEIGHT (300)`
* **비주얼 사양**: 각 불량 리턴 코드별 비율 및 텍스트 겹침 에러 예방을 위해 상위 5개 코드 위주 세그먼트 표출 및 라벨 바인딩.

---

## 6. 기술 표준 및 구현 제약 조건 (Technical Constraints)

* **이모지 사용 전면 금지 및 Material Symbols 표준**:
  * Streamlit UI 페이지, 탭 라벨, 마크다운 텍스트, 버튼, 토스트 등 모든 영역에서 일반 유니코드 이모지(Emoji) 사용을 금지합니다.
  * 아이콘이 필요한 영역에서는 무조건 Streamlit 기본 Google Material 아이콘 구문(예: `st.tab("리턴 분석", icon=":material/analytics:")`)만을 활용해야 합니다.
* **캐싱 수칙 적용**:
  * 대용량 데이터 전처리를 수행하는 `hgws_return_df.py` 서비스 함수에는 무조건 `@st.cache_data(ttl=1800)` 데코레이터를 적용합니다.
* **차트 정합성 및 예외 가드**:
  * 데이터가 조회되지 않는 조건(Empty DataFrame)이 전달되는 경우 화면이 붕괴하지 않도록 `if df.empty:` 구문을 UI와 시각화 드로잉 전반에 꼼꼼히 탑재합니다.
* **엄격한 물리 격벽 수호**:
  * `hgws_return_dashboard_page.py`는 `client.py`를 호출하여 직접 DB에 접근해서는 절대 안 되며, 반드시 `hgws_return_df.py`를 통해서만 데이터프레임을 받아옵니다.
  * `hgws_return_dashboard_plots.py`는 `streamlit` 라이브러리를 임포트하거나 화면 관련 UI 컴포넌트를 직접 호출하지 않습니다.

---

## 7. 향후 일정 및 검증 계획 (Testing Plan)
1. **1단계: 쿼리 및 서비스 하네스 검증**:
   * 기존 프로덕션 코드를 전혀 수정하지 않은 채, `tests/hgws_return_test.py` 스탠드얼론 스크립트를 독립적으로 생성하여 SQL 생성 및 PPM 변환 연산의 논리 무결성을 블랙박스로 사전 테스트합니다.
   * `PYTHONPATH` 및 `goeq` 가상환경 인터페이스를 활용한 실행 검증.
2. **2단계: UI 레이어 렌더링 검증**:
   * 서비스 레이어 연동 및 Streamlit 실행 후 화면 레이아웃, 이중 축 트렌드 및 PPM 지표 정합성 정밀 수동 테스트 수행.
