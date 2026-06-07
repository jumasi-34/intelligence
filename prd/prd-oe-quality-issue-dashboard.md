# [PRD] OE 품질 이슈 대시보드 개발 명세서 (Draft for AI Developer Agent)

> **[필독] AI 에이전트 수호 수칙**: 본 작업은 `L2-architecture.md`에 정의된 3-레이어 아키텍처 규칙과 프로젝트 명명 표준을 엄격히 따릅니다. 임의로 기존 프로덕션 코드를 수정해서는 안 되며, 신규 개발 파일 배치는 지정된 경로에 한정해야 합니다.

---

## 1. 제품 요구사항 및 배경 (Objective & Scope)
* **목적 (Why)**: 글로벌 OE(Original Equipment) 고객의 품질 이슈 현황을 종합 분석하고, 주요 품질 지수인 OEQI(OE Quality Index) 및 품질 문제 종결 소요 일수인 MTTC(Mean Time to Closure)를 다각도(연도별, 월별, 공장별, OEM별, 시장별, 제품유형별)로 추적/시각화하여 비즈니스 의사결정을 보좌합니다.
* **범위 (Scope)**:
  * 최근 3개년 글로벌 OEQI 및 이슈 건수 트렌드 시각화.
  * 당해 연도 vs 전년도 월간 상세 트렌드 분석.
  * 공장별 출하량 대비 품질 지수 비교 수평 막대 차트 구현.
  * 품질 종결 프로세스 4단계 마일스톤(등록, 회수, 대책, 완료보고)별 MTTC 게이지 개발.
  * 단일 공장 중심의 프로젝트, 출하, 품질 이슈, 상세 리스트 조회 탭 개발.

---

## 2. 타겟 디렉터리 및 대상 파일 (Target Layers & Files)

본 개발은 아래 3-레이어 아키텍처 구조를 엄격히 준수하여 배치되어야 합니다.

| 레이어 (Layer) | 대상 파일 경로 (File Path) | 역할 및 구현 내용 (Role) |
| :--- | :--- | :--- |
| **UI 레이어** | `app/pages/_10_dashboard/oe_quality_issue_dashboard_page.py` | 화면 제어, 사이드바 필터 바인딩, 레이아웃 및 탭 구성 |
| **시각화 레이어** | `app/pages/_10_dashboard/oe_quality_issue_dashboard_plots.py` | Plotly 차트 드로잉 함수 정의 (Streamlit 종속 코드 사용 금지) |
| **서비스 레이어** | `app/service/cqms_df.py` 및 `hope_df.py` | 데이터 수집 및 Pandas 가공 전처리 파이프라인 구축 및 캐싱 |
| **쿼리 레이어** | `app/queries/cqms_query.py` 및 `hope_query.py` | SQL 쿼리 빌더 정의 (DB Client 직접 실행 금지) |

---

## 3. 데이터 흐름 및 데이터클래스 스펙 (Data Flow & Parameters)

```mermaid
flowchart LR
    Page["app/pages/..._page.py<br>(UI / Layout Control)"]
    Plots["app/pages/..._plots.py<br>(Plotly Drawings)"]
    Service["app/service/cqms_df.py<br>& hope_df.py (Pandas Preprocessing)"]
    Query["app/queries/cqms_query.py<br>& hope_query.py (Pure SQL Generation)"]
    DB["Databricks / Oracle SQL<br>(Database Execution)"]

    Page -->|1. Call with params| Service
    Service -->|2. Generate SQL| Query
    Service -->|3. Query & Cache| DB
    Service -->|4. Return pd.DataFrame| Page
    Page -->|5. Pass DataFrames| Plots
    Plots -->|6. Return go.Figure| Page
    Page -->|7. Render st.plotly_chart| Page

    %% 격리 규칙 표시
    Page -.x|[금지] DIRECT DB ACCESS BLOCK| DB
    Service -.x|[금지] NO STREAMLIT/PLOTLY IMPORT| Page
```

* **파라미터 정의**:
  * 사용할 파라미터 클래스: `app/core/params/parameters.py` 에 정의된 `QualityIssueTasksParams` 및 `OEAppTasksParams` 사용.
* **호출 대상 서비스**:
  * `app/service/cqms_df.py` 내 `transform_qi_dashboard_df(params, selected_year)`를 호출하여 전처리된 연간/월간 추이와 피벗 테이블 수집.
  * `app/service/hope_df.py` 의 공급량 및 출하 수량 데이터 바인딩.

---

## 4. 사용자 화면 및 레이아웃 스펙 (UI / UX Layout)

### ① 사이드바 입력 필터 (Sidebar Filters)
* **Select Year (연도 선택)**: `st.selectbox` 활용, 2023년부터 현재 연도(`config.this_year`)까지 선택 가능하며 디폴트는 최근 연도로 지정.
* **Plant Select for Plant Tab (공장 선택)**: `st.selectbox` 활용, 실 생산 공장 코드 목록 바인딩.

### ② 메인 레이아웃 및 탭 구성 (Tab Structure)

#### Tab 1: Global Tab (글로벌 종합 분석)
1. **Global OE Quality Index & Q-Issue Count (2행 3열 그리드)**
   * **1행 (OEQI 분석)**:
     * `[차트 1-1]` 3-years OEQI (막대 차트)
     * `[차트 1-2]` Monthly OEQI Trend (선 차트 - 당해 vs 전년 대비)
     * `[차트 1-3]` OEM Distribution (원형 차트 - 이슈 비중)
   * **2행 (이슈 건수 분석)**:
     * `[차트 2-1]` 3-years Q-Issue Count (막대 차트)
     * `[차트 2-2]` Monthly Q-Issue Count (막대 차트)
     * `[차트 2-3]` Market Distribution (원형 차트)
2. **Quality Metrics by Plant (1행 4열 가로형 막대 배치)**
   * 공장별 지표 비교: `SKU by Plant`, `Supply Quantity by Plant`, `Issue Count by Plant`, `OEQI by Plant`
   * `st.expander` 내부에 공장별 비중 파이 차트 3종 배치.
3. **Categorize Quality Issues by Type**
   * 이슈 대/중/소 분류 트리맵(`Issue Type TreeMap`) 및 공장별 최다 발생 누적 막대 그래프(`Worst by Plant`) 렌더링.
4. **MTTC Index & Milestone Gauges**
   * 최근 3개년 MTTC 막대 차트, 글로벌 종합 MTTC 게이지 및 마일스톤 4단계 상세 게이지 인디케이터(등록, 회수, 대책, 완료보고) 배치.

#### Tab 2: Plant Tab (개별 공장 상세 분석)
1. **Plant KPI Summary Cards (4개 메트릭 컬럼)**
   * `Projects` (양산/개발 품목 수), `Supplies` (총 OE 공급량), `Quality Issue` (종결/진행 건수), `Index` (OEQI / MTTC)
2. **Comparison & Trends (1행 2열 배치)**
   * `[좌측]` 선택 공장이 전체 평균 대비 어느 수준인지 하이라이트된 공장 비교 바 차트.
   * `[우측]` 선택 공장의 월간 OEQI 및 이슈 건수 시계열 추이 선/막대 차트.
3. **Quality Issue List (데이터 테이블)**
   * `COMMON_REMAIN_COLUMNS` 기준 열 정렬 및 공통 디자인 테이블 컴포넌트(`COMMON_COLUMN_CONFIG`) 적용.

#### Tab 3: OEQG Tab (운영 그룹별 분석)
1. **OEQG Trends (1행 2열 배치)**
   * `[좌측]` OEQG별 월간 품질 이슈 발생 건수 트렌드 차트.
   * `[우측]` OEQG별 월간 OEQI 지수 시계열 트렌드 차트.
2. **OEQG MTTC Comparisons**
   * 그룹별 연간/마일스톤별 소요 일수 비교 다차원 막대 차트 시각화.

---

## 5. 시각화 개별 스펙 (Chart Specifications)

### ① draw_three_years_oeqi_barplot(df: pd.DataFrame) -> go.Figure
* **차트 타입**: Bar Chart
* **높이 스펙**: `STANDARD_HEIGHT (300)`
* **컬러 시스템**: `three_color_lst` (`colors.light_gray`, `colors.gray`, `colors.orange_500` 교차 적용)
* **호버 명세**: `hovertemplate="<b>Year</b>: %{x}<br><b>OEQI</b>: %{y:.1f}<extra></extra>"`
* **예외 가드**: `viz_helper.validate_chart_data` 미통과 시 빈 차트 컴포넌트 반환.

### ② draw_monthly_oeqi_trend_lineplot(df: pd.DataFrame, selected_year: int) -> go.Figure
* **차트 타입**: Multi-Line Chart
* **높이 스펙**: `STANDARD_HEIGHT (300)`
* **컬러 시스템**: 당해 연도(`colors.orange_500`), 전년도(`colors.gray`) 교차 적용.
* **호버 명세**: 당월 및 연도별 정확한 수치 오버레이 포맷 정의.

*(이외 `oe_quality_issue_dashboard_plots.py` 내 모든 드로잉 기능은 이와 유사한 헥사 코드 격벽 및 예외 처리 규격을 준수함)*

---

## 6. 기술 표준 및 구현 제약 조건 (Technical Constraints)
* **캐싱 강제**: 서비스 단의 주요 집계 연산 함수는 반드시 `@st.cache_data(ttl=3600)`를 적용하여 반복 쿼리 비용을 절감하십시오.
* **공통 UI 활용**: 페이지 타이틀 및 메트릭 장식 시 `app/core/ui/components.py` 내의 헤더나 컴포넌트 유틸리티를 최대한 적용하십시오.
* **차트 유효성 가드**: 차트 드로잉 시 `viz_helper.validate_chart_data`를 사용하여 빈 데이터에 대한 화면 붕괴를 예방하십시오.
* **SQL 헬퍼 적용**: 조건 조립 시 `app/core/query/query_helper.py`의 `QueryFilter`를 활용하여 안전한 SQL 결합을 설계하십시오.
