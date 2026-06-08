# L3-service.md (L3 서비스 레이어 개발 규칙)

이 문서는 비즈니스 로직과 데이터 가공 및 캐싱을 담당하는 **서비스 레이어 (`app/service/`)**의 핵심 개발 표준 및 안전 규칙을 정의합니다.

---

## 1. 서비스 레이어의 핵심 역할 및 위치
- **위치**: `app/service/` 아래에 배치
- **파일명**: `*_df.py` 명명 규칙 준수
- **책임**: DB 클라이언트를 통해 조회된 원시 데이터프레임(Raw DataFrame)을 비즈니스 로직, 데이터 타입 복구, 결측치 대체, 통계/그룹 집계 연산 등을 거쳐 뷰 레이어에 적합한 Pandas DataFrame으로 정제하여 반환합니다.

---

## 2. 금지 규칙 (Strict Guardrails)
> [!IMPORTANT]
> 레이어 간 상호 작용 및 고수준 의존성 격벽 제약 조건은 단일 진실 공급원(SSOT)인 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**의 규칙을 엄격히 준수합니다.

1. **Inplace Mutation 금지 (No Inplace)**:
   - 데이터프레임 가공 시 `inplace=True` 옵션 사용을 금지하며, 원본 데이터의 불변성을 유지하고 사이드 이펙트를 원천 차단합니다.
   - [안티패턴] `df.dropna(inplace=True)` -> `df = df.dropna()`

---

## 3. 데이터 가공 및 캐싱 4대 표준
1. **성능 캐싱 의무화 (Streamlit Caching)**:
   - 무거운 DB 쿼리 및 1차 데이터 전처리 과정이 수행되는 함수에는 반드시 캐싱 데코레이터(`@st.cache_data`)를 선언하고, 적절한 만료 시간을 부여합니다.
   - 배치형 분석/대시보드: `ttl=3600`(1시간) 또는 `ttl="1h"`
2. **함수 시그니처 및 리턴 스키마 영속성**:
   - UI 레이어의 렌더링 파괴를 방지하기 위해, 공용 API 함수의 명세(이름, 파라미터 타입) 및 결과 DataFrame의 핵심 컬럼명/데이터 타입을 영구히 보존합니다.
3. **인터페이스 파라미터 데이터클래스 통일**:
   - 서비스 함수의 필터 인자는 낱개 변수가 아닌, 반드시 `app/core/params/parameters.py`에 선언된 `*Params` 데이터클래스 객체로 일괄 수신합니다.
4. **메서드 체이닝 및 로깅 파이프라인**:
   - 가급적 판다스 메소드 체이닝 구조를 활용하여 연산의 선형 흐름을 유지하고, 필요 시 중간 가공 로그를 남깁니다.

---

## 4. 표준 명명 규칙 (Naming Standard)
* **1차 전처리 및 데이터 수집**: `preprocessing_<도메인>_*_rawdata(...)`
  - 예: `preprocessing_qi_general_rawdata(...)`
* **2차 형태 변환 및 피벗 가공**: `transform_<업무/차트>_df(...)`
  - 예: `transform_qi_dashboard_df(...)`
* **통계 및 그룹 집계 연산**: `preprocessing_<업무>_*_agg(...)`
  - 예: `preprocessing_ncf_daily_agg(...)`
* **모듈 내부 비공개 헬퍼 함수**: `_fetch_*` 또는 `_apply_*`
  - 외부 노출을 막기 위해 언더바(`_`) 접두사 필수 사용
