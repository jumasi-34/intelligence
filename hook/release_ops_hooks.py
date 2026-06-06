import os
import glob
import urllib.request
from datetime import datetime
from typing import List, Optional, Dict, Any


class ReleaseOpsHooks:
    """배포 후 정적 진단 및 런타임 에러 캡처 시 최근 패치 연관성을 추적하는 읽기 전용 운영 훅 클래스입니다."""

    def __init__(self, run_archive_dir: str = "intelligence/runs"):
        # 가상환경 또는 프로젝트 루트 기준 상대/절대 경로 대응
        self.archive_dir = os.path.abspath(run_archive_dir)

    def run_smoke_test(self, port: int = 8501) -> bool:
        """배포 후 Streamlit 로컬 웹포트 응답 200 OK 여부를 초고속 검증합니다.

        안전한 읽기 전용 헤드리스 GET 요청을 사용하여 가용성을 진단합니다.
        """
        url = f"http://localhost:{port}"
        try:
            # 5초 타임아웃을 적용하여 가벼운 HTTP GET 요청 수행
            req = urllib.request.Request(url, headers={"User-Agent": "OpsSmokeTester/1.0"})
            with urllib.request.urlopen(req, timeout=5.0) as response:
                status = response.getcode()
                content = response.read().decode("utf-8", errors="ignore")

                # Streamlit 메인 페이지가 렌더링되거나 기본 HTML 구조가 반환되는지 확인
                # "OEquality BI", "Login", 혹은 streamlit 관련 지표 검색
                is_ok = (status == 200) and (
                    "OEquality BI" in content
                    or "Login" in content
                    or "streamlit" in content
                    or "st." in content
                    or "__streamlit" in content
                    or "<title>" in content
                )

                if is_ok:
                    print(f"[OpsHook] ✔ 배포 후 스모크 테스트 통과: Streamlit 가동 중 ({url})")
                    return True
                else:
                    print(f"[OpsHook] ⚠️ 스모크 테스트 응답 수신했으나 기대 텍스트 검색 실패 (상태 코드: {status})")
                    return False
        except Exception as e:
            print(f"[OpsHook] 🚨 배포 후 스모크 테스트 실패! 포트 {port} 응답 에러: {str(e)}")
            return False

    def triage_incident(self, traceback_err: str) -> dict:
        """장애 Traceback 인입 시 최근 24시간 내 intelligence/runs/ 패치들 중 연관 변경 파일을 격리 매핑합니다.

        철저히 읽기 전용으로 연관성만 매핑하며 어떠한 자동 복구 및 무단 롤백도 트리거하지 않습니다.
        """
        analysis_report = {
            "status": "No suspicious diff found",
            "suspect_run_id": None,
            "suspect_file": None,
            "checklist_created": False,
            "rollback_checklist_path": None,
        }

        # 1. 에러 로그 상에서 파일 단서 색출 (예: iqm_df.py)
        suspect_file_clue = ""
        potential_files = [
            "iqm_df.py",
            "cqms_df.py",
            "gmes_df.py",
            "sqlite_utils.py",
            "hope_df.py",
            "hgws_df.py",
            "qrs_df.py",
        ]
        for file_pattern in potential_files:
            if file_pattern in traceback_err:
                suspect_file_clue = file_pattern
                break

        if not suspect_file_clue:
            print("[OpsHook] ℹ️ 에러 Traceback 내에서 일치하는 주요 서비스 파일 단서를 찾지 못했습니다.")
            return analysis_report

        # 2. intelligence/runs/* 아래의 최근 diff.patch 전수 검색
        runs_pattern = os.path.join(self.archive_dir, "run_*")
        runs_list = glob.glob(runs_pattern)

        # 수정 시간(mtime) 기준으로 정렬하여 가장 최근에 생성된 run부터 분석 수행
        runs_list.sort(key=lambda p: os.path.getmtime(p) if os.path.exists(p) else 0, reverse=True)

        for run_path in runs_list:
            diff_patch_path = os.path.join(run_path, "diff.patch")
            if os.path.exists(diff_patch_path):
                try:
                    with open(diff_patch_path, "r", encoding="utf-8") as f:
                        patch_content = f.read()

                    # 패치 변경 본문에 에러 추적 대상 파일이 연루되었는지 대조
                    if suspect_file_clue in patch_content:
                        run_id = os.path.basename(run_path)
                        checklist_path = os.path.join(run_path, "rollback_checklist.md")

                        analysis_report.update(
                            {
                                "status": "🚨 SUSPECT DIFF DETECTED!",
                                "suspect_run_id": run_id,
                                "suspect_file": suspect_file_clue,
                                "checklist_created": True,
                                "rollback_checklist_path": checklist_path,
                            }
                        )

                        # 롤백 가이드 자동 어셈블
                        self._generate_rollback_checklist(run_id, suspect_file_clue, run_path, checklist_path)
                        break  # 최신에 변경된 가장 유력한 1개만 매핑 후 안전 브레이크
                except Exception as e:
                    print(f"[OpsHook] Run {run_path} 의 패치 분석 중 오류 발생: {str(e)}")

        return analysis_report

    def _generate_rollback_checklist(self, run_id: str, suspect_file: str, run_path: str, checklist_path: str):
        """장애 유발 의심 패치가 발견될 시 읽기 전용 복구 체크리스트를 자동 조합하여 보관합니다.

        가이드는 오직 관리자의 수동 복원을 보조하는 형태로 설계되며 자동 복원 명령을 단독 실행하지 않습니다.
        """
        checklist_content = f"""# 🚨 Incident Rollback Checklist ({run_id})

본 보고서는 최근 런타임 에러 추적 결과와 에이전트 수정 내역 간의 연관 분석을 통과해 자동 조립된 복구 가이드라인입니다.

## 1. 장애 분석 결과 요약
- **의심 유발 변경점**: `{suspect_file}`
- **장애 연계 Run ID**: `{run_id}`
- **분석 상태**: 최근 수정 영역과 에러 발생 Traceback 영역 일치율 초고위험
- **분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 2. 안전 롤백 실행 가이드 (수동 수행용)
> [!IMPORTANT]
> 인프라 안정성을 위해 자동 롤백은 차단되어 있습니다. 관리자가 수동 검토 후 아래 절차를 직접 처리하십시오.
>
> **🚫 4대 금지령 준수 확인**:
> 1. 자동 복구 스크립트를 직접 실행하지 마십시오 (Manual Git Rollback 권장).
> 2. 어드민 DB에 무단 테스트 데이터를 입력하여 검증하지 마십시오.
> 3. VM 정지나 Docker 프로세스 킬을 임의로 하지 마십시오.
> 4. 로그나 체크리스트 메일 본문에 패스워드나 시크릿 토큰을 기재해선 안 됩니다.

- [ ] **Step 1**: 위험 패치 수동 롤백 (로컬 복원)
  ```bash
  git apply -R {run_path}/diff.patch
  ```
- [ ] **Step 2**: 로컬 구문 무결성 정적 검증
  ```bash
  make verify
  ```
- [ ] **Step 3**: SQLite 세션 로그 잔존 락 클리어 여부 확인
- [ ] **Step 4**: 배포 서버 재가동 및 스모크 테스트 가동 (`ReleaseOpsHooks.run_smoke_test`)
"""
        try:
            with open(checklist_path, "w", encoding="utf-8") as f:
                f.write(checklist_content)
            print(
                f"[OpsHook] 📋 {run_id} 복구용 롤백 체크리스트(rollback_checklist.md)가 안전하게 자동 빌드 완료되었습니다."
            )
        except Exception as e:
            print(f"[OpsHook] 🚨 롤백 체크리스트 저장 실패: {str(e)}")

    def calculate_release_risk_score(
        self, diff_content: str, changed_files: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """분석 대상 패치의 변경 내역(diff)을 기반으로 안전 배포 위험도를 자동 산정합니다.

        - Low: 테스트 코드 전용 수정, 문서 변경, 영향 없는 리팩토링
        - Medium: 서비스/쿼리/신규 화면 변경, 캐시 TTL 수정
        - High: DB 스키마 수정, 인증/권한 수정, 운영 DB 커넥터/참조 변경, 대용량 패치 (>500 lines)
        """
        reasons: List[str] = []
        high_risk_triggers: List[str] = []
        medium_risk_triggers: List[str] = []

        # 1. 대상 파일 분석
        if changed_files is None:
            changed_files = []
            for line in diff_content.splitlines():
                if line.startswith("+++ b/"):
                    changed_files.append(line[6:].strip())

        # 2. 라인 수 기준으로 대규모 패치 검출 (Unclear Rollback)
        diff_lines = diff_content.splitlines()
        added_lines = [line for line in diff_lines if line.startswith("+") and not line.startswith("+++")]
        removed_lines = [line for line in diff_lines if line.startswith("-") and not line.startswith("---")]

        total_changed_lines = len(added_lines) + len(removed_lines)
        if total_changed_lines > 500:
            high_risk_triggers.append(
                f"Unclear Rollback: Large-scale patch detected ({total_changed_lines} changed lines)."
            )

        # 3. 파일 성격에 따른 리스크 분류
        has_production_files = False
        has_pages_files = False
        has_tests_or_docs_only = True

        for filepath in changed_files:
            filepath_lower = filepath.lower()
            if "tests/" in filepath_lower or filepath_lower.endswith(".md") or "requirements.txt" in filepath_lower:
                continue

            has_tests_or_docs_only = False
            if "pages/" in filepath_lower:
                has_pages_files = True
            elif "service/" in filepath_lower or "queries/" in filepath_lower or filepath_lower == "app.py":
                has_production_files = True

        if has_production_files:
            medium_risk_triggers.append("Modifications to Service or Query layer files.")
        if has_pages_files:
            medium_risk_triggers.append("Modifications to Streamlit Page/UI files.")

        # 4. 소스 코드 내 위협 패턴 검색 (추가된 라인 중심)
        added_content_block = "\n".join(added_lines).lower()

        # HIGH RISK: DB Schema Modification
        db_schema_keywords = ["create table", "alter table", "drop table", "drop column", "add column", "create index"]
        for kw in db_schema_keywords:
            if kw in added_content_block:
                high_risk_triggers.append(f"DB Schema Alteration: Found '{kw}' keyword in patch.")
                break

        # HIGH RISK: Auth / Permissions Modification
        auth_keywords = ["password", "credential", "secret_token", "jwt", "auth_key", "secret_key"]
        for kw in auth_keywords:
            if kw in added_content_block:
                high_risk_triggers.append(f"Auth/Permissions Change: Found security-sensitive '{kw}' keyword in patch.")
                break

        # HIGH RISK: Production DB Reference modification or direct get_client change
        prod_db_keywords = ["oracle_bi", "oracle_mes", "databricks", "db_client"]
        for kw in prod_db_keywords:
            if kw in added_content_block:
                # verify it's in a production file or query file, not in tests
                if any("tests/" not in f for f in changed_files):
                    high_risk_triggers.append(
                        f"Production DB Reference: Modified core connector / table reference of '{kw}'."
                    )
                    break

        # HIGH RISK: Sensitive files direct modifications
        for filepath in changed_files:
            if "login_page.py" in filepath or "db_client.py" in filepath or ".env" in filepath:
                high_risk_triggers.append(
                    f"Security Guardrail: Direct modification to core security file '{os.path.basename(filepath)}'."
                )

        # MEDIUM RISK: Cache TTL Modifications
        cache_keywords = ["@st.cache_data", "@st.cache_resource", "ttl="]
        for kw in cache_keywords:
            if kw in added_content_block or kw in "\n".join(removed_lines).lower():
                medium_risk_triggers.append(f"Cache TTL Modification: Caching behavior adjusted ({kw}).")
                break

        # 5. 최종 리스크 점수 및 등급 산정
        if high_risk_triggers:
            risk_level = "High"
            risk_score = min(100, 80 + len(high_risk_triggers) * 5)
            reasons = high_risk_triggers
            requires_approval = True
        elif medium_risk_triggers:
            risk_level = "Medium"
            risk_score = min(79, 40 + len(medium_risk_triggers) * 10)
            reasons = medium_risk_triggers
            requires_approval = False
        else:
            risk_level = "Low"
            risk_score = 10 if has_tests_or_docs_only else 25
            reasons = (
                ["Only tests, configurations, or minor documentation changes detected."]
                if has_tests_or_docs_only
                else ["Low impact changes."]
            )
            requires_approval = False

        return {
            "risk_level": risk_level,
            "risk_score": risk_score,
            "reasons": reasons,
            "requires_approval": requires_approval,
        }
