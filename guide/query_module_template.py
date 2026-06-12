"""
[TEMPLATE] 쿼리 모듈 표준 템플릿 (app/queries/*_query.py)

- 작성일: 2026-06-12
- 작성자: Antigravity AI
- 설명: 쿼리 모듈 생성 시 일관성을 확보하고 빠르게 뼈대를 잡기 위한 파이썬 모듈 템플릿입니다.
  본 템플릿을 복사하여 신규 쿼리 모듈의 기본 베이스라인으로 활용하십시오.
"""

# =========================================================================
# SECTION 1. Imports & Config (필수 라이브러리 및 쿼리 헬퍼, 테이블 변수 임포트)
# =========================================================================
from dataclasses import dataclass
from typing import List, Optional

# 실제 프로젝트 개발 시 아래와 같이 필수 공통 모듈들을 임포트합니다.
# from app.core.params.parameters import BaseFilterParams  # 예시
# from app.core.query.query_database import DatabricksTables, OracleTables
# from app.core.query.query_helper import QueryFilter, SQLConverter

# 💡 [참고] 테스트 검증 및 템플릿 독립 동작을 위한 임시/Mock 정의 (실제 모듈 생성 시 제거)
@dataclass
class TemplateFilterParams:
    start_date: str
    end_date: str
    plant_list: List[str]
    mcode_list: Optional[List[str]] = None
    status_filter: Optional[bool] = False

class DatabricksTables:
    cqms_qi_main = "hkt_system_dw.eqms.cqms_quality_issue"
    cqms_qi_mcode = "hkt_system_dw.eqms.cqms_quality_mcode"
    gmes_spec_product_master = "hkt_dw.specification.mas_d_lmastr101"
    ctms_ctl_result_raw = "hkt_system_dw.ctms.ctms_result_data"

class QueryFilter:
    @staticmethod
    def where_in(column: str, values: Optional[List[str]]) -> Optional[str]:
        if not values:
            return None
        formatted_values = ", ".join([f"'{v}'" for v in values])
        return f"{column} IN ({formatted_values})"

    @staticmethod
    def where_date_between(start: str, end: str, column: str) -> Optional[str]:
        return f"{column} BETWEEN '{start}' AND '{end}'"

    @staticmethod
    def build_where(conditions: List[Optional[str]]) -> str:
        valid_conds = [c for v in conditions if (c := v) is not None]
        if not valid_conds:
            return ""
        return "WHERE " + " AND ".join(valid_conds)


# =========================================================================
# SECTION 2. Style A: 단순 조회 및 단일 테이블 마스터형 (Simple Master Target)
# =========================================================================
# - 규칙: JOIN이 없거나 조건문이 극히 단순한 기준 정보, 마스터 테이블 조회용
# - 함수명: get_{system}_{domain}_{조건/설명/general}_{agg/rawdata} 공식 준수
# - (예: system=gmes, domain=spec, 조건=product_master, rawdata 타입)
# =========================================================================

def get_gmes_spec_product_master(params: TemplateFilterParams) -> str:
    """
    제품 사양 마스터 정보 조회 쿼리 (Style A)
    """
    # 1) 조건절 조립
    conditions = [
        QueryFilter.where_in("M_CODE", params.mcode_list)
    ]
    where_clause = QueryFilter.build_where(conditions)
    
    # 2) 최종 SQL 문자열 조립 및 반환 (f-string & --sql 주석 활용)
    query = f"""--sql
    SELECT 
        M_CODE,
        M_NAME,
        SPEC_LOWER,
        SPEC_UPPER,
        UPDATE_DT
    FROM {DatabricksTables.gmes_spec_product_master}
    {where_clause}
    ORDER BY M_CODE ASC;
    """
    return query


# =========================================================================
# SECTION 3. Style B: 다중 조인 및 가변 필터형 (Dynamic Multi-Join Target)
# =========================================================================
# - 규칙: 복수 테이블 JOIN 및 사용자 조건 입력 유무에 따른 동적 WHERE절 결합
# - 함수명: get_{system}_{domain}_{조건/설명/general}_{agg/rawdata} 공식 준수
# - (예: system=cqms, domain=qi, 설명=mttc_defect, rawdata 타입)
# =========================================================================

def get_cqms_qi_mttc_defect_rawdata(params: TemplateFilterParams) -> str:
    """
    품질 이슈 MTTC 불량 원시 데이터 조회 쿼리 (Style B)
    """
    # 1) 조건 리스트 캡슐화 (conditions 복수 명사 사용 일관화)
    conditions = [
        QueryFilter.where_in("QI.PLANT", params.plant_list),
        QueryFilter.where_date_between(params.start_date, params.end_date, "QI.REG_DATE"),
        # 특정 조건 만족 시에만 동적 바인딩
        QueryFilter.where_in("QI.STATUS", ["On-going"]) if params.status_filter else None
    ]
    where_clause = QueryFilter.build_where(conditions)
    
    # 2) 최종 SQL 문자열 조립 및 반환 (가독성 높은 정렬 준수)
    query = f"""--sql
    SELECT 
        QI.SEQ,
        QI.PLANT,
        QI.STATUS,
        QI.REG_DATE,
        M.M_CODE,
        M.DEFECT_QTY
    FROM {DatabricksTables.cqms_qi_main} QI
    INNER JOIN {DatabricksTables.cqms_qi_mcode} M 
        ON QI.SEQ = M.CQMS_QUALITY_ISSUE_SEQ
    {where_clause}
    ORDER BY QI.REG_DATE DESC, QI.SEQ DESC;
    """
    return query


# =========================================================================
# SECTION 4. Style C: 대규모 CTE 구조화형 (Complex CTE-Structured Target)
# =========================================================================
# - 규칙: 서브 쿼리를 외부 함수나 파일로 분리하지 않고, WITH문 단일 SQL로 통합 조립
# - 함수명: get_{system}_{domain}_{조건/설명/general}_{agg/rawdata} 공식 준수
# - (예: system=ctms, domain=ctl, 설명=daily_window, agg 집계 타입)
# =========================================================================

def get_ctms_ctl_daily_window_agg(params: TemplateFilterParams) -> str:
    """
    CTMS 일자별 통계 및 윈도우 순위 집계 쿼리 (Style C)
    """
    # 1) 조건절 사전 수립
    conditions = [
        QueryFilter.where_in("PLANT", params.plant_list),
        QueryFilter.where_date_between(params.start_date, params.end_date, "MRM_DATE")
    ]
    where_clause = QueryFilter.build_where(conditions)
    
    # 2) 단일 Full Query 문자열 내에 CTE 계층 수렴 조립 (쪼개기 절대 금지)
    query = f"""--sql
    WITH base_mrm AS (
        SELECT 
            DOC_NO, 
            PLANT, 
            TO_DATE(MRM_DATE, 'yyyyMMdd') AS MRM_DATE,
            VAL_1,
            VAL_2
        FROM {DatabricksTables.ctms_ctl_result_raw}
        {where_clause}
    ),
    calculated_stats AS (
        SELECT 
            PLANT,
            MRM_DATE,
            COUNT(DOC_NO) AS TOTAL_CNT,
            AVG(VAL_1) AS AVG_VAL_1,
            SUM(VAL_2) AS SUM_VAL_2
        FROM base_mrm
        GROUP BY PLANT, MRM_DATE
    ),
    ranked_stats AS (
        SELECT 
            PLANT,
            MRM_DATE,
            TOTAL_CNT,
            AVG_VAL_1,
            SUM_VAL_2,
            ROW_NUMBER() OVER(PARTITION BY PLANT ORDER BY AVG_VAL_1 DESC) AS RANK_IDX
        FROM calculated_stats
    )
    SELECT 
        PLANT,
        MRM_DATE,
        TOTAL_CNT,
        AVG_VAL_1,
        SUM_VAL_2,
        RANK_IDX
    FROM ranked_stats
    WHERE RANK_IDX <= 10
    ORDER BY PLANT ASC, AVG_VAL_1 DESC;
    """
    return query
