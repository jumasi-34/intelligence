# skill/ (에이전트 자율 실행 단위 스킬 레이어)

이 디렉터리는 AI 에이전트가 자율적으로 실행할 수 있는 **단일 책임 단위 작업(Atomic Unit Task)** 파이썬 스크립트 도구를 보관하는 공간입니다.

---

## 1. 스킬 개발 및 문서화 표준

* **문서 슬림화 원칙 (Self-documenting Code)**:
  * 본 `README.md` 파일은 스킬의 존재 여부와 핵심 구동 명령만 간결히 보여주는 **인덱스(색인)** 역할만 수행합니다.
  * 아규먼트 설명, 입출력 포맷 등 상세 인터페이스 명세는 **개별 스크립트 소스코드 상단 Docstring 및 `--help` 명령어 출력**에 작성하여 관리합니다. 이를 통해 문서가 불필요하게 비대해지는 것을 방지합니다.
* **단위 설계 3대 제약**: **단일 책임**(Unit Task), **무상태성**(Stateless), **부작용 최소화**(Dry-run 지원).

---

## 2. 단위 스킬 인덱스 (Skill Catalog Index)

| 스킬 파일명 | 핵심 단위 작업 목적 (1줄 요약) | 기본 실행법 예시 |
| :--- | :--- | :--- |
| `skill_sql_static_analyzer.py` | SQL 쿼리 빌더의 5대 불변 규칙 정적 검사 | `python skill_sql_static_analyzer.py --sql-file path` |
| `skill_db_schema_loader.py` | 대상 DB 테이블의 물리 컬럼 구조 로드 | `python skill_db_schema_loader.py --table table_name` |
| `skill_data_profiler.py` | 전처리 데이터프레임의 결측치 및 통계적 요약 리포트 | `python skill_data_profiler.py --data-file path` |
| `skill_sync_agents.py` | 에이전트 레지스트리 기반 매니페스트 및 문서 일괄 동기화 | `python skill_sync_agents.py` |
