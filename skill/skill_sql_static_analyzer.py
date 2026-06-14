#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
skill_sql_static_analyzer.py - SQL 쿼리 레이어 표준 및 5대 불변 규칙 정적 분석 스킬

이 스크립트는 app/queries/ 내의 모든 SQL 빌더 파일들을 분석하여
SQL 쿼리 내 한글 AS Alias 사용 금지 수칙, 테이블 경로 직접 하드코딩, 
쿼리 파일 내 직접 DB 실행 행위 등을 정적으로 분석하여 보고합니다.
"""

import os
import sys
import re
import argparse
from typing import List, Dict, Any

# 정적 분석 정규식 패턴들
# 1. 한글 AS Alias (예: AS "공장코드", AS '품질', AS 한글 등)
HANGEUL_ALIAS_PATTERN = re.compile(r'AS\s+["\']?([^"\'\s]*[가-힣]+[^"\'\s]*)["\']?', re.IGNORECASE)

# 2. SELECT * 사용 탐지
SELECT_STAR_PATTERN = re.compile(r"SELECT\s+\*", re.IGNORECASE)

# 3. 테이블 경로 직접 하드코딩 (예: hkt_system_dw.eqms...)
HARDCODED_TABLE_PATTERN = re.compile(r"hkt_system_dw\.[a-zA-Z0-9_.]+", re.IGNORECASE)

# 4. 직접 DB 실행 함수 호출 (execute, connect 등)
DIRECT_EXECUTE_PATTERN = re.compile(r"\b(execute|cursor|connect|get_client)\b")


def analyze_query_file(filepath: str) -> List[Dict[str, Any]]:
    """단일 쿼리 파일의 정적 코드를 분석하여 규정 위반 목록을 수집합니다."""
    violations = []

    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
    except Exception as e:
        return [{"type": "SYSTEM", "line": 0, "message": f"파일 로드 실패: {str(e)}"}]

    for line_idx, line in enumerate(lines, 1):
        clean_line = line.strip()
        if not clean_line or clean_line.startswith("#"):
            continue

        # 1. 한글 AS Alias 사용 금지 수칙 검사
        alias_matches = HANGEUL_ALIAS_PATTERN.findall(clean_line)
        if alias_matches:
            for alias in alias_matches:
                violations.append(
                    {
                        "type": "HANGEUL_ALIAS",
                        "line": line_idx,
                        "content": clean_line,
                        "message": f"한글 AS Alias(별칭) 사용 금지 규정 위반: '{alias}' 별칭이 감지되었습니다. (물리 컬럼명을 보존하고 UI에서 동적으로 컬럼 설정 매핑해야 합니다.)",
                    }
                )

        # 2. 쿼리 레이어의 직접 실행 금지 규정 검사 (execute 등 호출)
        if DIRECT_EXECUTE_PATTERN.search(clean_line):
            # 단순 주석이나 다른 정상적인 임포트명 등 예외 처리
            if "query_database" not in clean_line and "import" not in clean_line:
                violations.append(
                    {
                        "type": "DIRECT_DB_EXECUTE",
                        "line": line_idx,
                        "content": clean_line,
                        "message": "쿼리 레이어 내부에서 직접 DB 실행 구문(execute, cursor, connect 등)이 호출된 것으로 추정됩니다. (쿼리 레이어는 오직 순수 SQL 문자열만 반환해야 합니다.)",
                    }
                )

        # 3. Databricks 테이블 경로 직접 하드코딩 검사
        table_matches = HARDCODED_TABLE_PATTERN.findall(clean_line)
        if table_matches:
            for table in table_matches:
                violations.append(
                    {
                        "type": "HARDCODED_TABLE",
                        "line": line_idx,
                        "content": clean_line,
                        "message": f"테이블 경로 하드코딩 감지: '{table}'. (반드시 DatabricksTables 상수를 사용하여 중앙에서 관리되는 경로를 바인딩하십시오.)",
                    }
                )

        # 4. SELECT * 사용 감사 (Warning 등급)
        if SELECT_STAR_PATTERN.search(clean_line):
            violations.append(
                {
                    "type": "SELECT_STAR_WARN",
                    "line": line_idx,
                    "content": clean_line,
                    "message": "SELECT * 사용 감지. (가급적 필요한 물리 컬럼명을 명시하는 것이 표준 권장사항입니다.)",
                }
            )

    return violations


def scan_queries_folder(root_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    """queries 폴더 내부의 모든 쿼리 파일을 정적 스캔합니다."""
    report: Dict[str, List[Dict[str, Any]]] = {}
    queries_dir = os.path.join(root_dir, "app", "queries")

    if not os.path.exists(queries_dir):
        return report

    for root, dirs, files in os.walk(queries_dir):
        # __pycache__ 제외
        dirs[:] = [d for d in dirs if d != "__pycache__"]

        for file in files:
            if file.endswith(".py") and (file.startswith("q_") or file.endswith("_query.py")):
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, root_dir)
                violations = analyze_query_file(filepath)
                if violations:
                    report[rel_path] = violations

    return report


def main():
    parser = argparse.ArgumentParser(description="SQL Layer Standard Static Analyzer Skill")
    parser.add_argument("target_path", nargs="?", default=".", help="Workspace root path to scan")
    parser.add_argument("--quiet", "-q", action="store_true", help="Only exit with status code, suppress output")
    args = parser.parse_args()

    workspace_root = os.path.abspath(args.target_path)

    # 만약 app/queries 디렉토리가 하위에 없으면 상위 조정 시도
    if not os.path.exists(os.path.join(workspace_root, "app", "queries")):
        workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

    report = scan_queries_folder(workspace_root)

    # 위반 유형 중 심각한 에러 등급 분류 (SELECT_STAR_WARN은 경고이므로 빌드 차단 미수행)
    critical_count = 0
    total_violations = 0

    for filepath, violations in report.items():
        for v in violations:
            total_violations += 1
            if v["type"] != "SELECT_STAR_WARN":
                critical_count += 1

    if critical_count > 0:
        if not args.quiet:
            print("\033[91m\033[1m[SQL LAYERING VIOLATION] SQL 쿼리 레이어 표준 위반 발견!\033[0m")
            print(
                "  한글 AS Alias 사용 금지 수칙, 테이블 하드코딩 배제 및 쿼리 실행 책임 분리 규정을 준증해야 합니다.\n"
            )
            for filepath, violations in report.items():
                # 심각한 에러가 있는 파일만 먼저 출력
                file_criticals = [v for v in violations if v["type"] != "SELECT_STAR_WARN"]
                if file_criticals:
                    print(f"▶ 파일: \033[93m{filepath}\033[0m")
                    for v in file_criticals:
                        print(f"  └ Line {v['line']}: {v['message']}")
                        print(f"    └ 소스코드: \033[90m{v['content']}\033[0m")
                    print()
        sys.exit(1)
    else:
        if not args.quiet:
            print("\033[92m[PASSED]\033[0m : SQL 쿼리 레이어 정적 무결성 분석 완료")
            # 경고 메시지만 보조 출력
            if report:
                print("\n\033[94m[INFO] 권장 분석 피드백 (Warnings):\033[0m")
                for filepath, violations in report.items():
                    warns = [v for v in violations if v["type"] == "SELECT_STAR_WARN"]
                    if warns:
                        print(f"  - {filepath}:")
                        for w in warns:
                            print(f"    └ Line {w['line']}: {w['message']}")
        sys.exit(0)


if __name__ == "__main__":
    main()
