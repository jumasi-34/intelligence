## GMES 쿼리 중복 함수군 (통합 후보)

### Production
- `get_gmes_production_by_plant` / `get_gmes_production_by_mcode` / `get_gmes_production_by_period`
  - 공통: `MAS` + `PRDT` CTE 조합, `PLANT/SPEC_CD` 조인, 집계 컬럼만 차이
  - 통합 후보: `build_production_agg(select_cols, group_cols, order_cols)`
- `get_gmes_production_by_machine` / `get_gmes_production_by_spec_daily`
  - 공통: `spec_master` + `dates` + `prdt` CTE, CROSS JOIN 날짜 채움
  - 통합 후보: `build_production_daily_cte(include_machine: bool)`

### NCF
- `get_gmes_ncf_rawdata` / `get_gmes_ncf_by_dft_cd` / `get_gmes_ncf_by_plant`
- `get_gmes_ncf_by_mcode` / `get_gmes_ncf_by_period`
  - 공통: `MAS` + `NCF` CTE + (scrap 시) `SHP` union, 동일 조인 조건
  - 통합 후보: `build_ncf_union_cte(params)` + `build_ncf_aggregation(select_cols, group_cols)`
  - 기간 집계는 `get_date_field_by_period` 공통 템플릿 적용 가능

### UF
- `get_gmes_uf_rawdata` / `get_gmes_uf_by_mcode`
  - 공통: `MAS` + `UF` CTE, 동일 조인 조건
  - 통합 후보: `build_uf_base_cte(params)` + `build_uf_grade_agg(group_cols)`
- `get_gmes_uf_standard` / `get_gmes_uf_full_standard`
  - 공통: `MAS` + 기준 테이블 조인, 컬럼/필터만 차이

### GT Weight
- `get_gmes_gt_wt_rawdata` / `get_gmes_gt_wt_by_period`
  - 공통: `MAS` + `WT` CTE, 기간 집계/상세 출력 차이
  - 통합 후보: `build_gt_weight_base_cte(params)` + `build_period_aggregation(...)`
