#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
commit_msg_validator.py - Git 커밋 메시지 규정 준수 검증 가드레일

이 스크립트는 L1-git.md 및 GEMINI.md 규정에 의거하여 커밋 메시지가
지정된 태그를 지키고, 한국어로 명확히 작성되었는지 검증합니다.
"""

import sys
import os
import re
import argparse

from typing import Tuple

# 허용되는 Git 커밋 태그 목록
ALLOWED_TAGS = {"[FEAT]", "[FIX]", "[REFACTOR]", "[STYLE]", "[DOCS]", "[RULE]", "[TEST]", "[CHORE]"}


def validate_commit_message(msg: str) -> Tuple[bool, str]:
    """커밋 메시지가 가이드라인을 준수하는지 검증합니다.


    Returns:
        (bool, str) - (성공 여부, 오류 메시지)
    """
    msg = msg.strip()
    if not msg:
        return False, "커밋 메시지가 비어 있습니다."

    lines = msg.splitlines()
    title = lines[0].strip()

    if not title:
        return False, "커밋 메시지의 제목이 비어 있습니다."

    # 1. 태그 준수 여부 검증
    # 대괄호로 둘러싸인 태그 매칭
    tag_match = re.match(r"^(\[[A-Z]+\])", title)
    if not tag_match:
        return False, "커밋 메시지 제목 맨 앞에 대괄호 태그(예: [FEAT], [FIX] 등)가 누락되었습니다."

    tag = tag_match.group(1)
    if tag not in ALLOWED_TAGS:
        return False, f"허용되지 않는 태그가 사용되었습니다: '{tag}'. (허용 태그: {', '.join(sorted(ALLOWED_TAGS))})"

    # 2. 한국어 엄수 원칙 검증
    # 한글 완성자(가-힣) 또는 자음/모음이 최소한 1자 이상 들어있어야 한글 작성으로 간주
    has_korean = bool(re.search(r"[가-힣ㄱ-ㅎㅏ-ㅣ]", msg))
    if not has_korean:
        return (
            False,
            "커밋 메시지는 'L1-git.md' 규정에 따라 반드시 한국어 기반으로 작성해야 합니다. (영문 및 특수기호 단독 커밋 금지)",
        )

    return True, ""


def main():
    parser = argparse.ArgumentParser(description="Git Commit Message Validator Guardrail")
    parser.add_argument(
        "commit_msg_file", nargs="?", help="Path to the file containing the commit message (e.g. .git/COMMIT_EDITMSG)"
    )
    parser.add_argument("--message", "-m", help="Raw commit message string to validate directly")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress detailed outputs, only exit with code")
    args = parser.parse_args()

    msg_content = ""

    if args.message:
        msg_content = args.message
    elif args.commit_msg_file:
        if not os.path.exists(args.commit_msg_file):
            print(f"[ERROR] 커밋 메시지 파일을 찾을 수 없습니다: {args.commit_msg_file}")
            sys.exit(1)
        try:
            with open(args.commit_msg_file, "r", encoding="utf-8", errors="ignore") as f:
                msg_content = f.read()
        except Exception as e:
            print(f"[ERROR] 커밋 메시지 파일 로드 실패: {str(e)}")
            sys.exit(1)
    else:
        # 인자나 옵션이 없으면 stdin에서 읽음 (파이프라인 연동 지원)
        if not sys.stdin.isatty():
            msg_content = sys.stdin.read()
        else:
            parser.print_help()
            sys.exit(1)

    success, err_msg = validate_commit_message(msg_content)

    if not success:
        if not args.quiet:
            print("\033[91m\033[1m[COMMIT MSG GUARDRAIL VIOLATION] Git 커밋 메시지 규정 위반!\033[0m")
            print(f"  \033[93m사유: {err_msg}\033[0m\n")
            print("  올바른 커밋 작성 템플릿:")
            print("    [FEAT] 대시보드 신규 탭 추가 및 정렬 로직 보완")
            print("    [FIX] Databricks 연결 시간 초과 오류 해결")
            print("    [REFACTOR] 중복 쿼리 빌더 전처리 클래스 단순화\n")
            print("  자세한 세부 사항은 'intelligence/rules/L1-git.md' 문서를 참조하십시오.")
        sys.exit(1)
    else:
        if not args.quiet:
            print("\033[92m[PASSED]\033[0m : Git 커밋 메시지 작성 규정 무결함")
        sys.exit(0)


if __name__ == "__main__":
    main()
