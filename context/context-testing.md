# context-testing.md (테스트 격리 격벽 및 공통 테스트 맥락 설계서)

이 문서는 AI 에이전트(`Test Writer Agent` 등)가 안전하게 테스트 코드를 설계 및 기동하고, 원천 데이터베이스의 통신 오버헤드 없이 인메모리 상에서 격리 테스트를 수행할 수 있도록 지원하는 **공통 테스트 템플릿 및 스키마 맥락(Context)**입니다.

---

## 1. 테스트 격리 원칙 (Test Isolation & Guardrails)

프로덕션 환경의 안정성과 비용 수호를 위해 모든 테스트 파일은 다음 원칙을 절대 엄수하여 작성해야 합니다.

1. **원천 DB 통신 차단**: 테스트 실행 시 Databricks, Oracle 등의 실 물리 데이터베이스 커넥션을 맺어서는 안 됩니다.
2. **인메모리 모의(Mocking) 객체 활용**: `unittest.mock`을 적극 활용하여 데이터베이스 클라이언트의 `.execute()` 호출 시 정해진 가상의 Pandas DataFrame을 반환하도록 설계해야 합니다.
3. **영속성 보존**: SQLite 관련 DML 테스트 시에는 실제 사용자 세션 로그(`log.db`)나 스테이징 데이터(`staging.db`)를 훼손하지 않도록 가상의 인메모리 SQLite 커넥션을 사용합니다.

---

## 2. 데이터베이스 모의 객체 모범 템플릿 (Mocking Pattern)

에이전트가 새 테스트를 작성할 때 복사해서 사용할 수 있는 **데이터베이스 클라이언트 모사 템플릿**입니다.

```python
import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from core.params.parameters import BaseFilterParams

# 테스트 대상 서비스 모듈 (예시: CQMS 데이터 전처리)
from service.cqms_df import preprocessing_qi_general_rawdata

class TestCQMSPreprocessingRegression(unittest.TestCase):

    @patch("core.operate.db_client.get_client")
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

---

## 3. 핵심 비즈니스 데이터 골든 스키마 규격 (Golden Schema)

가상 데이터를 작성할 때 에이전트가 길을 잃지 않도록, 각 도메인별 핵심 데이터의 원시 스펙 명세를 규정해 둡니다.

### 1) CQMS (고객 품질 이슈)
- **필수 키 컬럼**: `PLANT` (공장), `MCODE` (자재코드), `REG_DATE` (등록일), `QI_CNT` (불량 건수), `SUPP_QTY` (납품 수량)
- **비즈니스 수식**: `OEQI = QI_CNT / SUPP_QTY * 1,000,000`

### 2) GMES (생산 품질 데이터 - NCF 불합격)
- **필수 키 컬럼**: `PLANT`, `WORK_DATE`, `NCF_CNT` (불합격 수량), `PROD_QTY` (생산 수량)
- **비즈니스 수식**: `NCF_RATE = NCF_CNT / PROD_QTY * 100` (%)

---

## 4. 테스트 하네스 기동 방법

에이전트가 새로운 회귀/골든 테스트를 `tests/` 하위에 작성한 뒤, 해당 테스트가 문법적 결함 없이 온전히 통과하는지 CLI 상에서 자율 검증할 때는 아래 명령어를 콘텍스트로 참조하여 수행합니다.

```bash
# 특정 신규 테스트 파일 단독 기동 검증
PYTHONPATH=/home/jumasi/workstation /home/jumasi/miniconda3/envs/goeq/bin/python -m unittest tests/test_cqms_regression.py
```
