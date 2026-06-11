# 📊 쿼리 모듈 메타데이터 준수 정밀 검증 보고서
> **문서 상태**: 검증 완료  
> **검증 대상**: `app/queries/` 하위 전수 모듈  
> **기준 사양**: `app/core/query/query_tables_metadata.json` (테이블 메타데이터)

---

## 1. 검증 개요

본 보고서는 `app/queries/` 디렉터리에 구현된 쿼리 모듈들이 핵심 메타데이터 정의서인 `app/core/query/query_tables_metadata.json`의 설계 표준을 충실히 준수하며 개발되었는지 검증한 결과입니다. 

자동화된 정적 코드 분석(AST 및 정규식)과 비즈니스 상수 매핑 검증 기법을 활용하여 아래 4가지 관점을 정밀하게 진단하였습니다.

1. **스키마 정의 정합성**: 메타데이터 JSON과 `app/core/query/query_database.py` 테이블 매핑 클래스의 1:1 일치 여부
2. **테이블 사용성 (`is_used`)**: 메타데이터상의 사용 여부 플래그와 실제 쿼리 코드 내 참조 여부의 일치성
3. **추천 컬럼 별칭 (`recommended_alias`)**: 쿼리 SELECT 문에서 메타데이터의 추천 앨리어스를 준수하는지 여부
4. **값 상수 (`value_constants`)**: 테이블 컬럼별 가용 상태값/상수 정의가 실제 현업 비즈니스 상수와 부합하는지 여부

---

## 2. 핵심 검증 결과 요약

| 검증 영역 | 평가 결과 | 발견된 주요 이슈 및 특징 |
| :--- | :---: | :--- |
| **1. 스키마 정의 정합성** | **⚠️ 부분 불일치** | 메타데이터 JSON에 등록되지 않은 채 `query_database.py`에만 추가된 신규 테이블 **7건** 감지. |
| **2. 테이블 사용성 (`is_used`)** | **⚠️ 불일치 (4건)** | 메타데이터에는 `is_used: true`로 되어 있으나 쿼리 코드에서 미사용 중인 테이블 **4건** 감지. |
| **3. 추천 컬럼 별칭 준수** | **🚨 미준수 다수 (127건)** | 쿼리 내에서 `PLANT`, `M_CODE`, `SPEC_CD` 등을 조회할 때 메타데이터의 `recommended_alias` (`plant_code`, `material_code`, `spec_code`)로 변환(AS)하지 않고 raw 컬럼명을 그대로 조회하는 패턴이 지배적임. |
| **4. 값 상수 일치성** | **⚠️ 부분 불일치 (2건)** | 품질 이슈 마스터 및 외부 감사 테이블의 `STATUS` 상수가 4M의 상태 코드 사양을 잘못 복사한 오류(000~007)로 추정됨. 실제 비즈니스에서는 텍스트 상태값(`On-going` 등)을 사용 중. |

---

## 3. 검증 영역별 상세 분석 결과

### 🔍 [검증 1] 메타데이터 VS `query_database.py` 매핑 불일치
* **메타데이터 대비 누락 테이블 (7건)**: 
  `query_database.py`에는 활발하게 선언되어 활용되고 있으나, 기준 메타데이터 JSON 파일에는 아예 정의 스키마가 누락된 테이블들입니다.
  1. `oe_application` (hkt_system_dw.tableau.sap_zstt70041)
  2. `iqm_mcode_datasheet` (product_audit_mcode_data)
  3. `cqms_doc_brand_pp_info` (hkt_system_dw.eqms.oe_doc_cate_sales_brand_pp_info)
  4. `ref_hk_personnel_info` (hkt_dw.master.mst_d_lcomtr108_p)
  5. `cqms_doc_brand_pp_detail` (hkt_system_dw.eqms.oe_doc_cate_sales_brand_pp_d)
  6. `prd_audit_iqm_plus_agg_cum` (product_audit_iqm_plus_agg_cum)
  7. `cqms_doc_brand_pp_main` (hkt_system_dw.eqms.oe_doc_cate_sales_brand_pp_m)

> [!WARNING]
> 누락된 테이블들은 신규 기능 개발 또는 마이그레이션 도중 메타데이터 문서 업데이트가 누락된 대표적인 사례입니다. 특히 실적 데이터 집계에 쓰이는 `prd_audit_iqm_plus_agg_cum` 및 `iqm_mcode_datasheet`에 대한 메타데이터 보완이 시급합니다.

---

### 🔄 [검증 2] 테이블 사용성 (`is_used`) 불일치 (4건)
메타데이터 설계 상으로는 사용 중(`is_used: true`)으로 분류되었으나, `app/queries/` 하위 파이썬 쿼리 빌더 전수 조사 결과 단 한 번도 호출되지 않은 유령 테이블들입니다.

1. `cut_bec_strip_op_qrs` (정의됨, 쿼리 내 미사용)
2. `login_log` (Streamlit 세션 로깅용 등으로 사용될 수 있으나 쿼리 레이어인 `app/queries` 내에는 사용 안 됨)
3. `sqliteStaging_iqm_ncf` (stage용 정기 집계 테이블이나 실제 쿼리에서는 우회되거나 미참조)
4. `fm_library` (정의만 존재하고 미사용)

> [!TIP]
> 반대로 메타데이터상 `is_used: false` 로 기록된 비활성 테이블들이 쿼리 내에서 역으로 오용되는 정황은 식별되지 않았습니다. 즉, 비사용 테이블의 안전 제어는 원활합니다.

---

### 🚨 [검증 3] 추천 컬럼 별칭 (`recommended_alias`) 미준수 분석 (127건)
가장 높은 불일치율을 보인 영역입니다. `query_tables_metadata.json` 에는 각 테이블의 주요 컬럼들을 조회할 때 아래와 같이 의미 있는 카멜케이스/스네이크케이스 별칭으로 변환하도록 권장하고 있습니다.

* **대표 권장 앨리어싱 예시**:
  * `PLANT` ➡️ `plant_code`
  * `M_CODE` ➡️ `material_code`
  * `SPEC_CD` ➡️ `spec_code`
  * `PRDT_QTY` ➡️ `production_qty`
  * `STXC` ➡️ `stxc_val`

* **현황**:
  실제 `app/queries/` 하위 모듈(특히 `q_iqm_plus.py`, `qrs_query.py`, `plm_query.py`)에서는 해당 컬럼들을 SELECT 문에서 전혀 앨리어싱(Alias)하지 않고 **`PLANT`, `M_CODE`, `SPEC_CD` 형태의 원시 컬럼명 그대로 조회**하고 있습니다.

#### 💡 원인 분석 및 아키텍처적 정합성
이는 단순 누락이나 개발 실수가 아닌, **레이어 간 역할 분담(L2 Architecture)에 따른 고의적인 설계 양상**일 가능성이 큽니다.
1. **쿼리 레이어 (`app/queries/`)**: DB가 제공하는 오리지널 물리 스키마 형태를 직관적으로 유지하기 위해 Alias 적용을 최소화하여 SQL 유지보수성을 극대화합니다.
2. **서비스 레이어 (`app/service/*_df.py`)**: 쿼리를 통해 로드된 원시 Pandas DataFrame을 조작할 때, 공통 비즈니스 상수인 `COLS_TO_RENAME` 사전을 활용하여 한 번에 컬럼명을 변환(`df.rename(columns=COLS_TO_RENAME)`)하여 사용합니다.

> [!NOTE]
> 결과적으로 데이터 정제 표준은 충색되고 있으나, 메타데이터 JSON이 지향하는 "쿼리 단에서의 Recommended Alias 강제 적용"과는 괴리가 있습니다. 아키텍처 규칙 상 컬럼 리네임의 최적 수행 위치(쿼리 레이어 vs 서비스 레이어)를 단일화하고 메타데이터 정의의 톤을 맞출 필요가 있습니다.

---

### ⚠️ [검증 4] 값 상수 (`value_constants`) 정합성 불일치 (2건)
* **발견된 문제**:
  * `cqms_quality_main` (품질 이슈 마스터) 및 `cqms_audit_main` (외부 감사 실적) 테이블의 `STATUS` 컬럼 메타데이터를 보면, `000` (Saved), `001` (Awaiting approval), ... 등의 4M 변경 관리 전용의 숫자 상태 코드(000~007)가 매핑되어 있습니다.
  * 그러나 실제 비즈니스 로직 및 쿼리(`cqms_query.py`)를 조사해보면, 해당 품질 이슈 테이블들은 숫자가 아닌 `On-going` 등의 문자열 상태 상수를 사용하거나 비즈니스 전역 상수인 `STATUS_DICT`와 통신하고 있어 정합성이 전혀 맞지 않습니다.

* **추정 원인**:
  * CQMS 메타데이터 최초 설계 단계에서 `cqms_4m_main` (설계/생산 변경) 테이블의 `STATUS` 명세를 작성한 뒤, 품질이슈(`cqms_quality_main`)와 외부감사(`cqms_audit_main`) 테이블에도 동일한 컬럼명이 존재하자 세부 사양을 검토하지 않고 **복사 붙여넣기(Copy & Paste)**하면서 발생한 메타데이터 오류로 판단됩니다.

---

## 4. 아키텍처 정합성 향상을 위한 개선 제안 (Action Items)

본 검증 결과를 바탕으로 시스템의 아키텍처 일관성(SSOT)을 지키기 위한 구체적 개선 조치를 제안합니다.

1. **메타데이터 동기화 (최우선)**
   * `query_tables_metadata.json` 파일에 누락된 7개 핵심 테이블 사양(특히 `prd_audit_iqm_plus_agg_cum`)을 신속하게 반영해야 합니다.
2. **`is_used` 및 불필요 메타 명세 정리**
   * 실제 쿼리에서 사용되지 않는 테이블들의 사용 여부 플래그를 정비하고, `STATUS` 컬럼의 복사 붙여넣기 오류 사양을 실제 비즈니스 상수 표준에 맞춰 수정합니다.
3. **컬럼 앨리어싱 변환 시점 명확화 및 문서화**
   * 메타데이터의 `recommended_alias`를 강제 가이드하는 것보다, 서비스 레이어의 Pandas 전처리 단계에서 일괄 변환(Renaming Method-Chaining)하는 것이 현재 프로덕션 코드의 핵심 기조입니다. 이를 `L2-architecture.md` 등의 공식 문서에 기술하고, 메타데이터에 기재된 별칭 가이드의 어조(Tone)를 "쿼리 필수 적용"에서 "서비스 레이어 리네임 참조용"으로 정정할 것을 제안합니다.

---
*본 검증 보고서는 Antigravity 검증 에이전트에 의해 자율 검증 및 작성되었습니다.*
