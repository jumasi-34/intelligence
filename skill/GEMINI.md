# GEMINI.md (skill/ 로컬 가이드라인 및 인덱스)

이 문서는 `intelligence/skill/` (에이전트 자율 실행 단위 스킬 레이어) 고유의 로컬 규칙과 보유 파일 정보를 신속히 인지하기 위한 마이크로 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **단 단위 작업의 격리**: 각 스킬은 오직 하나의 단위 작업(Atomic Unit Task)만 완결성 있게 수행해야 합니다. 복합적인 작업 설계는 철저히 지양합니다.
* **무상태성 및 부작용 방지**: 스킬은 실행 시 디스크에 상태를 남기지 않으며, 모든 조건은 아규먼트로 입력받고 표준 출력(`stdout`)으로 JSON 등을 반환합니다. 쓰기 작업 수반 시 `--dry-run`을 필수적으로 지원해야 합니다.
* **코드 인덱스 동기화**: 신규 스킬이 추가되거나 명세가 바뀔 시, 본 폴더 내의 `README.md` 내 인덱스를 갱신해야 합니다.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `README.md` | 단위 스킬 개발 가이드라인 및 스킬 검색용 미니 인덱스 |
| `skill_sync_agents.py` | 에이전트 레지스트리 데이터를 바탕으로 매니페스트 및 문서를 자동 정비하는 스킬 |
| *(구현 대기)* `skill_sql_static_analyzer.py` | SQL 쿼리 빌더가 반환하는 문법 및 5대 불변 규칙 정적 검사기 스킬 |
| *(구현 대기)* `skill_db_schema_loader.py` | Databricks, Oracle 등 원천 운영 디비의 테이블 스키마 및 컬럼 정보 로더 스킬 |
| *(구현 대기)* `skill_data_profiler.py` | 가공 완료된 데이터프레임의 결측치 및 통계적 수치 분포 리포팅 스킬 |

---

## 3. 변경 이력 (Changelog)

* **2026-06-14**:
  * [Feat] 에이전트와 스킬 역할 분리를 위해, 기존 `agent/sync_agents.py`를 본 폴더 아래 [skill_sync_agents.py](file:///home/jumasi/workstation/intelligence/skill/skill_sync_agents.py)로 성공적으로 경로 및 Shebang을 정렬하여 이관 완료.
  * [Feat] 스킬 폴더 전용 `GEMINI.md` 마이크로 가이드라인 최초 수립 및 비치.
