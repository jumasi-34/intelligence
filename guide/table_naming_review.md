# 테이블 변수명 네이밍 컨벤션 검토 보고서 (query_database.py)

본 보고서는 `app/core/query/query_database.py` 파일의 테이블 데이터 클래스(`DatabricksTables`, `SQLiteTables`) 및 해당 속성(테이블 변수명)들이 프로젝트 **L2 코드베이스 명명 규칙 표준([L2-naming-convention.md](file:///home/jumasi/workstation/intelligence/rules/L2-naming-convention.md))** 및 **[table_naming_convention.json](file:///home/jumasi/workstation/intelligence/rules/table_naming_convention.json)** 표준 가이드라인에 부합하는지 정밀 검토한 결과입니다.

---

## 1. 검토 요약 (Executive Summary)

검토 결과, 사용자의 지적대로 `app/core/query/query_database.py`의 테이블 변수명 중 상당수가 최신 **L2 명명 표준을 따르지 않고 레거시 명칭을 그대로 유지**하고 있음이 확인되었습니다.

* **DatabricksTables**: 
  - `cqms_*` 및 `plm_spec_*` 계열은 `{system}_{domain}_{contents}` 공식을 잘 준수하고 있습니다.
  - 그러나 `product_master`, `spec_revision` 등 공통/GMES 테이블과 `ext_tread_op_qrs` 등 `QRS` 계열 테이블은 접두사 누락, 접미사 혼용 등으로 규칙을 준수하지 않고 있습니다.
* **SQLiteTables**:
  - 판다스 데이터프레임 변수 명명 규칙(`sqliteStaging_` 등 카멜케이스)이 테이블 클래스의 정적 속성명에 오용되는 심각한 네이밍 불일치가 발견되었습니다.
* **영향도(Impact)**:
  - 이 변수명들은 런타임에 `query_metadata.json` 파일과 동적 바인딩(`_bind_metadata_to_classes`)될 뿐만 아니라, **`app/queries/` 하위의 모든 쿼리 빌더 파일에서 직접 참조**되고 있어, 단순 변수명 변경 시 전체 시스템에 `AttributeError`를 초래하는 대규모 영향도를 가지고 있습니다.
  - 따라서 `GEMINI.md`의 **Safety Lock(소스 코드 수정 제한)** 규칙에 의거하여, 본 분석 보고서를 선제적으로 제출하며 사용자의 명시적 승인 후 마이그레이션 작업을 일괄 또는 단계적으로 수행할 것을 제안합니다.

---

## 2. 세부 검토 및 컨벤션 불일치 항목 (Detailed Gap Analysis)

### ① `DatabricksTables` 클래스 내 분석

> **L2 표준 공식**: `{system}_{domain}_{contents}` (소문자 스네이크 케이스)

| 레거시 테이블 변수명 | 실제 물리적 테이블 경로 (Databricks) | 표준 부합 여부 | 권장 변경 (To-Be) | 미준수 사유 및 분석 |
| :--- | :--- | :---: | :--- | :--- |
| `product_master` | `hkt_dw.specification.mas_d_lmastr101` | **X** | `gmes_spec_product_master` | GMES 시스템의 스펙 도메인이므로 `gmes_spec_` 접두사가 와야 함. |
| `spec_revision` | `hkt_dw.specification.par_f_lmastr144` | **X** | `gmes_spec_revision` | 상동 |
| `mes_code_master` | `hkt_dw.master.mst_d_lcomtr107` | **X** | `gmes_mes_code_master` | `system=gmes`, `domain=mes`에 해당함. |
| `production_volume` | `hkt_dw.production.wrk_f_lwrkts118` | **X** | `gmes_prd_production_volume` | `system=gmes`, `domain=prd`에 해당함. |
| `barcode_record` | `hkt_dw.production.wrk_f_lwrktr140` | **X** | `gmes_barcode_record` | `system=gmes`, `domain=barcode`에 해당하며 접두사 누락. |
| `production_machine` | `hkt_dw.production.wrk_f_lwrktr106` | **X** | `gmes_mach_production_machine` | `system=gmes`, `domain=mach`에 해당함. |
| `building_manufacture_report` | `hkt_dw.quality.qlt_f_lqlttr127` | **X** | `gmes_build_manufacture_report` | `system=gmes`, `domain=build`에 해당함. |
| `rr_lot_samples` | `hkt_dw.quality.qlt_d_lqlttr309` | **X** | `gmes_rr_lot_samples` | GMES의 `rr` 품질 도메인이므로 `gmes_rr_` 접두사 필수. |
| `rr_test_result` | `hkt_dw.quality.qlt_f_lqlttr316` | **X** | `gmes_rr_test_result` | 상동 |
| `rr_standard` | `hkt_dw.quality.qlt_d_lqlttr510` | **X** | `gmes_rr_standard` | 상동 |
| `uf_inspection_result` | `hkt_dw.quality.qlt_f_lqlttr105` | **X** | `gmes_uf_inspection_result` | GMES의 `uf`(Uniformity) 도메인에 해당함. |
| `uf_inspection_standard` | `hkt_dw.quality.qlt_d_lcomtr201` | **X** | `gmes_uf_inspection_standard` | 상동 |
| `uf_db_standard` | `hkt_dw.quality.qlt_d_lcomtr202` | **X** | `gmes_uf_db_standard` | 상동 |
| `gmes_rework_defect_raw` | `hkt_dw.quality.qlt_f_lqltts112` | **X** | `gmes_ncf_rework_defect_raw` | `rework`는 정식 도메인이 아니며 불합격/품질 비적합성은 `ncf` 도메인에 속함. |
| `shipment_inspection_result` | `hkt_dw.quality.qlt_f_lqlttr120` | **X** | `gmes_ncf_shipment_inspection_result` | `system=gmes`, `domain=ncf`에 속함. |
| `finished_product_inspection_result`| `hkt_dw.quality.qlt_f_lqlttr107` | **X** | `gmes_ncf_finished_product_inspection_result`| 상동 |
| `worksheet_building_overall` | `hkt_dw.quality.qlt_d_loprtr178` | **X** | `gmes_build_worksheet_overall` | `system=gmes`, `domain=build` 혹은 `qrs_build_worksheet_overall`로 분류되어야 함. |
| `hgws` | `hkt_system_dw.tableau.sap_zsrt10000` | **X** | `hgws_general_result` (예시) | 별도 시스템 명시 및 도메인/내용 세분화 필요. |
| `ctms` | `hkt_system_dw.tableau.ctms_result_data` | **X** | `ctms_general_result` (예시) | 상동 |
| `oe_application` | `hkt_system_dw.tableau.sap_zstt70041` | **X** | `hope_oe_application` | `HOPE` 시스템 테이블로 접두사 및 세부내용 정합성 필요. |
| `ext_tread_op_qrs` / `cal_op_qrs` / `cut_trc_op_qrs` 등 (QRS 계열 14개) | `hkt_dw.quality.qlt_d_loprtr...` | **X** | `qrs_ext_tread_op`, `qrs_cal_op`, `qrs_cut_trc_op` 등 | QRS 시스템 테이블들이나 `qrs_`가 뒤에 접미사로 결합되고 도메인(`ext`, `cal`, `cut`)이 앞에 오는 주객전도 현상. `qrs_{domain}_{contents}` 공식으로 역정렬 필요. |
| `rpa_test_result` | `hkt_dw.quality.qlt_f_lqlttr268` | **X** | `gmes_rpa_test_result` | `system=gmes`, `domain=rpa`에 속함. |
| `lot_track` | `hkt_dw.production.wrk_f_lwrktr140` | **X** | `gmes_barcode_lot_track` (예시) | `system=gmes`, `domain=barcode`에 해당함. (물리 테이블이 `barcode_record`와 중복) |

---

## 2. SQLiteTables 클래스 내 분석

> **L2 표준 명명 위반**: 판다스 로딩 변수용 명명 공식(`sqliteStaging_iqm_specMaster` 등)을 테이블 클래스 내부 속성에 오용.

* **발견된 문제점**:
  - `sqliteStaging_` 및 `sqliteOps_` 형태는 `app/service/*_df.py`에서 **로컬 SQLite 데이터베이스 결과를 저장할 변수(`pd.DataFrame`)**를 명명할 때 사용하는 전용 공식입니다. (예: `sqliteStaging_iqm_specMaster = pd.read_sql(...)`)
  - 그러나 `query_database.py`는 **테이블명(문자열)을 보관하는 정적 데이터 클래스**입니다. 따라서 카멜케이스가 섞인 형태는 변수명 컨벤션에 정면 위배되며, 순수 소문자 스네이크 케이스 기반의 `{system}_{domain}_{contents}` 또는 SQLite의 성격(`sqlite_staging_`, `sqlite_ops_`)을 투명하게 반영하는 명칭이어야 합니다.

| 레거시 테이블 변수명 | 실제 SQLite 테이블명 | 권장 변경 (To-Be) | 비고 |
| :--- | :--- | :--- | :--- |
| `sqliteStaging_iqm_specMaster` | `product_audit_spec_master` | `sqlite_staging_iqm_spec_master` | 스네이크 케이스 통일 |
| `sqliteStaging_iqm_prdt` | `product_audit_pdrt` | `sqlite_staging_iqm_prdt` | 상동 |
| `sqliteStaging_iqm_ncf` | `product_audit_ncf` | `sqlite_staging_iqm_ncf` | 상동 |
| `sqliteStaging_iqm_scrap` | `product_audit_scrap` | `sqlite_staging_iqm_scrap` | 상동 (삭제대기 주석 포함) |
| `sqliteOps_iqm_devSpecList` | `product_audit_regular_development` | `sqlite_ops_iqm_dev_spec_list` | 상동 |
| `sqliteOps_iqm_mcodeMapping` | `product_audit_mcode_master` | `sqlite_ops_iqm_mcode_mapping` | 상동 |
| `fm_library` | `quality_issue_management` | `sqlite_ops_fm_library` | SQLite `ops` 테이블 정보 명시 |

---

## 3. 마이그레이션 시 영향도 평가 (Impact Analysis)

만약 `query_database.py` 내의 미준수 테이블 변수명들을 일괄 수정할 경우, 아래 구성요소들의 연쇄 수정이 불가피합니다.

### ① 메타데이터 파일 동기화 (`query_metadata.json`)
* `query_database.py` 하단부의 `_bind_metadata_to_classes()` 함수는 `query_metadata.json`의 키와 데이터 클래스 속성을 1:1로 매칭합니다.
* 따라서 파이썬 코드 수정 시, **`query_metadata.json`에 정의된 50여 개의 대형 키 명칭 역시 동시 변경**되어야 합니다.

### ② 쿼리 레이어 참조 파일 (`app/queries/*.py`)
* `DatabricksTables`를 정적으로 임포트하여 SQL을 생성하는 약 10개 이상의 쿼리 빌더 파일의 파이썬 코드 전체 수정이 동반됩니다.
* **영향을 받는 주요 파일**:
  - [cqms_query.py](file:///home/jumasi/workstation/app/queries/cqms_query.py) (cqms, oe_application 관련 참조)
  - [gmes_query.py](file:///home/jumasi/workstation/app/queries/gmes_query.py) (product_master, rr_*, uf_*, shipment_* 등 수십 개 최다 참조)
  - [ctms_query.py](file:///home/jumasi/workstation/app/queries/ctms_query.py) (ctms 테이블 참조)

### ③ Streamlit 페이지 어드민 화면 (`app/pages/_80_admin/`)
* 테이블의 전체 정보를 검사하거나 디버깅하는 어드민 화면 역시 데이터 클래스의 속성 필드들을 리플렉션(`fields(DatabricksTables)`)하여 활용하고 있습니다.
* **영향을 받는 화면 코드**:
  - [db_table_explorer_page.py](file:///home/jumasi/workstation/app/pages/_80_admin/db_table_explorer_page.py)
  - [analysis_individual_page.py](file:///home/jumasi/workstation/app/pages/_80_admin/analysis_individual_page.py)

---

## 4. 제안하는 액션 플랜 (Action Plan Suggestions)

이러한 대규모 영향도를 안전하게 관리하기 위해 두 가지 방식 중 하나를 제안합니다.

### [방식 A] 점진적 마이그레이션 (하위 호환성 유지) - 권장 🌟
* `query_database.py` 내에 **기존 레거시 변수명을 프로퍼티(Property)나 별칭(Alias)으로 존치**시키고, 표준을 따르는 신규 변수명을 정식 추가합니다.
* `query_metadata.json`에도 임시로 두 키 모두를 수용할 수 있게 설계하여, 기존 프로덕션 코드에 영향 없이 순차적으로 쿼리 레이어들을 고쳐나갑니다.
* 모든 쿼리 파일 마이그레이션이 완료된 시점에 최종적으로 레거시 변수명을 제거합니다.

### [방식 B] 일괄 단일 커밋 마이그레이션
* 전체 파일의 모든 참조를 한 번에 교체하는 방식으로, 변경 스코프가 대단히 큽니다.
* 수동으로 수정할 경우 실수할 가능성이 높으므로 자동 변환 스크립트 작성 및 테스트 하네스를 통한 철저한 안전 검증이 필요합니다.

---

## 5. 피드백 및 승인 요청 (Feedback Request)

> [!IMPORTANT]
> `GEMINI.md` 안전 장치 수칙에 따라, 사용자의 명시적인 승인 또는 세부 방향성 결정(예: "방식 A로 순차 진행하라", "방식 B로 자동 수정하라" 등)이 내려질 때까지는 프로덕션 코드를 변경하지 않고 대기합니다.
> 어떤 방식을 선호하시는지 하단의 질문 항목이나 텍스트를 통해 알려주시면 맞춰서 완벽하게 조치하겠습니다.
