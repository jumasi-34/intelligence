# context-iqm-checklist.md (통합 품질 분석 도메인 운영 안전 체크리스트)

이 체크리스트는 IQM 및 IQM Plus 도메인 관련 파일(`service/iqm_df.py`, `queries/q_iqm_plus.py` 등)의 신규 피처 추가나 수정 작업이 수행될 때, 배포 전 에이전트 및 시니어 엔지니어가 반드시 자가 검증해야 하는 **안전성 진단 체크리스트**입니다.

---

## 1. 품질 지표 수식 안전 진단 (Formula Safety Guard)
- [ ] OEQI 계산 공식이 `(QI_CNT / SUPP_QTY) * 1,000,000` 표준과 완벽히 일치하며 임의 상수가 대입되지 않았는가?
- [ ] NCF_RATE 계산 공식이 `(NCF_CNT / PROD_QTY) * 100` 수식을 따르며 오차가 없는가?
- [ ] 나눗셈 분모(`SUPP_QTY`, `PROD_QTY`)에 0이 유입될 경우를 대비해 `np.where` 또는 `try-except` 기반의 **0 분모 격벽 장치**가 확실히 적용되었는가?
- [ ] 가중 품질 결함치 연산 도중 `float` 자료형의 정밀도 한계로 인한 오차가 발생하지 않도록 `round()` 또는 데이터 캐스팅 처리가 지정되었는가?

---

## 2. 비용 및 캐싱 최적화 진단 (Caching & Cost Control)
- [ ] 메인 데이터 가공 함수에 `@st.cache_data(ttl=3600)`(혹은 적정 시간 이상) 데코레이터가 누락 없이 지정되었는가?
- [ ] 함수의 입력 인자가 Streamlit 캐시 키로 온전히 사용될 수 있는 해시 가능한 데이터 타입(예: immutable dataclass 또는 기본형 변수)인가?
- [ ] 대용량 Databricks 테이블 조회 시, 필터에 `START_DATE`, `END_DATE` 및 `PLANT_CODE` 등의 물리 파티션 키가 반드시 바인딩되어 비용을 억제하고 있는가?

---

## 3. UI 렌더링 및 레이아웃 안정성 (Visual Delivery Guard)
- [ ] `iqm_plus_main_plots.py` 내의 모든 Plotly Figure 객체가 테두리 여백 최소화(`margin`) 설정을 포함하고 있는가?
- [ ] 차트에 사용되는 폰트가 `Inter, Roboto, sans-serif`로 명시되어 시스템 테마와 비주얼 일관성을 보존하고 있는가?
- [ ] 요약 지표 카드(`st.metric`) 렌더링 시, 전월/전분기 대비 증감 수치(`delta`)가 정상적으로 연동되는가?
- [ ] 조회 결과가 빈 데이터프레임(`empty dataframe`)일 때, 대화형 차트 영역이 찌그러지거나 에러 메시지가 쏟아지지 않고 정갈한 안내 배너(`st.warning`)가 등장하도록 방어 처리했는가?

---

## 5. 역동기화 재발 방지 대책 (Reverse Sync Auto-Prevention)
> [!IMPORTANT]
> 이 조항은 하네스 자가 치유(Self-Healing) 엔진에 의해 런타임 오류로부터 자동 도출된 필수 예방 규격입니다.

- [ ] [Layer_Boundary_Violation] 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것.
