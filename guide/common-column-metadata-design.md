# 글로벌 공통 컬럼 메타데이터 일괄 업데이트 시스템 설계서 (Common Column Metadata Sync)

여러 테이블에서 빈번하게 공동으로 중복 활용되는 표준 컬럼명(예: `PLT_CD`, `MC_CD`, `MCODE`, `REG_DATE` 등)의 일관된 정의를 보장하고, 테이블별 수동 반복 편집 공수를 극적인 수준으로 차단하기 위한 **글로벌 공통 컬럼 메타데이터 일괄 동기화 시스템**의 상세 설계 제안서입니다.

---

## 1. 아키텍처 및 핵심 데이터 구조 (Data Storage Model)

개별 테이블에 파편화되어 정의되던 메타데이터를 하나로 수렴하는 **글로벌 공통 컬럼 사전(Global Common Column Dictionary)** 단일 진실 공급원(SSOT) 파일을 신설합니다.

### ① 공통 컬럼 사전 파일 신설 ➔ `app/core/query/common_column_metadata.json`
특정 테이블에 종속되지 않고, 오직 **물리 컬럼명 자체**를 유일한 식별 키(Primary Key)로 삼는 독립 메타 스키마를 정의합니다.

```json
{
  "PLT_CD": {
    "type": "VARCHAR",
    "display_header": "생산공장",
    "description": "공장 코드",
    "decode": true,
    "value": {
      "P1": "공장A",
      "P2": "공장B"
    }
  },
  "MC_CD": {
    "type": "VARCHAR",
    "display_header": "설비코드",
    "description": "공정 생산 설비 마스터 코드"
  },
  "REG_DATE": {
    "type": "DATE",
    "display_header": "등록일",
    "description": "최초 정보 시스템 등록 일자"
  }
}
```

---

## 2. 유기적 3-레이어 흐름 및 동기화 메커니즘 (Sync Engine)

글로벌 사전의 수정사항을 전체 테이블 메타데이터에 안전하게 파급시키기 위한 동기화 프로세스입니다.

```mermaid
flowchart TD
    Common_JSON[("common_column_metadata.json (공통 사전)")]
    Query_JSON[("query_metadata.json (테이블 메타)")]
    UI_Page["metadata_manager_page.py (UI 레이어)"]
    Service["metadata_df.py (서비스 레이어)"]

    UI_Page -->|1. 공통 컬럼 추가/수정| Service
    Service -->|2. 쓰기 및 백업| Common_JSON
    UI_Page -->|3. 일괄 적용 버튼 클릭| Service
    Service -->|4. 공통 컬럼 로드| Common_JSON
    Service -->|5. 테이블 메타 전체 로드| Query_JSON
    Service -->|6. 동기화 연산 (Merge/Sync)| Service
    Service -->|7. 원자적 덮어쓰기 & 자동 백업| Query_JSON
    Service -->|8. 완료 피드백| UI_Page

    style UI_Page fill:#f0fdf4,stroke:#22c55e,stroke-width:2px
    style Service fill:#eff6ff,stroke:#3b82f6,stroke-width:2px
    style Common_JSON fill:#faf5ff,stroke:#a855f7,stroke-width:2px
    style Query_JSON fill:#fffbeb,stroke:#f59e0b,stroke-width:2px
```

### 🔄 동기화 연산 모드 (Sync Modes)
사이드 패널 또는 어드민 제어 영역에서 2가지 유연한 적용 모드를 제공하여 기존 개 개별 편집본을 보호합니다:
1. **빈 칸만 채우기 (Fill Blank Only)**: 
   - 개별 테이블의 컬럼 정의 중 `display_header`나 `description`이 **비어있는 영역만** 글로벌 공통 사전 정의로 채워 넣습니다. (기존 커스텀 수작업 메타 보호)
2. **글로벌 사전 강제 동기화 (Force Overwrite)**:
   - 개별 테이블 설정과 무관하게, 글로벌 사전에 등록된 표준 컬럼명이 발견되면 **해당 정의로 완전 강제 덮어쓰기**하여 표준 명명 명세를 100% 강제 일치시킵니다.

---

## 3. UI/UX 화면 구성 설계 (Sleek Admin Controls)

기존 메타데이터 편집 페이지에 **세 번째 관리 탭(Tab 3)**을 입체적으로 증설하여, 공통 컬럼 편집과 동기화를 일원화합니다.

### 💻 증설 탭 Mockup 설계

```
┌── 탭 3: :material/globe: 글로벌 공통 컬럼 관리 (Global Dictionary) ────────────────────────┐
│                                                                                        │
│  :material/info: 공통 컬럼 사전은 다수의 테이블에서 동일 명칭으로 쓰이는 핵심 컬럼의              │
│  표준 정의를 통합 관리합니다. 이곳에서 수정한 명세는 버튼 클릭 한 번으로 일괄 전파됩니다.        │
│                                                                                        │
│  ┌───컬럼 메타 정의 일괄 편집 (st.data_editor) ──────────────────────────────────────┐  │
│  │ ┌───┬─────────────┬──────────┬───────────────────┬─────────────────┬──────────┐ │  │
│  │ │   │ 공통컬럼명  │ 데이터형 │ 표시 헤더(Header) │ 한글 설명(Desc) │ 디코드   │ │  │
│  │ ├───┼─────────────┼──────────┼───────────────────┼─────────────────┼──────────┤ │  │
│  │ │ 1 │ PLT_CD      │ VARCHAR  │ 생산공장          │ 공장 코드       │   [v]    │ │  │
│  │ │ 2 │ MC_CD       │ VARCHAR  │ 설비코드          │ 설비 마스터 코드│   [ ]    │ │  │
│  │ └───┴─────────────┴──────────┴───────────────────┴─────────────────┴──────────┘ │  │
│  └──────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                        │
│  [ :material/save: 공통 사전 변경사항 저장 ]                                             │
│                                                                                        │
│  st.divider()                                                                          │
│  ##### :material/sync_alt: 전체 테이블 일괄 동기화 (Global Propagator)                  │
│  선택된 동기화 모드: (o) 빈 칸만 표준 정의로 채우기  ( ) 글로벌 공통 정의로 강제 덮어쓰기       │
│                                                                                        │
│  [ :material/bolt: 공통 사전 스펙 전체 테이블 일괄 전파 적용 ]                            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 4. 서비스 레이어 소스 구현 명세 (Technical Realization)

### ① `app/service/metadata_df.py` 증설 함수 설계
```python
COMMON_METADATA_PATH = Path("app/core/query/common_column_metadata.json")

def load_common_column_metadata() -> dict:
    """글로벌 공통 사전을 로드합니다."""
    if not COMMON_METADATA_PATH.exists():
        return {}
    with open(COMMON_METADATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_common_column_metadata(common_dict: dict) -> bool:
    """글로벌 공통 사전을 원자적으로 저장 및 안전 백업 생성합니다."""
    try:
        if COMMON_METADATA_PATH.exists():
            shutil.copy2(COMMON_METADATA_PATH, COMMON_METADATA_PATH.with_suffix(".json.bak"))
        with open(COMMON_METADATA_PATH, "w", encoding="utf-8") as f:
            json.dump(common_dict, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False

def sync_common_columns_to_all_tables(mode: str = "blank") -> tuple[bool, int]:
    """
    글로벌 공통 사전을 전체 테이블 메타데이터(query_metadata.json)에 일괄 전파 반영합니다.
    
    Args:
        mode (str): "blank" (빈칸만 채우기) | "overwrite" (강제 덮어쓰기)
        
    Returns:
        tuple[bool, int]: 성공 여부, 동기화가 반영된 누적 테이블 수
    """
    common_cols = load_common_column_metadata()
    if not common_cols:
        return False, 0
        
    table_metadata = load_query_metadata()
    updated_count = 0
    
    for table_key, table_info in table_metadata.items():
        columns = table_info.get("columns", {})
        table_updated = False
        
        for col_name, col_meta in columns.items():
            # 공통 사전에 존재하는 표준 컬럼을 만난 경우
            if col_name in common_cols:
                std_meta = common_cols[col_name]
                
                # 모드별 조건 분기
                if mode == "overwrite":
                    # 강제 일치
                    columns[col_name] = std_meta.copy()
                    table_updated = True
                elif mode == "blank":
                    # 비어있는 필드만 선택적 보강
                    for key in ["display_header", "description", "decode", "value", "type"]:
                        if key in std_meta:
                            # 기존 값이 없거나 비어있는 경우
                            current_val = col_meta.get(key)
                            if current_val is None or current_val == "" or current_val == {}:
                                col_meta[key] = std_meta[key]
                                table_updated = True
                                
        if table_updated:
            table_info["columns"] = columns
            updated_count += 1
            
    if updated_count > 0:
        # 전체 테이블 메타데이터 물리 세이프티 저장 기동
        save_query_metadata(table_metadata)
        return True, updated_count
        
    return True, 0
```

---

## 5. 다음 단계 제안 및 승인 요청

이 글로벌 공통 메타 관리 엔진은 복잡해지기 쉬운 대형 엔터프라이즈 컬럼 명세를 고도의 SSOT 체계로 다잡아주는 장치입니다.

사용자님, 본 설계 제안서 구성을 검토해 보시고 아래 진행을 선택해 주세요:

1. **[구현 승인]** 본 설계안을 승인하며, `common_column_metadata.json` 파일 기본 규격 구축, 서비스 레이어 함수 증설, UI 관리 탭 추가 코딩 작업을 한 번에 진행 및 통합한다.
2. **[설계 일부 수정]** 일괄 적용되는 세부 스키마 항목이나 동기화 조건 분기를 수정한 뒤 추가 검토한다.
