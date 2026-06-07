# [PRD] - {기능명 / 화면명} 개발 명세서

> **[필독] AI 에이전트 수호 수칙**: 본 작업은 `L2-architecture.md`에 정의된 3-레이어 아키텍처 규칙과 프로젝트 명명 표준을 엄격히 따릅니다. 임의로 기존 프로덕션 코드를 수정해서는 안 되며, 신규 개발 파일 배치는 지정된 경로에 한정해야 합니다.

---

## 1. 제품 요구사항 및 배경 (Objective & Scope)
* **목적 (Why)**: 
  * *예: 글로벌 수주 성공률 및 개발 진척 현황을 가시화하여, 품질 이외의 수주 진척률 및 파이프라인 관리 편의성 제공.*
* **범위 (Scope)**:
  * *예: 연도별 수주 실적 지표 카드, 공장별 수주 성공률 바 차트, 영업본부별 월간 추이 트렌드 차트 및 원시 데이터 그리드 출력.*

---

## 2. 타겟 디렉터리 및 대상 파일 (Target Layers & Files)
작성해야 할 파일의 경로를 3-레이어 표준에 의거하여 명시하십시오.

| 레이어 (Layer) | 대상 파일 경로 (File Path) | 역할 및 구현 내용 (Role) |
| :--- | :--- | :--- |
| **UI 레이어** | `app/pages/[메뉴폴더]/[기능명]_page.py` | 화면 제어, 사이드바 필터 바인딩, 레이아웃 및 탭 구성 |
| **시각화 레이어** | `app/pages/[메뉴폴더]/[기능명]_plots.py` | Plotly 차트 드로잉 함수 정의 (Streamlit 종속 코드 사용 금지) |
| **서비스 레이어** | `app/service/df_[도메인명].py` | 데이터 처리, 비즈니스 계산 로직, Pandas 파이프라인 및 `@st.cache_data` 캐싱 |
| **쿼리 레이어** | `app/queries/[도메인명]_query.py` | Pure SQL 쿼리 문자열 조립 함수 정의 (DB 직접 실행 금지) |

---

## 3. 데이터 흐름 및 데이터클래스 스펙 (Data Flow & Parameters)

```mermaid
flowchart LR
    Page["app/pages/..._page.py<br>(UI / Layout Control)"]
    Plots["app/pages/..._plots.py<br>(Plotly Drawings)"]
    Service["app/service/df_*.py<br>(Pandas Preprocessing)"]
    Query["app/queries/*_query.py<br>(Pure SQL Generation)"]
    DB["Database Execution<br>(Databricks / Oracle SQL)"]

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
  * 사용할 파라미터 클래스: `app/core/params/parameters.py` 에 정의된 `[필터데이터클래스명]` 사용.
  * *필요시 신규 데이터클래스가 필요할 경우 `app/core/params/parameters.py`에 추가 작성할 명세 기입.*
* **데이터 흐름 흐름도**:
  `UI_Page(st.sidebar_filter) -> Service_DF(with DataClass) -> Query_SQL(pure string) -> DB(Databricks/Oracle Execution) -> Service_DF(Pandas Preprocess & Caching) -> UI_Page -> UI_Plots(draw go.Figure) -> UI_Page(st.plotly_chart)`

---

## 4. 사용자 화면 및 레이아웃 스펙 (UI / UX Layout)
화면 구조와 컴포넌트 구성을 와이어프레임 형태 또는 설명으로 기입하십시오.

### ① 사이드바 입력 필터 (Sidebar Filters)
* *예: `Select Year` (selectbox), `Division Select` (multiselect) 등*

### ② 메인 레이아웃 및 탭 구성 (Tab / Layout Structure)
* **Tab 1: [탭이름 1]**
  * *예: KPI 요약 지표 카드 3개 (st.columns)*
  * *예: 1행 2열 배치 - [좌] 연도별 추이 그래프, [우] 대리점별 점유율 파이 차트*
* **Tab 2: [탭이름 2]**
  * *예: 상세 정보 조회 테이블 및 엑셀 다운로드 링크*

---

## 5. 시각화 개별 스펙 (Chart Specifications)
구현할 개별 차트의 세부 명세와 차트 드로잉 함수 형태를 지정하십시오.

### ① [차트 1] - {차트 타이틀}
* **함수명**: `draw_[차트내용]_[차트타입](df: pd.DataFrame) -> go.Figure`
* **차트 타입**: *예: Line, Stacked Bar, Grouped Bar, TreeMap, Gauge 등*
* **컬러 규칙**: *예: `colors.orange_500`과 `colors.gray`를 교차 바인딩하여 트렌드 비교 하이라이트 제공*
* **디자인 및 높이**: `STANDARD_HEIGHT (300)` 적용, 범례(Legend) 표시 여부, 틱 포맷 등 기입.
* **호버 명세**: `hovertemplate`에 표시할 속성과 포맷 기입.

### ② [차트 2] - {차트 타이틀}
* ...

---

## 6. 기술 표준 및 구현 제약 조건 (Technical Constraints)
* **캐싱 강제**: 서비스 단의 주요 집계 연산 함수는 반드시 `@st.cache_data(ttl=3600)`를 적용하여 반복 쿼리 비용을 절감하십시오.
* **공통 UI 활용**: 페이지 타이틀 및 메트릭 장식 시 `app/core/ui/components.py` 내의 헤더나 컴포넌트 유틸리티를 최대한 적용하십시오.
* **차트 유효성 가드**: 차트 드로잉 시 `viz_helper.validate_chart_data`를 사용하여 빈 데이터에 대한 화면 붕괴를 예방하십시오.
* **SQL 헬퍼 적용**: 조건 조립 시 `app/core/query/query_helper.py`의 `QueryFilter`를 활용하여 안전한 SQL 결합을 설계하십시오.

---

### AI 에이전트를 가이드할 때 유용한 팁
1. **SSOT 원칙 강조**: AI에게 코딩을 시킬 때 항상 `L2-architecture.md`를 먼저 정독(view_file)한 뒤 작업을 개시하도록 지시하십시오.
2. **리팩토링 범위 제어**: 기존의 서비스 모듈(`cqms_df.py` 등)을 고칠 경우, "기존 인터페이스(`preprocessing_*_rawdata` 등)를 훼손하지 않고 신규 대시보드용 `transform_*_df` 함수를 추가하는 방식"으로 범위를 명확히 규정하여 하위 호환성을 확보하십시오.
3. **에러 가드 삽입 요구**: 데이터가 아예 안 넘어오는 테스트 케이스를 가상으로 통과할 수 있도록 `if df.empty` 분기문과 `try-except`를 UI 및 Plots 함수 곳곳에 꼼꼼히 채워 달라고 요구하십시오.
