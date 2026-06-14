# 메타데이터 컬럼 필요 여부(is_essential) 추가 및 필터링 기능 설계서

이 설계서는 사용자가 데이터 분석 및 메타데이터 정비를 수행할 때 불필요하거나 분석 가치가 낮은 컬럼을 배제하고, 필요한 컬럼 위주로 정비할 수 있도록 하는 **"컬럼 필요 여부(is_essential)"** 메타데이터 필드 추가 및 **"필터링 UI"** 구축 계획을 제시합니다.

특히, Streamlit `st.data_editor` 상에서 필터링이 활성화된 상태에서 데이터를 저장할 때 발생할 수 있는 **"화면에 보이지 않는 행 데이터의 유실(Data Loss)" 현상을 아키텍처 수준에서 완벽하게 차단**하는 데이터 병합 설계를 내포하고 있습니다.

---

## 1. 아키텍처 및 데이터 무결성 설계 (Data Integrity)

### ① 메타데이터 스키마 확장
*   `query_metadata.json` 및 `common_column_metadata.json` 내의 컬럼 정의 속성에 `"is_essential"` (Boolean, 기본값 `true`) 필드를 신설합니다.
*   **하위 호환성 및 안정 장치**: 기존에 생성된 대량의 메타데이터에는 이 필드가 없으므로, 로딩/가공 단계에서 이 값이 누락되어 있을 경우 자동으로 `True`(필수 컬럼)로 해석 및 상속하여 이전 환경을 영구 보존합니다.

```json
// 예시: query_metadata.json 또는 common_column_metadata.json
"columns": {
  "PLANT_CODE": {
    "type": "VARCHAR",
    "display_header": "공장코드",
    "description": "생산 공장 구분 코드",
    "is_essential": true       <-- 신설
  },
  "TEMP_LOG_ID": {
    "type": "VARCHAR",
    "display_header": "로그식별자",
    "description": "분석에 불필요한 일회성 정적 ID",
    "is_essential": false      <-- 신설
  }
}
```

### ② 필터링 편집 시 "데이터 유실 방지 병합 알고리즘" 도입
사용자가 화면 상에서 `필수(분석용) 컬럼만 표시` 토글을 활성화하면, 데이터 에디터에는 필수 컬럼만 노출됩니다. 이때 변경사항을 그냥 저장하면 화면에 표시되지 않던 비필수 컬럼들이 유실되어 삭제될 수 있습니다.
이 치명적인 위협을 해소하기 위해 아래와 같이 **안전 격리 병합**을 적용합니다.

*   **테이블 개별 메타데이터 저장 시 (`serialize_edited_df_to_json`)**:
    *   완전히 새로 덮어쓰는 대신, `query_metadata.json` 내 해당 테이블의 기존 전체 컬럼 메타데이터 사본을 메모리에 선적합니다.
    *   화면(에디터) 상에서 수정되어 넘어온 부분집합 레코드들에 대해서만 루프를 돌며 개별 속성을 신뢰도 높게 덮어쓰기(Upsert) 합니다.
    *   에디터 상에 존재하지 않던(비필수여서 가려졌던) 컬럼들은 기존 정의값을 그대로 100% 보존합니다.
*   **글로벌 공통 사전 저장 시 (`serialize_common_metadata_to_json`)**:
    *   글로벌 사전은 행 추가/삭제(`num_rows="dynamic"`) 기능이 가동되므로 좀 더 세밀한 판정이 필요합니다.
    *   에디터 상에서 명시적으로 삭제된 필수 컬럼은 사용자가 진짜 삭제한 것으로 판정하여 소멸시킵니다.
    *   에디터 상에 존재하지 않으면서, 기존 글로벌 사전에서 `"is_essential": false` 인 컬럼들(가려져 있던 항목)은 **명시적 유실 방지 대상**으로 분류되어 최종 직렬화 사전에 강제 병합 복원됩니다.

---

## 2. 레이어별 세부 수정 계획 (Diff Proposal)

### ① 서비스 레이어 (`app/service/metadata_df.py`)

#### 1) `get_merged_columns_df` 개정
*   실제 DB 컬럼과 JSON 명세를 Outer Join 병합할 때, 공통 사전으로부터 `"is_essential"` 가치를 상속받고, 최종 DF 빌딩 시 포함시킵니다.
```python
        # 글로벌 사전에 정의되어 있는 경우 개별 테이블 컬럼 사양 실시간 보강 (Auto-Fill)
        if normalized_col in common_cols:
            std_meta = common_cols[normalized_col]
            col_meta = col_meta.copy() if col_meta else {}
            # 전파 대상 목록에 "is_essential" 추가
            for key in ["display_header", "description", "decode", "value", "type", "is_essential"]:
                if key in std_meta:
                    current_val = col_meta.get(key)
                    # 비어있거나, False인 decode 속성 또는 빈 딕셔너리인 경우 글로벌 표준 사양 전파
                    if current_val is None or current_val == "" or current_val == {} or (key == "decode" and current_val is False):
                        col_meta[key] = std_meta[key]

        merged_records.append({
            "column_name": col,
            "type": col_meta.get("type", "VARCHAR"),
            "display_header": col_meta.get("display_header", ""),
            "description": col_meta.get("description", ""),
            "decode": col_meta.get("decode", False),
            "is_essential": col_meta.get("is_essential", True),  # 기본값 True 주입
            "value_map": val_map_str,
            "is_in_db": col in db_cols,
            "is_in_json": col in json_cols
        })
```

#### 2) `serialize_edited_df_to_json` 개정 (데이터 유실 방지 구조)
```python
def serialize_edited_df_to_json(table_key: str, edited_df: pd.DataFrame, table_description: str) -> dict:
    current_metadata = load_query_metadata()
    table_meta = current_metadata.setdefault(table_key, {})
    table_meta["description"] = table_description.strip()
    
    # 타입 및 기존 미노출 컬럼 유실 가드: 기존 컬럼 정의 딕셔너리 안전 확보
    columns_dict = dict(table_meta.get("columns", {}))

    for _, row in edited_df.iterrows():
        col_name = str(row["column_name"]).strip()
        if not col_name:
            continue

        if not COLUMN_NAME_PATTERN.match(col_name):
            raise ValueError(f"컬럼명 '{col_name}' 형식이 올바르지 않습니다.")

        col_type = str(row.get("type", columns_dict.get(col_name, {}).get("type", "VARCHAR"))).strip()
        display_header = str(row["display_header"]).strip()
        description = str(row["description"]).strip()
        decode = bool(row["decode"])
        is_essential = bool(row.get("is_essential", True))  # 필요 유무 수집

        # value_map 파싱
        value_dict = {}
        val_map_str = str(row["value_map"]).strip() if pd.notna(row["value_map"]) else ""
        if decode and not val_map_str:
            raise ValueError(f"컬럼 '{col_name}'의 디코드가 활성화되었으나 코드 매핑 JSON이 입력되지 않았습니다.")

        if val_map_str:
            if not DECODE_JSON_PATTERN.match(val_map_str):
                raise ValueError(f"컬럼 '{col_name}'의 코드 매핑 형식이 올바르지 않습니다.")
            try:
                value_dict = json.loads(val_map_str)
            except json.JSONDecodeError:
                raise ValueError(f"컬럼 '{col_name}'의 코드 매핑 JSON 파싱 실패.")

        # 병합 덮어쓰기 실행 (나머지 미표시 컬럼은 기존 정의 보존)
        columns_dict[col_name] = {
            "type": col_type,
            "description": description,
            "display_header": display_header,
            "is_essential": is_essential
        }

        if decode or value_dict:
            columns_dict[col_name]["decode"] = decode
            columns_dict[col_name]["value"] = value_dict

    table_meta["columns"] = columns_dict
    return current_metadata
```

#### 3) `serialize_common_metadata_to_json` 개정 (글로벌 사전 유실 방지)
```python
def serialize_common_metadata_to_json(edited_df: pd.DataFrame) -> dict:
    try:
        existing_common = load_common_column_metadata()
    except Exception:
        existing_common = {}

    edited_cols = set()
    temp_dict = {}

    for _, row in edited_df.iterrows():
        col_name = str(row["column_name"]).strip().upper()
        if not col_name:
            continue
        edited_cols.add(col_name)

        if not COLUMN_NAME_PATTERN.match(col_name):
            raise ValueError(f"공통 컬럼명 '{col_name}' 형식이 올바르지 않습니다.")

        col_type = str(row.get("type", existing_common.get(col_name, {}).get("type", "VARCHAR"))).strip()
        display_header = str(row["display_header"]).strip()
        description = str(row["description"]).strip()
        decode = bool(row["decode"])
        is_essential = bool(row.get("is_essential", True))  # 필요 유무 수집

        # value_map 파싱
        value_dict = {}
        val_map_str = str(row["value_map"]).strip() if pd.notna(row["value_map"]) else ""
        if decode and not val_map_str:
            raise ValueError(f"공통 컬럼 '{col_name}'의 디코드가 활성화되었으나 코드 매핑 JSON이 입력되지 않았습니다.")

        if val_map_str:
            if not DECODE_JSON_PATTERN.match(val_map_str):
                raise ValueError(f"공통 컬럼 '{col_name}'의 코드 매핑 형식이 올바르지 않습니다.")
            try:
                value_dict = json.loads(val_map_str)
            except json.JSONDecodeError:
                raise ValueError("JSON 파싱 실패.")

        temp_dict[col_name] = {
            "type": col_type,
            "description": description,
            "display_header": display_header,
            "is_essential": is_essential
        }
        if decode or value_dict:
            temp_dict[col_name]["decode"] = decode
            temp_dict[col_name]["value"] = value_dict

    # 유실 방지 지능형 병합 조립
    final_common_dict = {}
    for col, meta in temp_dict.items():
        final_common_dict[col] = meta

    for col, meta in existing_common.items():
        if col not in edited_cols:
            # 에디터 필터로 인해 노출되지 않아 수집에 불참한 '비필수' 표준 컬럼은 안전히 이전 상속
            if not meta.get("is_essential", True):
                final_common_dict[col] = meta

    return final_common_dict
```

#### 4) `sync_common_columns_to_all_tables` (일괄 전파 도구) 보강
*   전파 대상 덮어쓰기 및 빈칸 보강 목록(`for key in [...]`)에 `"is_essential"`을 동시 포함시킵니다.

---

## 3. UI 레이어 (`app/pages/_70_settings/metadata_manager_page.py`)

#### 1) 탭 1 (테이블 개별 컬럼 명세 편집) UI 개정
*   **필터 컨트롤러 주입**: 데이터 에디터 바로 상단에 토글 필터 배치
```python
        # st.data_editor 바로 위에 필터 체크박스 가동
        filter_essential_only = st.checkbox(
            ":material/filter_list: 필수(분석용) 컬럼만 표시",
            value=False,
            help="필요 유무(is_essential)가 활성화되어(True) 있는 주요 핵심 컬럼들만 데이터 에디터에 필터링하여 노출합니다."
        )

        display_columns_df = merged_columns_df.copy()
        if filter_essential_only:
            # is_essential 속성이 True 인 행만 부분집합으로 투영
            display_columns_df = display_columns_df[display_columns_df["is_essential"] == True]
```
*   **에디터 컬럼 명세 확장**: Grid Config에 `is_essential` 체크박스 컬럼 추가
```python
        grid_column_configs = {
            "column_name": st.column_config.TextColumn(
                "물리 컬럼명 (DB)",
                help="실제 데이터베이스 컬럼 식별 키",
                disabled=True,
                width="medium"
            ),
            "is_essential": st.column_config.CheckboxColumn(
                "필요 여부 (Essential)",
                help="이 컬럼이 분석 목적이나 데이터 이해에 반드시 필요한 표준 분석 대상인지 여부를 지정합니다.",
                width="small"
            ),
            # ... display_header, description, decode, value_map 등 기존 명세 동일 유지
        }
```

#### 2) 탭 2 (글로벌 공통 컬럼 사전 편집) UI 개정
*   **공통 사전 레코드 가공에 `is_essential` 적용** (712번째 줄 부근)
```python
                common_records.append({
                    "column_name": col,
                    "type": meta.get("type", "VARCHAR"),
                    "display_header": meta.get("display_header", ""),
                    "description": meta.get("description", ""),
                    "decode": meta.get("decode", False),
                    "is_essential": meta.get("is_essential", True),  # 추가
                    "value_map": val_map_str
                })
```
*   **필터 컨트롤러 주입 및 에디터 컬럼 확장**:
    *   동일하게 에디터 상단에 `필수 공통 컬럼만 표시` 체크박스 탑재.
    *   `common_grid_configs`에 `"is_essential"`의 `CheckboxColumn` 추가 정의.

---

## 4. 검증 계획 (Harness Validation)
새롭게 추가된 메타데이터 필요 유무 컬럼 및 필터링 세이프티 가드레일은 기존에 빌드한 하네스 엔지니어링 파일(`tests/metadata_manager_test.py`)에 정밀 테스트 케이스를 연동하여 검증합니다.

1.  **[TEST 4] 컬럼별 '필요 유무(is_essential)' 속성 신설 및 정상 상속 검증**
2.  **[TEST 5] 필터링 시 미노출 컬럼 영구 보존(Data Loss Prevention) 결합 무결성 검증**

테스트를 가동하여 단 1바이트의 유실도 없는 최고 수준의 데이터 정합성을 확인한 뒤 원격에 릴리즈합니다.
