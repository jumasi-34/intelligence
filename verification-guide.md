# verification-guide.md (코드 무결성 및 문법 검증 가이드)

이 문서는 이 프로젝트에서 작성되는 모든 파이썬 파일의 구문 정합성, 인덴트 구조, 문법 무결성을 안전하게 검증하기 위한 **검증 명령어 가이드라인**입니다.

---

## 1. 검증 도구 개요 (`verify_code.py`)

기존 프로덕션 코드를 보호하고, 신규 생성하는 인텔리전스 에이전트 레이어(`intelligence/`)나 독립 테스트 하네스(`tests/`) 소스 코드에 잠재적인 `SyntaxError`, `IndentationError` 등이 포함되지 않았는지 점검하기 위해 **표준 라이브러리 기반 정적 분석 스크립트**를 도입했습니다.

- **위치**: [tests/verify_code.py](file:///home/jumasi/workstation/tests/verify_code.py)
- **핵심 아키텍처**:
  - **`py_compile.compile`**: 파이썬 파일을 물리적으로 가상 컴파일하여, 인덴트 불일치나 인터프리터 수준의 구문 에러를 1차 필터링합니다.
  - **`ast.parse`**: 추상 구문 트리(Abstract Syntax Tree) 분석을 수행하여 문법적 무결성 및 코드의 구조적 정밀도를 검사합니다.
  - **Zero-Dependency**: 외부 패키지 설치 없이 파이썬 표준 라이브러리만으로 즉시 동작하므로 속도가 극도로 빠르며, 의존성 충돌 위험이 전혀 없습니다.

---

## 2. 실행 명령어 및 사용 가이드

모든 명령어는 가상환경 파이썬 인터프리터 경로(`/home/jumasi/miniconda3/envs/goeq/bin/python`) 및 루트 디렉터리를 포함한 `PYTHONPATH` 설정을 필요로 합니다.

### 1) 프로젝트 전체 파이썬 파일 일괄 검증 (Full Verification)
프로젝트 전체(제외 폴더 제외)의 모든 파이썬 파일을 신속하게 탐색하여 무결성을 진단합니다.
```bash
PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py
```

### 2) 신규 인텔리전스 폴더만 집중 검증 (Targeted Verification)
우리가 새로 개발하고 있는 `intelligence/` 디렉터리 내부 파일들만 타겟 지정해 신속하게 검사합니다.
```bash
PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py intelligence/
```

### 3) 특정 소스 파일 1개만 정밀 단독 검증 (Single File Verification)
지정된 파일 1개만 정밀 검사합니다.
```bash
PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py app/service/cqms_df.py
```

---

## 3. 검증 통과 가이드 및 조치 사항

- **성공 시 (`Passed`)**:
  터미널에 초록색 `[통과] PASSED` 표시와 함께 정상 보고됩니다. 안심하고 자율적인 다음 테스트 주기로 나아갈 수 있습니다.
- **실패 시 (`Failed`)**:
  터미널에 빨간색 `[실패] FAILED` 문구와 함께 **에러가 발생한 파일명, 라인 번호, 상세 에러 트레이스백, 그리고 해당 에러 라인의 코드 스니펫**이 시각적으로 즉각 표시됩니다.
  - 개발자는 검증 결과를 확인하고 해당 에러 라인 위치의 오타, 인덴트 구조, 혹은 문법 오류를 올바르게 디버깅해야 합니다.

---

## 4. 추가적인 정적 분석 (Type Checking & Linting)

가상환경 내에서 엄격한 타입 체킹이나 추가적인 코드 스타일 분석을 병행하려는 경우 다음 옵션들을 실행할 수 있습니다.

* **엄격한 정적 타입 검증 (mypy)**:
  가상환경에 `mypy`가 필요하다면 가상환경 pip로 설치한 뒤, 아래와 같이 특정 폴더를 검사합니다.
  ```bash
  /home/jumasi/miniconda3/envs/goeq/bin/python -m pip install mypy
  /home/jumasi/miniconda3/envs/goeq/bin/python -m mypy intelligence/
  ```
