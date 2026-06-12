# testing-verification.md (테스트 격리 및 코드 무결성 검증 통합 가이드)

이 문서는 시스템의 안정적인 작동을 유지하기 위하여 개발자 및 AI 에이전트가 안전하게 테스트 코드를 설계 및 기동하고, 물리 데이터베이스 통신 없이 독립 격리 테스트를 수행하며, 표준 라이브러리 기반 정적 분석 스크립트를 통해 소스 코드 무결성을 검증하는 지침을 제공합니다.

---

## 1. 테스트 격리 원칙 (Test Isolation & Guardrails)

프로덕션 환경의 안정성과 비용 수호를 위해 모든 테스트 파일은 다음 원칙을 절대 엄수하여 작성해야 합니다.

* **원천 DB 통신 차단**: 테스트 실행 시 Databricks, Oracle 등의 실 물리 데이터베이스 커넥션을 맺어서는 안 됩니다.
* **인메모리 모의(Mocking) 객체 활용**: `unittest.mock`을 적극 활용하여 데이터베이스 클라이언트의 `.execute()` 호출 시 정해진 가상의 Pandas DataFrame을 반환하도록 설계해야 합니다.
* **영속성 보존**: SQLite 관련 DML 테스트 시에는 실제 사용자 세션 로그(log.db)나 스테이징 데이터(staging.db)를 훼손하지 않도록 가상의 인메모리 SQLite 커넥션을 사용합니다.

---

## 2. 데이터베이스 모의 객체 템플릿 (Mocking Pattern)

에이전트가 새 테스트를 작성할 때 활용할 수 있는 데이터베이스 클라이언트 모사 템플릿입니다.

```python
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from core.params.parameters import BaseFilterParams

# 테스트 대상 서비스 모듈 (예시: CQMS 데이터 전처리)
from service.cqms_df import preprocessing_qi_general_rawdata

class TestCQMSPreprocessingRegression(unittest.TestCase):

    @patch("core.db.client.get_client")
    def test_golden_path_qi_preprocessing(self, mock_get_client):
        """CQMS 품질 이슈 가공 로직에 대한 골든 시나리오 테스트"""

        # 1. Mock DB 클라이언트 및 가상 DataFrame 설계
        mock_client = MagicMock()
        mock_get_client.return_value = mock_client

        # Databricks에서 내려오는 원시 데이터셋 완벽 모사 (Golden Schema)
        mock_raw_data = {
            "PLANT": ["KP", "DP", "IP"],
            "MCODE": ["MC001", "MC002", "MC003"],
            "REG_DATE": ["2024-01-01", "2024-01-02", "2024-01-03"],
            "QI_CNT": [5, 10, 0],
            "SUPP_QTY": [10000, 20000, 5000]
        }
        mock_df = pd.DataFrame(mock_raw_data)

        # 클라이언트의 .execute() 실행 시 가상 DataFrame이 즉각 반환되도록 패치
        mock_client.execute.return_value = mock_df

        # 2. 파라미터 데이터클래스를 통한 테스트 실행
        params = BaseFilterParams(
            plant_list=["KP", "DP", "IP"],
            mcode_list=["MC001", "MC002"]
        )

        # 실제 비즈니스 가공 함수 실행 (실제 DB를 찌르지 않고 가상 Mock을 경유)
        processed_df = preprocessing_qi_general_rawdata(params=params)

        # 3. 비즈니스 계산 정합성 및 스키마 검증 (Assertion)
        self.assertIsNotNone(processed_df)
        self.assertFalse(processed_df.empty)
        self.assertIn("OEQI", processed_df.columns)  # 수식 연산에 의한 새 컬럼 추가 검증

        # OEQI 공식: QI_CNT / SUPP_QTY * 1,000,000
        # KP 공장 OEQI 기대치 = 5 / 10000 * 1_000_000 = 500.0
        expected_oeqi = (5 / 10000) * 1000000
        self.assertAlmostEqual(processed_df.loc[0, "OEQI"], expected_oeqi)

if __name__ == "__main__":
    unittest.main()
```

### 테스트 하네스 단독 기동 방법
```bash
PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python -m unittest tests/test_cqms_regression.py
```

---

## 3. 핵심 비즈니스 데이터 골든 스키마 규격 (Golden Schema)

가상 데이터를 작성할 때 참고할 각 도메인별 핵심 데이터의 원시 스펙 명세입니다.

### (1) CQMS (고객 품질 이슈)
* **필수 키 컬럼**: `PLANT` (공장), `MCODE` (자재코드), `REG_DATE` (등록일), `QI_CNT` (불량 건수), `SUPP_QTY` (납품 수량)
* **비즈니스 수식**: `OEQI = QI_CNT / SUPP_QTY * 1,000,000`

### (2) GMES (생산 품질 데이터 - NCF 불합격)
* **필수 키 컬럼**: `PLANT`, `WORK_DATE`, `NCF_CNT` (불합격 수량), `PROD_QTY` (생산 수량)
* **비즈니스 수식**: `NCF_RATE = NCF_CNT / PROD_QTY * 100` (%)

---

## 4. 코드 무결성 검증 도구 및 사용법 (verify_code.py)

기존 프로덕션 코드를 보호하고, 신규 생성하는 인텔리전스 에이전트 레이어(`intelligence/`)나 독립 테스트 하네스(`tests/`) 소스 코드에 잠재적인 구문 오류(`SyntaxError`, `IndentationError`)가 포함되지 않았는지 점검하기 위해 표준 라이브러리 기반 정적 분석 스크립트를 도입하여 활용합니다.

* **스크립트 주소**: tests/verify_code.py
* **핵심 아키텍처**:
  * **py_compile.compile**: 파이썬 파일을 가상 컴파일하여, 인덴트 불일치나 인터프리터 수준의 구문 에러를 1차 필터링합니다.
  * **ast.parse**: 추상 구문 트리(Abstract Syntax Tree) 분석을 수행하여 문법적 무결성 및 코드의 구조적 정밀도를 검사합니다.
  * **Zero-Dependency**: 외부 패키지 설치 없이 파이썬 표준 라이브러리만으로 즉시 동작하므로 속도가 빠르고, 의존성 충돌 위험이 전혀 없습니다.

### (1) 실행 명령어 가이드
모든 명령어는 가상환경 파이썬 인터프리터 경로 및 루트 디렉터리를 포함한 `PYTHONPATH` 설정을 필요로 합니다.

* **프로젝트 전체 파이썬 파일 일괄 검증 (Full Verification)**
  ```bash
  PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py
  ```
* **인텔리전스 폴더만 집중 검증 (Targeted Verification)**
  ```bash
  PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py intelligence/
  ```
* **특정 소스 파일 1개만 정밀 단독 검증 (Single File Verification)**
  ```bash
  PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python tests/verify_code.py app/service/cqms_df.py
  ```

### (2) 검증 통과 및 조치 가이드
* **성공 시 (Passed)**: 터미널에 `[통과] PASSED` 표시가 출력됩니다. 구문 문법상 결함이 없음을 검증 완료한 상태입니다.
* **실패 시 (Failed)**: 터미널에 `[실패] FAILED` 문구와 함께 **에러 발생 파일명, 라인 번호, 상세 트레이스백, 그리고 해당 라인의 코드 스니펫**이 시각적으로 표시됩니다. 즉시 지시된 에러 라인 위치를 확인하여 오타, 인덴트 결함 등을 해결해야 합니다.

### (3) 추가 정적 타입 분석 (mypy)
가상환경 내에서 엄격한 타입 체킹이나 스타일 분석을 병행하려는 경우 다음 옵션을 수행할 수 있습니다.
```bash
/home/jumasi/miniconda3/envs/goeq/bin/python -m pip install mypy
/home/jumasi/miniconda3/envs/goeq/bin/python -m mypy intelligence/
```
