# GEMINI.md (infra/ 로컬 가이드라인 및 인덱스)

이 문서는 `intelligence/infra/` (시스템 및 물리 인프라 사양 레이어) 고유의 로컬 규칙과 파일 정보를 신속히 인지하기 위한 마이크로 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **물리 기술 전문성 (Infrastructure Focus)**: 이 폴더는 오로지 물리 데이터베이스 인스턴스, 스키마 레이아웃, 포트, 드라이버 환경설정, 외부 API의 기계적 통신 규격 등 컴퓨터 공학적 제원과 인프라 설정만을 기술합니다. 비즈니스 맥락이나 논리적 등급 공식은 절대로 작성하지 마십시오. (→ `domain/`로 이관)
* **민감 정보 안전 보호 (Secret Protection)**: DB 패스워드, SSH 키, API Private Token 등 민감한 자격 정보는 이 디렉터리의 마크다운에 절대 평문으로 하드코딩하지 않습니다. 민감 정보는 `.env` 환경 변수 관리 사양 혹은 보안 주입 표준으로만 정의하십시오.
* **실행 모듈의 역할 한정**: 이 폴더 내에 위치한 파이썬 스크립트(`generate_korean_metadata_json.py` 등)는 인프라 메타데이터를 정적 지식 데이터로 자동 추출/가공/싱크해주는 **유틸리티성 작업 보조 도구**로 역할을 엄격히 국한합니다. 비즈니스 트랜잭션 처리나 에이전트 핵심 행동 코드는 포함할 수 없습니다.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `infrastructure-summary.md` | 플랫폼 서버 및 연합 데이터베이스 분산 아키텍처 인프라 연동 총괄 가이드 |
| `database-metadata.md` | 분산 물리 테이블 스키마, 컬럼명, 물리 타입, 한글 설명 매핑 메타데이터 원장 |
| `environment.md` | 로컬 가상환경(Miniconda `goeq`), Oracle 인스턴트 클라이언트 및 OS 종속 라이브러리 설정 가이드 |
| `queries-specification.md` | SQL 쿼리 설계 표준 및 `app/queries/` 레이어에 연동하기 위한 물리 빌더 가이드 |
| `service-specification.md` | `app/service/` 레이어의 전처리 및 데이터프레임 구조화 물리적 구현 사양서 |
| `pages-specification.md` | Streamlit 페이지 구성 및 물리 렌더링 레이아웃 인터페이스 명세서 |
| `core-specification.md` | DB 커넥터 및 공통 소스 모듈인 `app/core/` 하위 컴포넌트 연동 규격 |
| `automation-log-specification.md` | 시스템 자동 가동을 위한 로깅 레벨 및 로깅 파일 저장 관리 인터페이스 명세서 |
| `generate_korean_metadata_json.py` | DB 스키마로부터 다국어/한국어 메타데이터 맵을 추출 및 싱크하는 빌드 유틸리티 |

---

## 3. 변경 이력 (Changelog)

* **2026-06-14**:
  * [REFACTOR] `infra/` 레이어 정의를 특정 플랫폼(Databricks 등)에 고착되지 않는 범용 '시스템 및 물리 인프라 사양 레이어'로 승격하고, 민감 데이터 하드코딩 엄금 및 실행 코드의 도구 한정 규칙 추가.
  * [Feat] 인프라 폴더 전용 `GEMINI.md` 최초 비치.
