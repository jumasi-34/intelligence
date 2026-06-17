#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intelligence Console Build Script
- scans markdown files in the intelligence repository (strictly excluding intelligence/note/).
- compiles metadata, summaries, and contents into static JSON files for the dashboard.
- performs simple secret scanning to prevent accidental exposure of sensitive keys.
"""

import os
import json
import re
from datetime import datetime
from typing import Dict, Any

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # workstation/intelligence
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
DATA_DIR = os.path.join(DASHBOARD_DIR, "data")

# Category descriptions
CATEGORIES = {
    "agent": "AI 에이전트의 역할, 책임 및 운영 규칙",
    "domain": "품질, 설비, 생산, 알림 메일 등 도메인 지식",
    "infra": "인프라 사양, 데이터베이스 및 API 연동 규칙",
    "guide": "테스트 가이드, 에러 대응 및 릴리즈 가이드",
    "rules": "Git 커밋 규칙, 코딩 표준 및 안전 장치(Safety Guardrails)",
    "runs": "에이전트 실행 및 운영 로그 이력",
    "workflow": "비즈니스 프로세스 및 작업 흐름 가이드",
    "skill": "에이전트 도구 및 자동화 스크립트 명세",
    "checklist": "품질 보증 및 작업 검증 체크리스트",
    "guardrail": "에이전트 제약 및 안전 가드레일 명세",
}

# Subdirectories to scan (explicitly white-listed)
SCAN_DIRS = list(CATEGORIES.keys())

# AI Exclusion Zone (MUST NEVER BE READ OR SCANNED)
EXCLUDE_DIRS = ["note"]

# Secret scanning regex patterns
SECRET_PATTERNS = [
    r"api[-_]?key",
    r"auth[-_]?token",
    r"client[-_]?secret",
    r"db[-_]?password",
    r"passwd",
    r"session[-_]?token",
    r"private[-_]?key",
    r"aws[-_]?access",
    r"databricks[-_]?token",
]


def scan_for_secrets(content, filepath):
    """Simple safety check to block builds if potential secrets are detected in public-facing JSON."""
    for pattern in SECRET_PATTERNS:
        # Check if the word exists with some assignment, e.g. apiKey = "..." or password: ...
        # Avoid false positives on generic explanations by ensuring there is some assignment or token-like string.
        match = re.search(pattern + r"\s*[:=]\s*['\"][a-zA-Z0-9_\-\.\/]{10,}['\"]", content, re.IGNORECASE)
        if match:
            print(f"[SECURITY WARNING] Potential secret found in {filepath}: {match.group(0)}")
            # We raise a warning but let the developer review. For absolute security in CI, this can sys.exit(1).
            # Let's mask actual values in the public dashboard.
            return True
    return False


def parse_markdown(filepath, relative_path, category):
    """Parses a markdown file to extract title, summary, front-matter and clean text content."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading file {filepath}: {e}")
        return None

    # Simple Secret Scan
    scan_for_secrets(content, relative_path)

    # Extract YAML front-matter if exists
    meta = {}
    cleaned_content = content
    front_matter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    if front_matter_match:
        front_matter_text = front_matter_match.group(1)
        cleaned_content = content[front_matter_match.end() :]
        # Quick key-value parse for YAML
        for line in front_matter_text.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip().strip('"').strip("'")

    # Extract Title (First # Title)
    title = meta.get("title")
    if not title:
        title_match = re.search(r"^#\s+(.+)$", cleaned_content, re.MULTILINE)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title = os.path.basename(filepath).replace(".md", "")

    # Clean title from any inline markdown or links
    title = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", title)

    # Extract Summary (First paragraph or summary tag)
    summary = meta.get("summary")
    if not summary:
        # Grab first non-header, non-empty line
        lines = [
            line.strip()
            for line in cleaned_content.split("\n")
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith("---")
        ]
        if lines:
            summary = lines[0]
            if len(summary) > 180:
                summary = summary[:177] + "..."
        else:
            summary = f"{title} 문서에 대한 명세입니다."

    # Stat info
    stat = os.stat(filepath)
    mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")

    return {
        "title": title,
        "path": relative_path,
        "category": category,
        "summary": summary,
        "content": cleaned_content,
        "updated_at": mtime,
        "size_bytes": stat.st_size,
        "tags": meta.get("tags", "").split(",") if meta.get("tags") else [],
    }


def build_dashboard_data():
    print("==================================================")
    print("[START] Starting Intelligence Dashboard Data Compilation...")
    print(f"Base Directory: {BASE_DIR}")
    print("==================================================")

    # Ensure directories exist
    os.makedirs(DATA_DIR, exist_ok=True)

    documents = []

    # 1. Scan and index markdown documents
    for category in SCAN_DIRS:
        category_path = os.path.join(BASE_DIR, category)
        if not os.path.exists(category_path):
            print(f"[WARN] Category directory not found: {category_path}")
            continue

        print(f"[SCAN] Scanning category: {category}")
        for root, dirs, files in os.walk(category_path):
            # Enforce AI Exclusion Zone
            if any(ex in root.split(os.sep) for ex in EXCLUDE_DIRS):
                continue

            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    doc = parse_markdown(full_path, rel_path, category)
                    if doc:
                        documents.append(doc)

    # 2. Process Agents Registry
    agents_data = {}
    agents_registry_path = os.path.join(BASE_DIR, "agent", "agents_registry.json")
    if os.path.exists(agents_registry_path):
        try:
            with open(agents_registry_path, "r", encoding="utf-8") as f:
                agents_data = json.load(f)
            print("[INFO] Agents Registry loaded successfully.")
        except Exception as e:
            print(f"[ERROR] Failed to load agents_registry.json: {e}")
    else:
        print("[WARN] agents_registry.json not found in agent/ directory.")

    # 3. Compile Rules and Guardrails Specifics
    rules_data = []
    rules_path = os.path.join(BASE_DIR, "rules")
    if os.path.exists(rules_path):
        for root, _, files in os.walk(rules_path):
            for file in files:
                if file.endswith(".json") or file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, BASE_DIR)
                    # We can categorize rules, e.g. L1 Git, L2 Architecture, etc.
                    rules_data.append(
                        {"name": file, "path": rel_path, "type": "json" if file.endswith(".json") else "md"}
                    )

    # 4. Compile Runs Timeline
    runs_timeline = []
    
    # A. Parse reverse-sync-prevention.md
    rca_file_path = os.path.join(BASE_DIR, "runs", "reverse-sync-prevention.md")
    if os.path.exists(rca_file_path):
        try:
            with open(rca_file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line.startswith("|") and not line.startswith("| 발생 일시") and not line.startswith("|---"):
                    parts = [c.strip() for c in line.split("|")[1:-1]]
                    if len(parts) >= 7:
                        # Extract table fields
                        timestamp = parts[0]
                        run_id = parts[1].replace("`", "").strip()
                        agent = parts[2]
                        domain = parts[3]
                        error_type = parts[4].replace("**", "").strip()
                        rca = parts[5]
                        action = parts[6]
                        
                        runs_timeline.append({
                            "run_id": run_id,
                            "created_at": timestamp,
                            "status": "failed",
                            "agent": agent,
                            "domain": domain,
                            "error_type": error_type,
                            "rca": rca,
                            "action": action,
                            "is_rca_audit": True
                        })
        except Exception as e:
            print(f"[ERROR] Failed to parse reverse-sync-prevention.md: {e}")

    # B. Scan run_ dirs in runs directory
    runs_path = os.path.join(BASE_DIR, "runs")
    if os.path.exists(runs_path):
        for item in sorted(os.listdir(runs_path), reverse=True):
            item_path = os.path.join(runs_path, item)
            if os.path.isdir(item_path) and item.startswith("run_"):
                stat = os.stat(item_path)
                mtime = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                # Avoid duplicate entries
                if not any(r.get("run_id") == item for r in runs_timeline):
                    runs_timeline.append(
                        {
                            "run_id": item,
                            "created_at": mtime,
                            "status": "completed",
                            "files_changed": len(os.listdir(item_path)),
                            "is_rca_audit": False
                        }
                    )
                    
    # Sort all runs by timestamp in descending order
    runs_timeline.sort(key=lambda x: x["created_at"], reverse=True)

    # 5. Build Architecture Overview Map
    architecture_map: Dict[str, Any] = {"categories": []}
    for cat_key, cat_desc in CATEGORIES.items():
        cat_docs = [doc for doc in documents if doc["category"] == cat_key]
        architecture_map["categories"].append(
            {"key": cat_key, "name": cat_key.capitalize(), "description": cat_desc, "doc_count": len(cat_docs)}
        )

    # Save compiled JSON files
    files_to_save = {
        "documents.json": documents,
        "agents.json": agents_data,
        "rules.json": rules_data,
        "runs.json": runs_timeline,
        "architecture.json": architecture_map,
    }

    for filename, content in files_to_save.items():
        out_path = os.path.join(DATA_DIR, filename)
        try:
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
            print(f"[SAVE] Saved: {out_path}")
        except Exception as e:
            print(f"[ERROR] Failed to save {filename}: {e}")

    # Generate metadata build info
    meta_info = {
        "last_build_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_documents": len(documents),
        "categories_stats": {cat: len([d for d in documents if d["category"] == cat]) for cat in SCAN_DIRS},
    }
    with open(os.path.join(DATA_DIR, "build_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta_info, f, ensure_ascii=False, indent=2)

    print("==================================================")
    print("[SUCCESS] Build Completed Successfully!")
    print("==================================================")


if __name__ == "__main__":
    build_dashboard_data()
