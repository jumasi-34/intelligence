# 메뉴 카테고리 정의 및 페이지 매핑 가이드 (Menu Navigation Specification)

이 문서는 CQ-BI 애플리케이션의 네비게이션 메뉴 구조를 체계적으로 관리하기 위해 각 **카테고리별 명확한 정의**와 **페이지 매핑 표준**을 수립한 단일 진실 공급원(SSOT) 문서입니다.

---

## 1. 개요 및 목적
현재 CQ-BI 시스템은 Streamlit의 멀티 페이지 네비게이션 방식을 채택하여 여러 분석 화면을 제공하고 있습니다. 하지만 각 메뉴 카테고리의 명확한 정의가 부족하여, 물리적인 폴더 위치와 논리적인 메뉴 카테고리가 일치하지 않는 현상이 존재합니다.
본 가이드는 각 카테고리의 본질적인 목적과 대상을 재정의하고, 물리-논리 정합성을 일치시키기 위한 매핑 표준을 정의하여 시스템의 직관성과 유지보수성을 극대화하는 것을 목적으로 합니다.

---

## 2. 메뉴 카테고리별 상세 정의 및 매핑 기준

CQ-BI의 메뉴는 총 9개의 표준 카테고리로 분류되며, 각 카테고리의 정의와 매핑 기준은 다음과 같습니다.

| 폴더 접두사 | 카테고리명 (Category) | 정의 및 핵심 목적 (Definition & Purpose) | 주요 대상 사용자 (Target Audience) | 페이지 매핑 기준 및 예시 |
| :---: | :--- | :--- | :--- | :--- |
| **`_10_`** | **Dashboard** | 본부 및 전사 품질 KPI, 이슈 현황을 한눈에 조망할 수 있는 고수준 요약 화면. 즉각적인 상황 인지와 의사결정을 지원합니다. | 경영진, 관리자, 전 실무자 | 고수준 요약 지표, 전체 트렌드 오버뷰, 현황 대시보드<br>*(예: OE Quality Dashboard)* |
| **`_20_`** | **Analysis** | 품질 문제의 원인 규명 및 통계적 검증을 위해 다양한 필터와 다차원 축 분석 기능을 제공하는 정밀 분석 공간입니다. | 품질 분석가, 개발/기술 실무자 | 다변량 분석, CPK 통계 분석, 개별/상세 트렌드 분석<br>*(예: OEM CPK Test, Data Analysis)* |
| **`_30_`** | **Monitoring** | 일/주/월 단위의 주기적인 품질 데이터 감시, 이상치(Outlier) 감지 및 실시간 현황을 추적하는 모니터링 공간입니다. | 현업 실무자, 모니터링 담당자 | 주기적 데이터 뷰어, 알림 캘린더, 실시간 트래커, 반품 모니터<br>*(예: Weekly CQMS Monitor)* |
| **`_40_`** | **Collaboration** | 사외 OEM사, 타 부서 또는 협력사와의 품질 평가, 공동 대응 워크시트 및 지식 라이브러리를 공유하고 소통하는 공간입니다. | 협력사 담당자, 타 부서 협업자, 품질 담당 | 품질 평가서, 공동 워크시트, 기술 표준 공유 라이브러리<br>*(예: FM Monitoring, WQRS Worksheet)* |
| **`_50_`** | **User Guide** | 일반 사용자 및 신규 사용자가 시스템을 원활하게 활용할 수 있도록 매뉴얼, 공통 가이드 및 업무 규격 문서를 제공하는 학습 공간입니다. | 전체 시스템 사용자 | 일반 시스템 가이드, 사용법 매뉴얼, 공용 품질 문서 뷰어<br>*(예: CQ-BI User Guide)* |
| **`_60_`** | **Workplace** | 실무 담당자가 원천 데이터를 직접 수동 관리, 수정, 비교 분석, 로컬 임포트 및 매칭 등의 실무 처리를 수행하는 전용 작업장입니다. | 데이터 관리 실무자, Contributor | 로컬 데이터 임포트, 원천-로컬 비교 시뮬레이션, 수동 데이터 수정<br>*(예: IQM Plus Management)* |
| **`_70_`** | **Settings** | 시스템 운영 전반에 사용되는 글로벌 공통 코드, 데이터 맵핑 딕셔너리, 메타데이터 규격을 설정하고 보정하는 공간입니다. | 시스템 운영자, Admin | 메타데이터 맵핑 관리, 마스터 코드 관리, UI 글로벌 사전 제어<br>*(예: Metadata Manager)* |
| **`_80_`** | **Admin** | 사용자 인사 정보 관리, 권한 통제, 로컬 DB(SQLite) 관리, 데이터 테이블 탐색, 가이드 등 시스템 관리 전용 백오피스 공간입니다. | 시스템 총괄 관리자, Admin | 권한/인사 관리, 로컬 DB 관리자 도구, 에러 로그 모니터<br>*(예: SQLite Management, Personnel Management)* |
| **`_90_`** | **System** | 로그인/로그아웃, 전체 페이지 라우팅 제어 등 애플리케이션의 핵심 인프라 구동 및 보호를 수행하는 비기능적 시스템 공간입니다. | 시스템 (자동 처리 및 공통) | 로그인 화면, 전체 네비게이션 허브 등<br>*(예: Navigation)* |

---

## 3. 물리-논리 불일치 현황 및 개선 매핑 제안

현재 설정(`app/core/page/config_pages.py`)과 물리적 디렉토리(`app/pages/`) 구조를 정밀 분석한 결과, 아래와 같이 **물리적 위치와 논리 카테고리가 일치하지 않는 아키텍처 위배 사항**이 발견되었습니다. 이에 대해 정합성을 일치시키는 개선 맵핑을 아래와 같이 제안합니다.

### 1) "Individual Trend Analysis" 페이지
* **현황**: 
  * 물리 파일 경로: `app/pages/_80_admin/analysis_individual_page.py`
  * 설정 상 카테고리: `Analysis` (`_20_analysis/` 에 상응)
* **문제점**: 실무자의 품질 상세 트렌드 분석 화면이 관리자 백오피스(`_80_admin`) 폴더에 잘못 방치되어 있어 물리-논리 정합성이 깨집니다.
* **개선 제안**:
  * 물리 파일 이동: `app/pages/_80_admin/analysis_individual_page.py` -> `app/pages/_20_analysis/analysis_individual_page.py`
  * 설정 파일(`config_pages.py`) 내 경로를 신규 경로로 업데이트합니다.

### 2) "CQMS System Admin Guide" 페이지
* **현황**:
  * 물리 파일 경로: `app/pages/_50_user_guide/cqms_userguide_page.py`
  * 설정 상 카테고리: `Admin` (`_80_admin/` 에 상응)
* **문제점**: 일반 사용자들이 접근하는 가이드 폴더(`_50_user_guide`) 하위에 시스템 총괄 관리자(`Admin` 역할) 전용 가이드가 혼재되어 보안 및 격리 수준이 약화됩니다.
* **개선 제안**:
  * 물리 파일 이동: `app/pages/_50_user_guide/cqms_userguide_page.py` -> `app/pages/_80_admin/cqms_userguide_page.py`
  * 설정 파일(`config_pages.py`) 내 경로를 신규 경로로 업데이트합니다.

---

## 4. 소스 코드 수정 및 검증 계획 (Action Plan)

사용자 승인이 완료되면 즉시 다음 단계에 따라 물리 파일 이동 및 코드 수정을 진행합니다.

1. **물리 파일 안전 이동 (Git MV)**
   * `git mv app/pages/_80_admin/analysis_individual_page.py app/pages/_20_analysis/analysis_individual_page.py`
   * `git mv app/pages/_50_user_guide/cqms_userguide_page.py app/pages/_80_admin/cqms_userguide_page.py`
2. **네비게이션 설정 업데이트 (`app/core/page/config_pages.py`)**
   * 각 페이지의 `"filename"` 속성을 새로 이동된 경로로 정확히 수정합니다.
3. **무결성 검증 실행**
   * `/home/jumasi/miniconda3/envs/goeq/bin/python` 인터프리터를 사용하여 네비게이션 설정 유효성 검증 함수(`validate_all_configs()`)가 예외 없이 완벽하게 작동하는지 테스트합니다.
