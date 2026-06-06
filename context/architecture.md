# architecture.md (3-레이어 아키텍처 및 리팩토링 정합성 지침서)

이 문서는 AI 에이전트(`Refactor Agent` 등)가 시스템의 효율화 및 클린 코드 고도화를 수행할 때, 결코 깨뜨려서는 안 되는 **CQ-BI 시스템 고유의 3-레이어 아키텍처 철학 및 인터페이스 영속성 규칙**을 정의하는 맥락(Context) 가이드입니다.

> [!IMPORTANT]
> **아키텍처 규칙 통합 관리(SSOT) 알림**
> 본 프로젝트의 파일 구조, 레이어 격리, 명명 규칙, 상세 코딩 표준 및 금지 사항 등 구체적인 아키텍처 표준 규칙은 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**에서 단일 진실 공급원(SSOT)으로 통합하여 관리합니다.
> 
> 모든 리팩토링 및 신규 페이지 추가 작업 시, 본 문서의 기본 흐름을 숙지하고 실질적인 검증 수칙 및 규제 사항은 반드시 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**를 기준으로 검증 및 전개해 주십시오.

---

## 1. 3-레이어 아키텍처 구조 요약

본 프로젝트는 구조가 명확히 분리된 **3-레이어 아키텍처**를 따르고 있습니다. 리팩토링 시 어떠한 코드도 이 레이어 격벽을 뛰어넘어 혼용되어서는 안 됩니다.

* **UI 레이어 (`pages/`)**: 오직 Streamlit 뷰 렌더링과 Plotly 시각화 전담
* **서비스 레이어 (`service/`)**: 데이터 전처리, 타입 복구, 계산 집계 전담 (Pandas DataFrame 반환 및 캐싱 데코레이터 적용)
* **쿼리 레이어 (`queries/`)**: SQL 문자열 조립만 전담 (Pure string SQL 리턴, 직접적인 DB execute 금지)

> [!TIP]
> 상세 레이어 구조, 파일 명명 가이드, 레이어 격리 조건에 관한 물리적 가이드라인은 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)** 문서를 열람하십시오.

---

## 2. 공개 인터페이스 영속성 보장 (No Public Interface Modification)

리팩토링 에이전트는 코드 가독성을 올리는 와중에도, 타 레이어에 영향이 가지 않도록 **공개 인터페이스(Public API)를 반드시 그대로 보존**해야 합니다.

1. **파라미터 데이터클래스 보존**:
   - `core/params/parameters.py`에 선언된 파라미터 `dataclass`의 인자 구성, 타입 힌트, 디폴트값을 임의로 수정/삭제해서는 안 됩니다.
2. **함수 호출 명세(Signature) 유지**:
   - `service/` 및 `queries/`에 작성된 공용 API 함수의 이름, 파라미터 타입, 리턴 타입을 절대로 보존해야 합니다.
3. **결과 데이터프레임 스키마 무결성**:
   - 서비스 모듈이 최종 반환하는 Pandas DataFrame의 핵심 컬럼명 및 데이터 타입은 한 자도 변경할 수 없습니다.

---

## 3. 성능 캐싱 메커니즘 보증 (Caching Preservation)

수정 중 자칫 Streamlit의 고유 강점인 **메모리 캐싱(Caching) 규칙**을 무력화하여 Databricks 쿼리 비용 폭증을 유발하지 않도록 규제합니다.

- **`@st.cache_data` 준수**:
  - 데이터 수집 및 연산을 가공하는 서비스 레이어 함수에 지정된 캐싱 데코레이터와 TTL 설정을 함부로 제거하거나 변형하지 마십시오.
  - 가급적 에이전트는 캐시 효율성이 좋은 **순수 함수(Side-Effect가 없는 Pure Function)** 형태로 로직을 고도화해야 합니다.

---

## 4. 무단 접근 금지 구역 (Strict No-Touch Zones)

시스템의 기둥 역할을 하는 아래 영역들은 에이전트의 수정 사정거리에서 **영구 배제**됩니다.
* **사용자 세션 및 로그인 보안 제어 구역**: `pages/_90_system/login_page.py` 및 SQLite 인증 DB 연동 로직
* **데이터베이스 물리적 커넥터 구역**: `core/db/client.py` 및 `core/operate/db_client.py`
* **SQLite 스키마 마이그레이션 및 DML 구역**: `automation/` 하위 스크립트 및 `ops.db`/`staging.db`를 핸들링하는 로직
