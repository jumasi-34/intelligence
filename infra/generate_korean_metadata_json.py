import os
import re
import json
import sqlite3

# 파일 경로 정의
workspace_dir = "/home/jumasi/workstation"
query_db_py_path = f"{workspace_dir}/app/core/query/query_database.py"
biz_constants_json_path = f"{workspace_dir}/app/core/constants/business_constants.json"
output_json_path = f"{workspace_dir}/app/core/query/query_tables_metadata.json"
output_md_path = f"{workspace_dir}/intelligence/infra/database-metadata.md"

sqlite_db_paths = {
    "log": os.path.expanduser("~/database/log.db"),
    "staging": os.path.expanduser("~/database/staging.db"),
    "ops": os.path.expanduser("~/database/ops.db"),
}

# 비즈니스 상수 로드
try:
    with open(biz_constants_json_path, "r", encoding="utf-8") as f:
        BIZ_CONSTANTS = json.load(f)
except Exception as e:
    print(f"[MetadataGenerator] 비즈니스 상수 파일 로드 실패: {e}")
    BIZ_CONSTANTS = {}

# 공통 컬럼 메타 사양 정의 (Alias 추천 및 카테고리)
COMMON_COLUMN_META = {
    "PLANT": {"alias": "plant_code", "category": "공장코드", "constants_key": "PLANT_CODE_MAPPING_DICT"},
    "PLT_CD": {"alias": "plant_code", "category": "공장코드", "constants_key": "PLANT_CODE_MAPPING_DICT"},
    "PLANT_CD": {"alias": "plant_code", "category": "공장코드", "constants_key": "PLANT_CODE_MAPPING_DICT"},
    "WERKS": {"alias": "plant_code", "category": "공장코드", "constants_key": "PLANT_CODE_MAPPING_DICT"},
    
    "M_CODE": {"alias": "material_code", "category": "자재코드", "constants_key": None},
    "PRD_CD": {"alias": "material_code", "category": "자재코드", "constants_key": None},
    "SPEC_CD": {"alias": "spec_code", "category": "규격코드", "constants_key": None},
    
    "BARCODE_NO": {"alias": "barcode_no", "category": "바코드번호", "constants_key": None},
    "BARCD_NO": {"alias": "barcode_no", "category": "바코드번호", "constants_key": None},
    "ZBARCODE": {"alias": "barcode_no", "category": "바코드번호", "constants_key": None},
    
    "WORK_DATE": {"alias": "work_date", "category": "날짜/시간", "constants_key": None},
    "WRK_DATE": {"alias": "work_date", "category": "날짜/시간", "constants_key": None},
    "PROD_DATE": {"alias": "production_date", "category": "날짜/시간", "constants_key": None},
    "INS_DATE": {"alias": "inspect_date", "category": "날짜/시간", "constants_key": None},
    "TEST_DATE": {"alias": "test_date", "category": "날짜/시간", "constants_key": None},
    "REG_DATE": {"alias": "register_date", "category": "날짜/시간", "constants_key": None},
    "OCCUR_DATE": {"alias": "occur_date", "category": "날짜/시간", "constants_key": None},
    "AUDIT_DATE": {"alias": "audit_date", "category": "날짜/시간", "constants_key": None},
    "RETURN_DATE": {"alias": "return_date", "category": "날짜/시간", "constants_key": None},
    "CURE_PRDT_DTM": {"alias": "cure_production_datetime", "category": "날짜/시간", "constants_key": None},
    
    "PRDT_QTY": {"alias": "production_qty", "category": "수량/실적", "constants_key": None},
    "RETURN_QTY": {"alias": "return_qty", "category": "수량/실적", "constants_key": None},
    "DEFECT_QTY": {"alias": "defect_qty", "category": "수량/실적", "constants_key": None},
    "NCF_QTY": {"alias": "nonconformity_qty", "category": "수량/실적", "constants_key": None},
    "SCRAP_QTY": {"alias": "scrap_qty", "category": "수량/실적", "constants_key": None},
    "REWORK_QTY": {"alias": "rework_qty", "category": "수량/실적", "constants_key": None},
    "DFT_QTY": {"alias": "defect_qty", "category": "수량/실적", "constants_key": None},
    
    "STATUS": {"alias": "status", "category": "상태값", "constants_key": "STATUS_4M_DICT"},
    "PGS_STS": {"alias": "progress_status", "category": "상태값", "constants_key": "JDG_DICT"},
    "DIRECTION": {"alias": "direction_flag", "category": "상태값", "constants_key": None},
    "INS_FG": {"alias": "inspect_flag", "category": "상태값", "constants_key": "INCLUDED_INS_FG_LIST"},
    
    "GRADE": {"alias": "grade", "category": "품질등급", "constants_key": "JDG_DICT"},
    "JDG_GR": {"alias": "judge_grade", "category": "품질등급", "constants_key": "JDG_DICT"},
    
    "TITLE": {"alias": "title", "category": "텍스트", "constants_key": None},
    "REQ_NO": {"alias": "request_no", "category": "요청번호", "constants_key": None},
    "AUDIT_NO": {"alias": "audit_no", "category": "감사번호", "constants_key": None},
    "ISSUE_NO": {"alias": "issue_no", "category": "품질이슈번호", "constants_key": None},
    "DOC_NO": {"alias": "doc_no", "category": "문서번호", "constants_key": None},
    "REVISION_NO": {"alias": "revision_no", "category": "개정번호", "constants_key": None},
    
    "SIZE_CD": {"alias": "size_code", "category": "사이즈코드", "constants_key": None},
    "PATTERN_CD": {"alias": "pattern_code", "category": "패턴코드", "constants_key": None},
    "SIZE_NAME": {"alias": "size_name", "category": "사이즈명", "constants_key": None},
    "PATTERN_NM": {"alias": "pattern_name", "category": "패턴명", "constants_key": None},
    "STXC": {"alias": "stxc_val", "category": "규격값", "constants_key": None},
    
    "MACHINE_CD": {"alias": "machine_code", "category": "설비코드", "constants_key": None},
    "SHIFT_CD": {"alias": "shift_code", "category": "근무교대조", "constants_key": "SHIFT_DICT"},
    "REG_USER": {"alias": "register_user", "category": "등록자", "constants_key": None},
    "AUDIT_USER": {"alias": "audit_user", "category": "감사자", "constants_key": None},
    
    "DFT_CD": {"alias": "defect_code", "category": "불량코드", "constants_key": "NCF_SUBCATEGORY_DIC"},
    "CATEGORY_CD": {"alias": "category_code", "category": "분류코드", "constants_key": "NCF_CATEGORY_DIC"},
    "CLAIM_CD": {"alias": "claim_code", "category": "클레임코드", "constants_key": "SAFETY_RETURN_CODE_LIST"},
    "ZAREA": {"alias": "country_area", "category": "지역코드", "constants_key": "ZAREA_MAPPING_DICT"},
}

# 테이블별 한글 요약 및 주요 컬럼 수동 사전 정의 (기존의 사양들 완전 유지)
TABLE_MANUAL_DICTS = {
    # CQMS
    "cqms_4m_main": {
        "summary": "CQMS 4M 설계 및 생산 변경 요청 마스터 정보",
        "columns": ["PLANT", "REQ_NO", "TITLE", "REG_USER", "REG_DATE", "M_CODE", "STATUS", "CHG_REASON", "CHG_DESC"]
    },
    "cqms_4m_mcode": {
        "summary": "CQMS 4M 변경건에 대한 대상 자재 매핑 상세 이력",
        "columns": ["REQ_NO", "M_CODE", "M_NAME"]
    },
    "cqms_quality_main": {
        "summary": "CQMS 완성품 품질 이슈 및 클레임 내역 마스터",
        "columns": ["ISSUE_NO", "TITLE", "REG_DATE", "OCCUR_DATE", "PLANT", "M_CODE", "DEFECT_CD", "DEFECT_NM", "DEFECT_QTY", "STATUS"]
    },
    "cqms_quality_category": {
        "summary": "CQMS 품질 이슈 유형 및 카테고리 마스터 코드",
        "columns": ["CATEGORY_CD", "CATEGORY_NM", "PARENT_CD"]
    },
    "cqms_quality_mcode": {
        "summary": "CQMS 품질 이슈에 해당하는 영향 자재 매핑 정보",
        "columns": ["ISSUE_NO", "M_CODE", "M_NAME"]
    },
    "cqms_quality_breakdown": {
        "summary": "CQMS 품질 불량 파손 부위 유형 코드 매핑",
        "columns": ["ISSUE_NO", "BREAK_DOWN_CD", "BREAK_DOWN_NM"]
    },
    "cqms_audit_main": {
        "summary": "CQMS 외부/고객사 품질 감사(Audit) 실적 정보",
        "columns": ["AUDIT_NO", "TITLE", "AUDIT_DATE", "AUDIT_USER", "PLANT", "STATUS"]
    },
    "cqms_audit_mcode": {
        "summary": "CQMS 외부 감사 대상 자재 매핑 정보",
        "columns": ["AUDIT_NO", "M_CODE"]
    },
    "app_info_mcode": {
        "summary": "CQMS 인증 사양 자재 정보",
        "columns": ["DOC_NO", "M_CODE"]
    },
    "app_info_contents": {
        "summary": "CQMS 인증 사양서 개정이력 및 본문 텍스트",
        "columns": ["DOC_NO", "REVISION_NO", "CONTENTS", "FILE_NAME"]
    },
    "cqms_doc_code_table": {
        "summary": "CQMS OEM 품질 표준 카테고리 코드 관리 체계",
        "columns": ["CATE_CD", "CATE_NM", "PARENT_CD"]
    },
    "cqms_doc_oem_cat_main": {
        "summary": "CQMS OEM 기술 사양 표준 마스터 정보",
        "columns": ["CATE_CD", "DOC_NO", "TITLE"]
    },
    "cqms_doc_oem_cat_rev_mgnt": {
        "summary": "CQMS OEM 규격 사양의 유효 개정이력 및 적용 날짜",
        "columns": ["DOC_NO", "REVISION_NO", "APPLY_DATE"]
    },
    "cqms_doc_pp_detail": {
        "summary": "CQMS PP(Process Parameter) 제조 공정 처방 데이터 상세",
        "columns": ["PP_NO", "M_CODE", "SPEC_CD"]
    },
    "cqms_doc_pp_info": {
        "summary": "CQMS 공정 처방 규격 문서 상세 메타 속성",
        "columns": ["PP_NO", "TITLE", "REG_DATE"]
    },
    "cqms_doc_pp_main": {
        "summary": "CQMS 공정 파라미터 매핑 마스터 규격 관계 정보",
        "columns": ["PP_NO", "DOC_NO", "REVISION_NO"]
    },
    "cqms_doc_sales_brand_detail": {
        "summary": "CQMS 판매 브랜드별 가용 타이어 자재 매핑 정보",
        "columns": ["BRAND_NO", "M_CODE"]
    },
    "cqms_doc_sales_brand_main": {
        "summary": "CQMS 판매 및 유통 브랜드 마스터 코드 대장",
        "columns": ["BRAND_NO", "TITLE"]
    },
    "cqms_doc_sales_brand_pp_detail": {
        "summary": "CQMS 브랜드별 제조 공라벨(Label) 파라미터 상세 정보",
        "columns": ["BRAND_PP_NO", "M_CODE"]
    },
    "cqms_doc_sales_brand_pp_info": {
        "summary": "CQMS 브랜드 공정 파라미터 마스터 기본 제목 설명",
        "columns": ["BRAND_PP_NO", "TITLE"]
    },
    "cqms_doc_sales_brand_pp_main": {
        "summary": "CQMS 브랜드 공정 파라미터 규격 마스터 관계 정보",
        "columns": ["BRAND_PP_NO", "DOC_NO"]
    },
    "cqms_row_visibility": {
        "summary": "품질 문서 및 데이터 조회 가시성 제어 권한 테이블",
        "columns": ["TABLE_NAME", "ROW_ID", "IS_VISIBLE"]
    },
    "cqms_row_visibility_log": {
        "summary": "품질 데이터 권한 조정 및 로그 열람 감사 추적 이력",
        "columns": ["TABLE_NAME", "ROW_ID", "ACTION", "WORKER", "ACTION_DATE"]
    },
    "cqms_iqm_main": {
        "summary": "CQMS IQM 정밀 품질 종합 부적합 판정 대장",
        "columns": ["IQM_NO", "TITLE", "PLANT", "M_CODE", "REG_DATE"]
    },
    "cqms_iqm_status": {
        "summary": "CQMS IQM 품질 판정 및 결재 진행 상황 추적",
        "columns": ["IQM_NO", "STATUS", "UPDATE_DATE"]
    },
    "cqms_iqm_test_item": {
        "summary": "CQMS IQM 품질 계측 정밀 시험 항목 물리 규격 스펙",
        "columns": ["IQM_NO", "TEST_CD", "TEST_NM", "SPEC_VAL"]
    },
    "cqms_iqm_test_item_req": {
        "summary": "CQMS IQM 정밀 시험에서 요구되는 고객사 합격 조건 스펙",
        "columns": ["IQM_NO", "TEST_CD", "REQ_VAL"]
    },
    "cqms_iqm_test_main": {
        "summary": "CQMS IQM 품질 시험 측정 실행 마스터 기록",
        "columns": ["IQM_NO", "TEST_DATE", "TEST_USER"]
    },
    "qi_d1_team": {
        "summary": "품질 이슈 8D 개선 활동 구성팀 매핑 정보",
        "columns": ["ISSUE_NO", "TEAM_CD", "TEAM_NM"]
    },
    "qi_d7_prevention": {
        "summary": "품질 이슈 재발 방지를 위한 8D 예방 대책 상세 매핑",
        "columns": ["ISSUE_NO", "PREVENT_CD", "PREVENT_NM"]
    },
    "qi_root_cause": {
        "summary": "품질 결함 원인 분석 및 근본 원인 도출 코드 매핑 정보",
        "columns": ["ISSUE_NO", "CAUSE_CD", "CAUSE_NM"]
    },
    "cqms_attachment": {
        "summary": "CQMS 품질 보증 활동 및 클레임 첨부문서 파일 매핑 테이블",
        "columns": ["ATTACH_ID", "PARENT_ID", "FILE_NAME", "FILE_PATH"]
    },
    
    # Common
    "product_master": {
        "summary": "전사 타이어 완제품 자재정보 마스터 (사이즈/패턴/규격 일치)",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "SIZE_CD", "PATTERN_CD", "STXC", "SIZE_NAME", "PATTERN_NM"]
    },
    "spec_revision": {
        "summary": "제품 규격 스펙의 개정 이력 및 적용일자 관리",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "REVISION_NO", "APPLY_DATE"]
    },
    "mes_code_master": {
        "summary": "MES 생산설비 및 공정 운영에 활용되는 전사 공통 코드 마스터",
        "columns": ["CD_ITEM", "CD_ITEM_NM", "CD_VAL", "CD_VAL_NM"]
    },
    "production_volume": {
        "summary": "공장/일자/자재별 실 생산 수량 및 스크랩, 재작업 실적 집계",
        "columns": ["PLANT", "M_CODE", "WORK_DATE", "PRDT_QTY", "SCRAP_QTY", "REWORK_QTY"]
    },
    "full_spec": {
        "summary": "전사 완전한 타이어 물리 설계 제원 종합 마스터",
        "columns": ["SPEC_CD", "M_CODE", "SIZE_NAME", "PATTERN_NM", "STXC"]
    },
    "barcode_record": {
        "summary": "제품 가류 바코드 단위 실시간 생산 이력 및 설비 이력",
        "columns": ["BARCODE_NO", "PLANT", "M_CODE", "SPEC_CD", "PROD_DATE", "SHIFT_CD", "MACHINE_CD"]
    },
    
    # Production
    "production_machine": {
        "summary": "생산 설비 가동 시간 및 가동 실적 매핑 정보",
        "columns": ["PLANT", "M_CODE", "WORK_DATE", "MACHINE_CD", "PRDT_QTY"]
    },
    "building_manufacture_report": {
        "summary": "반제품 성형(Building) 공정 실 생산량 및 설비 보고 정보",
        "columns": ["PLANT", "M_CODE", "WORK_DATE", "SPEC_CD", "PRDT_QTY"]
    },
    
    # RR / Uniformity
    "rr_lot_samples": {
        "summary": "RR(Rolling Resistance, 회전저항) 품질 측정 샘플 랏 정보",
        "columns": ["PLANT", "M_CODE", "BARCODE_NO", "PGS_STS", "INS_DATE", "RR_VALUE", "GRADE"]
    },
    "rr_test_result": {
        "summary": "RR 품질 검사 실 계측 데이터 및 등재 첨부파일",
        "columns": ["BARCODE_NO", "INS_DATE", "RR_VALUE", "GRADE", "ATTACH_FILE_NAME"]
    },
    "rr_standard": {
        "summary": "차종/고객사별 RR 스펙 표준값 및 허용 한계(UCL/LCL) 마스터",
        "columns": ["PLANT", "M_CODE", "CAR_MAKER", "VEHICLE", "UCL", "LCL"]
    },
    "uf_inspection_result": {
        "summary": "완제품 유니포미티(Uniformity) 품질 계측 정밀 결과",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "STXC", "INS_DATE", "RFV", "LFV", "CON", "HAR", "JDG_GR", "INS_FG"]
    },
    "uf_inspection_standard": {
        "summary": "유니포미티 물리 측정 규격 한계 최대치 기준값",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "RFV_MAX", "LFV_MAX", "CON_MAX", "HAR_MAX"]
    },
    "uf_db_standard": {
        "summary": "유니포미티 통계적 관리 한계치(UCL/LCL) 기준값",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "RFV_UCL", "LFV_UCL", "CON_UCL", "HAR_UCL"]
    },
    
    # Nonconformity
    "shipment_inspection_result": {
        "summary": "최종 완제품 출하 검사 품질 부적합(Defect) 판정 결과",
        "columns": ["PLANT", "M_CODE", "INS_DATE", "DFT_CD", "DFT_DESC", "NCF_QTY"]
    },
    "finished_product_inspection_result": {
        "summary": "완제품 완성 단계 정밀 완성검사 부적합 이력",
        "columns": ["PLANT", "M_CODE", "INS_DATE", "DFT_CD", "DFT_DESC", "NCF_QTY"]
    },
    
    # PLM
    "plm_spec_label": {
        "summary": "PLM 규격 내 타이어 라벨 스펙 정보 및 관리 공차",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "ITEM_LABEL", "UCL_VAL", "LCL_VAL"]
    },
    "plm_uf_db_standard": {
        "summary": "PLM 완제품 유니포미티 관리 규격 한계 마스터",
        "columns": ["PLANT", "M_CODE", "SPEC_CD", "ITEM_LABEL", "UCL_VAL", "LCL_VAL"]
    },
    "worksheet_building_overall": {
        "summary": "생산 성형 공정 종합 집계 작업 보고 시트",
        "columns": ["PLANT", "M_CODE", "WORK_DATE", "BUILD_QTY"]
    },
    
    # HGWS / CTMS / HOPE / QRS / RPA / TDR
    "hgws": {
        "summary": "HGWS 글로벌 클레임 청구 및 반품(Return) 이력",
        "columns": ["PLANT", "WERKS", "M_CODE", "RETURN_DATE", "RETURN_QTY", "CLAIM_CD", "CLAIM_DESC", "ZAREA"]
    },
    "ctms": {
        "summary": "CTMS 원자재 품질 물리 계측 시험(Lab) 결과 정보",
        "columns": ["PLANT", "M_CODE", "TEST_DATE", "CTL_VALUE", "DIRECTION", "UPPER_VAL", "LOWER_VAL"]
    },
    "oe_application": {
        "summary": "SOP 전 OE 공급 승인 신청(Application) 이력 정보",
        "columns": ["PLANT", "M_CODE", "APPLICATION_NO", "REG_DATE"]
    },
    "rpa_test_result": {
        "summary": "RPA 기기 계측 품질 시험 이력 및 자동 판정 등급",
        "columns": ["PLANT", "M_CODE", "TEST_DATE", "TAND_VAL", "GRADE"]
    },
    "tdr": {
        "summary": "TDR 개발 사양 및 원자재 물리 특성 설계 마스터",
        "columns": ["PLANT", "M_CODE", "DOC_NO", "TITLE", "REG_DATE"]
    },
    "lot_track": {
        "summary": "가류 바코드 기준 생산 추적 및 원자재 추적 랏 트래킹",
        "columns": ["BARCODE_NO", "PLANT", "M_CODE", "PROD_DATE"]
    },
    
    # SQLite Tables (log, staging, ops)
    "login_log": {
        "summary": "로컬 사용자 시스템 로그인 이력 세션 데이터",
        "columns": ["id", "employee_id", "login_time"]
    },
    "sqliteStaging_iqm_specMaster": {
        "summary": "IQM 플러스 단계별 제품 개정 규격 정보 동기화 테이블",
        "columns": ["MCODE", "YEAR", "PLANT", "MP_GATE_DT", "MFG_MCODE", "SPEC_CD", "STXC", "RCPE_VER"]
    },
    "sqliteStaging_iqm_prdt": {
        "summary": "IQM 플러스 수동 집계 대상 완제품 실 생산량 동기화 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "MASS_PERIOD", "PRDT_QTY"]
    },
    "sqliteStaging_iqm_ncf": {
        "summary": "IQM 플러스 분석용 비정규 폐기/재작업률 중간 집계 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "SCRAP_DFT_QTY", "SCRAP_RATE", "REWORK_DFT_QTY", "REWORK_RATE"]
    },
    "sqliteStaging_iqm_scrap": {
        "summary": "IQM 플러스 분석용 원자재 스크랩 집계 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "SCRAP_DFT_QTY", "SCRAP_RATE"]
    },
    "sqliteStaging_iqm_rework": {
        "summary": "IQM 플러스 분석용 재작업(Rework) 발생 집계 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "REWORK_DFT_QTY", "REWORK_RATE"]
    },
    "sqliteStaging_iqm_gtWt": {
        "summary": "IQM 플러스 완성 중량(G/T Weight) 검사 합격 통계 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "GT_WT_PASS_COUNT", "GT_WT_INS_COUNT", "GT_WT_PASS_RATE"]
    },
    "sqliteStaging_iqm_uf": {
        "summary": "IQM 플러스 완제품 Uniformity 검사 합격률 통계 집계 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "UF_PASS_COUNT", "UF_INS_COUNT", "UF_PASS_RATE"]
    },
    "sqliteStaging_iqm_rr": {
        "summary": "IQM 플러스 회전저항(RR) 시험 수치 및 분산 통계 집계 테이블",
        "columns": ["RR_MCODE", "PERIOD_NAME", "RR_AVG", "RR_STD", "RR_COUNT", "RR_SPEC_MAX"]
    },
    "sqliteStaging_iqm_ctl": {
        "summary": "IQM 플러스 CTL 시험 합격률 실적 중간 동기화 테이블",
        "columns": ["MFG_MCODE", "PERIOD_NAME", "CTL_COUNT", "CTL_PASS_RATE_CUM"]
    },
    "sellin_monthly_agg": {
        "summary": "Sell-in 대리점 공급 실적 월별 수동 집계 정보",
        "columns": ["RE/OE", "M_CODE", "YYYY", "MM", "SUPP_QTY"]
    },
    "mcode_mapping_mgt": {
        "summary": "MCODE 간의 생산용 및 대외용 자재 맵핑 관계 관리 정보",
        "columns": ["MCODE", "MFG_MCODE", "RR_MCODE", "DELETE_MCODE"]
    },
    "fm_library": {
        "summary": "현장 이상 발생 라이브러리 및 불량 발생 사진 매핑 테이블",
        "columns": ["id", "category", "non_conformity_classification", "cause_analysis_result"]
    }
}


def parse_query_database_py_for_usage() -> dict:
    """query_database.py의 내용을 정적 파싱하여 상수명, 실제 경로, 사용유무 정보를 추출합니다."""
    with open(query_db_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # DatabricksTables 클래스 추출
    dbx_match = re.search(r'class DatabricksTables:\s*"""(.*?)"""(.*?)class SQLiteTables:', content, re.DOTALL)
    dbx_body = dbx_match.group(2) if dbx_match else ""

    # SQLiteTables 클래스 추출
    sqlite_match = re.search(r'class SQLiteTables:\s*"""(.*?)"""(.*)', content, re.DOTALL)
    sqlite_body = sqlite_match.group(2) if sqlite_match else ""

    parsed_data = {}

    # DatabricksTables 줄 파싱
    for line in dbx_body.split("\n"):
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue
        
        # name: str = "val" # 사용 유무 주석
        match = re.match(r'^([a-zA-Z0-9_]+)\s*:\s*str\s*=\s*(?:\(\s*)?["\'](.*?)(?:["\']\s*\))?\s*(?:#\s*(.*))?$', line_strip)
        if match:
            var_name = match.group(1)
            table_path = match.group(2).strip().strip('"').strip("'")
            comment = match.group(3) if match.group(3) else ""
            
            is_used = "사용" in comment and "미사용" not in comment
            
            parsed_data[var_name] = {
                "table_path": table_path,
                "is_used": is_used,
                "db_type": "Databricks"
            }

    # SQLiteTables 줄 파싱
    for line in sqlite_body.split("\n"):
        line_strip = line.strip()
        if not line_strip or line_strip.startswith("#"):
            continue
        
        match = re.match(r'^([a-zA-Z0-9_]+)\s*:\s*str\s*=\s*(?:\(\s*)?["\'](.*?)(?:["\']\s*\))?\s*(?:#\s*(.*))?$', line_strip)
        if match:
            var_name = match.group(1)
            table_path = match.group(2).strip().strip('"').strip("'")
            comment = match.group(3) if match.group(3) else ""
            
            is_used = "사용" in comment and "미사용" not in comment
            
            parsed_data[var_name] = {
                "table_path": table_path,
                "is_used": is_used,
                "db_type": "SQLite"
            }

    return parsed_data


def get_sqlite_db_type(var_name: str) -> str:
    """SQLite 테이블이 속한 원본 DB 유형을 판별합니다 (log, staging, ops)."""
    if "log" in var_name.lower():
        return "log"
    elif "staging" in var_name.lower():
        return "staging"
    else:
        return "ops"


def get_sqlite_columns(sqlite_type: str, table_name: str) -> list:
    """SQLite DB 파일에서 실제 테이블 컬럼 및 메타 속성(PK 등)을 실시간으로 가져옵니다."""
    db_path = sqlite_db_paths.get(sqlite_type)
    if not db_path or not os.path.exists(db_path):
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()
        # columns_info: (cid, name, type, notnull, dflt_value, pk)
        columns = []
        for col in columns_info:
            columns.append({
                "cid": col[0],
                "name": col[1],
                "type": col[2],
                "notnull": bool(col[3]),
                "default_value": col[4],
                "pk": bool(col[5])
            })
        conn.close()
        return columns
    except Exception as e:
        print(f"[MetadataGenerator] SQLite {table_name} ({sqlite_type}) 스키마 조회 에러: {e}")
        return []


def collect_query_references(parsed_tables: dict) -> dict:
    """app/queries/ 내의 모든 SQL 조립 파일에서 각 테이블 상수/경로의 사용처를 실시간 추적합니다."""
    query_dir = f"{workspace_dir}/app/queries"
    if not os.path.exists(query_dir):
        return {}

    query_files = [f for f in os.listdir(query_dir) if f.endswith(".py")]
    file_contents = {}
    for q_file in query_files:
        path = os.path.join(query_dir, q_file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_contents[q_file] = f.read()
        except Exception as e:
            print(f"[MetadataGenerator] 쿼리 파일 {q_file} 읽기 실패: {e}")

    referenced_map = {}
    for var_name, details in parsed_tables.items():
        table_path = details["table_path"]
        referenced = []
        for q_file, content in file_contents.items():
            if var_name in content or table_path in content:
                referenced.append(q_file)
        referenced_map[var_name] = sorted(referenced)

    return referenced_map


def get_table_category(var_name: str, db_type: str) -> str:
    """테이블의 도메인 카테고리를 직관적으로 도출합니다."""
    if db_type == "SQLite":
        sqlite_type = get_sqlite_db_type(var_name)
        if sqlite_type == "log":
            return "Log Database"
        elif sqlite_type == "staging":
            return "Staging Database"
        else:
            return "Operational Database"

    if var_name.startswith("cqms_doc_"):
        return "CQMS Document"
    elif var_name.startswith("cqms_iqm_"):
        return "CQMS IQM"
    elif var_name.startswith("cqms_"):
        return "CQMS"
    elif var_name.startswith("qi_"):
        return "Quality Issue"
    elif var_name.startswith("rr_"):
        return "Rolling Resistance"
    elif var_name.startswith("uf_"):
        return "Uniformity"
    elif var_name in ["product_master", "spec_revision", "mes_code_master", "production_volume", "full_spec", "barcode_record"]:
        return "Common Master"
    elif var_name in ["production_machine", "building_manufacture_report"]:
        return "Production"
    elif var_name in ["shipment_inspection_result", "finished_product_inspection_result"]:
        return "Nonconformity"
    else:
        return "Other Domain"


def build_markdown_report_from_integrated_json(metadata: dict) -> str:
    """통합된 query_tables_metadata.json 정보를 바탕으로 구조적이고 깔끔한 database-metadata.md 보고서를 생성합니다."""
    md = []
    md.append("# 📊 데이터베이스 테이블 및 쿼리 메타데이터 명세서 (Integrated Database Metadata Specification)")
    md.append("")
    md.append("> 이 문서는 `app/core/query/query_tables_metadata.json`에 일원화 관리되는 물리적 스펙과 비즈니스 논리 매핑 정보(한글, 상수)를 바탕으로 자동 갱신된 단일 진실 공급원(SSOT) 기술 명세서입니다.")
    md.append("> AI 에이전트의 정밀 코딩 및 쿼리 생성, 하네스 검증 시 스키마 무결성 판단 기준으로 사용됩니다.")
    md.append("")
    
    dbx_count = sum(1 for x in metadata.values() if x["db_type"] == "Databricks")
    sqlite_count = sum(1 for x in metadata.values() if x["db_type"] == "SQLite")
    used_count = sum(1 for x in metadata.values() if x["is_used"])

    md.append("## 📈 메타데이터 통계")
    md.append(f"- **전체 관리 테이블 수**: {len(metadata)} 개")
    md.append(f"  - ☁️ Databricks Cloud Tables: {dbx_count} 개")
    md.append(f"  - 💾 SQLite Local Tables: {sqlite_count} 개")
    md.append(f"  - 🚀 현재 활성화(사용 중) 테이블 수: {used_count} 개")
    md.append("")
    md.append("---")
    md.append("")
    
    # 1. Databricks 테이블 목록
    md.append("## ☁️ Databricks Cloud Tables")
    md.append("")
    
    # 카테고리 추출
    dbx_tables = {k: v for k, v in metadata.items() if v["db_type"] == "Databricks"}
    categories = sorted(list(set(x["category"] for x in dbx_tables.values())))
    
    for cat in categories:
        md.append(f"### 📁 분류: {cat}")
        md.append("")
        md.append("| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |")
        md.append("|---|---|---|:---:|---|")
        
        cat_items = {k: v for k, v in dbx_tables.items() if v["category"] == cat}
        for var_name, info in sorted(cat_items.items()):
            ref_summary = ", ".join([f"`{q}`" for q in info["referenced_in_queries"]]) if info["referenced_in_queries"] else "-"
            used_status = "✅ 사용" if info["is_used"] else "❌ 미사용"
            md.append(f"| `{var_name}` | **{info['summary_ko']}** | `{info['table_path']}` | {used_status} | {ref_summary} |")
        md.append("")
        
        # 상세 컬럼 명세 축소 제공 (가독성을 위한 드롭다운 구현)
        md.append("<details>")
        md.append("<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>")
        md.append("")
        for var_name, info in sorted(cat_items.items()):
            md.append(f"#### 📑 `{var_name}` ({info['summary_ko']})")
            md.append("| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |")
            md.append("|---|---|---|---|---|")
            for col_name, spec in info["columns_spec"].items():
                constants_desc = f"{len(spec['value_constants'])}개 상수 항목 매핑" if spec['value_constants'] else "-"
                md.append(f"| `{col_name}` | `{spec['type']}` | `{spec['recommended_alias']}` | {spec['category_type']} | {constants_desc} |")
            md.append("")
        md.append("</details>")
        md.append("")

    md.append("---")
    md.append("")

    # 2. SQLite 테이블 목록
    md.append("## 💾 SQLite Local Tables")
    md.append("")
    
    sqlite_tables = {k: v for k, v in metadata.items() if v["db_type"] == "SQLite"}
    sqlite_categories = sorted(list(set(x["category"] for x in sqlite_tables.values())))
    
    for cat in sqlite_categories:
        md.append(f"### 🗄️ Database: {cat}")
        md.append("")
        md.append("| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블명 (Table) | 사용 여부 | 주요 참조 쿼리 (Queries) |")
        md.append("|---|---|---|:---:|---|")
        
        cat_items = {k: v for k, v in sqlite_tables.items() if v["category"] == cat}
        for var_name, info in sorted(cat_items.items()):
            ref_summary = ", ".join([f"`{q}`" for q in info["referenced_in_queries"]]) if info["referenced_in_queries"] else "-"
            used_status = "✅ 사용" if info["is_used"] else "❌ 미사용"
            md.append(f"| `{var_name}` | **{info['summary_ko']}** | `{info['table_path']}` | {used_status} | {ref_summary} |")
        md.append("")
        
        md.append("<details>")
        md.append("<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>")
        md.append("")
        for var_name, info in sorted(cat_items.items()):
            md.append(f"#### 📑 `{var_name}` ({info['summary_ko']})")
            md.append("| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |")
            md.append("|---|---|:---:|:---:|---|---|---|")
            for col_name, spec in info["columns_spec"].items():
                pk_flag = "🔑" if spec.get("pk", False) else "-"
                notnull_flag = "Y" if spec.get("notnull", False) else "-"
                def_val = str(spec.get("default_value")) if spec.get("default_value") is not None else "-"
                md.append(f"| `{col_name}` | `{spec['type']}` | {pk_flag} | {notnull_flag} | `{def_val}` | `{spec['recommended_alias']}` | {spec['category_type']} |")
            md.append("")
        md.append("</details>")
        md.append("")

    return "\n".join(md)


def generate_json():
    print("[MetadataGenerator] query_database.py 정적 파싱 시작...")
    parsed_tables = parse_query_database_py_for_usage()
    
    print("[MetadataGenerator] app/queries 내 참조 관계 추적 분석 시작...")
    referenced_map = collect_query_references(parsed_tables)
    
    final_metadata = {}

    for var_name, details in parsed_tables.items():
        # 수동 한글 정보 사전 조회 (없으면 기본값)
        manual_info = TABLE_MANUAL_DICTS.get(var_name, {
            "summary": f"{details['db_type']} {var_name} 테이블 데이터",
            "columns": ["PLANT", "M_CODE", "SPEC_CD"]
        })
        
        db_type = details["db_type"]
        table_path = details["table_path"]
        
        # SQLite인 경우 실시간 스키마 데이터 패치 시도
        sqlite_cols_info = {}
        if db_type == "SQLite":
            sqlite_type = get_sqlite_db_type(var_name)
            sqlite_cols_info = {col["name"]: col for col in get_sqlite_columns(sqlite_type, table_path)}

        columns_detail = {}
        for col in manual_info["columns"]:
            # 공통 컬럼 설정 검색
            col_meta = COMMON_COLUMN_META.get(col, {
                "alias": col.lower(),
                "category": "일반속성",
                "constants_key": None
            })
            
            # 물리 컬럼 타입 결정 및 SQLite 특수 제약사항 처리
            col_type = "VARCHAR"
            extra_attrs = {}
            if db_type == "SQLite" and col in sqlite_cols_info:
                col_type = sqlite_cols_info[col]["type"] or "VARCHAR"
                extra_attrs["pk"] = sqlite_cols_info[col]["pk"]
                extra_attrs["notnull"] = sqlite_cols_info[col]["notnull"]
                extra_attrs["default_value"] = sqlite_cols_info[col]["default_value"]
            else:
                # Databricks의 경우 단순 이름 형태 매칭 기반 데이터 타입 추론 적용
                if any(x in col for x in ["DATE", "TIME"]):
                    col_type = "TIMESTAMP"
                elif any(x in col for x in ["QTY", "VAL", "NUM", "MAX", "UCL", "LCL", "WGT", "RFV", "LFV", "CON", "HAR", "RATE", "COUNT"]):
                    col_type = "DOUBLE"

            # 비즈니스 매핑 상수 사전 조회
            value_constants = {}
            constants_key = col_meta.get("constants_key")
            if constants_key:
                raw_constants = BIZ_CONSTANTS.get(constants_key, {})
                if isinstance(raw_constants, dict):
                    value_constants = raw_constants
                elif isinstance(raw_constants, list):
                    # 리스트 타입의 경우 딕셔너리로 형변환
                    value_constants = {str(i): val for i, val in enumerate(raw_constants)}

            columns_detail[col] = {
                "type": col_type,
                "recommended_alias": col_meta["alias"],
                "category_type": col_meta["category"],
                "value_constants": value_constants,
                **extra_attrs
            }
            
        final_metadata[var_name] = {
            "db_type": db_type,
            "table_path": table_path,
            "category": get_table_category(var_name, db_type),
            "summary_ko": manual_info["summary"],
            "is_used": details["is_used"],
            "referenced_in_queries": referenced_map.get(var_name, []),
            "columns_spec": columns_detail
        }
        
    # JSON 폴더 생성 및 저장
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(final_metadata, f, indent=4, ensure_ascii=False)
    print(f"[MetadataGenerator] 통합 메타데이터 생성 성공 -> {output_json_path}")
    
    # Markdown 기술 사양서 자동 생성 및 업데이트
    print("[MetadataGenerator] 통합 database-metadata.md 보고서 생성 시작...")
    md_content = build_markdown_report_from_integrated_json(final_metadata)
    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"[MetadataGenerator] 통합 기술 사양서 생성 성공 -> {output_md_path}")


if __name__ == "__main__":
    generate_json()
