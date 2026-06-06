# -*- coding: utf-8 -*-
"""
reverse_sync.py - Autonomous Reverse Sync & Recurrence Prevention System

This module implements the self-healing and auto-adaptation capabilities of the 
GoEQ BI Harness Engineering framework. It watches recent agent run logs, diagnoses 
runtime/static verification failures, formulates recurrence prevention guidelines, 
and synchronizes these rules back into the domain checklists and standards.
"""

import os
import re
import sys
from datetime import datetime


class ReverseSyncManager:
    """에이전트 실행 실패 이력을 역동적으로 감지하고 스스로 재발방지 대책을 세워 컨텍스트에 피드백(역동기화)하는 매니저 클래스입니다."""

    def __init__(self, run_archive_dir: str = "intelligence/runs", context_dir: str = "intelligence/context"):
        self.run_archive_dir = os.path.abspath(run_archive_dir)
        self.context_dir = os.path.abspath(context_dir)
        self.prevention_log_path = os.path.join(self.context_dir, "reverse_sync_prevention.md")

    def _get_latest_run_id(self) -> str | None:
        """가장 최근에 기록된 에이전트 RUN_ID를 조회합니다."""
        latest_run_txt = os.path.join(self.run_archive_dir, "latest_run_id.txt")
        if os.path.exists(latest_run_txt):
            try:
                with open(latest_run_txt, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        # "run_id,agent,domain" 구조 파싱
                        parts = content.split(",")
                        return parts[0]
            except Exception as e:
                print(f"[ReverseSync] ⚠️ latest_run_id.txt 읽기 실패: {str(e)}")

        # 파일이 없거나 오류 시 디렉터리 타임스탬프 역순 정렬
        if os.path.exists(self.run_archive_dir):
            runs = [
                d
                for d in os.listdir(self.run_archive_dir)
                if os.path.isdir(os.path.join(self.run_archive_dir, d)) and d.startswith("run_")
            ]
            if runs:
                runs.sort()
                return runs[-1]
        return None

    def _read_run_info(self, run_id: str) -> tuple[str, str, str, str]:
        """지정된 실행 아카이브 내에서 에이전트 이름, 도메인, 태스크 설명 및 오류 로그를 추출합니다."""
        run_dir = os.path.join(self.run_archive_dir, run_id)
        agent_name = "UnknownAgent"
        domain = "general"
        task_desc = "Unknown Task"
        error_log = ""

        # context-manifest.yaml 에서 도메인 파싱
        manifest_path = os.path.join(run_dir, "context-manifest.yaml")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r", encoding="utf-8") as f:
                content = f.read()
                domain_match = re.search(
                    r"domain_context:\s*intelligence/context/([a-zA-Z0-9_\-]+)\.summary\.md", content
                )
                if domain_match:
                    domain = domain_match.group(1)

        # task.md 에서 에이전트명 및 요구사항 파싱
        task_path = os.path.join(run_dir, "task.md")
        if os.path.exists(task_path):
            with open(task_path, "r", encoding="utf-8") as f:
                content = f.read()
                agent_match = re.search(r"-\s*\*\*Agent\*\*:\s*([^\n]+)", content)
                if agent_match:
                    agent_name = agent_match.group(1).strip()

                desc_match = re.search(r"## Task Description\n(.*)", content, re.DOTALL)
                if desc_match:
                    task_desc = desc_match.group(1).strip()

        # test.log 에서 에러 로그 추출
        test_log_path = os.path.join(run_dir, "test.log")
        if os.path.exists(test_log_path):
            with open(test_log_path, "r", encoding="utf-8") as f:
                error_log = f.read()

        return agent_name, domain, task_desc, error_log

    def analyze_and_diagnose(self, error_log: str) -> tuple[str, str, str]:
        """오류 로그의 시그니처를 정밀 분석하여 에러 분류, 근본 원인 및 재발방지 표준 가이드를 도출합니다."""

        # 1. 날짜 타입 및 ValueError 매칭
        if "ValueError" in error_log and ("where_date_between" in error_log or "invalid literal for int" in error_log):
            return (
                "Date_Format_Value_Error",
                "QueryFilter.where_date_between 또는 날짜 정수 형변환 중 하이픈(예: '2026-01-01') 문자열이 정수로 파싱되지 않고 실패함.",
                "QueryFilter.where_date_between 사용 시 하이픈(-)이 없고 캐스팅이 보장되는 YYYYMMDD 형태의 날짜 문자열만 전달하도록 입력 규격을 보장하거나 문자열 정제 작업을 경유할 것.",
            )

        # 2. Pandas 컬럼 누락에 따른 KeyError 매칭
        if "KeyError" in error_log and (
            "not in index" in error_log
            or "not in the [columns]" in error_log
            or "PERIOD_NAME" in error_log
            or "INDEX_COLUMNS" in error_log
        ):
            return (
                "Pandas_Missing_Schema_Error",
                "Pandas DataFrame을 다루는 전처리 또는 피벗 연산 중 필요한 필수 지표 컬럼(INDEX_COLUMNS 등) 혹은 메타 데이터 컬럼이 모의 데이터셋이나 소스 연산 결과에 누락되어 조작 실패.",
                "DataFrame 조작 및 피벗 연산 함수(예: preprocessing_cum_df, preprocessing_cum_pivot_df)를 테스트하거나 호출할 때는, 필수 식별 컬럼들과 지표값들이 온전히 포함되어 데이터 구조가 보장되도록 Mock 및 파라미터를 완전하게 재현할 것.",
            )

        # 3. AssertionError 컬럼 불일치 매칭
        if "AssertionError" in error_log and ("not found in Index" in error_log or "rawdata.columns" in error_log):
            return (
                "Assertion_Column_Mismatch",
                "데이터 파이프라인의 결과물이 기대 명세(ALL_YN_INPUT 등)와 일치하지 않아 유닛 테스트 Assert 단계에서 검증 실패.",
                "데이터 파이프라인 결과에 대해 assert 검사 시, 실제 추가/수정 완료되는 명세 컬럼(예: ALL_YN, JDG_YN)을 정확히 인지하여 정합성 검사를 기술하고, 임의의 레거시 명칭을 어서트하지 말 것.",
            )

        # 4. 레이어 경계 위반 매칭
        if "LayerBoundaryViolation" in error_log or "test_layer_boundary" in error_log:
            return (
                "Layer_Boundary_Violation",
                "3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생.",
                "경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것.",
            )

        # 5. MyPy 타입 에러 매칭
        if "MyPy type check failed" in error_log or "Success: no issues found" not in error_log and "mypy" in error_log:
            return (
                "Static_Type_Check_Failure",
                "MyPy 정적 타입 분석 과정에서 자료형 지정을 생략하거나, 다중 파라미터 간 타입 불합치 사태 감출.",
                "모든 함수의 인자, 리턴 타입 및 DataFrame/Series 반환 형태에 정밀한 Type Annotation(예: pd.DataFrame, Optional[str])을 수립할 것.",
            )

        # 6. 기타 일반 예외
        return (
            "Generic_Runtime_Exception",
            "동작 중 예상치 못한 런타임 예외 혹은 유닛 테스트 실패 발생.",
            "동일 실패가 재발하지 않도록 단위 테스트 커버리지를 보완하고, 예외 안전장치(Defensive programming)를 소스 코드 및 테스트 스캐폴딩에 탑재할 것.",
        )

    def write_prevention_report(
        self, run_id: str, agent_name: str, domain: str, task: str, category: str, cause: str, prevention: str
    ) -> None:
        """중앙 역동기화 장애 대응 및 재발방지 리포트(reverse_sync_prevention.md)에 이력을 기록합니다."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        os.makedirs(self.context_dir, exist_ok=True)

        # 파일이 없을 시 헤더 생성
        if not os.path.exists(self.prevention_log_path):
            with open(self.prevention_log_path, "w", encoding="utf-8") as f:
                f.write("# 🔄 역동기화 재발방지 및 자체 피드백 로그 (Reverse Sync Prevention Logs)\n\n")
                f.write(
                    "이 파일은 에이전트 구동 과정에서 지속/누적되는 오류를 감지하여, 하네스 자체 역동기화 훅이 수립한 **근본 원인 분석(RCA)** 및 **재발방지 조치 사항**을 아카이빙하는 문서입니다. 향후 에이전트는 본 로그를 최우선 참고하여 실수를 자가 정제해야 합니다.\n\n"
                )
                f.write(
                    "| 발생 일시 | RUN ID | 에이전트 | 도메인 | 에러 분류 | 근본 원인 (RCA) | 재발방지 조치 사항 |\n"
                )
                f.write("|---|---|---|---|---|---|---|\n")

        # 테이블 행 추가
        row = f"| {timestamp} | `{run_id}` | {agent_name} | {domain.upper()} | **{category}** | {cause} | {prevention} |\n"
        with open(self.prevention_log_path, "a", encoding="utf-8") as f:
            f.write(row)

        print(f"[ReverseSync] 📝 중앙 예방 조치서 리포팅 완료: {self.prevention_log_path}")

    def sync_to_domain_checklist(self, domain: str, category: str, prevention: str) -> bool:
        """도메인 안전 자가진단표(intelligence/context/*.checklist.md)에 역동기화 재발방지 검사 조항을 영속 주입합니다."""
        checklist_file = os.path.join(self.context_dir, f"{domain}.checklist.md")
        if not os.path.exists(checklist_file):
            print(f"[ReverseSync] ⚠️ {domain} 체크리스트 파일을 찾을 수 없어 역동기화를 건너뜁니다: {checklist_file}")
            return False

        with open(checklist_file, "r", encoding="utf-8") as f:
            content = f.read()

        # 중복 삽입 방지 체크
        unique_marker = f"[{category}]"
        if unique_marker in content or prevention[:20] in content:
            print(
                f"[ReverseSync] ℹ️ 이미 동등한 재발방지 규칙이 {domain} 체크리스트에 탑재되어 있습니다. (역동기화 중복 방지)"
            )
            return True

        # "## 🔄 5. 역동기화 재발 방지 대책" 섹션 존재 유무 탐지
        section_title = "## 🔄 5. 역동기화 재발 방지 대책 (Reverse Sync Auto-Prevention)"
        new_checkbox = f"- [ ] {unique_marker} {prevention}\n"

        if section_title in content:
            # 섹션이 이미 존재하므로 그 아래에 규칙을 추가
            parts = content.split(section_title)
            header_part = parts[0] + section_title + "\n"
            body_part = parts[1]

            # 본문의 첫 줄 아래나 끝부분에 배치
            updated_content = header_part + new_checkbox + body_part
        else:
            # 섹션이 없으므로 파일 끝에 신규 추가
            updated_content = (
                content.rstrip()
                + f"\n\n---\n\n{section_title}\n"
                + "> [!IMPORTANT]\n"
                + "> 이 조항은 하네스 자가 치유(Self-Healing) 엔진에 의해 런타임 오류로부터 자동 도출된 필수 예방 규격입니다.\n\n"
                + new_checkbox
            )

        with open(checklist_file, "w", encoding="utf-8") as f:
            f.write(updated_content)

        print(f"[ReverseSync] 🔄 역동기화 성공! {domain}.checklist.md 파일에 자가 예방수칙 주입 완료.")
        return True

    def execute_reverse_sync_cycle(self, run_id: str | None = None) -> bool:
        """전체 역동기화 워크플로우 루프를 가동합니다."""
        target_run = run_id or self._get_latest_run_id()
        if not target_run:
            print("[ReverseSync] ❌ 분석할 에이전트 실행 기록(RUN_ID)을 찾지 못했습니다.")
            return False

        print(f"[ReverseSync] 🔍 최신 에이전트 실행 기록을 로드하여 역동기화 정밀 분석을 실시합니다: {target_run}")
        agent_name, domain, task, error_log = self._read_run_info(target_run)

        # 오류 로그 확인
        if not error_log or "final_success: True" in error_log:
            # 성공한 세션이거나 분석 가능한 예외 로그가 확보되지 않은 경우
            if (
                "final_success: False" not in error_log
                and "ValueError" not in error_log
                and "KeyError" not in error_log
                and "AssertionError" not in error_log
            ):
                print(
                    f"[ReverseSync] 🎉 {target_run} 세션은 완결 성공 상태이거나 오류 로그가 없습니다. 루프를 평화롭게 종료합니다."
                )
                return True

        # 분석 및 예방조치 수립
        category, cause, prevention = self.analyze_and_diagnose(error_log)

        # 중앙 대장 기록
        self.write_prevention_report(
            run_id=target_run,
            agent_name=agent_name,
            domain=domain,
            task=task.replace("\n", " ").replace("|", "I"),
            category=category,
            cause=cause,
            prevention=prevention,
        )

        # 도메인 자가진단표 역동기화 결합
        if domain and domain != "general":
            self.sync_to_domain_checklist(domain=domain, category=category, prevention=prevention)

        # 일반 standards 파일 업데이트 반영도 가능
        return True


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OEquality BI Self-Healing & Reverse Sync Engine")
    parser.add_argument("--run-id", help="분석 타겟 에이전트 실행 ID (생략 시 최신 런 자동 검출)")
    args = parser.parse_args()

    sync_manager = ReverseSyncManager()
    success = sync_manager.execute_reverse_sync_cycle(run_id=args.run_id)
    if success:
        print("[ReverseSync] ✔ 자가 치유 역동기화 연산 사이클이 정상 작동 종료되었습니다.")
        sys.exit(0)
    else:
        print("[ReverseSync] ❌ 역동기화 구동 실패.")
        sys.exit(1)
