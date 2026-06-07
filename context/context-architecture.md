# context-architecture.md (3-레이어 아키텍처 인덱스 가이드)

이 문서는 이 프로젝트에서 유지해야 하는 3-레이어 아키텍처 철학 및 인터페이스 정합성에 대한 인덱스 맥락 가이드입니다. 

> [!IMPORTANT]
> **단일 진실 공급원 (SSOT) 적용**
> 3-레이어 아키텍처(UI, Service, Query) 및 상세 코딩 규정, 레이어별 명명 규칙, 프레임워크 사용법 등 구체적인 세부 규칙은 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**에서 단일 진실 공급원으로 관리되고 있습니다.
> 
> 모든 코드 수정 및 새로운 모듈 설계 시 반드시 **[L2-architecture.md](file:///home/jumasi/workstation/intelligence/rules/L2-architecture.md)**를 최우선 지침으로 삼아 전개 및 검증해 주십시오.

---

## 1. 아키텍처 레이어 요약
* **UI 레이어 (`pages/`)**: Streamlit 화면 및 Plotly 시각화 전담. 쿼리 레이어 직접 호출 절대 금지.
* **서비스 레이어 (`service/`)**: 데이터 수집 및 전처리 가공 수행. Pandas DataFrame 반환 및 캐싱 데코레이터 적용.
* **쿼리 레이어 (`queries/`)**: SQL 문자열 조립 전용 함수 모음. 직접적인 DB 실행 금지.

## 2. 인터페이스 영속성 규칙
1. **공개 API 시그니처 유지**: `service/` 및 `queries/`에 작성된 공용 API 함수의 이름과 타입을 변경하지 않습니다.
2. **파라미터 데이터클래스 준수**: `core/params/parameters.py`에 정의된 데이터클래스(`BaseFilterParams` 등)를 통해 파라미터를 전달받아야 합니다.
3. **스키마 무결성**: 반환되는 DataFrame의 핵심 컬럼명 및 타입 변경을 금지합니다.
