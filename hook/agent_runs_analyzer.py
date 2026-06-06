import os
import glob
import re
from datetime import datetime
from typing import Any


class AgentRunsAnalyzer:
    """intelligence/runs 디렉터리에 축적된 에이전트 실행 및 7대 아티팩트 데이터를 수집, 분석하여

    품질 게이트 통과율 및 변경 안정성 지표를 종합 분석하는 Level 5 관찰성 분석 클래스입니다.
    """

    def __init__(self, run_archive_dir: str = "intelligence/runs"):
        self.run_archive_dir = os.path.abspath(run_archive_dir)

    def scan_runs(self) -> list[dict[str, Any]]:
        """모든 run_* 디렉터리를 스캔하고, 각 실행의 핵심 메타데이터 및 아티팩트 상태를 분석하여 수집합니다."""
        runs_data: list[dict[str, Any]] = []
        if not os.path.exists(self.run_archive_dir):
            return runs_data

        run_dirs = glob.glob(os.path.join(self.run_archive_dir, "run_*"))
        # 시간 역순 정렬
        run_dirs.sort(key=lambda d: os.path.getmtime(d) if os.path.exists(d) else 0, reverse=True)

        for r_dir in run_dirs:
            run_id = os.path.basename(r_dir)
            run_info: dict[str, Any] = {
                "run_id": run_id,
                "timestamp": None,
                "agent_name": "Unknown",
                "domain": "Unknown",
                "has_task": os.path.exists(os.path.join(r_dir, "task.md")),
                "has_manifest": os.path.exists(os.path.join(r_dir, "context-manifest.yaml")),
                "has_plan": os.path.exists(os.path.join(r_dir, "plan.md")),
                "has_diff": os.path.exists(os.path.join(r_dir, "diff.patch")),
                "has_test_log": os.path.exists(os.path.join(r_dir, "test.log")),
                "has_review": os.path.exists(os.path.join(r_dir, "review.md")),
                "has_risk": os.path.exists(os.path.join(r_dir, "risk.md")),
                "test_passed": False,
                "risk_level": "Unknown",
                "modified_files": [],
            }

            # 1. task.md 파싱 (Timestamp, Agent, Domain)
            task_path = os.path.join(r_dir, "task.md")
            if run_info["has_task"]:
                try:
                    with open(task_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        agent_match = re.search(r"-\s+\*\*Agent\*\*:\s*(.*)", content)
                        domain_match = re.search(r"-\s+\*\*Domain\*\*:\s*(.*)", content)
                        time_match = re.search(r"-\s+\*\*Timestamp\*\*:\s*(.*)", content)

                        if agent_match:
                            run_info["agent_name"] = agent_match.group(1).strip()
                        if domain_match:
                            run_info["domain"] = domain_match.group(1).strip()
                        if time_match:
                            run_info["timestamp"] = time_match.group(1).strip()
                except Exception:
                    pass

            # 2. test.log 분석 (검증 성공 유무 파싱)
            test_log_path = os.path.join(r_dir, "test.log")
            if run_info["has_test_log"]:
                try:
                    with open(test_log_path, "r", encoding="utf-8") as f:
                        log_content = f.read()
                        # "검증 성공" 혹은 "Success: no issues found" 혹은 "passed in" 확인
                        if "검증 성공" in log_content or "Success: no issues found" in log_content:
                            run_info["test_passed"] = True
                        elif "failed" in log_content or "❌" in log_content:
                            run_info["test_passed"] = False
                        else:
                            # 기본적으로 에러 지표가 없으면 통과한 것으로 유추
                            run_info["test_passed"] = "Error" not in log_content.lower()
                except Exception:
                    pass

            # 3. risk.md 분석 (리스크 레벨 추출)
            risk_path = os.path.join(r_dir, "risk.md")
            if run_info["has_risk"]:
                try:
                    with open(risk_path, "r", encoding="utf-8") as f:
                        risk_content = f.read()
                        # Risk Level 추출
                        level_match = re.search(r"\*\*Risk Level\*\*:\s*(\w+)", risk_content, re.IGNORECASE)
                        if level_match:
                            run_info["risk_level"] = level_match.group(1).strip()
                except Exception:
                    pass

            # 4. diff.patch 분석 (변경된 파일 목록 추출)
            diff_path = os.path.join(r_dir, "diff.patch")
            if run_info["has_diff"]:
                try:
                    with open(diff_path, "r", encoding="utf-8") as f:
                        diff_content = f.read()
                        # +++ b/path/to/file 추출
                        files = re.findall(r"\+\+\+ b/(.*)", diff_content)
                        run_info["modified_files"] = [f.strip() for f in files]
                except Exception:
                    pass

            runs_data.append(run_info)

        return runs_data

    def calculate_statistics(self, runs_data: list[dict[str, Any]]) -> dict[str, Any]:
        """스캔된 데이터를 취합하여 합격률, 리스크 분포, 에이전트별 성능 통계를 산출합니다."""
        total_runs = len(runs_data)
        if total_runs == 0:
            return {
                "total_runs": 0,
                "artifact_completeness": 0.0,
                "test_pass_rate": 0.0,
                "risk_distribution": {},
                "agent_summary": {},
            }

        completed_artifacts_count = 0
        total_expected_artifacts = total_runs * 7  # 7대 핵심 아티팩트
        test_passes = 0
        risk_dist = {"Low": 0, "Medium": 0, "High": 0, "Unknown": 0}
        agent_stats = {}

        for run in runs_data:
            # 아티팩트 완성도 계산
            run_artifacts = [
                run["has_task"],
                run["has_manifest"],
                run["has_plan"],
                run["has_diff"],
                run["has_test_log"],
                run["has_review"],
                run["has_risk"],
            ]
            completed_artifacts_count += sum(run_artifacts)

            # 테스트 성공률 계산
            if run["test_passed"]:
                test_passes += 1

            # 리스크 레벨 누적
            r_lvl = run["risk_level"]
            if r_lvl in risk_dist:
                risk_dist[r_lvl] += 1
            else:
                risk_dist["Unknown"] += 1

            # 에이전트별 통계
            agent = run["agent_name"]
            if agent not in agent_stats:
                agent_stats[agent] = {"runs": 0, "passes": 0}
            agent_stats[agent]["runs"] += 1
            if run["test_passed"]:
                agent_stats[agent]["passes"] += 1

        artifact_completeness = (completed_artifacts_count / total_expected_artifacts) * 100
        test_pass_rate = (test_passes / total_runs) * 100

        return {
            "total_runs": total_runs,
            "artifact_completeness": round(artifact_completeness, 2),
            "test_pass_rate": round(test_pass_rate, 2),
            "risk_distribution": risk_dist,
            "agent_summary": agent_stats,
        }

    def generate_summary_report(self, output_path: str | None = None) -> str:
        """스캔 및 통계 결과를 시각적이고 전문적인 마크다운 종합 리포트로 내보냅니다."""
        if output_path is None:
            output_path = os.path.join(self.run_archive_dir, "harness_analytics_report.md")

        runs_data = self.scan_runs()
        stats = self.calculate_statistics(runs_data)

        # 마크다운 리포트 생성
        markdown = f"""# 📈 Test Harness & Agent Runs Analytics Report

이 보고서는 프로젝트의 AI 에이전트 실행 품질 지표를 분석하고 수집된 7대 아티팩트의 무결성을 정량적으로 추적하는 관찰성 분석 리포트입니다.

- **리포트 분석 시간**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **분석 대상 디렉터리**: `{self.run_archive_dir}`

---

## 📊 1. 종합 핵심 성과 지표 (KPI)

| 지표 | 측정값 | 설명 |
| :--- | :--- | :--- |
| **총 에이전트 수행 횟수 (Total Runs)** | `{stats['total_runs']} 회` | 수집된 총 고유 실행 세션 수 |
| **아티팩트 준수율 (Completeness)** | `{stats['artifact_completeness']}%` | 7대 핵심 아티팩트가 모두 보관되었는지 검증 비율 |
| **품질 관문 통과율 (Test Pass Rate)** | `{stats['test_pass_rate']}%` | 정적 구문 및 테스트 검증 통과 비율 |

---

## 🛡️ 2. 배포 리스크 수준 분포 (Risk Distribution)

에이전트 변경 사항에 대해 배포 가드가 할당한 위험도 통계입니다.

- **Low Risk**: `{stats['risk_distribution'].get('Low', 0)}` 건
- **Medium Risk**: `{stats['risk_distribution'].get('Medium', 0)}` 건
- **High Risk**: `{stats['risk_distribution'].get('High', 0)}` 건
- **Unknown**: `{stats['risk_distribution'].get('Unknown', 0)}` 건

---

## 🤖 3. 에이전트별 구문 검증 합격률 (Agent Performance)

| 에이전트 이름 | 실행 횟수 | 합격 횟수 | 합격률 |
| :--- | :---: | :---: | :---: |
"""

        for agent, a_stat in stats["agent_summary"].items():
            rate = round((a_stat["passes"] / a_stat["runs"]) * 100, 2)
            markdown += f"| `{agent}` | {a_stat['runs']} | {a_stat['passes']} | `{rate}%` |\n"

        markdown += """
---

## 📋 4. 개별 에이전트 실행 타임라인 이력

최근 실행된 세션들의 아티팩트 수집 상세 상태 정보입니다.

| 실행 ID | 에이전트 | 도메인 | 테스트 통과 | 리스크 | 수집된 아티팩트 목록 |
| :--- | :--- | :--- | :---: | :---: | :--- |
"""

        for run in runs_data:
            test_icon = "✅ PASS" if run["test_passed"] else "❌ FAIL"
            artifacts = []
            if run["has_task"]:
                artifacts.append("Task")
            if run["has_manifest"]:
                artifacts.append("Manifest")
            if run["has_plan"]:
                artifacts.append("Plan")
            if run["has_diff"]:
                artifacts.append("Diff")
            if run["has_test_log"]:
                artifacts.append("TestLog")
            if run["has_review"]:
                artifacts.append("Review")
            if run["has_risk"]:
                artifacts.append("Risk")

            artifacts_str = ", ".join(artifacts) if artifacts else "없음"

            markdown += f"| `{run['run_id']}` | `{run['agent_name']}` | `{run['domain']}` | {test_icon} | `{run['risk_level']}` | {artifacts_str} |\n"

        # 디렉터리 존재 보장 및 쓰기
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        return os.path.abspath(output_path)


if __name__ == "__main__":
    analyzer = AgentRunsAnalyzer()
    report_file = analyzer.generate_summary_report()
    print(f"[Analyzer] ✔ 대시보드 리포트가 성공적으로 저장되었습니다: {report_file}")
