# \[PAGES\] pages/ — UI 레이어 컨텍스트

> **LAYER:** `pages/` · UI 레이어 — Streamlit 화면 렌더링·사용자 입력 처리·데이터 시각화.

---

## 역할

Streamlit 화면 렌더링, 사용자 입력 처리, 데이터 시각화를 담당하는 최상위 레이어.
비즈니스 로직은 포함하지 않으며, `service/` 레이어를 호출해 DataFrame을 받아 표시한다.

## 파일 명명 규칙

| 접미어 | 역할 |
|--------|------|
| `*_page.py` | Streamlit 화면 메인 파일. 사용자 입력 위젯, 탭, 레이아웃 구성 |
| `*_plots.py` | Plotly 차트 생성 함수 모음. `*_page.py`와 1:1로 매핑됨 |

`*_plots.py`는 순수 함수(DataFrame → Figure)만 포함하며, `st.*` 호출을 최소화한다.

## 카테고리 구조

```
pages/
├── _10_dashboard/     # 대시보드 — IQM Plus 메인, OE 품질 이슈
├── _20_analysis/      # 데이터 분석 — RR 분석, CPK, 데이터 분석 지원
├── _30_monitoring/    # 모니터링 — 진행 현황 트래커, CQMS 주간 모니터, 캘린더
├── _40_collaboration/ # 협업 — FM 라이브러리, FM 모니터링, 개발 제품 평가, QRS 워크시트
├── _50_user_guide/    # 사용자 가이드 문서 (CQMS, OE Quality BI, 테스트 매뉴얼)
├── _60_workplace/     # 실무 도구 — IQM 분석, IQM Plus 관리/집계, RR/UF 비교
├── _70_settings/      # 설정 — 수동 집계 실행
├── _80_admin/         # 관리자 전용 — 개별 분석, 평가 이력, DB 관리
└── _90_system/        # 시스템 — 로그인, 세션 관리
```

## 페이지 등록 및 보안 권한 관리

새 페이지는 `core/page/config_pages.py`의 `PAGE_CONFIGS` dict에 등록해야 하며, 접근 권한 관리(Access Control)는 점진적 검증 표준을 엄격히 따라야 합니다.

```python
"페이지 표시명": {
    "filename": "pages/_10_dashboard/feature_page.py",
    "icon": ":material/아이콘명:",
    "category": "Dashboard",   # VALID_CATEGORIES 중 하나
    "roles": ["Admin"],        # [주의] 최초 생성 시 보안 격리를 위해 Admin 단독으로 시작
}
```

역할 계층: `Viewer` < `Contributor` < `Admin`

### 신규 페이지 초기 권한 격리 수칙 (Admin-Only Sandbox)
* **최초 등록**: 신규 개발 페이지가 처음 등록될 때는 **무조건 `roles: ["Admin"]`으로만 접근 역할을 한정**해야 합니다. 화면 검증이 완료되지 않은 상태에서 일반 사용자(`Viewer`, `Contributor`)에게 미완성 화면이 유출되는 것을 예방하기 위한 안전한 샌드박스(Sandbox) 정책입니다.
* **권한 확장**: 개발 완료 후 운영자 및 실제 유저의 화면 승인이 명시적으로 확인된 이후에만 `["Viewer", "Contributor", "Admin"]` 등 점진적으로 권한 역할을 확장 및 해제합니다.

## Streamlit 패턴

### 캐싱

```python
@st.cache_data(ttl=3600)   # Databricks 쿼리 — 필수
@st.cache_data(ttl=1800)   # 사용자 정보
@st.cache_data(ttl=7200)   # 네비게이션
```

SQLite 쿼리는 가볍기 때문에 캐시 선택적 적용.

### Fragment

독립적으로 재실행되어야 하는 섹션에 `@st.fragment` 사용.
필터 위젯이 변경될 때 전체 페이지 재실행을 방지한다.

```python
@st.fragment
def section_with_filter():
    plant = st.multiselect("Plant", options=[...])
    df = service_function(plant)
    st.dataframe(df)
```

### 레이아웃 관례

- `st.columns(2)` 또는 `st.columns([2, 1])` 으로 좌우 분할
- `st.tabs([...])` 로 논리적 섹션 분리
- `st.expander` 는 부가 정보(상세 설명, 원시 데이터) 표시에 사용

## 주요 파일 목록

| 파일 | 설명 |
|------|------|
| `_10_dashboard/iqm_plus_main_page.py` | IQM Plus 메인 대시보드 |
| `_10_dashboard/oe_quality_issue_dashboard_page.py` | OE 품질 이슈 대시보드 |
| `_20_analysis/data_analysis_page.py` | 통합 데이터 분석 메인 |
| `_20_analysis/data_analysis_plots.py` | 통합 분석 플롯 모듈 |
| `_20_analysis/oem_cpk_test_page.py` | OEM CPK 분석 |
| `_20_analysis/rr_analysis_page.py` | 구름저항(RR) 분석 |
| `_30_monitoring/ongoing_status_tracker_page.py` | 진행 현황 트래커 |
| `_30_monitoring/weekly_cqms_monitor_page.py` | 주간 CQMS 모니터 |
| `_30_monitoring/calendar_page.py` | 캘린더 |
| `_40_collaboration/fm_library_page.py` | FM(불량 모드) 라이브러리 |
| `_40_collaboration/fm_monitoring_page.py` | FM 모니터링 |
| `_40_collaboration/dev_product_assessment_page.py` | 개발 제품 평가 |
| `_40_collaboration/qrs_worksheet_monitoring_page.py` | QRS 워크시트 모니터링 |
| `_60_workplace/iqm_analysis_page.py` | IQM 부적합 분석 |
| `_60_workplace/iqm_plus_management_page.py` | IQM Plus 규격 관리 |
| `_60_workplace/iqm_plus_agg_page.py` | IQM Plus 집계 실행 |
| `_60_workplace/rr_compare_oe_std_label_page.py` | RR OE vs 표준 비교 |
| `_60_workplace/uf_balance_compare_page.py` | UF 밸런스 비교 |
| `_70_settings/manual_aggregator_page.py` | 수동 집계 실행 |
| `_80_admin/analysis_individual_page.py` | 개별 규격·제품 심층 분석 |
| `_80_admin/sqlite_management_page.py` | SQLite DB 관리 |
| `_80_admin/assess_log_temp_page.py` | 평가 로그 (임시) |

---

## UI 레이어 일관성 정합성 및 안티패턴 금지 규칙

전체 페이지 검토 결과, 구현 방식이 혼재되어 유지보수성과 시각적 일관성을 저해하는 대표적인 6대 영역을 식별하였습니다. 향후 페이지 신규 개발 및 리팩토링 시 아래의 **일관성 표준 및 안티패턴 금지 조항**을 반드시 준수해야 합니다.

### 1. 3-레이어 아키텍처 준수 (UI 내 DB 직접 결합 금지)
* **[안티패턴] 안티패턴**: `pages/*_page.py` 내에서 `get_client()`를 가져와 직접 DB 인스턴스를 생성하거나, `queries/`에서 SQL 조립 헬퍼를 직접 가져와서 `.execute(query)`를 실행하는 행위.
* **[통과] 권장 규칙**: 모든 SQL 실행 및 원시 데이터 가공은 오직 서비스 레이어(`service/*_df.py`) 내부에서 수행되어야 합니다. UI 레이어에서는 오직 서비스 함수를 호출하여 정제된 Pandas DataFrame만 반환받아 화면을 렌더링해야 합니다.

### 2. UI 스타일링(CSS) 일원화 (하드코딩 HTML/CSS 인젝션 금지)
* **[안티패턴] 안티패턴**: 개별 페이지 내에서 `st.markdown("<style> ...", unsafe_allow_html=True)`나 인라인 HTML 태그(`<style>`, `<br>`)를 독자적으로 작성하여 디자인을 개별 통제하는 행위.
* **[통과] 권장 규칙**: `core/ui/styles.py`와 `core/ui/components.py`를 필수로 임포트하여 사용합니다. 카드형 지표, 헤더, 서브헤더 등의 렌더링 시에는 공통 모듈에 기정의된 헬퍼 컴포넌트(예: `mini_header_panel()`, `metric_card()`)를 표준 호출하여 전체 대시보드의 프리미엄 브랜딩 스타일을 통일성 있게 유지해야 합니다.

### 3. 규격화된 파라미터 데이터클래스 필수 사용
* **[안티패턴] 안티패턴**: 서비스 함수나 쿼리 빌더 호출 시, `mcode_list` 나 `ncf_type` 등의 입력 필터값들을 개별 낱개 문자열/리스트 인자(Argument)로 흩뿌려 전달하는 행위.
* **[통과] 권장 규칙**: `core/params/parameters.py`에 선언된 도메인별 파라미터 데이터클래스(예: `NonconformityParams`, `ProductionParams`, `AuditTaskParams` 등)를 상속 계층에 맞게 명시적으로 인스턴스화하여 하나의 객체로만 인자를 전달하도록 표준화합니다.

### 4. 캐싱(`st.cache_data`) 규칙 준수 및 TTL 단일 진실 원천(SSOT)화
* **[안티패턴] 안티패턴**: 한 화면 내에서 데이터 성격을 고려하지 않고 임의의 TTL(1800, 3600 등)을 설정하거나, 무거운 Databricks 빅데이터 조회에 캐싱 데코레이터를 누락시키는 행위.
* **[통과] 권장 규칙**: 
  * 배치 분석용 데이터 또는 쿼리 비용이 비싼 Databricks 쿼리: `@st.cache_data(ttl=3600)` (1시간) 필수 적용.
  * 실시간에 가까운 현황 및 가벼운 마스터 데이터: `@st.cache_data(ttl=1800)` (30분) 혹은 상황에 맞춰 일관성 있게 지정.
  * 캐싱 만료 상수 기준은 점진적으로 `core/common_config.py`로 집중시켜 참조하는 방향으로 개선해야 합니다.

### 5. 시각화(Plots) 개발 표준 및 디자인 시스템 연계 강화
* **[안티패턴] 안티패턴**:
  - 플롯 파일(`*_plots.py`) 내의 트레이스 및 레이아웃에 직접 `#8B5E34`, `#2F6F4E`, `#d62728` 같은 헥사 컬러 코드나 `"black"` 등을 하드코딩하는 행위.
  - `go.Layout`을 무단으로 독립 빌드하거나 `template="plotly_white"`, `"simple_white"` 등을 혼용하여 통합 테마의 여백, 그리드, 타이포그래피 정합성을 저해하는 행위.
  - 마우스 오버(Hover) 등 인터랙션을 제한하고 스타일 톤앤매너를 깨트리는 정적 시각화 라이브러리(Matplotlib 등)를 무차별 혼재하는 행위.
  - 호버 툴팁(Hover Tooltip) 설계를 아예 누락시키거나, 사용자 친화적인 설명 없이 불성실한 기본 디폴트 툴팁 상태 그대로 방치하여 차트 탐색 편의성을 저해하는 행위.
  - UCL/LCL 한계값 연산, p-chart 통계 연산, Pareto 80% Cutoff 계산 등 무거운 비즈니스/통계 전처리 알고리즘을 `*_plots.py` 내부에서 직접 구현하여 관심사 분리(SoC)를 저해하는 행위.
* **[통과] 권장 규칙**:
  - **공통 컴포넌트 필수 적용**: `core/plot/viz_plotly_design.py` 내의 `get_default_trace_config(chart_type)` 및 `get_default_layout_config(chart_type)`를 `**trace_config`, `**layout_config` 형태로 반드시 상속받아 차트의 구조를 설계해야 합니다.
  - **테마 컬러 및 폰트 바인딩**: `core/common_design_parameter.py`의 `colors` 객체 및 `create_plotly_font_dict`를 사용하여 일괄 타이포그래피와 브랜드 팔레트를 보장합니다. 투명 처리는 `viz_helper.get_transparent_colors` 공통 함수를 통합니다.
  - **풍부한 호버 인터랙션 설계 (Hover-First Design)**: 차트를 신규 생성하거나 기존 차트를 리팩토링할 때는 **항상 유저 친화적인 마우스 호버(Hover) 툴팁을 필수로 설계 및 반영**해야 합니다. 단순 수치 출력에 그치지 않고, 가독성을 고려한 굵은 텍스트(`<b>`), 줄바꿈(`<br>`), 단위 명시 및 유의미한 결합 메타데이터(예: 비율, 공장 코드, 이전 기간 대비 증감 등)가 정돈된 텍스트 템플릿(`hovertemplate="%{text}<extra></extra>"`) 형태로 직관적으로 출력되도록 시각화 전처리를 수행해야 합니다.
  - **전처리 경계 엄격 분리**: 시각화 전용 전처리(Hover text 조립, 단순 Visual top-N 슬라이싱)를 제외한 모든 데이터 통계 공식 연산은 서비스 레이어(`service/df_*.py`)에서 선행 연산 및 `@st.cache_data` 캐싱 처리 완료 후 순수 DataFrame 형태로 전달받아야 합니다. ([preprocessing-boundary.md](intelligence/guide/preprocessing-boundary.md) 표준 준수)
  - **인터랙티브 차트로 단일화**: Matplotlib를 사용한 레거시 정적 플롯(예: 레이더 차트)은 점진적으로 Plotly의 대화형 차트(`go.Scatterpolar` 등)로 전면 변환 및 통합합니다.


### 6. 세션 상태(`st.session_state`) 키 관리 및 충돌 방지
* **[안티패턴] 안티패턴**: 개별 페이지 단위로 `st.session_state["active_tab"]`, `st.session_state["selected_item"]` 등 일관되지 않은 로컬 명칭의 임의 스트링 키로 세션 상태를 직접 조작하는 행위.
* **[통과] 권장 규칙**: 공유 또는 페이지 간 전환이 수반되는 세션 키 목록은 `core/constants/` 또는 `core/page/` 아래에 전역 상수로 명시적으로 명문화(Enum 등)하여 네임스페이스 충돌을 방지하고 상태 흐름을 추적할 수 있도록 개선해야 합니다.

### 7. 오프라인/사내망 환경 하 아이콘(웹 폰트) 깨짐 대응 및 무사용 지향
* **[안티패턴] 안티패턴**: 페이지 제목, 서브헤더, 본문 마크다운 및 버튼 라벨 등 화면 곳곳에 `:material/icon_name:` 구문을 남발하는 행위. 만약 사용자가 프라이빗 보안망이나 인터넷 통신이 단절된 오프라인 인프라에서 시스템을 실행할 경우, 브라우저가 Google Fonts CDN으로부터 아이콘 웹 폰트 파일(.woff2 등)을 로드하지 못해 화면상에 영문 기호나 깨진 기호 박스가 여과 없이 노출되는 미관상 버그를 겪게 됩니다.
* **[통과] 권장 규칙**:
  - **텍스트 중심의 정교한 미니멀리즘 설계**: UI 페이지 내부의 타이틀, 마크다운 텍스트, 경고 메시지, 버튼, 탭 라벨 등 사용자에게 노출되는 모든 텍스트에서는 웹 폰트 심볼 `:material/...` 구문을 **원천 배제**하는 것을 원칙으로 합니다.
  - **레이아웃과 타이포그래피 집중**: 시각 기호에 의존하는 대시보드 대신, 적절한 라인 간격(Spacing), 굵기 대비(Font weight), 정갈하게 조화된 UI 여백 및 CSS 그리드를 활용하여 아이콘 없이도 프리미엄 브랜딩 스타일이 살아나도록 빌드합니다.
  - **프레임워크 관리 영역의 예외**: 사이드바 및 네비게이션용 `st.Page(icon=...)` 등 Streamlit 코어가 공식적으로 백엔드/네이티브단에서 조율하는 영역 외에는 날것 마크다운 텍스트 내 아이콘 기입을 자제해야 안전합니다.


---

## UI 렌더링 예외 처리 및 수직 실행 중단 방지 규정 (Error-Safe Rendering SOP)

파이썬과 Streamlit은 코드를 **위에서 아래로 수직적으로 읽는 순차적 실행 구조**를 따릅니다. 이로 인해 스크립트 실행 중 단 한 군데의 차트 드로잉이나 데이터 가공에서 예외(KeyError, IndexError, DB 에러 등)가 발생하면, **해당 지점 이후의 모든 하위 탭, 지표, 사이드바 렌더링이 전체 중단되는 치명적인 화면 마비(Crash) 현상**이 발생합니다.

이를 완전히 방지하고 서비스의 회복 탄력성(Robustness)을 유지하기 위해 예외 격리 방어 설계 표준을 준수해야 합니다. 이에 대한 완벽하고 구체적인 아키텍처 및 세부 설계는 아래 가이드라인 문서를 참조하십시오.

> ** 핵심 설계 상세 가이드**: [error-handling.md](intelligence/guide/error-handling.md)

### 1. 시각화 컴포넌트 렌더링 단위 격리 (Try-Catch Wrapping)
* **[안티패턴] 안티패턴**: `st.plotly_chart(draw_some_chart(df))` 처럼 플롯 드로잉 함수를 안전장치 없이 날것으로 호출하여 한 영역의 장애가 페이지 전체를 마비시키는 행위.
* **[통과] 권장 규칙**: 개별 컴포넌트나 카드형 지표를 그릴 때는 공통 유틸리티 컨텍스트 매니저인 `st_error_boundary` 블록으로 실행 영역을 완전히 격리하여 감싸야 합니다.

```python
from core.utils.error_boundary import st_error_boundary

with st_error_boundary("PPM 결함 트렌드 분석 차트"):
    fig = draw_defect_trend_barplot(df_defect)
    st.plotly_chart(fig, use_container_width=True)
```

### 2. 빈 데이터프레임 방어벽 구축 (Defensive Data Guard)
* **[안티패턴] 안티패턴**: DataFrame의 상태를 점검하지 않고 바로 행 인덱싱(`df.iloc[0]`)을 시도하거나 컬럼 필터링 연산을 수행하여 `IndexError`, `KeyError`를 유발하는 행위.
* **[통과] 권장 규칙**: 모든 플롯팅 함수(`*_plots.py`) 및 세부 컴포넌트 함수의 가장 첫머리(Entry point)에는 **데이터 정합성과 빈 값 유무를 검사하는 가드 조건(Defensive Guard)**을 두고, 비어있을 시 즉시 빈 피규어로 조기 리턴(Early Return) 시킵니다. 데코레이터 `@error_safe_plot`를 적극 활용하십시오.

### 3. 서비스 데이터 호출 부 손상 방지 (Service Recovery)
* **[안티패턴] 안티패턴**: 데이터베이스 연결 실패, 네트워크 일시 오류, SQL 신택스 에러 등으로 서비스 호출이 터졌을 때 예외가 UI단까지 흘러와 전체 UI가 붕괴하게 방치하는 행위.
* **[통과] 권장 규칙**: 서비스 데이터 수집 함수(`service/df_*.py`) 내부에서 예외를 처리하고 **빈 데이터프레임(`pd.DataFrame()`) 등의 안전한 Fallback 객체**를 반환하여 UI 레이어가 안전하고 견고하게 다른 컴포넌트를 렌더링할 수 있도록 보장해야 합니다.



