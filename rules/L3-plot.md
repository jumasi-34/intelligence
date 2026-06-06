# L3-plot.md (L3 시각화/차트 개발 규칙)

이 문서는 Plotly 기반의 시각화 로직을 전문적으로 처리하는 **플롯 레이어 (`app/pages/`)**의 핵심 개발 표준 및 안전 규칙을 정의합니다.

---

## 1. 플롯 레이어의 핵심 역할 및 위치
- **위치**: `app/pages/` 산하 각 페이지 폴더(예: `_10_dashboard/`)에 page 파일과 함께 동거
- **파일명**: `*_plots.py` 명명 규칙 준수
- **책임**: 넘겨받은 정제된 Pandas DataFrame을 활용하여 호버 텍스트 가공, 차트 디자인 세부 옵션을 설정하고 최적화된 **Plotly Figure 객체**를 드로잉 및 반환합니다.

---

## 2. 플롯 레이어의 3대 금지 규칙 (Strict Guardrails)
1. **Streamlit 레이아웃 요소 호출 절대 금지 (No Streamlit Layout in Plots)**:
   - `*_plots.py` 내부에서는 `st.write`, `st.columns`, `st.sidebar`, `st.metric` 등 화면 레이아웃 및 UI 요소를 렌더링하는 함수를 절대 호출할 수 없습니다.
   - 오직 순수 시각화 차트 객체(`go.Figure`, `plt.Figure` 등)만을 생성하여 컨트롤러(`*_page.py`)로 전달하는 것에만 책임을 한정합니다.
2. **비즈니스 가공 금지 (No Business Logic)**:
   - 플롯 파일 내부에서 데이터 원본 필터링, 복잡한 통계 수식 적용, 결측값 전처리 등 비즈니스 서비스 레이어의 역할을 침범하지 않습니다.
3. **독립 임포트 차단 (No Direct Service Import)**:
   - `*_plots.py` 내부에서 직접 서비스 모듈(`df_*.py`)을 임포트하지 않습니다. 데이터프레임은 오직 호출자인 `*_page.py` 컨트롤러로부터 매개변수로 전달받아야 합니다.

---

## 3. 시각화 개발 3대 표준
1. **시각화 전처리 샌드박스 경계 (Preprocessing Boundary)**:
   - 마우스 호버(Hover)용 툴팁 텍스트 조립, 플롯 디자인에 맞춘 Top-N 자르기 및 `Others` 그룹화, 그래프 축 포맷팅(Tickformat) 등 **시각화 레이아웃에 직접 결속된 포맷팅 가공**만 플롯 레이어 내에서 수행합니다.
2. **컬러 코드 중앙화 및 테마 바인딩**:
   - 차트 마커나 라인 색상 지정 시 하드코딩된 임의의 헥사(Hex) 코드를 사용하지 않습니다.
   - 반드시 `app/core/common_design_parameter.py` 또는 `viz_plotly_design` 테마 컬러 변수를 가져와 바인딩함으로써 프로젝트 전반의 고급스럽고 일관된 룩앤필(Premium Look & Feel)을 보장해야 합니다.
3. **인터렉티브 호버 옵션 최적화**:
   - 정적 이미지 차트가 아닌, 사용자 마우스 오버 시 풍부하고 직관적인 데이터를 제공하도록 `hover_data` 혹은 `hovertemplate` 옵션을 미려하게 커스텀 구성합니다.

---

## 4. 표준 파일 명명 규칙 (Naming Standard)
- **차트 드로잉 파일**: `*_plots.py`
  - 반드시 화면 메인 컨트롤러(`*_page.py`)와 동일 디렉터리 내에서 1:1 대치 구조를 유지합니다.
  - 예: `cqms_dashboard_page.py`와 `cqms_dashboard_plots.py`
