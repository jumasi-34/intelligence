#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
emoji_checker.py - 소스코드 및 문서 자산 내 유니코드 이모지 사용 검증 가드레일

이 스크립트는 프로젝트 내 파이썬 소스 코드(.py) 및 마크다운 문서(.md)를 스캔하여
일반 유니코드 이모지가 사용되었는지 정적으로 검증합니다.
"""

import os
import sys
import re
import argparse
from typing import List, Tuple

# 유니코드 이모지 감지 정규식 패턴 (표준 이모지 및 특수 기호 영역)
EMOJI_PATTERN = re.compile(
    r"["
    r"\U0001F600-\U0001F64F"  # Emoticons
    r"\U0001F300-\U0001F5FF"  # Miscellaneous Symbols and Pictographs
    r"\U0001F680-\U0001F6FF"  # Transport and Map Symbols
    r"\U0001F1E6-\U0001F1FF"  # Regional Indicator Symbols (Flags)
    r"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    r"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    r"\u2600-\u26FF"  # Miscellaneous Symbols
    r"\u2700-\u27BF"  # Dingbats
    r"]",
    re.UNICODE,
)

# 스캔에서 무조건 제외할 폴더 목록
EXCLUDE_DIRS = {
    ".git",
    ".github",
    ".venv",
    "temp",
    "__pycache__",
    ".streamlit",
    ".vscode",
    ".claude",
    ".cursor",
    "node_modules",
    ".mypy_cache",
    ".ruff_cache",
    ".pytest_cache",
    "tests",
    "automation",
    "local.assets",
    "local.data",
    "logs",
    "app",
}

# AI Exclusion Zone 및 예외 경로
EXCLUDE_PATH_PATTERNS = [
    r"intelligence/note/",  # Private User Space (AI Exclusion Zone)
    r"intelligence/runs_archive/",  # 아카이브 폴더
    r"intelligence/runs/run_",  # 일회성 runs 세션 폴더
    r"intelligence/hook/",  # 기존 훅 자산 제외
    r"intelligence/guide/",  # 기존 가이드 템플릿 파일 제외
    r"intelligence/skill/skill_generate_korean_metadata.py",  # 레거시 스킬 제외
]


def should_exclude(filepath: str) -> bool:
    """주어진 파일 경로가 스캔 예외 대상인지 판별합니다."""
    normalized_path = filepath.replace("\\", "/")

    # 디렉토리 중 제외 대상이 있는지 체크
    parts = normalized_path.split("/")
    if any(part in EXCLUDE_DIRS for part in parts):
        return True

    # 경로 패턴 중 제외 대상이 있는지 체크
    for pattern in EXCLUDE_PATH_PATTERNS:
        if re.search(pattern, normalized_path):
            return True

    return False


def scan_files_for_emojis(root_dir: str) -> List[Tuple[str, int, int, str]]:
    """프로젝트 내 파이썬 소스 코드 파일을 스캔하여 이모지 감색 결과를 반환합니다.

    Returns:
        List of Tuple (파일상대경로, 라인번호, 컬럼번호, 감지된이모지문자)
    """
    violations = []

    for root, dirs, files in os.walk(root_dir):
        # 상위 디렉토리에서 제외 필터링 적용
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if not file.endswith(".py"):
                continue

            filepath = os.path.join(root, file)
            if should_exclude(filepath):
                continue

            rel_path = os.path.relpath(filepath, root_dir)

            try:
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line_idx, line in enumerate(f, 1):
                        for match in EMOJI_PATTERN.finditer(line):
                            emoji_char = match.group()
                            col_idx = match.start() + 1
                            violations.append((rel_path, line_idx, col_idx, emoji_char))
            except Exception:
                # 파일 읽기 중 에러가 발생하는 경우는 무시하거나 기록
                pass

    return violations


def main():
    parser = argparse.ArgumentParser(description="Unicode Emoji Usage Guardrail Checker")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress detailed output and only exit with code")
    parser.add_argument("target_dir", nargs="?", default=".", help="Directory to scan")
    args = parser.parse_args()

    target_dir = os.path.abspath(args.target_dir)
    violations = scan_files_for_emojis(target_dir)

    if violations:
        if not args.quiet:
            print("\033[91m\033[1m[EMOJI GUARDRAIL VIOLATION] 유니코드 이모지 사용 규정 위반 감지!\033[0m")
            print(
                "  Streamlit UI 가이드라인 및 프로젝트 정합성을 위해 코드와 마크다운 내 일반 유니코드 이모지 사용은 금지됩니다."
            )
            print("  대신 Streamlit Google Material Symbols (:material/icon_name:)를 활용하세요.\n")
            print(f"총 {len(violations)}개의 이모지 위반이 발견되었습니다:")
            for path, line, col, char in violations:
                print(f"  - \033[93m{path}:{line}:{col}\033[0m -> 감지된 이모지: '{char}'")
        sys.exit(1)
    else:
        if not args.quiet:
            print("\033[92m[PASSED]\033[0m : 유니코드 이모지 사용 규정 무결함 (스캔 완료)")
        sys.exit(0)


if __name__ == "__main__":
    main()
