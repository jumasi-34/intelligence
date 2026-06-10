# GMES Rework Query Comparison Analysis Report (재작업 쿼리 비교 분석 보고서)

본 보고서는 `app/queries/gmes_query.py`의 `get_gmes_rework_general_rawdata` 함수와 `app/queries/q_iqm_plus.py`의 `get_query_rework_from_mes` 함수의 구조, 대상 테이블, 필터 방식 및 수량 집계 비즈니스 로직을 비교 분석하고, 기준 함수(`get_gmes_rework_general_rawdata`)에 맞춰 정렬하기 위한 개선안을 제시합니다.

---

## 1. 개요 및 목적
- **`get_gmes_rework_general_rawdata` (기준)**: 개별 규격/Lot 단위의 재작업(Rework) 부적합 rawdata를 조회하는 화면용 쿼리입니다.
- **`get_query_rework_from_mes`**: 상품품질완성도(IQM PLUS)용으로, 지정된 규격 및 기간에 대해 제품 출시(초기 양산) 이후의 시점별(30D, 60D, ... 365D) 집계 결과를 스테이징하기 위한 쿼리입니다.
- **분석 목적**: 집계용 쿼리(`get_query_rework_from_mes`)가 원시 rawdata를 조회하는 기준 쿼리(`get_gmes_rework_general_rawdata`)와 동일한 기준 테이블 및 부적합 필터링 정합성을 가지도록 차이점을 규명하고 정렬 방향을 도출합니다.

---

## 2. 핵심 차이점 분석 (Core Differences)

### ① 대상 품질/부적합 테이블의 불일치
* **기준 (`get_gmes_rework_general_rawdata`)**:
  - 완제품 부적합 결과 테이블인 **`hkt_dw.quality.qlt_f_lqlttr107`** (Finished Product Inspection Result)을 NCF 원천 테이블로 사용합니다.
* **비교 대상 (`get_query_rework_from_mes`)**:
  - GMES 재작업 부적합 raw 테이블인 **`hkt_dw.quality.qlt_f_lqltts112`** (`DatabricksTables.gmes_rework_defect_raw`)을 사용합니다.
* **영향**: 두 테이블은 수집 경로와 담고 있는 데이터 정합성 수준이 다를 수 있으며, 비즈니스 요건상 **`qlt_f_lqlttr107`**이 기준이 되어야 하므로 정렬이 필요합니다.

### ② 부적합 유형 코드 (INS_TP_CD) 및 필터 불일치
* **기준 (`get_gmes_rework_general_rawdata`)**:
  - 부적합 구분 코드로 **`["4", "8", "C", "H", "R", "V"]`**를 하드코딩하여 필터링합니다. (참고: 공통 비즈니스 상수의 `NCF_REWORK_CODES`는 `["4", "6", "8", "C", "D", "H", "V"]`이지만, 기준 함수는 해당 6개 코드를 엄밀하게 사용)
* **비교 대상 (`get_query_rework_from_mes`)**:
  - 부적합 코드를 세 가지 부문으로 분기하여 개별 CTE(`rework_overflow`, `rework_sect`, `rework_grnd`)에서 처리합니다:
    1. **OVERFLOW**: `INS_TP_CD = 'D'`
    2. **SECTION**: `INS_TP_CD = '4'`
    3. **GRINDING**: `INS_TP_CD = 'C'`
  - **불일치 세부사항**:
    - 기준 쿼리가 수집하는 **`['8', 'H', 'R', 'V']`** 등의 재작업 코드가 집계 쿼리에서는 완전히 누락되어 집계에서 누락됩니다.
    - 반대로, 집계 쿼리에서 수집하는 **`'D' (OVERFLOW)`** 코드는 기준 쿼리 필터(`["4", "8", "C", "H", "R", "V"]`)에 포함되어 있지 않습니다.

### ③ 수량 필드 (Quantity Column) 및 쿼리 구조
* **기준 (`get_gmes_rework_general_rawdata`)**:
  - `qlt_f_lqlttr107` 테이블의 단일 부적합 수량 컬럼인 **`DFT_QTY`**를 공통으로 조회하고 사용합니다. 따라서 별도의 Union 구조가 필요 없습니다.
* **비교 대상 (`get_query_rework_from_mes`)**:
  - `qlt_f_lqltts112` 테이블의 구조 특성상 부적합 유형에 따라 컬럼이 나뉘어 있어 이를 UNION ALL로 결합하고 있습니다:
    - OVERFLOW ('D'): **`DFT_QTY`** 사용
    - SECTION ('4'): **`SECT_QTY`** 사용
    - GRINDING ('C'): **`GRND_QTY`** 사용
* **단순화 가능성**: 만약 집계용 쿼리의 대상 테이블을 기준 테이블인 `qlt_f_lqlttr107`로 변경할 경우, 모든 수량이 **`DFT_QTY`** 필드에 일관되게 저장되므로 복잡한 세 방향 분기(`rework_overflow`, `rework_sect`, `rework_grnd`) 및 UNION ALL 구조를 완전히 제거하고 **단일 SELECT** 문으로 극적으로 단순화할 수 있습니다.

### ④ 최종 Unpivot 집계의 카테고리(`CAT`, `SUBCAT`) 처리
* **비교 대상 (`get_query_rework_from_mes`)**:
  - 개별 CTE 생성 시 `SUBCAT` 컬럼에 `'OVERFLOW'`, `'SECTION'`, `'GRINDING'`을 부여하지만, 정작 최종 집계를 수행하는 `table_aggregated` CTE 단계에서는:
    ```sql
    GROUP BY PLT_CD, PRD_CD, SPEC_CD, MIN_WRK_DATE, CAT
    ```
    로만 그룹바이(Group By)를 수행합니다. 즉, `SUBCAT`은 최종 집계 단계에서 누락 및 병합되며, 모든 수량은 `'REWORK' AS CAT` 하위에 단순 가산됩니다.
* **영향**: 따라서, 기준 테이블(`qlt_f_lqlttr107`)로 정렬하여 하나의 단일 쿼리로 `DFT_QTY`를 `SUM` 처리하더라도 집계 값의 차원은 완전히 정합합니다.

---

## 3. 요약 일람표 (Side-by-Side Comparison)

| 비교 항목 | 기준 함수 (`get_gmes_rework_general_rawdata`) | 집계 함수 (`get_query_rework_from_mes`) | 차이 분석 및 개선 방향 |
| :--- | :--- | :--- | :--- |
| **목적** | Lot별 개별 재작업 부적합 rawdata 조회 | 최초 양산 후 일차별(30D~365D) 누적 재작업 집계 | 용도 차이이나 원천 및 필터는 동기화 필요 |
| **원천 품질 테이블** | **`hkt_dw.quality.qlt_f_lqlttr107`**<br>(Finished Product Inspection) | **`hkt_dw.quality.qlt_f_lqltts112`**<br>(GMES Rework Defect Raw) | **[불일치]** 집계 함수를 기준 테이블인 `qlt_f_lqlttr107`로 변경해야 함 |
| **대상 재작업 코드** | `["4", "8", "C", "H", "R", "V"]` | `['D']` (Overflow), `['4']` (Sect), `['C']` (Grnd) | **[불일치]** 집계 함수에 기준 코드 목록을 적용 (`'D'` 제외, `['8', 'H', 'R', 'V']` 포함) |
| **수량 추출 필드** | `NCF.DFT_QTY` | `DFT_QTY`, `SECT_QTY`, `GRND_QTY` | **[불일치]** 기준 테이블 변경 시 `DFT_QTY` 단일 필드로 통일 가능 |
| **날짜 기준 및 필터** | `SUBSTRING(NCF.INS_DATE, 1, 8)` 대상 기간 직접 조회 | 최초 양산일(`MIN_WRK_DATE`) 기준 `+364일` 바운더리 내 `DATEDIFF` 계산 | 집계 목적상 기간 계산 방식 유지, 단 날짜 필터 타겟은 동일 적용 |
| **쿼리 복잡도** | 단일 Join 기반 조회 구조 | 3개 CTE UNION 후 Aggregation & Cross Join Unpivot | 불필요한 UNION 구조를 걷어내고 단일 쿼리로 최적화 가능 |

---

## 4. 정렬 제안 코드 (Alignment Proposal)

기준 함수(`get_gmes_rework_general_rawdata`)의 대상 테이블 및 필터 로직을 이식하여, 훨씬 명확하고 정합성이 높은 형태로 `get_query_rework_from_mes` 함수를 재설계한 제안 코드입니다.

### [개선된 `get_query_rework_from_mes` 구현안]

```python
def get_query_rework_from_mes(mcode_list_for_query: str | list[str]) -> str:
    """상품품질완성도(IQM PLUS) 재작업(Rework) 부적합 집계 쿼리를 생성합니다.
    
    get_gmes_rework_general_rawdata의 원천 테이블(qlt_f_lqlttr107) 및 
    부적합 코드 필터(["4", "8", "C", "H", "R", "V"])와 일관성을 유지하도록 정렬되었습니다.
    """
    mcode_clause = _format_mcode_list(mcode_list_for_query)
    
    # get_gmes_rework_general_rawdata 기준 재작업 부적합 유형 코드 목록
    rework_codes_str = ", ".join([f"'{c}'" for cls, c in [("str", x) for x in ["4", "8", "C", "H", "R", "V"]]])
    
    query = f"""--sql
        WITH
        prd AS (  -- M-Code 마스터
            SELECT PLT_CD, PRD_CD, SPEC_CD FROM {DatabricksTables.product_master}
            WHERE PRD_CD IN ({mcode_clause})
                AND STXC IN ('S', 'M', 'T')
                AND SPEC_CD LIKE 'KT%'
        ),
        -- 최종 양산 스펙
        SPEC_REV AS (
            SELECT
                prd.PLT_CD,
                prd.PRD_CD,
                prd.SPEC_CD,
                MIN(SPEC_REV.VLDT_SRT_DATE) AS MIN_VLDT_SRT_DATE
            FROM prd
            LEFT JOIN {DatabricksTables.spec_revision} AS SPEC_REV
                ON prd.PLT_CD = SPEC_REV.PLT_CD
                    AND prd.SPEC_CD = SPEC_REV.SPEC_CD
            WHERE SPEC_REV.STXC IN ('S', 'M', 'T')
            GROUP BY prd.PLT_CD, prd.PRD_CD, prd.SPEC_CD, SPEC_REV.STXC
        ),
        -- 양산 시작일 계산
        prdt_start_date AS (
            SELECT
                SPEC_REV.PLT_CD,
                SPEC_REV.PRD_CD,
                SPEC_REV.SPEC_CD,
                TO_DATE(MIN(prdt_start_date.WRK_DATE), 'yyyyMMdd') AS MIN_WRK_DATE
            FROM SPEC_REV
            LEFT JOIN {DatabricksTables.production_volume} AS prdt_start_date
                ON SPEC_REV.PLT_CD = prdt_start_date.PLT_CD
                    AND SPEC_REV.SPEC_CD = prdt_start_date.SPEC_CD
                    AND SPEC_REV.MIN_VLDT_SRT_DATE <= prdt_start_date.WRK_DATE -- 양산스펙 발행 이후 최초 양산 시작일
            GROUP BY SPEC_REV.PLT_CD, SPEC_REV.PRD_CD, SPEC_REV.SPEC_CD
        ),
        -- REWORK 부적합 원천 조회 (get_gmes_rework_general_rawdata 정렬 적용)
        rework_raw AS (
            SELECT
                psd.PLT_CD,
                psd.PRD_CD,
                psd.SPEC_CD,
                psd.MIN_WRK_DATE,
                'REWORK' AS CAT,
                NCF.DFT_QTY,
                TO_DATE(NCF.INS_DATE, 'yyyyMMdd') AS INS_DATE,
                DATEDIFF(TO_DATE(NCF.INS_DATE, 'yyyyMMdd'), psd.MIN_WRK_DATE) + 1 AS DATEDIFF
            FROM prdt_start_date AS psd
            -- 완제품 부적합 결과 테이블(qlt_f_lqlttr107) 조인
            LEFT JOIN {DatabricksTables.finished_product_inspection_result} AS NCF
                ON psd.PLT_CD = NCF.PLT_CD
                    AND psd.SPEC_CD = NCF.SPEC_CD
                    AND TO_DATE(NCF.INS_DATE, 'yyyyMMdd') BETWEEN psd.MIN_WRK_DATE AND DATE_ADD(psd.MIN_WRK_DATE, 364)
            WHERE NCF.INS_TP_CD IN ({rework_codes_str})
                AND NCF.DFT_QTY > 0
        ),
        table_aggregated AS (
            SELECT
                PLT_CD,
                PRD_CD,
                SPEC_CD,
                MIN_WRK_DATE,
                CAT,
                SUM(CASE WHEN DATEDIFF <= 30 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_30D,
                SUM(CASE WHEN DATEDIFF <= 60 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_60D,
                SUM(CASE WHEN DATEDIFF <= 90 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_90D,
                SUM(CASE WHEN DATEDIFF <= 180 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_180D,
                SUM(CASE WHEN DATEDIFF <= 270 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_270D,
                SUM(CASE WHEN DATEDIFF <= 365 THEN DFT_QTY ELSE 0 END) AS DFT_QTY_365D
            FROM rework_raw
            GROUP BY PLT_CD, PRD_CD, SPEC_CD, MIN_WRK_DATE, CAT
        ),
        periods AS (
            SELECT 30 AS days, '30D' AS PERIOD_NAME UNION ALL
            SELECT 60, '60D' UNION ALL SELECT 90, '90D' UNION ALL
            SELECT 180, '180D' UNION ALL SELECT 270, '270D' UNION ALL SELECT 365, '365D'
        )
        -- 최종 결과 : 집계한 부적합 수량을 Unpivot
        SELECT
            table_aggregated.PLT_CD,
            table_aggregated.PRD_CD,
            table_aggregated.SPEC_CD,
            table_aggregated.MIN_WRK_DATE,
            table_aggregated.CAT,
            periods.PERIOD_NAME,
            COALESCE(
                CASE periods.PERIOD_NAME
                    WHEN '30D' THEN table_aggregated.DFT_QTY_30D
                    WHEN '60D' THEN table_aggregated.DFT_QTY_60D
                    WHEN '90D' THEN table_aggregated.DFT_QTY_90D
                    WHEN '180D' THEN table_aggregated.DFT_QTY_180D
                    WHEN '270D' THEN table_aggregated.DFT_QTY_270D
                    WHEN '365D' THEN table_aggregated.DFT_QTY_365D
                END, 0
            ) AS DFT_QTY
        FROM table_aggregated
        CROSS JOIN periods
        ORDER BY table_aggregated.PRD_CD, table_aggregated.CAT, periods.days
        """
    return query
```

### [주요 개선 성과 및 이점]
1. **정합성 확보**: 기준이 되는 `get_gmes_rework_general_rawdata`와 동일한 부적합 테이블(`qlt_f_lqlttr107`) 및 재작업 코드 필터(`["4", "8", "C", "H", "R", "V"]`)를 적용함으로써 개별 상세 데이터와 기간별 누적 집계값 사이의 데이터 싱크가 일치하게 됩니다.
2. **복잡도 감소**: 3개의 개별 부적합 유형별 CTE 생성 및 이들을 `UNION ALL`로 묶던 비효율적이고 복잡한 구조를 단일 `rework_raw` 조회 및 집계 구조로 간소화하여 쿼리 성능이 개선되고 코드 가독성 및 유지보수성이 크게 증가했습니다.
3. **유지보수 단일 지점화**: 부적합 코드를 `rework_codes_str` 리스트 변수 기반으로 동적 생성하여 추후 재작업 코드가 변경되거나 추가될 때 기민하고 안전하게 대처가 가능합니다.
