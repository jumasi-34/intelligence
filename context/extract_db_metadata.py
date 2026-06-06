import os
import re
import json
import sqlite3
from typing import Any, List

# 파일 경로 정의
workspace_dir = "/home/jumasi/workstation"
query_db_py_path = f"{workspace_dir}/app/core/query/query_database.py"
output_json_path = f"{workspace_dir}/app/core/db/database-metadata.json"
output_md_path = f"{workspace_dir}/intelligence/context/context-database-metadata.md"

sqlite_db_paths = {
    "log": os.path.expanduser("~/database/log.db"),
    "staging": os.path.expanduser("~/database/staging.db"),
    "ops": os.path.expanduser("~/database/ops.db"),
}


def parse_query_database_py():
    with open(query_db_py_path, "r", encoding="utf-8") as f:
        content = f.read()

    # DatabricksTables 클래스 추출
    databricks_class_match = re.search(
        r'class DatabricksTables:\s*"""(.*?)"""(.*?)class SQLiteTables:', content, re.DOTALL
    )
    databricks_body = databricks_class_match.group(2) if databricks_class_match else ""

    # SQLiteTables 클래스 추출
    sqlite_class_match = re.search(r'class SQLiteTables:\s*"""(.*?)"""(.*)', content, re.DOTALL)
    sqlite_body = sqlite_class_match.group(2) if sqlite_class_match else ""

    metadata: List[Any] = []

    # Databricks 테이블 파싱
    current_category = "General"
    lines = databricks_body.split("\n")
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue

        # 주석으로 카테고리 파악 (예: # CQMS)
        if line_strip.startswith("#") and not line_strip.startswith("#!"):
            comment_val = line_strip.lstrip("#").strip()
            if comment_val and not any(x in comment_val for x in ["삭제대기", "압출", "압연", "재단"]):
                current_category = comment_val
            continue

        # 변수 정의 파싱: name: str = "val"
        var_match = re.match(r'^([a-zA-Z0-9_]+)\s*:\s*str\s*=\s*(["\'])(.*?)\2(?:\s*#\s*(.*))?$', line_strip)
        if var_match:
            var_name = var_match.group(1)
            table_path = var_match.group(3)
            inline_comment = var_match.group(4) if var_match.group(4) else ""

            metadata.append(
                {
                    "variable_name": var_name,
                    "table_path": table_path,
                    "db_type": "databricks",
                    "sqlite_type": None,
                    "category": current_category,
                    "description": inline_comment.strip() or f"Databricks {current_category} table: {var_name}",
                    "columns": [],
                    "referenced_in_queries": [],
                }
            )
            continue

        # 다중 라인 문자열 (예: cqms_doc_sales_brand_pp_detail)
        multiline_match = re.match(r'^([a-zA-Z0-9_]+)\s*:\s*str\s*=\s*\(\s*(["\'])(.*?)\2\s*\)$', line_strip)
        if multiline_match:
            var_name = multiline_match.group(1)
            table_path = multiline_match.group(3)
            metadata.append(
                {
                    "variable_name": var_name,
                    "table_path": table_path,
                    "db_type": "databricks",
                    "sqlite_type": None,
                    "category": current_category,
                    "description": f"Databricks {current_category} table: {var_name}",
                    "columns": [],
                    "referenced_in_queries": [],
                }
            )

    # SQLite 테이블 파싱
    sqlite_lines = sqlite_body.split("\n")
    current_sqlite_type = "ops"
    current_category = "SQLite General"

    for line in sqlite_lines:
        line_strip = line.strip()
        if not line_strip:
            continue

        # 주석으로 SQLite DB 타입 파악 (log, staging, ops)
        if line_strip.startswith("#") and not line_strip.startswith("#!"):
            comment_val = line_strip.lstrip("#").strip()
            if "log" in comment_val.lower():
                current_sqlite_type = "log"
                current_category = "Log Database"
            elif "staging" in comment_val.lower():
                current_sqlite_type = "staging"
                current_category = "Staging Database"
            elif "ops" in comment_val.lower():
                current_sqlite_type = "ops"
                current_category = "Operational Database"
            else:
                current_category = comment_val
            continue

        # 변수 정의 파싱
        var_match = re.match(r'^([a-zA-Z0-9_]+)\s*:\s*str\s*=\s*(["\'])(.*?)\2(?:\s*#\s*(.*))?$', line_strip)
        if var_match:
            var_name = var_match.group(1)
            table_name = var_match.group(3)
            inline_comment = var_match.group(4) if var_match.group(4) else ""

            metadata.append(
                {
                    "variable_name": var_name,
                    "table_path": table_name,
                    "db_type": f"sqlite ({current_sqlite_type})",
                    "sqlite_type": current_sqlite_type,
                    "category": current_category,
                    "description": inline_comment.strip() or f"SQLite {current_sqlite_type} table: {var_name}",
                    "columns": [],
                    "referenced_in_queries": [],
                }
            )

    return metadata


def get_sqlite_columns(sqlite_type, table_name):
    db_path = sqlite_db_paths.get(sqlite_type)
    if not db_path or not os.path.exists(db_path):
        return []

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 컬럼 정보 획득
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns_info = cursor.fetchall()

        # columns_info 구조: (cid, name, type, notnull, dflt_value, pk)
        columns = []
        for col in columns_info:
            columns.append(
                {
                    "cid": col[0],
                    "name": col[1],
                    "type": col[2],
                    "notnull": bool(col[3]),
                    "default_value": col[4],
                    "pk": bool(col[5]),
                }
            )

        conn.close()
        return columns
    except Exception as e:
        print(f"Error fetching schema for SQLite table {table_name} from {sqlite_type}: {e}")
        return []


def enrich_databricks_columns(metadata):
    # 정밀 정의된 Databricks 테이블 컬럼 명세
    hints = {
        # CQMS
        "change_main": [
            "PLANT",
            "REQ_NO",
            "TITLE",
            "REG_USER",
            "REG_DATE",
            "M_CODE",
            "STATUS",
            "CHG_REASON",
            "CHG_DESC",
        ],
        "change_mcode": ["REQ_NO", "M_CODE", "M_NAME"],
        "qi_main": [
            "ISSUE_NO",
            "TITLE",
            "REG_DATE",
            "OCCUR_DATE",
            "PLANT",
            "M_CODE",
            "DEFECT_CD",
            "DEFECT_NM",
            "DEFECT_QTY",
            "STATUS",
        ],
        "qi_category": ["CATEGORY_CD", "CATEGORY_NM", "PARENT_CD"],
        "qi_mcode": ["ISSUE_NO", "M_CODE", "M_NAME"],
        "qi_breakdown": ["ISSUE_NO", "BREAK_DOWN_CD", "BREAK_DOWN_NM"],
        "audit_main": ["AUDIT_NO", "TITLE", "AUDIT_DATE", "AUDIT_USER", "PLANT", "STATUS"],
        "audit_mcode": ["AUDIT_NO", "M_CODE"],
        "app_info_mcode": ["DOC_NO", "M_CODE"],
        "app_info_contents": ["DOC_NO", "REVISION_NO", "CONTENTS", "FILE_NAME"],
        "cqms_doc_code_table": ["CATE_CD", "CATE_NM", "PARENT_CD"],
        "cqms_doc_oem_cat_main": ["CATE_CD", "DOC_NO", "TITLE"],
        "cqms_doc_oem_cat_rev_mgnt": ["DOC_NO", "REVISION_NO", "APPLY_DATE"],
        "cqms_doc_pp_detail": ["PP_NO", "M_CODE", "SPEC_CD"],
        "cqms_doc_pp_info": ["PP_NO", "TITLE", "REG_DATE"],
        "cqms_doc_pp_main": ["PP_NO", "DOC_NO", "REVISION_NO"],
        "cqms_doc_sales_brand_detail": ["BRAND_NO", "M_CODE"],
        "cqms_doc_sales_brand_main": ["BRAND_NO", "TITLE"],
        "cqms_doc_sales_brand_pp_detail": ["BRAND_PP_NO", "M_CODE"],
        "cqms_doc_sales_brand_pp_info": ["BRAND_PP_NO", "TITLE"],
        "cqms_doc_sales_brand_pp_main": ["BRAND_PP_NO", "DOC_NO"],
        "cqms_row_visibility": ["TABLE_NAME", "ROW_ID", "IS_VISIBLE"],
        "cqms_row_visibility_log": ["TABLE_NAME", "ROW_ID", "ACTION", "WORKER", "ACTION_DATE"],
        "cqms_iqm_main": ["IQM_NO", "TITLE", "PLANT", "M_CODE", "REG_DATE"],
        "cqms_iqm_status": ["IQM_NO", "STATUS", "UPDATE_DATE"],
        "cqms_iqm_test_item": ["IQM_NO", "TEST_CD", "TEST_NM", "SPEC_VAL"],
        "cqms_iqm_test_item_req": ["IQM_NO", "TEST_CD", "REQ_VAL"],
        "cqms_iqm_test_main": ["IQM_NO", "TEST_DATE", "TEST_USER"],
        "qi_d1_team": ["ISSUE_NO", "TEAM_CD", "TEAM_NM"],
        "qi_d7_prevention": ["ISSUE_NO", "PREVENT_CD", "PREVENT_NM"],
        "qi_root_cause": ["ISSUE_NO", "CAUSE_CD", "CAUSE_NM"],
        "cqms_attachment": ["ATTACH_ID", "PARENT_ID", "FILE_NAME", "FILE_PATH"],
        # Common
        "product_master": ["PLANT", "M_CODE", "SPEC_CD", "SIZE_CD", "PATTERN_CD", "STXC", "SIZE_NAME", "PATTERN_NM"],
        "spec_revision": ["PLANT", "M_CODE", "SPEC_CD", "REVISION_NO", "APPLY_DATE"],
        "mes_code_master": ["CD_ITEM", "CD_ITEM_NM", "CD_VAL", "CD_VAL_NM"],
        "production_volume": ["PLANT", "M_CODE", "WORK_DATE", "PRDT_QTY", "SCRAP_QTY", "REWORK_QTY"],
        "full_spec": ["SPEC_CD", "M_CODE", "SIZE_NAME", "PATTERN_NM", "STXC"],
        "barcode_record": ["BARCODE_NO", "PLANT", "M_CODE", "SPEC_CD", "PROD_DATE", "SHIFT_CD", "MACHINE_CD"],
        "production_machine": ["PLANT", "M_CODE", "WORK_DATE", "MACHINE_CD", "PRDT_QTY"],
        "building_manufacture_report": ["PLANT", "M_CODE", "WORK_DATE", "SPEC_CD", "PRDT_QTY"],
        # RR
        "rr_lot_samples": ["PLANT", "M_CODE", "BARCODE_NO", "PGS_STS", "INS_DATE", "RR_VALUE", "GRADE"],
        "rr_test_result": ["BARCODE_NO", "INS_DATE", "RR_VALUE", "GRADE", "ATTACH_FILE_NAME"],
        "rr_standard": ["PLANT", "M_CODE", "CAR_MAKER", "VEHICLE", "UCL", "LCL"],
        # Uniformity
        "uf_inspection_result": [
            "PLANT",
            "M_CODE",
            "SPEC_CD",
            "STXC",
            "INS_DATE",
            "RFV",
            "LFV",
            "CON",
            "HAR",
            "JDG_GR",
            "INS_FG",
        ],
        "uf_inspection_standard": ["PLANT", "M_CODE", "SPEC_CD", "RFV_MAX", "LFV_MAX", "CON_MAX", "HAR_MAX"],
        "uf_db_standard": ["PLANT", "M_CODE", "SPEC_CD", "RFV_UCL", "LFV_UCL", "CON_UCL", "HAR_UCL"],
        # Nonconformity
        "shipment_inspection_result": ["PLANT", "M_CODE", "INS_DATE", "DFT_CD", "DFT_DESC", "NCF_QTY"],
        "finished_product_inspection_result": ["PLANT", "M_CODE", "INS_DATE", "DFT_CD", "DFT_DESC", "NCF_QTY"],
        # PLM
        "plm_uf_db_standard": ["PLANT", "M_CODE", "SPEC_CD", "ITEM_LABEL", "UCL_VAL", "LCL_VAL"],
        "worksheet_building_overall": ["PLANT", "M_CODE", "WORK_DATE", "BUILD_QTY"],
        # HGWS / CTMS / HOPE / QRS / RPA / TDR
        "hgws": ["PLANT", "M_CODE", "RETURN_DATE", "RETURN_QTY", "CLAIM_CD", "CLAIM_DESC"],
        "ctms": ["PLANT", "M_CODE", "TEST_DATE", "CTL_VALUE", "DIRECTION", "UPPER_VAL", "LOWER_VAL"],
        "oe_application": ["PLANT", "M_CODE", "APPLICATION_NO", "REG_DATE"],
        "rpa_test_result": ["PLANT", "M_CODE", "TEST_DATE", "TAND_VAL", "GRADE"],
        "tdr": ["PLANT", "M_CODE", "DOC_NO", "TITLE", "REG_DATE"],
        "lot_track": ["BARCODE_NO", "PLANT", "M_CODE", "PROD_DATE"],
    }

    # 쿼리 파일들에서 참조 관계 수집 (정규식 백트래킹 문제를 예방하기 위해 단순 문자열 `in` 탐색을 사용)
    query_dir = f"{workspace_dir}/app/queries"
    query_files = [f for f in os.listdir(query_dir) if f.endswith(".py")]

    file_contents = {}
    for q_file in query_files:
        path = os.path.join(query_dir, q_file)
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_contents[q_file] = f.read()
        except Exception as e:
            print(f"Error reading query file {q_file}: {e}")

    for item in metadata:
        var_name = item["variable_name"]
        table_path = item["table_path"]

        # 1. 컬럼 매핑
        col_list = hints.get(var_name, [])
        if col_list:
            item["columns"] = []
            for col in col_list:
                col_type = "VARCHAR"
                if any(x in col for x in ["DATE", "TIME"]):
                    col_type = "TIMESTAMP"
                elif any(x in col for x in ["QTY", "VAL", "NUM", "MAX", "UCL", "LCL", "WGT"]):
                    col_type = "DOUBLE"

                item["columns"].append(
                    {"name": col, "type": col_type, "description": f"Column representing {col.lower()}"}
                )

        # 2. 참조 파일 추적 (간단하고 무조건 빠른 in 연산 사용)
        referenced = []
        for q_file, content in file_contents.items():
            # 변수명 또는 테이블 경로가 코드 내에 나타나는지 확인
            if var_name in content or table_path in content:
                referenced.append(q_file)
        item["referenced_in_queries"] = sorted(referenced)


def build_markdown_report(metadata):
    md = []
    md.append("# 데이터베이스 테이블 메타데이터 명세서 (Database Metadata Specification)")
    md.append("")
    md.append(
        "> 이 문서는 `app/core/query/query_database.py`에 정의된 모든 데이터베이스 테이블의 변수명, 실제 경로, 시스템 요약 및 스키마 메타정보를 자동으로 수집 및 정리한 명세서입니다."
    )
    md.append("> 시스템 인텔리전스 및 하네스 테스트, 신규 쿼리 작성 시 단일 진실 공급원(SSOT)으로 사용됩니다.")
    md.append("")
    md.append("## 📊 데이터베이스 분류 통계")
    md.append("")

    dbx_count = sum(1 for x in metadata if "databricks" in x["db_type"])
    sqlite_count = sum(1 for x in metadata if "sqlite" in x["db_type"])

    md.append(f"- **전체 정의된 테이블 수**: {len(metadata)} 개")
    md.append(f"- **Databricks Cloud Tables**: {dbx_count} 개")
    md.append(f"- **SQLite Local Tables**: {sqlite_count} 개")
    md.append("")
    md.append("---")
    md.append("")
    md.append("## ☁️ Databricks Cloud Tables")
    md.append("")

    # 카테고리별로 정렬
    categories = sorted(list(set(x["category"] for x in metadata if x["db_type"] == "databricks")))
    for cat in categories:
        md.append(f"### 📁 카테고리: {cat}")
        md.append("")
        md.append(
            "| 변수명 (Variable Name) | 실제 테이블 경로 (Table Path) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 주요 컬럼 (Columns Summary) |"
        )
        md.append("|---|---|---|---|---|")

        cat_items = [x for x in metadata if x["db_type"] == "databricks" and x["category"] == cat]
        for item in cat_items:
            cols_summary = ", ".join([col["name"] for col in item["columns"]]) if item["columns"] else "N/A"
            ref_summary = (
                ", ".join([f"`{q}`" for q in item["referenced_in_queries"]])
                if item["referenced_in_queries"]
                else "None"
            )
            md.append(
                f"| `{item['variable_name']}` | `{item['table_path']}` | {item['description']} | {ref_summary} | {cols_summary} |"
            )
        md.append("")

    md.append("---")
    md.append("")
    md.append("## 💾 SQLite Local Tables")
    md.append("")

    sqlite_types = ["log", "staging", "ops"]
    for s_type in sqlite_types:
        md.append(f"### 🗄️ SQLite Database: {s_type.upper()} (`{s_type}.db`)")
        md.append("")
        md.append(
            "| 변수명 (Variable Name) | 실제 테이블명 (Table Name) | 설명 (Description) | 주요 참조 쿼리 (Queries) | 컬럼 명세 (Columns Info) |"
        )
        md.append("|---|---|---|---|---|")

        type_items = [x for x in metadata if "sqlite" in x["db_type"] and x["sqlite_type"] == s_type]
        for item in type_items:
            ref_summary = (
                ", ".join([f"`{q}`" for q in item["referenced_in_queries"]])
                if item["referenced_in_queries"]
                else "None"
            )
            if item["columns"]:
                cols_desc = "<br>".join(
                    [
                        f"• <b>{col['name']}</b> ({col['type']}){ ' [PK]' if col['pk'] else ''}"
                        for col in item["columns"]
                    ]
                )
            else:
                cols_desc = "N/A"
            md.append(
                f"| `{item['variable_name']}` | `{item['table_path']}` | {item['description']} | {ref_summary} | {cols_desc} |"
            )
        md.append("")

    return "\n".join(md)


def main():
    print("Parsing query_database.py...")
    metadata = parse_query_database_py()

    print("Enriching SQLite schemas...")
    for item in metadata:
        if "sqlite" in item["db_type"]:
            cols = get_sqlite_columns(item["sqlite_type"], item["table_path"])
            item["columns"] = cols

    print("Enriching Databricks column hints and references...")
    enrich_databricks_columns(metadata)

    # JSON 출력 폴더 생성
    os.makedirs(os.path.dirname(output_json_path), exist_ok=True)

    print(f"Writing metadata to JSON: {output_json_path}")
    with open(output_json_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=4, ensure_ascii=False)

    print(f"Generating Markdown report: {output_md_path}")
    md_content = build_markdown_report(metadata)
    with open(output_md_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("Done! Metadata files created successfully.")


if __name__ == "__main__":
    main()
