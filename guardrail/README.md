# guardrail/ (품질 및 규정 준수 가드레일 레이어)

이 디렉터리는 프로젝트 및 인텔리전스 레이어 전반의 품질을 제어하기 위한 **실행 가능 검사기(Rule Engine) 및 코드/데이터 분석기**를 보관하는 공간입니다.

이곳에 정의된 스크립트들은 `hook/` 산하의 Git Hook 트리거에 의해 자동으로 실행되어 위반 사항이 있을 경우 커밋이나 푸시를 엄격하게 차단합니다.

---

## 1. 가드레일 개발 및 배치 원칙

* **검사기 책임의 분리**: 하나의 검사기 스크립트는 하나의 특정 규칙(Rule) 또는 일련의 규칙 세트 검사에 집중합니다. (예: `emoji_checker.py`, `sqlite_schema_validator.py`)
* **Exit Code 표준 규칙**:
  * **`0`**: 검사 통과 (Success)
  * **`1` 이상**: 규칙 위반 감지 및 실패 (Failure). 에러 내용과 위반된 파일/라인 정보를 표준 출력(`stdout`) 또는 표준 에러(`stderr`)로 상세히 출력해야 합니다.
* **무소음 원칙 (Quiet Mode 지원)**: 자동화 빌드 시 불필요한 출력을 줄이고 성능을 극대화하기 위해 `--quiet` 옵션을 필수 제공해야 합니다.

---

## 2. 가드레일 목록 및 연동 스펙

| 가드레일 스크립트 | 대상 검사 범위 | 연동되는 훅 (`hook/`) | 비고 |
| :--- | :--- | :--- | :--- |
| *(작성 예정)* | 이모지 사용 전면 금지 검사 | `pre-commit` | 소스 및 마크다운 내 유니코드 이모지 스캔 |
| *(작성 예정)* | 골든 스키마 위반 탐지 | `pre-push` | SQLite DB 테이블 구조 정합성 검증 |
| *(작성 예정)* | 한국어 커밋 메시지 검사 | `commit-msg` | 커밋 메시지 규칙 준수 여부 판별 |

---

## 3. 검사기 작성 예시 (템플릿)

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
