# iqm.summary.md (통합 품질 분석 및 종합 지표 도메인 요약)

이 시스템에서 'IQM(Integrated Quality Management) 및 IQM Plus'는 경영진 및 품질 책임자가 전사의 핵심 품질 현황을 한눈에 조망할 수 있는 **최상위 요약 지표 및 의사결정 대시보드**를 제공하는 최고 민감 영역입니다.

---

## 1. 도메인 규칙 및 불변 조건 (Invariants)
- **핵심 수식의 무오류 보장 (Formula Integrity)**:
  - **OEQI (OE Quality Index, OE 품질지수)**: `(QI_CNT / SUPP_QTY) * 1,000,000` (백만 납품 수량 당 필드 불량 발생 가중 건수)
  - **NCF_RATE (NCF 불합격률)**: `(NCF_CNT / PROD_QTY) * 100` (%)
  - 수식 상의 산정 가중치나 분모/분자 매핑 관계는 경영 보고의 정합성을 위해 임의 변형을 절대 금지합니다.
- **성능 게이트키핑 (Performance Guard)**:
  - 경영 보고 화면의 특성상 로딩 지연이 발생해서는 안 되며, Databricks 데이터 수집은 무조건 `@st.cache_data(ttl=3600)`를 통과해 사전에 중간 집계된 캐시로부터 취득해야 합니다.
- **분모 0 처리 예외 회피 (Zero-Value Guard)**:
  - 납품량(`SUPP_QTY`) 또는 생산량(`PROD_QTY`)이 `0`인 조기 런칭 자재나 가입 공장의 데이터 인입 시, 지표 연산이 예외로 중단되지 않고 안전하게 `0.0`으로 대체 가공되도록 정밀 처리해야 합니다.

---

## 2. 민감 소스 파일 (Sensitive Files)
- `service/iqm_df.py` (종합 품질지표 가공 및 NCF, OEQI, IQM Plus 연산 핵심 전처리)
- `queries/q_iqm_plus.py` (종합 지표에 유입되는 원시 실적 데이터 수집 빌더)
- `pages/_10_dashboard/iqm_plus_main_page.py` (임원 보고용 메인 화면 및 렌더링 카드 컨트롤러)
- `pages/_10_dashboard/iqm_plus_main_plots.py` (종합 트렌드 및 분기 대비 게이지 차트 생성)

---

## 3. 절대 금지 행동 (Prohibited Actions)
- OEQI 및 NCF 계산 공식에 사용되는 매칭 파라미터나 가중치를 상의 없이 하드코딩 변경하는 행위.
- 캐싱 데코레이터(`@st.cache_data`)를 무단 삭제하거나 캐싱 유지 시간(TTL)을 과도하게 단축하여 빅데이터 웨어하우스(Databricks)에 쿼리 비용 폭탄을 유발하는 행위.
- 필터 조건 상 대상 자재(`MCODE`)나 조회 기간이 완전히 누락된 전체 대용량 테이블 스캔(Full Table Scan) 쿼리 설계.

---

## 4. 필수 테스트 시나리오 (Required Test Scenarios)
- **Zero Division 테스트**: 납품량과 생산량이 `0`인 기형 실적 데이터가 인입될 때 전체 데이터프레임 집계 연산이 예외 크래시 없이 무사 통과하는가?
- **캐시 성능 히트 테스트**: 동일 일자/자재 조건으로 대시보드를 반복 조회할 때, DB 클라이언트가 직접 쿼리를 수행하지 않고 메모리 캐싱 데이터가 지연 없이(100ms 이내) 반환되는가?
- **누적 수치 데이터 정합성 검증**: 연간 누적 및 분기 집계 연산 시, 각 월별 데이터프레임의 합산과 분기 가중치 집계 결과가 소수점 4째 자리까지 정확히 일치하는가?
