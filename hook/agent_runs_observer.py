import os
import subprocess
from datetime import datetime


def _parse_bool(value: str) -> bool:
    """Parse CLI boolean values without argparse's bool("false") pitfall."""
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    raise ValueError(f"Unsupported boolean value: {value}")


class AgentRunsObserver:
    """에이전트 실행 주기를 모니터링하고 7대 핵심 아티팩트 이력을 영속 로깅하는 프로덕션 레벨 관찰 훅 클래스입니다."""

    def __init__(self, agent_name: str, domain: str, run_archive_dir: str = "intelligence/runs"):
        self.agent_name = agent_name
        self.domain = domain
        # 고유한 실행 ID 발급
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(3).hex()}"
        self.run_archive_dir = os.path.abspath(run_archive_dir)
        self.run_dir = os.path.join(self.run_archive_dir, self.run_id)

    def before_agent_run(
        self,
        task_description: str,
        base_standards_path: str = "intelligence/context/coding-standards.md",
        plan_content: str | None = None,
    ):
        """에이전트 실행 전, RUN_ID 아카이브 디렉터리를 생성하고 작업 명세, 컨텍스트 매니페스트 및 계획을 로깅합니다."""
        os.makedirs(self.run_dir, exist_ok=True)

        # [1] task.md 기록
        task_path = os.path.join(self.run_dir, "task.md")
        with open(task_path, "w", encoding="utf-8") as f:
            f.write(f"# Agent Run Task Specification ({self.run_id})\n\n")
            f.write(f"- **Agent**: {self.agent_name}\n")
            f.write(f"- **Domain**: {self.domain}\n")
            f.write(f"- **Timestamp**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Task Description\n{task_description}\n")

        # [2] context-manifest.yaml 기록
        manifest_path = os.path.join(self.run_dir, "context-manifest.yaml")
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(f"run_id: {self.run_id}\n")
            f.write(f"base_standards: {base_standards_path}\n")
            f.write(f"domain_context: intelligence/context/{self.domain}.summary.md\n")
            f.write(f"timestamp: {datetime.now().isoformat()}\n")

        # [3] plan.md 기록 (실행 계획 및 결정 근거)
        plan_path = os.path.join(self.run_dir, "plan.md")
        with open(plan_path, "w", encoding="utf-8") as f:
            f.write(f"# Agent Execution Plan ({self.run_id})\n\n")
            if plan_content:
                f.write(plan_content)
            else:
                f.write(f"## 1. 분석 계획\n- 에이전트 '{self.agent_name}' 가 업무 요청 분석을 시작합니다.\n\n")
                f.write(
                    "## 2. 세부 설계 단계\n- 문법 정합성 검증 및 3-Layer 코딩 표준을 위배하지 않도록 검사 단계를 정의합니다.\n"
                )

    def after_agent_run(
        self,
        success: bool,
        diff_content: str,
        review_content: str | None = None,
        risk_content: str | None = None,
    ):
        """에이전트 구동 완료 후, 코드 변경점 패치, 검증 테스트 결과, 코드 리뷰, 리스크 평가서를 일괄 수집 보관합니다."""
        os.makedirs(self.run_dir, exist_ok=True)

        # [4] diff.patch 기록
        diff_path = os.path.join(self.run_dir, "diff.patch")
        with open(diff_path, "w", encoding="utf-8") as f:
            f.write(diff_content)

        # [5] test.log 기록 (정적 검증 tests/verify_code.py 실행 결과 수집)
        test_log_path = os.path.join(self.run_dir, "test.log")
        final_success = success
        try:
            # pytest 내에서 재귀 루프가 도는 것을 방지하기 위해 구문 검증 스크립트만 실행합니다.
            import sys

            result = subprocess.run(
                [sys.executable, "tests/verify_code.py"],
                capture_output=True,
                text=True,
                cwd=os.getcwd(),
            )
            final_success = success and result.returncode == 0
            with open(test_log_path, "w", encoding="utf-8") as f:
                f.write("=== Syntax Verification Execution Log ===\n")
                f.write(f"requested_success: {success}\n")
                f.write(f"verifier_exit_code: {result.returncode}\n")
                f.write(f"final_success: {final_success}\n\n")
                f.write(result.stdout)
                if result.stderr:
                    f.write("\n=== Standard Error Stream ===\n")
                    f.write(result.stderr)
        except Exception as e:
            final_success = False
            with open(test_log_path, "w", encoding="utf-8") as f:
                f.write("=== Syntax Verification Execution Log ===\n")
                f.write(f"requested_success: {success}\n")
                f.write("final_success: False\n\n")
                f.write(f"정적 빌드 검증 실행 중 예외 발생: {str(e)}")

        # [6] review.md 기록 (qa-reviewer 피드백서)
        review_path = os.path.join(self.run_dir, "review.md")
        with open(review_path, "w", encoding="utf-8") as f:
            f.write(f"# QA Review Specification ({self.run_id})\n\n")
            if review_content:
                f.write(review_content)
            else:
                f.write(
                    "## 1. 코드 스타일 및 린트 피드백\n- PEP 8 및 프로젝트 아키텍처 규칙을 위반하지 않았습니다.\n\n"
                )
                f.write("## 2. 아키텍처 규칙 정합성\n- 3-Layer 규칙이 정상 준수되었습니다.\n")

        # [7] risk.md 기록 (ops-release-guard 배포 리스크 리포트)
        risk_path = os.path.join(self.run_dir, "risk.md")
        with open(risk_path, "w", encoding="utf-8") as f:
            f.write(f"# Operations Release Guard Risk Assessment ({self.run_id})\n\n")
            if risk_content:
                f.write(risk_content)
            else:
                default_risk = "Low" if final_success else "High"
                f.write(f"## 1. 배포 리스크 분석 결과\n- **Risk Level**: {default_risk}\n\n")
                if not final_success:
                    f.write("- 검증 성공 플래그 또는 정적 검증 결과가 실패 상태입니다.\n\n")
                f.write("## 2. 롤백 가용성\n- git apply -R 패치를 통한 즉각 수동 복구 가이드를 내포합니다.\n")

        print(f"[Observer] ✔ {self.run_id} 에이전트 실행에 대한 7대 관찰 아티팩트 보관 완료.")

        # [실시간 피드백 루프 자동화] 에이전트 완료 즉시 전체 지표 통계를 종합 업데이트합니다.
        try:
            from intelligence.hook.agent_runs_analyzer import AgentRunsAnalyzer

            analyzer = AgentRunsAnalyzer(run_archive_dir=self.run_archive_dir)
            report_file = analyzer.generate_summary_report()
            print(f"[Observer] 📈 [실시간 관찰성] 전체 에이전트 누적 지표 보고서 업데이트 완료: {report_file}")
        except Exception as e:
            print(f"[Observer] ⚠️ 누적 통계 보고서 갱신 중 예외 발생 (무시하고 계속 진행): {str(e)}")

        # [역동기화 자가치유 피드백 루프 자동화] 실행이 실패했을 경우, 역동기화 모듈을 트리거하여 재발방지 수칙을 자동으로 도출/주입합니다.
        if not final_success:
            try:
                from intelligence.hook.reverse_sync import ReverseSyncManager

                default_archive_dir = os.path.abspath("intelligence/runs")
                if self.run_archive_dir == default_archive_dir:
                    sync_manager = ReverseSyncManager(run_archive_dir=self.run_archive_dir)
                else:
                    isolated_context_dir = os.path.join(self.run_archive_dir, "_context")
                    sync_manager = ReverseSyncManager(
                        run_archive_dir=self.run_archive_dir,
                        context_dir=isolated_context_dir,
                    )
                sync_manager.execute_reverse_sync_cycle(run_id=self.run_id)
                print(
                    f"[Observer] 🔄 [자가 치유 역동기화] 실패 세션 '{self.run_id}' 에 대한 재발방지 대책 도출 및 체크리스트 주입 성공."
                )
            except Exception as se:
                print(f"[Observer] ⚠️ 자가 치유 역동기화 구동 중 예외 발생 (무시하고 계속 진행): {str(se)}")


if __name__ == "__main__":
    import argparse
    import sys

    parser = argparse.ArgumentParser(description="OEquality BI AI Agent Runs Observer CLI")
    subparsers = parser.add_subparsers(dest="command", help="실행 명령 (start, finish)")

    # [1] start 명령 정의
    start_parser = subparsers.add_parser("start", help="에이전트 실행 시작 선언 및 초기 아티팩트 보관")
    start_parser.add_argument("--agent", required=True, help="에이전트 이름 (예: qa-reviewer)")
    start_parser.add_argument("--domain", required=True, help="업무 도메인 (예: cqms, gmes)")
    start_parser.add_argument("--task", required=True, help="수행할 작업 구체 명세")
    start_parser.add_argument("--plan", help="생각의 흐름 CoT 계획 (생략 시 디폴트 생성)")

    # [2] finish 명령 정의
    finish_parser = subparsers.add_parser("finish", help="에이전트 완료 선언 및 7대 아티팩트 일괄 보관")
    finish_parser.add_argument("--run-id", help="에이전트 실행 ID (생략 시 가장 최근에 시작된 세션 ID 자동 검출)")
    finish_parser.add_argument(
        "--success",
        type=_parse_bool,
        default=True,
        help="테스트 정합 성공 및 작업 완수 여부 (true/false)",
    )
    finish_parser.add_argument("--diff", default="", help="코드 변경점 패치 내역")
    finish_parser.add_argument("--review", help="리뷰어 피드백 가이드라인")
    finish_parser.add_argument("--risk", help="릴리즈 배포 가드 리스크 평가")

    args = parser.parse_args()

    # 세션 락 경로
    latest_run_path = os.path.abspath("intelligence/runs/latest_run_id.txt")

    if args.command == "start":
        observer = AgentRunsObserver(agent_name=args.agent, domain=args.domain)
        observer.before_agent_run(task_description=args.task, plan_content=args.plan)

        # 최신 실행 세션 기록 보관 (상태 저장)
        try:
            os.makedirs(os.path.dirname(latest_run_path), exist_ok=True)
            with open(latest_run_path, "w", encoding="utf-8") as f:
                f.write(f"{observer.run_id},{args.agent},{args.domain}")
        except Exception:
            pass

        print("✔ [Observer CLI] 에이전트 실행이 성공적으로 시작되었습니다.")
        print(f"👉 RUN_ID: {observer.run_id}")
        print(f"📁 ARCHIVE: {observer.run_dir}")

    elif args.command == "finish":
        run_id = args.run_id
        agent_name = "UnknownAgent"
        domain = "cqms"

        # run_id 생략 시 최신 기동한 세션 정보 자동 탐색 복구
        if not run_id:
            if os.path.exists(latest_run_path):
                try:
                    with open(latest_run_path, "r", encoding="utf-8") as f:
                        data = f.read().strip().split(",")
                        run_id = data[0]
                        if len(data) > 1:
                            agent_name = data[1]
                        if len(data) > 2:
                            domain = data[2]
                    print(f"ℹ [Observer CLI] 최근 실행 세션을 자동 검출해 롤백/복원했습니다: {run_id}")
                except Exception:
                    pass

        if not run_id:
            print("🚨 [Observer CLI] 오류: 완료할 RUN_ID를 찾지 못했습니다. --run-id 를 명시하십시오.", file=sys.stderr)
            sys.exit(1)

        # 복구된 정보로 Observer 재생성
        observer = AgentRunsObserver(agent_name=agent_name, domain=domain)
        # run_id와 run_dir 재할당 강제화
        observer.run_id = run_id
        observer.run_dir = os.path.join(observer.run_archive_dir, run_id)

        observer.after_agent_run(
            success=args.success,
            diff_content=args.diff,
            review_content=args.review,
            risk_content=args.risk,
        )
        print(f"✔ [Observer CLI] 에이전트 실행 품질 아티팩트 관찰 로깅이 완료되었습니다: {run_id}")

    else:
        parser.print_help()
