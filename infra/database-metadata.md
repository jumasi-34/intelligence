# 📊 데이터베이스 테이블 및 쿼리 메타데이터 명세서 (Integrated Database Metadata Specification)

> 이 문서는 `app/core/query/query_tables_metadata.json`에 일원화 관리되는 물리적 스펙과 비즈니스 논리 매핑 정보(한글, 상수)를 바탕으로 자동 갱신된 단일 진실 공급원(SSOT) 기술 명세서입니다.
> AI 에이전트의 정밀 코딩 및 쿼리 생성, 하네스 검증 시 스키마 무결성 판단 기준으로 사용됩니다.

## 📈 메타데이터 통계
- **전체 관리 테이블 수**: 86 개
  - ☁️ Databricks Cloud Tables: 71 개
  - 💾 SQLite Local Tables: 15 개
  - 🚀 현재 활성화(사용 중) 테이블 수: 61 개

---

## ☁️ Databricks Cloud Tables

### 📁 분류: CQMS

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `cqms_4m_main` | **CQMS 4M 설계 및 생산 변경 요청 마스터 정보** | `hkt_system_dw.eqms.cqms_change_m` | ✅ 사용 | `cqms_query.py` |
| `cqms_4m_mcode` | **CQMS 4M 변경건에 대한 대상 자재 매핑 상세 이력** | `hkt_system_dw.eqms.cqms_sub_mcode_d` | ✅ 사용 | `cqms_query.py` |
| `cqms_attach_file` | **Databricks cqms_attach_file 테이블 데이터** | `hkt_system_dw.eqms.cqms_attach_file_onedrive` | ❌ 미사용 | - |
| `cqms_audit_main` | **CQMS 외부/고객사 품질 감사(Audit) 실적 정보** | `hkt_system_dw.eqms.cqms_customer_audit` | ✅ 사용 | `cqms_query.py` |
| `cqms_audit_mcode` | **CQMS 외부 감사 대상 자재 매핑 정보** | `hkt_system_dw.eqms.cqms_customer_audit_material` | ✅ 사용 | `cqms_query.py` |
| `cqms_quality_breakdown` | **CQMS 품질 불량 파손 부위 유형 코드 매핑** | `hkt_system_dw.eqms.cqms_quality_issue_break_down` | ❌ 미사용 | - |
| `cqms_quality_category` | **CQMS 품질 이슈 유형 및 카테고리 마스터 코드** | `hkt_system_dw.eqms.cqms_issue_category_data_oere` | ✅ 사용 | `cqms_query.py` |
| `cqms_quality_d1team` | **Databricks cqms_quality_d1team 테이블 데이터** | `hkt_system_dw.eqms.cqms_quality_issue_d1_team` | ❌ 미사용 | - |
| `cqms_quality_d7prevent` | **Databricks cqms_quality_d7prevent 테이블 데이터** | `hkt_system_dw.eqms.cqms_quality_issue_d7_prevent` | ❌ 미사용 | - |
| `cqms_quality_main` | **CQMS 완성품 품질 이슈 및 클레임 내역 마스터** | `hkt_system_dw.eqms.cqms_quality_issue` | ✅ 사용 | `cqms_query.py` |
| `cqms_quality_mcode` | **CQMS 품질 이슈에 해당하는 영향 자재 매핑 정보** | `hkt_system_dw.eqms.cqms_quality_issue_material` | ✅ 사용 | `cqms_query.py` |
| `cqms_quality_rootcause` | **Databricks cqms_quality_rootcause 테이블 데이터** | `hkt_system_dw.eqms.cqms_quality_issue_root_cause` | ❌ 미사용 | - |
| `cqms_row_visibility` | **품질 문서 및 데이터 조회 가시성 제어 권한 테이블** | `hkt_system_dw.eqms.cqms_row_hide_show_m` | ❌ 미사용 | - |
| `cqms_row_visibility_log` | **품질 데이터 권한 조정 및 로그 열람 감사 추적 이력** | `hkt_system_dw.eqms.cqms_row_hide_show_m_log` | ❌ 미사용 | - |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `cqms_4m_main` (CQMS 4M 설계 및 생산 변경 요청 마스터 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `REQ_NO` | `VARCHAR` | `request_no` | 요청번호 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `REG_USER` | `VARCHAR` | `register_user` | 등록자 | - |
| `REG_DATE` | `TIMESTAMP` | `register_date` | 날짜/시간 | - |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `STATUS` | `VARCHAR` | `status` | 상태값 | 8개 상수 항목 매핑 |
| `CHG_REASON` | `VARCHAR` | `chg_reason` | 일반속성 | - |
| `CHG_DESC` | `VARCHAR` | `chg_desc` | 일반속성 | - |

#### 📑 `cqms_4m_mcode` (CQMS 4M 변경건에 대한 대상 자재 매핑 상세 이력)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `REQ_NO` | `VARCHAR` | `request_no` | 요청번호 | - |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `M_NAME` | `VARCHAR` | `m_name` | 일반속성 | - |

#### 📑 `cqms_attach_file` (Databricks cqms_attach_file 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_audit_main` (CQMS 외부/고객사 품질 감사(Audit) 실적 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `AUDIT_NO` | `VARCHAR` | `audit_no` | 감사번호 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `AUDIT_DATE` | `TIMESTAMP` | `audit_date` | 날짜/시간 | - |
| `AUDIT_USER` | `VARCHAR` | `audit_user` | 감사자 | - |
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `STATUS` | `VARCHAR` | `status` | 상태값 | 8개 상수 항목 매핑 |

#### 📑 `cqms_audit_mcode` (CQMS 외부 감사 대상 자재 매핑 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `AUDIT_NO` | `VARCHAR` | `audit_no` | 감사번호 | - |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |

#### 📑 `cqms_quality_breakdown` (CQMS 품질 불량 파손 부위 유형 코드 매핑)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `ISSUE_NO` | `VARCHAR` | `issue_no` | 품질이슈번호 | - |
| `BREAK_DOWN_CD` | `VARCHAR` | `break_down_cd` | 일반속성 | - |
| `BREAK_DOWN_NM` | `VARCHAR` | `break_down_nm` | 일반속성 | - |

#### 📑 `cqms_quality_category` (CQMS 품질 이슈 유형 및 카테고리 마스터 코드)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `CATEGORY_CD` | `VARCHAR` | `category_code` | 분류코드 | 11개 상수 항목 매핑 |
| `CATEGORY_NM` | `VARCHAR` | `category_nm` | 일반속성 | - |
| `PARENT_CD` | `VARCHAR` | `parent_cd` | 일반속성 | - |

#### 📑 `cqms_quality_d1team` (Databricks cqms_quality_d1team 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_quality_d7prevent` (Databricks cqms_quality_d7prevent 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_quality_main` (CQMS 완성품 품질 이슈 및 클레임 내역 마스터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `ISSUE_NO` | `VARCHAR` | `issue_no` | 품질이슈번호 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `REG_DATE` | `TIMESTAMP` | `register_date` | 날짜/시간 | - |
| `OCCUR_DATE` | `TIMESTAMP` | `occur_date` | 날짜/시간 | - |
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `DEFECT_CD` | `VARCHAR` | `defect_cd` | 일반속성 | - |
| `DEFECT_NM` | `VARCHAR` | `defect_nm` | 일반속성 | - |
| `DEFECT_QTY` | `DOUBLE` | `defect_qty` | 수량/실적 | - |
| `STATUS` | `VARCHAR` | `status` | 상태값 | 8개 상수 항목 매핑 |

#### 📑 `cqms_quality_mcode` (CQMS 품질 이슈에 해당하는 영향 자재 매핑 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `ISSUE_NO` | `VARCHAR` | `issue_no` | 품질이슈번호 | - |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `M_NAME` | `VARCHAR` | `m_name` | 일반속성 | - |

#### 📑 `cqms_quality_rootcause` (Databricks cqms_quality_rootcause 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_row_visibility` (품질 문서 및 데이터 조회 가시성 제어 권한 테이블)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `TABLE_NAME` | `VARCHAR` | `table_name` | 일반속성 | - |
| `ROW_ID` | `VARCHAR` | `row_id` | 일반속성 | - |
| `IS_VISIBLE` | `VARCHAR` | `is_visible` | 일반속성 | - |

#### 📑 `cqms_row_visibility_log` (품질 데이터 권한 조정 및 로그 열람 감사 추적 이력)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `TABLE_NAME` | `VARCHAR` | `table_name` | 일반속성 | - |
| `ROW_ID` | `VARCHAR` | `row_id` | 일반속성 | - |
| `ACTION` | `VARCHAR` | `action` | 일반속성 | - |
| `WORKER` | `VARCHAR` | `worker` | 일반속성 | - |
| `ACTION_DATE` | `TIMESTAMP` | `action_date` | 일반속성 | - |

</details>

### 📁 분류: CQMS Document

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `cqms_doc_brand_detail` | **Databricks cqms_doc_brand_detail 테이블 데이터** | `hkt_system_dw.eqms.oe_doc_cate_sales_brand_d` | ❌ 미사용 | - |
| `cqms_doc_brand_main` | **Databricks cqms_doc_brand_main 테이블 데이터** | `hkt_system_dw.eqms.oe_doc_cate_sales_brand_m` | ❌ 미사용 | - |
| `cqms_doc_code` | **Databricks cqms_doc_code 테이블 데이터** | `hkt_system_dw.eqms.oe_doc_cate_comm` | ❌ 미사용 | - |
| `cqms_doc_main` | **Databricks cqms_doc_main 테이블 데이터** | `hkt_system_dw.eqms.cqms_doc_m` | ❌ 미사용 | - |
| `cqms_doc_oem_detail` | **Databricks cqms_doc_oem_detail 테이블 데이터** | `hkt_system_dw.eqms.oe_doc_cate_d` | ❌ 미사용 | - |
| `cqms_doc_oem_main` | **Databricks cqms_doc_oem_main 테이블 데이터** | `hkt_system_dw.eqms.oe_doc_cate_m` | ❌ 미사용 | - |
| `cqms_doc_pp_detail` | **CQMS PP(Process Parameter) 제조 공정 처방 데이터 상세** | `hkt_system_dw.eqms.oe_doc_cate_pp_d` | ❌ 미사용 | - |
| `cqms_doc_pp_info` | **CQMS 공정 처방 규격 문서 상세 메타 속성** | `hkt_system_dw.eqms.oe_doc_cate_pp_info` | ❌ 미사용 | - |
| `cqms_doc_pp_main` | **CQMS 공정 파라미터 매핑 마스터 규격 관계 정보** | `hkt_system_dw.eqms.oe_doc_cate_pp_m` | ❌ 미사용 | - |
| `cqms_doc_revision` | **Databricks cqms_doc_revision 테이블 데이터** | `hkt_system_dw.eqms.cqms_doc_revision` | ❌ 미사용 | - |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `cqms_doc_brand_detail` (Databricks cqms_doc_brand_detail 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_brand_main` (Databricks cqms_doc_brand_main 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_code` (Databricks cqms_doc_code 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_main` (Databricks cqms_doc_main 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_oem_detail` (Databricks cqms_doc_oem_detail 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_oem_main` (Databricks cqms_doc_oem_main 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_pp_detail` (CQMS PP(Process Parameter) 제조 공정 처방 데이터 상세)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PP_NO` | `VARCHAR` | `pp_no` | 일반속성 | - |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cqms_doc_pp_info` (CQMS 공정 처방 규격 문서 상세 메타 속성)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PP_NO` | `VARCHAR` | `pp_no` | 일반속성 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `REG_DATE` | `TIMESTAMP` | `register_date` | 날짜/시간 | - |

#### 📑 `cqms_doc_pp_main` (CQMS 공정 파라미터 매핑 마스터 규격 관계 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PP_NO` | `VARCHAR` | `pp_no` | 일반속성 | - |
| `DOC_NO` | `VARCHAR` | `doc_no` | 문서번호 | - |
| `REVISION_NO` | `VARCHAR` | `revision_no` | 개정번호 | - |

#### 📑 `cqms_doc_revision` (Databricks cqms_doc_revision 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

</details>

### 📁 분류: CQMS IQM

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `cqms_iqm_main` | **CQMS IQM 정밀 품질 종합 부적합 판정 대장** | `hkt_system_dw.eqms.cqms_iqm_m` | ❌ 미사용 | - |
| `cqms_iqm_status` | **CQMS IQM 품질 판정 및 결재 진행 상황 추적** | `hkt_system_dw.eqms.cqms_iqm_status_m` | ❌ 미사용 | - |
| `cqms_iqm_test_item` | **CQMS IQM 품질 계측 정밀 시험 항목 물리 규격 스펙** | `hkt_system_dw.eqms.cqms_iqm_test_item_info` | ❌ 미사용 | - |
| `cqms_iqm_test_item_req` | **CQMS IQM 정밀 시험에서 요구되는 고객사 합격 조건 스펙** | `hkt_system_dw.eqms.cqms_iqm_test_item_info_req` | ❌ 미사용 | - |
| `cqms_iqm_test_main` | **CQMS IQM 품질 시험 측정 실행 마스터 기록** | `hkt_system_dw.eqms.cqms_iqm_test_m` | ❌ 미사용 | - |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `cqms_iqm_main` (CQMS IQM 정밀 품질 종합 부적합 판정 대장)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `IQM_NO` | `VARCHAR` | `iqm_no` | 일반속성 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `REG_DATE` | `TIMESTAMP` | `register_date` | 날짜/시간 | - |

#### 📑 `cqms_iqm_status` (CQMS IQM 품질 판정 및 결재 진행 상황 추적)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `IQM_NO` | `VARCHAR` | `iqm_no` | 일반속성 | - |
| `STATUS` | `VARCHAR` | `status` | 상태값 | 8개 상수 항목 매핑 |
| `UPDATE_DATE` | `TIMESTAMP` | `update_date` | 일반속성 | - |

#### 📑 `cqms_iqm_test_item` (CQMS IQM 품질 계측 정밀 시험 항목 물리 규격 스펙)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `IQM_NO` | `VARCHAR` | `iqm_no` | 일반속성 | - |
| `TEST_CD` | `VARCHAR` | `test_cd` | 일반속성 | - |
| `TEST_NM` | `VARCHAR` | `test_nm` | 일반속성 | - |
| `SPEC_VAL` | `DOUBLE` | `spec_val` | 일반속성 | - |

#### 📑 `cqms_iqm_test_item_req` (CQMS IQM 정밀 시험에서 요구되는 고객사 합격 조건 스펙)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `IQM_NO` | `VARCHAR` | `iqm_no` | 일반속성 | - |
| `TEST_CD` | `VARCHAR` | `test_cd` | 일반속성 | - |
| `REQ_VAL` | `DOUBLE` | `req_val` | 일반속성 | - |

#### 📑 `cqms_iqm_test_main` (CQMS IQM 품질 시험 측정 실행 마스터 기록)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `IQM_NO` | `VARCHAR` | `iqm_no` | 일반속성 | - |
| `TEST_DATE` | `TIMESTAMP` | `test_date` | 날짜/시간 | - |
| `TEST_USER` | `VARCHAR` | `test_user` | 일반속성 | - |

</details>

### 📁 분류: Common Master

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `barcode_record` | **제품 가류 바코드 단위 실시간 생산 이력 및 설비 이력** | `hkt_dw.production.wrk_f_lwrktr140` | ✅ 사용 | `ev3_query.py`, `gmes_query.py`, `hgws_return_query.py` |
| `mes_code_master` | **MES 생산설비 및 공정 운영에 활용되는 전사 공통 코드 마스터** | `hkt_dw.master.mst_d_lcomtr107` | ✅ 사용 | `gmes_query.py` |
| `product_master` | **전사 타이어 완제품 자재정보 마스터 (사이즈/패턴/규격 일치)** | `hkt_dw.specification.mas_d_lmastr101` | ✅ 사용 | `gmes_query.py`, `hgws_return_query.py`, `q_iqm_plus.py` |
| `production_volume` | **공장/일자/자재별 실 생산 수량 및 스크랩, 재작업 실적 집계** | `hkt_dw.production.wrk_f_lwrkts118` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |
| `spec_revision` | **제품 규격 스펙의 개정 이력 및 적용일자 관리** | `hkt_dw.specification.par_f_lmastr144` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `barcode_record` (제품 가류 바코드 단위 실시간 생산 이력 및 설비 이력)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `BARCODE_NO` | `VARCHAR` | `barcode_no` | 바코드번호 | - |
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `PROD_DATE` | `TIMESTAMP` | `production_date` | 날짜/시간 | - |
| `SHIFT_CD` | `VARCHAR` | `shift_code` | 근무교대조 | 3개 상수 항목 매핑 |
| `MACHINE_CD` | `VARCHAR` | `machine_code` | 설비코드 | - |

#### 📑 `mes_code_master` (MES 생산설비 및 공정 운영에 활용되는 전사 공통 코드 마스터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `CD_ITEM` | `VARCHAR` | `cd_item` | 일반속성 | - |
| `CD_ITEM_NM` | `VARCHAR` | `cd_item_nm` | 일반속성 | - |
| `CD_VAL` | `DOUBLE` | `cd_val` | 일반속성 | - |
| `CD_VAL_NM` | `DOUBLE` | `cd_val_nm` | 일반속성 | - |

#### 📑 `product_master` (전사 타이어 완제품 자재정보 마스터 (사이즈/패턴/규격 일치))
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `SIZE_CD` | `VARCHAR` | `size_code` | 사이즈코드 | - |
| `PATTERN_CD` | `VARCHAR` | `pattern_code` | 패턴코드 | - |
| `STXC` | `VARCHAR` | `stxc_val` | 규격값 | - |
| `SIZE_NAME` | `VARCHAR` | `size_name` | 사이즈명 | - |
| `PATTERN_NM` | `VARCHAR` | `pattern_name` | 패턴명 | - |

#### 📑 `production_volume` (공장/일자/자재별 실 생산 수량 및 스크랩, 재작업 실적 집계)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `WORK_DATE` | `TIMESTAMP` | `work_date` | 날짜/시간 | - |
| `PRDT_QTY` | `DOUBLE` | `production_qty` | 수량/실적 | - |
| `SCRAP_QTY` | `DOUBLE` | `scrap_qty` | 수량/실적 | - |
| `REWORK_QTY` | `DOUBLE` | `rework_qty` | 수량/실적 | - |

#### 📑 `spec_revision` (제품 규격 스펙의 개정 이력 및 적용일자 관리)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `REVISION_NO` | `VARCHAR` | `revision_no` | 개정번호 | - |
| `APPLY_DATE` | `TIMESTAMP` | `apply_date` | 일반속성 | - |

</details>

### 📁 분류: Nonconformity

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `finished_product_inspection_result` | **완제품 완성 단계 정밀 완성검사 부적합 이력** | `hkt_dw.quality.qlt_f_lqlttr107` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |
| `shipment_inspection_result` | **최종 완제품 출하 검사 품질 부적합(Defect) 판정 결과** | `hkt_dw.quality.qlt_f_lqlttr120` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `finished_product_inspection_result` (완제품 완성 단계 정밀 완성검사 부적합 이력)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `INS_DATE` | `TIMESTAMP` | `inspect_date` | 날짜/시간 | - |
| `DFT_CD` | `VARCHAR` | `defect_code` | 불량코드 | 26개 상수 항목 매핑 |
| `DFT_DESC` | `VARCHAR` | `dft_desc` | 일반속성 | - |
| `NCF_QTY` | `DOUBLE` | `nonconformity_qty` | 수량/실적 | - |

#### 📑 `shipment_inspection_result` (최종 완제품 출하 검사 품질 부적합(Defect) 판정 결과)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `INS_DATE` | `TIMESTAMP` | `inspect_date` | 날짜/시간 | - |
| `DFT_CD` | `VARCHAR` | `defect_code` | 불량코드 | 26개 상수 항목 매핑 |
| `DFT_DESC` | `VARCHAR` | `dft_desc` | 일반속성 | - |
| `NCF_QTY` | `DOUBLE` | `nonconformity_qty` | 수량/실적 | - |

</details>

### 📁 분류: Other Domain

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `cal_let_off_qrs` | **Databricks cal_let_off_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr127` | ✅ 사용 | `qrs_query.py` |
| `cal_op_qrs` | **Databricks cal_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr125` | ✅ 사용 | `qrs_query.py` |
| `cal_winding_qrs` | **Databricks cal_winding_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr126` | ✅ 사용 | `qrs_query.py` |
| `ctms` | **CTMS 원자재 품질 물리 계측 시험(Lab) 결과 정보** | `hkt_system_dw.tableau.ctms_result_data` | ✅ 사용 | `ctms_query.py`, `plm_query.py` |
| `cut_bec_op_qrs` | **Databricks cut_bec_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr139` | ✅ 사용 | `qrs_query.py` |
| `cut_bec_strip_op_qrs` | **Databricks cut_bec_strip_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr144` | ✅ 사용 | - |
| `cut_edge_sliter_qrs` | **Databricks cut_edge_sliter_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr142` | ✅ 사용 | `qrs_query.py` |
| `cut_mini_sliter_qrs` | **Databricks cut_mini_sliter_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr141` | ✅ 사용 | `qrs_query.py` |
| `cut_pcr_il_op_qrs` | **Databricks cut_pcr_il_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr137` | ✅ 사용 | `qrs_query.py` |
| `cut_sbc_op_qrs` | **Databricks cut_sbc_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr133` | ✅ 사용 | `qrs_query.py` |
| `cut_sheet_op_qrs` | **Databricks cut_sheet_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr143` | ✅ 사용 | `qrs_query.py` |
| `cut_src_op_qrs` | **Databricks cut_src_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr135` | ✅ 사용 | `qrs_query.py` |
| `cut_tbc_op_qrs` | **Databricks cut_tbc_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr136` | ✅ 사용 | `qrs_query.py` |
| `cut_tbr_il_op_qrs` | **Databricks cut_tbr_il_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr138` | ✅ 사용 | `qrs_query.py` |
| `cut_trc_op_qrs` | **Databricks cut_trc_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr134` | ✅ 사용 | `qrs_query.py` |
| `cut_wide_sliter_qrs` | **Databricks cut_wide_sliter_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr140` | ✅ 사용 | `qrs_query.py` |
| `ext_sidewall_op_qrs` | **Databricks ext_sidewall_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr122` | ✅ 사용 | `qrs_query.py` |
| `ext_tread_op_qrs` | **Databricks ext_tread_op_qrs 테이블 데이터** | `hkt_dw.quality.qlt_d_loprtr120` | ✅ 사용 | `qrs_query.py` |
| `gmes_rework_defect_raw` | **Databricks gmes_rework_defect_raw 테이블 데이터** | `hkt_dw.quality.qlt_f_lqltts112` | ❌ 미사용 | - |
| `gmes_uf_result_raw` | **Databricks gmes_uf_result_raw 테이블 데이터** | `hkt_quality.inspection.uniformity_result_raw` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |
| `hgws` | **HGWS 글로벌 클레임 청구 및 반품(Return) 이력** | `hkt_system_dw.tableau.sap_zsrt10000` | ✅ 사용 | `ev3_query.py`, `hgws_return_query.py` |
| `lot_track` | **가류 바코드 기준 생산 추적 및 원자재 추적 랏 트래킹** | `hkt_dw.production.wrk_f_lwrktr140` | ✅ 사용 | `gmes_query.py` |
| `plm_spec_full` | **Databricks plm_spec_full 테이블 데이터** | `hkt_rnd_dw.full_specification.tb_pl_if_plmspec_rcx_bas` | ✅ 사용 | `plm_query.py` |
| `plm_spec_label` | **PLM 규격 내 타이어 라벨 스펙 정보 및 관리 공차** | `hkt_rnd_dw.specification.tb_pl_dw_spec_pd_item_label_bas` | ✅ 사용 | `gmes_query.py` |
| `rpa_test_result` | **RPA 기기 계측 품질 시험 이력 및 자동 판정 등급** | `hkt_dw.quality.qlt_f_lqlttr268` | ✅ 사용 | `gmes_query.py` |
| `tdr` | **TDR 개발 사양 및 원자재 물리 특성 설계 마스터** | `hkt_system_dw.tdr.v_gate_document_to_oda` | ❌ 미사용 | - |
| `worksheet_building_overall` | **생산 성형 공정 종합 집계 작업 보고 시트** | `hkt_dw.quality.qlt_d_loprtr178` | ❌ 미사용 | - |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `cal_let_off_qrs` (Databricks cal_let_off_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cal_op_qrs` (Databricks cal_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cal_winding_qrs` (Databricks cal_winding_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `ctms` (CTMS 원자재 품질 물리 계측 시험(Lab) 결과 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `TEST_DATE` | `TIMESTAMP` | `test_date` | 날짜/시간 | - |
| `CTL_VALUE` | `DOUBLE` | `ctl_value` | 일반속성 | - |
| `DIRECTION` | `VARCHAR` | `direction_flag` | 상태값 | - |
| `UPPER_VAL` | `DOUBLE` | `upper_val` | 일반속성 | - |
| `LOWER_VAL` | `DOUBLE` | `lower_val` | 일반속성 | - |

#### 📑 `cut_bec_op_qrs` (Databricks cut_bec_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_bec_strip_op_qrs` (Databricks cut_bec_strip_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_edge_sliter_qrs` (Databricks cut_edge_sliter_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_mini_sliter_qrs` (Databricks cut_mini_sliter_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_pcr_il_op_qrs` (Databricks cut_pcr_il_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_sbc_op_qrs` (Databricks cut_sbc_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_sheet_op_qrs` (Databricks cut_sheet_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_src_op_qrs` (Databricks cut_src_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_tbc_op_qrs` (Databricks cut_tbc_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_tbr_il_op_qrs` (Databricks cut_tbr_il_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_trc_op_qrs` (Databricks cut_trc_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `cut_wide_sliter_qrs` (Databricks cut_wide_sliter_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `ext_sidewall_op_qrs` (Databricks ext_sidewall_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `ext_tread_op_qrs` (Databricks ext_tread_op_qrs 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `gmes_rework_defect_raw` (Databricks gmes_rework_defect_raw 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `gmes_uf_result_raw` (Databricks gmes_uf_result_raw 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `hgws` (HGWS 글로벌 클레임 청구 및 반품(Return) 이력)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `WERKS` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `RETURN_DATE` | `TIMESTAMP` | `return_date` | 날짜/시간 | - |
| `RETURN_QTY` | `DOUBLE` | `return_qty` | 수량/실적 | - |
| `CLAIM_CD` | `VARCHAR` | `claim_code` | 클레임코드 | 23개 상수 항목 매핑 |
| `CLAIM_DESC` | `VARCHAR` | `claim_desc` | 일반속성 | - |
| `ZAREA` | `VARCHAR` | `country_area` | 지역코드 | 5개 상수 항목 매핑 |

#### 📑 `lot_track` (가류 바코드 기준 생산 추적 및 원자재 추적 랏 트래킹)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `BARCODE_NO` | `VARCHAR` | `barcode_no` | 바코드번호 | - |
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `PROD_DATE` | `TIMESTAMP` | `production_date` | 날짜/시간 | - |

#### 📑 `plm_spec_full` (Databricks plm_spec_full 테이블 데이터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |

#### 📑 `plm_spec_label` (PLM 규격 내 타이어 라벨 스펙 정보 및 관리 공차)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `ITEM_LABEL` | `VARCHAR` | `item_label` | 일반속성 | - |
| `UCL_VAL` | `DOUBLE` | `ucl_val` | 일반속성 | - |
| `LCL_VAL` | `DOUBLE` | `lcl_val` | 일반속성 | - |

#### 📑 `rpa_test_result` (RPA 기기 계측 품질 시험 이력 및 자동 판정 등급)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `TEST_DATE` | `TIMESTAMP` | `test_date` | 날짜/시간 | - |
| `TAND_VAL` | `DOUBLE` | `tand_val` | 일반속성 | - |
| `GRADE` | `VARCHAR` | `grade` | 품질등급 | 4개 상수 항목 매핑 |

#### 📑 `tdr` (TDR 개발 사양 및 원자재 물리 특성 설계 마스터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `DOC_NO` | `VARCHAR` | `doc_no` | 문서번호 | - |
| `TITLE` | `VARCHAR` | `title` | 텍스트 | - |
| `REG_DATE` | `TIMESTAMP` | `register_date` | 날짜/시간 | - |

#### 📑 `worksheet_building_overall` (생산 성형 공정 종합 집계 작업 보고 시트)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `WORK_DATE` | `TIMESTAMP` | `work_date` | 날짜/시간 | - |
| `BUILD_QTY` | `DOUBLE` | `build_qty` | 일반속성 | - |

</details>

### 📁 분류: Production

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `building_manufacture_report` | **반제품 성형(Building) 공정 실 생산량 및 설비 보고 정보** | `hkt_dw.quality.qlt_f_lqlttr127` | ✅ 사용 | `gmes_query.py`, `q_iqm_plus.py` |
| `production_machine` | **생산 설비 가동 시간 및 가동 실적 매핑 정보** | `hkt_dw.production.wrk_f_lwrktr106` | ✅ 사용 | `gmes_query.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `building_manufacture_report` (반제품 성형(Building) 공정 실 생산량 및 설비 보고 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `WORK_DATE` | `TIMESTAMP` | `work_date` | 날짜/시간 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `PRDT_QTY` | `DOUBLE` | `production_qty` | 수량/실적 | - |

#### 📑 `production_machine` (생산 설비 가동 시간 및 가동 실적 매핑 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `WORK_DATE` | `TIMESTAMP` | `work_date` | 날짜/시간 | - |
| `MACHINE_CD` | `VARCHAR` | `machine_code` | 설비코드 | - |
| `PRDT_QTY` | `DOUBLE` | `production_qty` | 수량/실적 | - |

</details>

### 📁 분류: Rolling Resistance

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `rr_lot_samples` | **RR(Rolling Resistance, 회전저항) 품질 측정 샘플 랏 정보** | `hkt_dw.quality.qlt_d_lqlttr309` | ✅ 사용 | `gmes_query.py` |
| `rr_standard` | **차종/고객사별 RR 스펙 표준값 및 허용 한계(UCL/LCL) 마스터** | `hkt_dw.quality.qlt_d_lqlttr510` | ✅ 사용 | `gmes_query.py` |
| `rr_test_result` | **RR 품질 검사 실 계측 데이터 및 등재 첨부파일** | `hkt_dw.quality.qlt_f_lqlttr316` | ✅ 사용 | `gmes_query.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `rr_lot_samples` (RR(Rolling Resistance, 회전저항) 품질 측정 샘플 랏 정보)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `BARCODE_NO` | `VARCHAR` | `barcode_no` | 바코드번호 | - |
| `PGS_STS` | `VARCHAR` | `progress_status` | 상태값 | 4개 상수 항목 매핑 |
| `INS_DATE` | `TIMESTAMP` | `inspect_date` | 날짜/시간 | - |
| `RR_VALUE` | `DOUBLE` | `rr_value` | 일반속성 | - |
| `GRADE` | `VARCHAR` | `grade` | 품질등급 | 4개 상수 항목 매핑 |

#### 📑 `rr_standard` (차종/고객사별 RR 스펙 표준값 및 허용 한계(UCL/LCL) 마스터)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `CAR_MAKER` | `VARCHAR` | `car_maker` | 일반속성 | - |
| `VEHICLE` | `VARCHAR` | `vehicle` | 일반속성 | - |
| `UCL` | `DOUBLE` | `ucl` | 일반속성 | - |
| `LCL` | `DOUBLE` | `lcl` | 일반속성 | - |

#### 📑 `rr_test_result` (RR 품질 검사 실 계측 데이터 및 등재 첨부파일)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `BARCODE_NO` | `VARCHAR` | `barcode_no` | 바코드번호 | - |
| `INS_DATE` | `TIMESTAMP` | `inspect_date` | 날짜/시간 | - |
| `RR_VALUE` | `DOUBLE` | `rr_value` | 일반속성 | - |
| `GRADE` | `VARCHAR` | `grade` | 품질등급 | 4개 상수 항목 매핑 |
| `ATTACH_FILE_NAME` | `VARCHAR` | `attach_file_name` | 일반속성 | - |

</details>

### 📁 분류: Uniformity

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블 경로 (Table Path) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `uf_db_standard` | **유니포미티 통계적 관리 한계치(UCL/LCL) 기준값** | `hkt_dw.quality.qlt_d_lcomtr202` | ✅ 사용 | `gmes_query.py` |
| `uf_inspection_result` | **완제품 유니포미티(Uniformity) 품질 계측 정밀 결과** | `hkt_dw.quality.qlt_f_lqlttr105` | ✅ 사용 | `gmes_query.py` |
| `uf_inspection_standard` | **유니포미티 물리 측정 규격 한계 최대치 기준값** | `hkt_dw.quality.qlt_d_lcomtr201` | ✅ 사용 | `gmes_query.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `uf_db_standard` (유니포미티 통계적 관리 한계치(UCL/LCL) 기준값)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `RFV_UCL` | `DOUBLE` | `rfv_ucl` | 일반속성 | - |
| `LFV_UCL` | `DOUBLE` | `lfv_ucl` | 일반속성 | - |
| `CON_UCL` | `DOUBLE` | `con_ucl` | 일반속성 | - |
| `HAR_UCL` | `DOUBLE` | `har_ucl` | 일반속성 | - |

#### 📑 `uf_inspection_result` (완제품 유니포미티(Uniformity) 품질 계측 정밀 결과)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `STXC` | `VARCHAR` | `stxc_val` | 규격값 | - |
| `INS_DATE` | `TIMESTAMP` | `inspect_date` | 날짜/시간 | - |
| `RFV` | `DOUBLE` | `rfv` | 일반속성 | - |
| `LFV` | `DOUBLE` | `lfv` | 일반속성 | - |
| `CON` | `DOUBLE` | `con` | 일반속성 | - |
| `HAR` | `DOUBLE` | `har` | 일반속성 | - |
| `JDG_GR` | `VARCHAR` | `judge_grade` | 품질등급 | 4개 상수 항목 매핑 |
| `INS_FG` | `VARCHAR` | `inspect_flag` | 상태값 | 1개 상수 항목 매핑 |

#### 📑 `uf_inspection_standard` (유니포미티 물리 측정 규격 한계 최대치 기준값)
| 컬럼명 (Column) | 물리 타입 (Type) | 별칭 추천 (Recommended Alias) | 대분류 (Category) | 매핑 상수 (Value Constants) |
|---|---|---|---|---|
| `PLANT` | `VARCHAR` | `plant_code` | 공장코드 | 8개 상수 항목 매핑 |
| `M_CODE` | `VARCHAR` | `material_code` | 자재코드 | - |
| `SPEC_CD` | `VARCHAR` | `spec_code` | 규격코드 | - |
| `RFV_MAX` | `DOUBLE` | `rfv_max` | 일반속성 | - |
| `LFV_MAX` | `DOUBLE` | `lfv_max` | 일반속성 | - |
| `CON_MAX` | `DOUBLE` | `con_max` | 일반속성 | - |
| `HAR_MAX` | `DOUBLE` | `har_max` | 일반속성 | - |

</details>

---

## 💾 SQLite Local Tables

### 🗄️ Database: Log Database

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블명 (Table) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `login_log` | **로컬 사용자 시스템 로그인 이력 세션 데이터** | `user_login` | ✅ 사용 | - |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `login_log` (로컬 사용자 시스템 로그인 이력 세션 데이터)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `id` | `INTEGER` | 🔑 | - | `-` | `id` | 일반속성 |
| `employee_id` | `TEXT` | - | Y | `-` | `employee_id` | 일반속성 |
| `login_time` | `TEXT` | - | Y | `-` | `login_time` | 일반속성 |

</details>

### 🗄️ Database: Operational Database

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블명 (Table) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `fm_library` | **현장 이상 발생 라이브러리 및 불량 발생 사진 매핑 테이블** | `quality_issue_management` | ✅ 사용 | - |
| `prd_audit_ctl_rawdata` | **SQLite prd_audit_ctl_rawdata 테이블 데이터** | `product_audit_ctl_rawdata` | ✅ 사용 | `q_iqm_plus.py` |
| `sellin_monthly_agg` | **Sell-in 대리점 공급 실적 월별 수동 집계 정보** | `sellin_monthly_agg` | ✅ 사용 | `hope_query.py`, `sqlite_query.py` |
| `sqliteOps_iqm_devSpecList` | **SQLite sqliteOps_iqm_devSpecList 테이블 데이터** | `product_audit_regular_development` | ✅ 사용 | `sqlite_query.py` |
| `sqliteOps_iqm_mcodeMapping` | **SQLite sqliteOps_iqm_mcodeMapping 테이블 데이터** | `product_audit_mcode_master` | ✅ 사용 | `q_iqm_plus.py`, `sqlite_query.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `fm_library` (현장 이상 발생 라이브러리 및 불량 발생 사진 매핑 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `id` | `INTEGER` | 🔑 | - | `-` | `id` | 일반속성 |
| `category` | `TEXT` | - | Y | `-` | `category` | 일반속성 |
| `non_conformity_classification` | `TEXT` | - | - | `-` | `non_conformity_classification` | 일반속성 |
| `cause_analysis_result` | `TEXT` | - | - | `-` | `cause_analysis_result` | 일반속성 |

#### 📑 `prd_audit_ctl_rawdata` (SQLite prd_audit_ctl_rawdata 테이블 데이터)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `PLANT` | `VARCHAR` | - | - | `-` | `plant_code` | 공장코드 |
| `M_CODE` | `VARCHAR` | - | - | `-` | `material_code` | 자재코드 |
| `SPEC_CD` | `VARCHAR` | - | - | `-` | `spec_code` | 규격코드 |

#### 📑 `sellin_monthly_agg` (Sell-in 대리점 공급 실적 월별 수동 집계 정보)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `RE/OE` | `VARCHAR` | - | - | `-` | `re/oe` | 일반속성 |
| `M_CODE` | `VARCHAR` | - | - | `-` | `material_code` | 자재코드 |
| `YYYY` | `VARCHAR` | - | - | `-` | `yyyy` | 일반속성 |
| `MM` | `VARCHAR` | - | - | `-` | `mm` | 일반속성 |
| `SUPP_QTY` | `DOUBLE` | - | - | `-` | `supp_qty` | 일반속성 |

#### 📑 `sqliteOps_iqm_devSpecList` (SQLite sqliteOps_iqm_devSpecList 테이블 데이터)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `PLANT` | `VARCHAR` | - | - | `-` | `plant_code` | 공장코드 |
| `M_CODE` | `VARCHAR` | - | - | `-` | `material_code` | 자재코드 |
| `SPEC_CD` | `VARCHAR` | - | - | `-` | `spec_code` | 규격코드 |

#### 📑 `sqliteOps_iqm_mcodeMapping` (SQLite sqliteOps_iqm_mcodeMapping 테이블 데이터)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `PLANT` | `VARCHAR` | - | - | `-` | `plant_code` | 공장코드 |
| `M_CODE` | `VARCHAR` | - | - | `-` | `material_code` | 자재코드 |
| `SPEC_CD` | `VARCHAR` | - | - | `-` | `spec_code` | 규격코드 |

</details>

### 🗄️ Database: Staging Database

| 변수명 (Variable) | 한글 요약 (Description) | 실제 테이블명 (Table) | 사용 여부 | 주요 참조 쿼리 (Queries) |
|---|---|---|:---:|---|
| `sqliteStaging_iqm_ctl` | **IQM 플러스 CTL 시험 합격률 실적 중간 동기화 테이블** | `product_audit_ctl` | ✅ 사용 | `q_iqm_plus.py` |
| `sqliteStaging_iqm_gtWt` | **IQM 플러스 완성 중량(G/T Weight) 검사 합격 통계 테이블** | `product_audit_gt_wt` | ✅ 사용 | `q_iqm_plus.py` |
| `sqliteStaging_iqm_ncf` | **IQM 플러스 분석용 비정규 폐기/재작업률 중간 집계 테이블** | `product_audit_ncf` | ✅ 사용 | - |
| `sqliteStaging_iqm_prdt` | **IQM 플러스 수동 집계 대상 완제품 실 생산량 동기화 테이블** | `product_audit_pdrt` | ✅ 사용 | `q_iqm_plus.py`, `sqlite_query.py` |
| `sqliteStaging_iqm_rework` | **IQM 플러스 분석용 재작업(Rework) 발생 집계 테이블** | `product_audit_rework` | ✅ 사용 | `q_iqm_plus.py` |
| `sqliteStaging_iqm_rr` | **IQM 플러스 회전저항(RR) 시험 수치 및 분산 통계 집계 테이블** | `product_audit_rr` | ✅ 사용 | `q_iqm_plus.py` |
| `sqliteStaging_iqm_scrap` | **IQM 플러스 분석용 원자재 스크랩 집계 테이블** | `product_audit_scrap` | ✅ 사용 | `q_iqm_plus.py` |
| `sqliteStaging_iqm_specMaster` | **IQM 플러스 단계별 제품 개정 규격 정보 동기화 테이블** | `product_audit_spec_master` | ✅ 사용 | `q_iqm_plus.py`, `sqlite_query.py` |
| `sqliteStaging_iqm_uf` | **IQM 플러스 완제품 Uniformity 검사 합격률 통계 집계 테이블** | `product_audit_uf` | ✅ 사용 | `q_iqm_plus.py` |

<details>
<summary>🔍 분류 내 테이블별 상세 컬럼 스펙 열기</summary>

#### 📑 `sqliteStaging_iqm_ctl` (IQM 플러스 CTL 시험 합격률 실적 중간 동기화 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `CTL_COUNT` | `INTEGER` | - | - | `-` | `ctl_count` | 일반속성 |
| `CTL_PASS_RATE_CUM` | `REAL` | - | - | `-` | `ctl_pass_rate_cum` | 일반속성 |

#### 📑 `sqliteStaging_iqm_gtWt` (IQM 플러스 완성 중량(G/T Weight) 검사 합격 통계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `GT_WT_PASS_COUNT` | `INTEGER` | - | - | `-` | `gt_wt_pass_count` | 일반속성 |
| `GT_WT_INS_COUNT` | `INTEGER` | - | - | `-` | `gt_wt_ins_count` | 일반속성 |
| `GT_WT_PASS_RATE` | `REAL` | - | - | `-` | `gt_wt_pass_rate` | 일반속성 |

#### 📑 `sqliteStaging_iqm_ncf` (IQM 플러스 분석용 비정규 폐기/재작업률 중간 집계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `SCRAP_DFT_QTY` | `REAL` | - | - | `-` | `scrap_dft_qty` | 일반속성 |
| `SCRAP_RATE` | `REAL` | - | - | `-` | `scrap_rate` | 일반속성 |
| `REWORK_DFT_QTY` | `TEXT` | - | - | `-` | `rework_dft_qty` | 일반속성 |
| `REWORK_RATE` | `TEXT` | - | - | `-` | `rework_rate` | 일반속성 |

#### 📑 `sqliteStaging_iqm_prdt` (IQM 플러스 수동 집계 대상 완제품 실 생산량 동기화 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `MASS_PERIOD` | `INTEGER` | - | - | `-` | `mass_period` | 일반속성 |
| `PRDT_QTY` | `REAL` | - | - | `-` | `production_qty` | 수량/실적 |

#### 📑 `sqliteStaging_iqm_rework` (IQM 플러스 분석용 재작업(Rework) 발생 집계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `REWORK_DFT_QTY` | `REAL` | - | - | `-` | `rework_dft_qty` | 일반속성 |
| `REWORK_RATE` | `REAL` | - | - | `-` | `rework_rate` | 일반속성 |

#### 📑 `sqliteStaging_iqm_rr` (IQM 플러스 회전저항(RR) 시험 수치 및 분산 통계 집계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `RR_MCODE` | `TEXT` | - | - | `-` | `rr_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `RR_AVG` | `REAL` | - | - | `-` | `rr_avg` | 일반속성 |
| `RR_STD` | `TEXT` | - | - | `-` | `rr_std` | 일반속성 |
| `RR_COUNT` | `INTEGER` | - | - | `-` | `rr_count` | 일반속성 |
| `RR_SPEC_MAX` | `REAL` | - | - | `-` | `rr_spec_max` | 일반속성 |

#### 📑 `sqliteStaging_iqm_scrap` (IQM 플러스 분석용 원자재 스크랩 집계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `SCRAP_DFT_QTY` | `REAL` | - | - | `-` | `scrap_dft_qty` | 일반속성 |
| `SCRAP_RATE` | `REAL` | - | - | `-` | `scrap_rate` | 일반속성 |

#### 📑 `sqliteStaging_iqm_specMaster` (IQM 플러스 단계별 제품 개정 규격 정보 동기화 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MCODE` | `TEXT` | - | - | `-` | `mcode` | 일반속성 |
| `YEAR` | `INTEGER` | - | - | `-` | `year` | 일반속성 |
| `PLANT` | `TEXT` | - | - | `-` | `plant_code` | 공장코드 |
| `MP_GATE_DT` | `TEXT` | - | - | `-` | `mp_gate_dt` | 일반속성 |
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `SPEC_CD` | `TEXT` | - | - | `-` | `spec_code` | 규격코드 |
| `STXC` | `TEXT` | - | - | `-` | `stxc_val` | 규격값 |
| `RCPE_VER` | `TEXT` | - | - | `-` | `rcpe_ver` | 일반속성 |

#### 📑 `sqliteStaging_iqm_uf` (IQM 플러스 완제품 Uniformity 검사 합격률 통계 집계 테이블)
| 컬럼명 (Column) | 타입 (Type) | PK | Not Null | 기본값 (Default) | 추천 별칭 | 대분류 |
|---|---|:---:|:---:|---|---|---|
| `MFG_MCODE` | `TEXT` | - | - | `-` | `mfg_mcode` | 일반속성 |
| `PERIOD_NAME` | `TEXT` | - | - | `-` | `period_name` | 일반속성 |
| `UF_PASS_COUNT` | `INTEGER` | - | - | `-` | `uf_pass_count` | 일반속성 |
| `UF_INS_COUNT` | `INTEGER` | - | - | `-` | `uf_ins_count` | 일반속성 |
| `UF_PASS_RATE` | `REAL` | - | - | `-` | `uf_pass_rate` | 일반속성 |

</details>
