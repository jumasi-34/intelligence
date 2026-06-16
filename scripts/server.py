#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Intelligence Console Web Server (server.py)
- Serves intelligence/dashboard/ static files.
- Provides an API endpoint (/api/build) to trigger build_dashboard.py.
- Resolves CORS / Local File fetch security blocks.
"""

import os
import subprocess
import sys
from flask import Flask, send_from_directory, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # workstation/intelligence
DASHBOARD_DIR = os.path.join(BASE_DIR, "dashboard")
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")

app = Flask(__name__, static_folder=DASHBOARD_DIR, static_url_path="")


@app.after_request
def disable_cache(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/")
def serve_index():
    return send_from_directory(DASHBOARD_DIR, "index.html")


@app.route("/<path:path>")
def serve_static(path):
    return send_from_directory(DASHBOARD_DIR, path)


@app.route("/api/build", methods=["POST"])
def trigger_build():
    build_script = os.path.join(SCRIPTS_DIR, "build_dashboard.py")
    # Use python environment path if possible, fallback to current sys.executable
    python_executable = sys.executable or "/home/jumasi/miniconda3/envs/goeq/bin/python"

    if not os.path.exists(build_script):
        return jsonify({"status": "error", "message": f"Build script not found: {build_script}"}), 500

    try:
        # Run the build script as a subprocess
        result = subprocess.run([python_executable, build_script], capture_output=True, text=True, check=True)
        print("[SERVER] Build script executed successfully.")
        print(result.stdout)

        return jsonify({"status": "success", "message": "인텔리전스 콘솔 리빌드가 정상적으로 완료되었습니다!"})
    except subprocess.CalledProcessError as e:
        print(f"[SERVER ERROR] Build script failed: {e}")
        print(e.stderr)
        return jsonify({"status": "error", "message": f"빌드 수행 실패: {e.stderr or str(e)}"}), 500


if __name__ == "__main__":
    print("==================================================")
    print("[START] Running Intelligence Console Server...")
    print(f"Directory: {DASHBOARD_DIR}")
    print("Address: http://localhost:8000")
    print("==================================================")
    app.run(host="0.0.0.0", port=8000, debug=False)
