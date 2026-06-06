# 데이터베이스 테이블 메타데이터 명세서 (Database Metadata Specification)

> 이 문서는 `app/core/query/query_database.py`에 정의된 모든 데이터베이스 테이블의 변수명, 실제 경로, 시스템 요약 및 스키마 메타정보를 자동으로 수집 및 정리한 명세서입니다.
> 시스템 인텔리전스 및 하네스 테스트, 신규 쿼리 작성 시 단일 진실 공급원(SSOT)으로 사용됩니다.

## 데이터베이스 분류 통계

- **전체 정의된 테이블 수**: 84 개
- **Databricks Cloud Tables**: 69 개
- **SQLite Local Tables**: 15 개

---

## Databricks Cloud Tables

### 카테고리: Barcode

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `barcode_record` | `hkt_dw.production.wrk_f_lwrktr140` | Databricks Barcode table: barcode_record | `ev3_query.py`, `gmes_query.py` | BARCODE_NO, PLANT, M_CODE, SPEC_CD, PROD_DATE, SHIFT_CD, MACHINE_CD |

### 카테고리: Building

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `building_manufacture_report` | `hkt_dw.quality.qlt_f_lqlttr127` | Databricks Building table: building_manufacture_report | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, WORK_DATE, SPEC_CD, PRDT_QTY |

### 카테고리: CQMS

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `change_main` | `hkt_system_dw.eqms.cqms_change_m` | Databricks CQMS table: change_main | `cqms_query.py` | PLANT, REQ_NO, TITLE, REG_USER, REG_DATE, M_CODE, STATUS, CHG_REASON, CHG_DESC |
| `change_mcode` | `hkt_system_dw.eqms.cqms_sub_mcode_d` | Databricks CQMS table: change_mcode | `cqms_query.py` | REQ_NO, M_CODE, M_NAME |
| `qi_main` | `hkt_system_dw.eqms.cqms_quality_issue` | Databricks CQMS table: qi_main | `cqms_query.py` | ISSUE_NO, TITLE, REG_DATE, OCCUR_DATE, PLANT, M_CODE, DEFECT_CD, DEFECT_NM, DEFECT_QTY, STATUS |
| `qi_category` | `hkt_system_dw.eqms.cqms_issue_category_data_oere` | Databricks CQMS table: qi_category | `cqms_query.py` | CATEGORY_CD, CATEGORY_NM, PARENT_CD |
| `qi_mcode` | `hkt_system_dw.eqms.cqms_quality_issue_material` | Databricks CQMS table: qi_mcode | `cqms_query.py` | ISSUE_NO, M_CODE, M_NAME |
| `qi_breakdown` | `hkt_system_dw.eqms.cqms_quality_issue_break_down` | Databricks CQMS table: qi_breakdown | None | ISSUE_NO, BREAK_DOWN_CD, BREAK_DOWN_NM |
| `audit_main` | `hkt_system_dw.eqms.cqms_customer_audit` | Databricks CQMS table: audit_main | `cqms_query.py` | AUDIT_NO, TITLE, AUDIT_DATE, AUDIT_USER, PLANT, STATUS |
| `audit_mcode` | `hkt_system_dw.eqms.cqms_customer_audit_material` | Databricks CQMS table: audit_mcode | `cqms_query.py` | AUDIT_NO, M_CODE |
| `app_info_mcode` | `hkt_system_dw.eqms.cqms_doc_m` | Databricks CQMS table: app_info_mcode | None | DOC_NO, M_CODE |
| `app_info_contents` | `hkt_system_dw.eqms.cqms_doc_revision` | Databricks CQMS table: app_info_contents | None | DOC_NO, REVISION_NO, CONTENTS, FILE_NAME |
| `cqms_doc_code_table` | `hkt_system_dw.eqms.oe_doc_cate_comm` | Databricks CQMS table: cqms_doc_code_table | None | CATE_CD, CATE_NM, PARENT_CD |
| `cqms_doc_oem_cat_main` | `hkt_system_dw.eqms.oe_doc_cate_d` | Databricks CQMS table: cqms_doc_oem_cat_main | None | CATE_CD, DOC_NO, TITLE |
| `cqms_doc_oem_cat_rev_mgnt` | `hkt_system_dw.eqms.oe_doc_cate_m` | Databricks CQMS table: cqms_doc_oem_cat_rev_mgnt | None | DOC_NO, REVISION_NO, APPLY_DATE |
| `cqms_doc_pp_detail` | `hkt_system_dw.eqms.oe_doc_cate_pp_d` | Databricks CQMS table: cqms_doc_pp_detail | None | PP_NO, M_CODE, SPEC_CD |
| `cqms_doc_pp_info` | `hkt_system_dw.eqms.oe_doc_cate_pp_info` | Databricks CQMS table: cqms_doc_pp_info | None | PP_NO, TITLE, REG_DATE |
| `cqms_doc_pp_main` | `hkt_system_dw.eqms.oe_doc_cate_pp_m` | Databricks CQMS table: cqms_doc_pp_main | None | PP_NO, DOC_NO, REVISION_NO |
| `cqms_doc_sales_brand_detail` | `hkt_system_dw.eqms.oe_doc_cate_sales_brand_d` | Databricks CQMS table: cqms_doc_sales_brand_detail | None | BRAND_NO, M_CODE |
| `cqms_doc_sales_brand_main` | `hkt_system_dw.eqms.oe_doc_cate_sales_brand_m` | Databricks CQMS table: cqms_doc_sales_brand_main | None | BRAND_NO, TITLE |
| `cqms_row_visibility` | `hkt_system_dw.eqms.cqms_row_hide_show_m` | Databricks CQMS table: cqms_row_visibility | None | TABLE_NAME, ROW_ID, IS_VISIBLE |
| `cqms_row_visibility_log` | `hkt_system_dw.eqms.cqms_row_hide_show_m_log` | Databricks CQMS table: cqms_row_visibility_log | None | TABLE_NAME, ROW_ID, ACTION, WORKER, ACTION_DATE |
| `cqms_iqm_main` | `hkt_system_dw.eqms.cqms_iqm_m` | Databricks CQMS table: cqms_iqm_main | None | IQM_NO, TITLE, PLANT, M_CODE, REG_DATE |
| `cqms_iqm_status` | `hkt_system_dw.eqms.cqms_iqm_status_m` | Databricks CQMS table: cqms_iqm_status | None | IQM_NO, STATUS, UPDATE_DATE |
| `cqms_iqm_test_item` | `hkt_system_dw.eqms.cqms_iqm_test_item_info` | Databricks CQMS table: cqms_iqm_test_item | None | IQM_NO, TEST_CD, TEST_NM, SPEC_VAL |
| `cqms_iqm_test_item_req` | `hkt_system_dw.eqms.cqms_iqm_test_item_info_req` | Databricks CQMS table: cqms_iqm_test_item_req | None | IQM_NO, TEST_CD, REQ_VAL |
| `cqms_iqm_test_main` | `hkt_system_dw.eqms.cqms_iqm_test_m` | Databricks CQMS table: cqms_iqm_test_main | None | IQM_NO, TEST_DATE, TEST_USER |
| `qi_d1_team` | `hkt_system_dw.eqms.cqms_quality_issue_d1_team` | Databricks CQMS table: qi_d1_team | None | ISSUE_NO, TEAM_CD, TEAM_NM |
| `qi_d7_prevention` | `hkt_system_dw.eqms.cqms_quality_issue_d7_prevent` | Databricks CQMS table: qi_d7_prevention | None | ISSUE_NO, PREVENT_CD, PREVENT_NM |
| `qi_root_cause` | `hkt_system_dw.eqms.cqms_quality_issue_root_cause` | Databricks CQMS table: qi_root_cause | None | ISSUE_NO, CAUSE_CD, CAUSE_NM |
| `cqms_attachment` | `hkt_system_dw.eqms.cqms_attach_file_onedrive` | Databricks CQMS table: cqms_attachment | None | ATTACH_ID, PARENT_ID, FILE_NAME, FILE_PATH |

### 카테고리: CTMS

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `ctms` | `hkt_system_dw.tableau.ctms_result_data` | Databricks CTMS table: ctms | `ctms_query.py`, `plm_query.py` | PLANT, M_CODE, TEST_DATE, CTL_VALUE, DIRECTION, UPPER_VAL, LOWER_VAL |

### 카테고리: Common

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `product_master` | `hkt_dw.specification.mas_d_lmastr101` | Databricks Common table: product_master | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, SPEC_CD, SIZE_CD, PATTERN_CD, STXC, SIZE_NAME, PATTERN_NM |
| `spec_revision` | `hkt_dw.specification.par_f_lmastr144` | Databricks Common table: spec_revision | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, SPEC_CD, REVISION_NO, APPLY_DATE |
| `mes_code_master` | `hkt_dw.master.mst_d_lcomtr107` | Databricks Common table: mes_code_master | `gmes_query.py` | CD_ITEM, CD_ITEM_NM, CD_VAL, CD_VAL_NM |
| `production_volume` | `hkt_dw.production.wrk_f_lwrkts118` | Databricks Common table: production_volume | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, WORK_DATE, PRDT_QTY, SCRAP_QTY, REWORK_QTY |
| `full_spec` | `hkt_rnd_dw.full_specification.tb_pl_if_plmspec_rcx_bas` | Databricks Common table: full_spec | `plm_query.py` | SPEC_CD, M_CODE, SIZE_NAME, PATTERN_NM, STXC |

### 카테고리: HGWS

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `hgws` | `hkt_system_dw.tableau.sap_zsrt10000` | Databricks HGWS table: hgws | `ev3_query.py`, `hgws_query.py` | PLANT, M_CODE, RETURN_DATE, RETURN_QTY, CLAIM_CD, CLAIM_DESC |

### 카테고리: Nonconformity

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `shipment_inspection_result` | `hkt_dw.quality.qlt_f_lqlttr120` | Databricks Nonconformity table: shipment_inspection_result | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, INS_DATE, DFT_CD, DFT_DESC, NCF_QTY |
| `finished_product_inspection_result` | `hkt_dw.quality.qlt_f_lqlttr107` | Databricks Nonconformity table: finished_product_inspection_result | `gmes_query.py` | PLANT, M_CODE, INS_DATE, DFT_CD, DFT_DESC, NCF_QTY |

### 카테고리: PLM

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `plm_uf_db_standard` | `hkt_rnd_dw.specification.tb_pl_dw_spec_pd_item_label_bas` | Databricks PLM table: plm_uf_db_standard | `gmes_query.py` | PLANT, M_CODE, SPEC_CD, ITEM_LABEL, UCL_VAL, LCL_VAL |

### 카테고리: Production (Machine)

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `production_machine` | `hkt_dw.production.wrk_f_lwrktr106` | Databricks Production (Machine) table: production_machine | `gmes_query.py` | PLANT, M_CODE, WORK_DATE, MACHINE_CD, PRDT_QTY |

### 카테고리: QRS

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `ext_tread_op_qrs` | `hkt_dw.quality.qlt_d_loprtr120` | Databricks QRS table: ext_tread_op_qrs | `qrs_query.py` | N/A |
| `ext_sidewall_op_qrs` | `hkt_dw.quality.qlt_d_loprtr122` | Databricks QRS table: ext_sidewall_op_qrs | `qrs_query.py` | N/A |
| `cal_op_qrs` | `hkt_dw.quality.qlt_d_loprtr125` | Databricks QRS table: cal_op_qrs | `qrs_query.py` | N/A |
| `cal_winding_qrs` | `hkt_dw.quality.qlt_d_loprtr126` | Databricks QRS table: cal_winding_qrs | `qrs_query.py` | N/A |
| `cal_let_off_qrs` | `hkt_dw.quality.qlt_d_loprtr127` | Databricks QRS table: cal_let_off_qrs | `qrs_query.py` | N/A |
| `cut_trc_op_qrs` | `hkt_dw.quality.qlt_d_loprtr134` | Databricks QRS table: cut_trc_op_qrs | `qrs_query.py` | N/A |
| `cut_src_op_qrs` | `hkt_dw.quality.qlt_d_loprtr135` | Databricks QRS table: cut_src_op_qrs | `qrs_query.py` | N/A |
| `cut_sbc_op_qrs` | `hkt_dw.quality.qlt_d_loprtr133` | Databricks QRS table: cut_sbc_op_qrs | `qrs_query.py` | N/A |
| `cut_pcr_il_op_qrs` | `hkt_dw.quality.qlt_d_loprtr137` | Databricks QRS table: cut_pcr_il_op_qrs | `qrs_query.py` | N/A |
| `cut_tbr_il_op_qrs` | `hkt_dw.quality.qlt_d_loprtr138` | Databricks QRS table: cut_tbr_il_op_qrs | `qrs_query.py` | N/A |
| `cut_tbc_op_qrs` | `hkt_dw.quality.qlt_d_loprtr136` | Databricks QRS table: cut_tbc_op_qrs | `qrs_query.py` | N/A |
| `cut_bec_op_qrs` | `hkt_dw.quality.qlt_d_loprtr139` | Databricks QRS table: cut_bec_op_qrs | `qrs_query.py` | N/A |
| `cut_wide_sliter_qrs` | `hkt_dw.quality.qlt_d_loprtr140` | Databricks QRS table: cut_wide_sliter_qrs | `qrs_query.py` | N/A |
| `cut_mini_sliter_qrs` | `hkt_dw.quality.qlt_d_loprtr141` | Databricks QRS table: cut_mini_sliter_qrs | `qrs_query.py` | N/A |
| `cut_edge_sliter_qrs` | `hkt_dw.quality.qlt_d_loprtr142` | Databricks QRS table: cut_edge_sliter_qrs | `qrs_query.py` | N/A |
| `cut_sheet_op_qrs` | `hkt_dw.quality.qlt_d_loprtr143` | Databricks QRS table: cut_sheet_op_qrs | `qrs_query.py` | N/A |
| `cut_bec_strip_op_qrs` | `hkt_dw.quality.qlt_d_loprtr144` | Databricks QRS table: cut_bec_strip_op_qrs | None | N/A |

### 카테고리: RPA

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `rpa_test_result` | `hkt_dw.quality.qlt_f_lqlttr268` | Databricks RPA table: rpa_test_result | `gmes_query.py` | PLANT, M_CODE, TEST_DATE, TAND_VAL, GRADE |

### 카테고리: RR

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `rr_lot_samples` | `hkt_dw.quality.qlt_d_lqlttr309` | Databricks RR table: rr_lot_samples | `gmes_query.py` | PLANT, M_CODE, BARCODE_NO, PGS_STS, INS_DATE, RR_VALUE, GRADE |
| `rr_test_result` | `hkt_dw.quality.qlt_f_lqlttr316` | Databricks RR table: rr_test_result | `gmes_query.py` | BARCODE_NO, INS_DATE, RR_VALUE, GRADE, ATTACH_FILE_NAME |
| `rr_standard` | `hkt_dw.quality.qlt_d_lqlttr510` | Databricks RR table: rr_standard | `gmes_query.py` | PLANT, M_CODE, CAR_MAKER, VEHICLE, UCL, LCL |

### 카테고리: TDR

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `tdr` | `hkt_system_dw.tdr.v_gate_document_to_oda` | Databricks TDR table: tdr | None | PLANT, M_CODE, DOC_NO, TITLE, REG_DATE |
| `lot_track` | `hkt_dw.production.wrk_f_lwrktr140` | Databricks TDR table: lot_track | `ev3_query.py`, `gmes_query.py` | BARCODE_NO, PLANT, M_CODE, PROD_DATE |

### 카테고리: Uniformity

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `uf_inspection_result` | `hkt_dw.quality.qlt_f_lqlttr105` | Databricks Uniformity table: uf_inspection_result | `gmes_query.py`, `q_iqm_plus.py` | PLANT, M_CODE, SPEC_CD, STXC, INS_DATE, RFV, LFV, CON, HAR, JDG_GR, INS_FG |
| `uf_inspection_standard` | `hkt_dw.quality.qlt_d_lcomtr201` | Databricks Uniformity table: uf_inspection_standard | `gmes_query.py` | PLANT, M_CODE, SPEC_CD, RFV_MAX, LFV_MAX, CON_MAX, HAR_MAX |
| `uf_db_standard` | `hkt_dw.quality.qlt_d_lcomtr202` | Databricks Uniformity table: uf_db_standard | `gmes_query.py` | PLANT, M_CODE, SPEC_CD, RFV_UCL, LFV_UCL, CON_UCL, HAR_UCL |

### 카테고리: Worksheet

| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |
|---|---|---|---|---|
| `worksheet_building_overall` | `hkt_dw.quality.qlt_d_loprtr178` | Databricks Worksheet table: worksheet_building_overall | None | PLANT, M_CODE, WORK_DATE, BUILD_QTY |

---

## SQLite Local Tables

### SQLite Database: LOG (`log.db`)

| 변수명 (Variable Name) | 실제 테이블명 (Table Name) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 컬럼 명세 (Columns Info) |
|---|---|---|---|---|
| `login_log` | `user_login` | SQLite log table: login_log | None | • <b>id</b> (INTEGER) [PK]<br>• <b>employee_id</b> (TEXT)<br>• <b>login_time</b> (TEXT) |

### SQLite Database: STAGING (`staging.db`)

| 변수명 (Variable Name) | 실제 테이블명 (Table Name) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 컬럼 명세 (Columns Info) |
|---|---|---|---|---|
| `prd_audit_spec_master` | `product_audit_spec_master` | -- Lv 2. Spec Master | `q_iqm_plus.py`, `sqlite_query.py` | • <b>MCODE</b> (TEXT)<br>• <b>YEAR</b> (INTEGER)<br>• <b>PLANT</b> (TEXT)<br>• <b>MP_GATE_DT</b> (TEXT)<br>• <b>MFG_MCODE</b> (TEXT)<br>• <b>RR_MCODE</b> (TEXT)<br>• <b>Remark</b> (TEXT)<br>• <b>Supply Status</b> (TEXT)<br>• <b>Car Maker</b> (TEXT)<br>• <b>Vehicle Model Local</b> (TEXT)<br>• <b>SPEC_CD</b> (TEXT)<br>• <b>STXC_1st</b> (TEXT)<br>• <b>RCPE_VER_1st</b> (TEXT)<br>• <b>VLDT_SRT_DATE_1st</b> (TEXT)<br>• <b>STXC</b> (TEXT)<br>• <b>RCPE_VER</b> (TEXT)<br>• <b>VLDT_SRT_DATE</b> (TEXT)<br>• <b>REVISION_COUNT</b> (TEXT)<br>• <b>MIN_WRK_DATE</b> (TEXT) |
| `prd_audit_pdrt` | `product_audit_pdrt` | -- Lv 2. Production Volume | `q_iqm_plus.py`, `sqlite_query.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>MASS_PERIOD</b> (INTEGER)<br>• <b>PRDT_QTY</b> (REAL) |
| `prd_audit_ncf` | `product_audit_ncf` | -- Lv 2. Nonconformity | None | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>SCRAP_DFT_QTY</b> (REAL)<br>• <b>SCRAP_RATE</b> (REAL)<br>• <b>SCRAP_INDEX</b> (REAL)<br>• <b>REWORK_DFT_QTY</b> (TEXT)<br>• <b>REWORK_RATE</b> (TEXT)<br>• <b>REWORK_INDEX</b> (TEXT) |
| `prd_audit_scrap` | `product_audit_scrap` | -- Lv 2. Scrap | `q_iqm_plus.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>SCRAP_DFT_QTY</b> (REAL)<br>• <b>SCRAP_RATE</b> (REAL)<br>• <b>SCRAP_INDEX</b> (REAL) |
| `prd_audit_rework` | `product_audit_rework` | -- Lv 2. Rework | `q_iqm_plus.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>REWORK_DFT_QTY</b> (REAL)<br>• <b>REWORK_RATE</b> (REAL)<br>• <b>REWORK_INDEX</b> (REAL) |
| `prd_audit_gt_wt` | `product_audit_gt_wt` | -- Lv 2. G/T Weight | `q_iqm_plus.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>GT_WT_PASS_COUNT</b> (INTEGER)<br>• <b>GT_WT_INS_COUNT</b> (INTEGER)<br>• <b>GT_WT_PASS_RATE</b> (REAL)<br>• <b>GT_WT_INDEX</b> (REAL) |
| `prd_audit_uf` | `product_audit_uf` | -- Lv 2. Uniformity | `q_iqm_plus.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>UF_PASS_COUNT</b> (INTEGER)<br>• <b>UF_INS_COUNT</b> (INTEGER)<br>• <b>UF_PASS_RATE</b> (REAL)<br>• <b>UF_INDEX</b> (REAL) |
| `prd_audit_rr` | `product_audit_rr` | -- Lv 2. RR | `q_iqm_plus.py` | • <b>RR_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>RR_AVG</b> (REAL)<br>• <b>RR_STD</b> (TEXT)<br>• <b>RR_COUNT</b> (INTEGER)<br>• <b>RR_SPEC_MAX</b> (REAL)<br>• <b>RR_SPEC_MIN</b> (TEXT)<br>• <b>RR_SIGMA_LEVEL</b> (TEXT)<br>• <b>RR_INDEX</b> (TEXT) |
| `prd_audit_ctl` | `product_audit_ctl` | -- Lv 2. CTL | `q_iqm_plus.py` | • <b>MFG_MCODE</b> (TEXT)<br>• <b>PERIOD_NAME</b> (TEXT)<br>• <b>CTL_COUNT</b> (INTEGER)<br>• <b>CTL_PASS_RATE_CUM</b> (REAL)<br>• <b>CTL_INDEX</b> (REAL) |
| `prd_audit_ctl_rawdata` | `product_audit_ctl_rawdata` | SQLite staging table: prd_audit_ctl_rawdata | `q_iqm_plus.py` | • <b>MEASUREMENT TYPE</b> (TEXT)<br>• <b>TIRE TYPE</b> (TEXT)<br>• <b>SIZE</b> (TEXT)<br>• <b>PATTERN</b> (TEXT)<br>• <b>USE CODE</b> (TEXT)<br>• <b>BRAND</b> (TEXT)<br>• <b>DATE</b> (TEXT)<br>• <b>REPORT NO.</b> (TEXT)<br>• <b>MFG SPEC</b> (TEXT)<br>• <b>CTL SPEC</b> (TEXT)<br>• <b>PURPOSE</b> (TEXT)<br>• <b>PLANT</b> (TEXT)<br>• <b>ITEM</b> (TEXT)<br>• <b>TOLERANCE</b> (TEXT)<br>• <b>SPECU</b> (TEXT)<br>• <b>SPECL</b> (TEXT)<br>• <b>MEASUREAVGU</b> (TEXT)<br>• <b>MEASUREAVGL</b> (TEXT)<br>• <b>MEASUREAVG</b> (TEXT)<br>• <b>OKNGU</b> (TEXT)<br>• <b>OKNGL</b> (TEXT)<br>• <b>OKNG</b> (TEXT)<br>• <b>M-CODE</b> (TEXT)<br>• <b>SPEC</b> (TEXT) |
| `sellin_monthly_agg` | `sellin_monthly_agg` | SQLite staging table: sellin_monthly_agg | `hope_query.py`, `sqlite_query.py` | • <b>RE/OE</b> (TEXT)<br>• <b>M_CODE</b> (TEXT)<br>• <b>YYYY</b> (TEXT)<br>• <b>MM</b> (TEXT)<br>• <b>SUPP_QTY</b> (INTEGER) |

### SQLite Database: OPS (`ops.db`)

| 변수명 (Variable Name) | 실제 테이블명 (Table Name) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 컬럼 명세 (Columns Info) |
|---|---|---|---|---|
| `hope_reg_dev` | `product_audit_regular_development` | -- Lv 0. 정규 개발 DB | `sqlite_query.py` | • <b>No.</b> (INTEGER)<br>• <b>Project Group</b> (TEXT)<br>• <b>Dev. Type</b> (TEXT)<br>• <b>Dev. Status</b> (TEXT)<br>• <b>OEM</b> (TEXT)<br>• <b>Project</b> (TEXT)<br>• <b>2Vehicle Group</b> (TEXT)<br>• <b>Vehicle</b> (TEXT)<br>• <b>KAM</b> (TEXT)<br>• <b>Team</b> (TEXT)<br>• <b>PM Name(Eng)</b> (TEXT)<br>• <b>PMO</b> (TEXT)<br>• <b>Project No.</b> (TEXT)<br>• <b>M-code</b> (INTEGER)<br>• <b>OE Component No.</b> (TEXT)<br>• <b>2Product Type </b> (TEXT)<br>• <b>Size</b> (TEXT)<br>• <b>Pattern</b> (TEXT)<br>• <b>Prod. Type</b> (TEXT)<br>• <b>Prod. Type.1</b> (TEXT)<br>• <b>PR</b> (INTEGER)<br>• <b>Plant</b> (TEXT)<br>• <b>OE Share</b> (TEXT)<br>• <b>OE Order Volume</b> (TEXT)<br>• <b>P Gate BP. End</b> (TEXT)<br>• <b>P Gate Act. End</b> (TEXT)<br>• <b>D Gate Pln End</b> (TEXT)<br>• <b>D Gate Act End</b> (TEXT)<br>• <b>Tech BP. End</b> (TEXT)<br>• <b>Tech Act. End</b> (TEXT)<br>• <b>V Gate BP. End</b> (TEXT)<br>• <b>V Gate Act. End</b> (TEXT)<br>• <b>ISIR BP. End</b> (TEXT)<br>• <b>ISIR Act. End</b> (TEXT)<br>• <b>MP Gate BP. End</b> (TEXT)<br>• <b>MP Gate Act. End</b> (TEXT)<br>• <b>SOP BP. End</b> (TEXT)<br>• <b>SOP Act. End</b> (TEXT) |
| `mcode_mapping_mgt` | `product_audit_mcode_master` | -- lv 1. MCODE Master DB | `q_iqm_plus.py`, `sqlite_query.py` | • <b>MCODE</b> (TEXT)<br>• <b>MFG_MCODE</b> (TEXT)<br>• <b>RR_MCODE</b> (TEXT)<br>• <b>DELETE_MCODE</b> (INTEGER)<br>• <b>Remark</b> (TEXT) |
| `fm_library` | `quality_issue_management` | SQLite ops table: fm_library | None | • <b>id</b> (INTEGER) [PK]<br>• <b>category</b> (TEXT)<br>• <b>non_conformity_classification</b> (TEXT)<br>• <b>cause_analysis_result</b> (TEXT)<br>• <b>occurrence_photo</b> (TEXT)<br>• <b>occurrence_location</b> (TEXT)<br>• <b>estimated_cause_process</b> (TEXT)<br>• <b>occurrence_frequency</b> (TEXT)<br>• <b>analysis_item</b> (TEXT)<br>• <b>occurrence_phenomenon_result</b> (TEXT)<br>• <b>created_at</b> (TIMESTAMP)<br>• <b>updated_at</b> (TIMESTAMP) |
