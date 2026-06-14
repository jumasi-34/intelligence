# GEMINI.md (guardrail/ 로컬 가이드라인 및 인덱스)

이 문서는 `intelligence/guardrail/` (추상 정책 및 무결성 검증 룰 엔진 레이어) 고유의 로컬 규칙과 파일 정보를 신속히 인지하기 위한 마이크로 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **Exit Code 엄수**: 가드레일 실행 엔진으로서 검사 통과 시에는 반드시 `sys.exit(0)`, 정책 위반이나 검사 실패 시에는 `sys.exit(1)` 이상을 반환해야 합니다.
* **입출력 독립성 (Interface Isolation)**: 검사기는 CLI, Git, API, DB 트리거 등 가동 매체(Trigger Interface)에 독립적이어야 합니다. 특정 타겟을 직접 변경하거나 입력을 임의 파싱하지 않고, 원천 대상 컨텍스트를 인자로 전달받아 검사만 수행해야 합니다.
* **에러 표준 출력 (Standard Error Output)**: 검사 실패 시에는 위반 사유, 규칙 메타데이터, 구체적 위반 위치(라인/필드)를 `stdout` 또는 `stderr`로 상세히 출력해야 합니다.
* **무소음 지원 (Quiet Mode)**: 파이프라인 성능 보존 및 배치 실행 시 조용한 연동을 위해 세부 분석 로그를 생략하고 결과 코드만 신속히 판단하도록 돕는 `--quiet` (또는 `-q`) 옵션을 항시 지원해야 합니다.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `emoji_checker.py` | 소스코드 및 문서 자산 내 유니코드 이모지 탑재 위반 여부를 검증하는 무결성 검사기 |
| `schema_validator.py` | 구조 자산(SQLite, Databricks 등)이 골든 정합 스키마 표준에 부합하는지 비교하는 정적 검사기 |
| `commit_msg_validator.py` | 표준 Git 커밋 태그 및 한국어 작성 정책 무결성을 판단하는 검사기 |


---

## 3. 검사기 작성 예시 (Template)

가드레일 검사기는 아래와 같이 실패 시 비정상 종료 코드(`sys.exit(1)`)를 반환하도록 작성해야 합니다.

```python
#!/home/jumasi/miniconda3/envs/goeq/bin/python
# -*- coding: utf-8 -*-
import sys

def run_check():
    # 1. 검사 대상 로직 수행
    violation_found = False
    
    # 2. 규칙 위반 시 에러 출력 및 sys.exit(1)
    if violation_found:
        print("[ERROR] 규정 위반이 감지되었습니다.")
        sys.exit(1)
        
    # 3. 통과 시 정상 종료
    print("[SUCCESS] 가드레일 통과")
    sys.exit(0)

if __name__ == "__main__":
    run_check()
```

---

## 4. 변경 이력 (Changelog)

* **2026-06-14**:
  * [REFACTOR] 하위폴더 중복 `README.md` 제거 수칙에 맞춰 가이드라인 통합 및 `README.md` 참조 제거.
  * [REFACTOR] `guardrail/` 레이어 정의를 단순 코드 정적 분석에서 '추상 정책 및 무결성 검증 룰 엔진'으로 승격하고, 입출력 독립성 및 아키텍처 가이드라인을 로컬 규칙에 추가.
  * [Feat] 가드레일 폴더 전용 `GEMINI.md` 최초 비치.
