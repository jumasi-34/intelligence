# agent-runs-observer.md (에이전트 실행 로깅 및 관찰 훅 아키텍처 명세서)

이 문서는 시스템 내 자율 에이전트(`dev-*`, `qa-*`, `ops-*`, `specialist-*`)들의 실행 이력을 안전하고 투명하게 기록·관찰하여, AI의 오작동을 통제하고 하네스 엔지니어링의 신뢰성을 지속적으로 개선하기 위해 설계된 **에이전트 실행 관찰 및 Runs 로깅 훅(Agent Execution Runs Logger & Hook)**의 인프라 및 동작 규격을 정의합니다.

---

## 1. 에이전트 관찰 아키텍처 및 Runs 저장소

에이전트가 작동할 때마다 고유한 `RUN_ID`를 발급하고, 해당 작업의 라이프사이클 전체를 입체적으로 모니터링하여 아래 7대 아티팩트(Artifacts)를 `ai/runs/` 하위에 영속 보관합니다.

```
ai/runs/
└── run_YYYYMMDD_HHMMSS_[hash]/         # 각 실행별 고유 디렉터리
    ├── task.md                         # [1] 에이전트 실행 대상 작업 명세서
    ├── context-manifest.yaml           # [2] 인입 도메인 컨텍스트 & 파일 명세
    ├── plan.md                         # [3] 코딩 수정 전 분석 계획 (CoT)
    ├── diff.patch                      # [4] 생성/수정된 소스 코드의 git diff
    ├── test.log                        # [5] 변경 후 'make verify' 구문 검사 로그
    ├── review.md                       # [6] qa-reviewer 에이전트 품질 리뷰서
    └── risk.md                         # [7] ops-release-guard 배포 리스크 평가서
```

---

## 2. 에이전트 훅 라이프사이클 (Lifecycle Hooks)

에이전트 구동 엔진은 아래의 전/후 처리 훅 이벤트를 의무 바인딩하여, 오작동 시 코드의 실제 변경을 취소(Rollback)하고 원천적인 안전성을 수호합니다.

### 1) `before_agent_run` (에이전트 구동 전 수비 훅)
- **작업 ID 생성**: 실행 시간 및 해시를 기반으로 표준 `RUN_ID`(예: `run_20260530_185937_c91a3b`)를 발급하고 디렉터리를 가개설합니다.
- **컨텍스트 패키징**: `coding-standards.md`와 수정 영역에 매핑되는 도메인 `summary.md`, `checklist.md`를 취합하여 에이전트의 프롬프트 메모리에 안전 패키징 주입합니다 (`context-manifest.yaml` 기록).
- **보안 권한 체크**: 에이전트의 구동 세션이 현재 파일 및 DB를 수정할 수 있는 정당한 권한(`No-Mutation` 하 격리 수정 권한)을 획득했는지 최종 검토합니다.

### 2) `after_agent_run` (에이전트 기동 후 검증 훅)
- **코드 무결성 수집**: 에이전트 작업 완료 즉시 `diff.patch`를 캡처하여 오디팅용으로 기록 보관합니다.
- **로컬 검증 게이트 가동**: `make verify` 및 격리 테스트 시나리오를 자동 트리거하고, 결과 터미널 출력을 `test.log`에 실시간으로 리디렉션 기록합니다.
- **실패 유형 동적 태깅 (Fault Tagging)**:
  - 구문 문법 오류 발견 시 -> `tag: LINT_ERROR`
  - 도메인 체크리스트 위반 검출 시 -> `tag: DOMAIN_CHECK_VIOLATION`
  - 테스트 및 0분모 방어 통과 실패 시 -> `tag: RUNTIME_TEST_FAIL`
- **롤백 가드 (Rollback Mechanism)**: `test.log` 상에 오류가 있거나 `tag` 에 결함 분류가 잡힐 경우, 생성/수정된 코드를 즉각 지우고 이전 상태로 롤백(In-Memory rollback or Git reset)을 수행하여 실 운영 소스 오염을 원천 예방합니다.

---

## 3. 관찰 훅 인터페이스 자동화 예시 (Python Interface)

아래는 에이전트 실행 오케스트레이터가 가동하는 관찰 훅의 파이썬 프로세스 제어 구조입니다. 에이전트 구동 스크립트는 이 데코레이터 또는 헬퍼 클래스를 경유하여 기동되어야 합니다.

```python
import os
import time
import subprocess
from datetime import datetime

class AgentRunsObserver:
    """에이전트 실행 주기를 모니터링하고 7대 아티팩트 이력을 영속 로깅하는 인프라 클래스입니다."""

    def __init__(self, agent_name: str, domain: str):
        self.agent_name = agent_name
        self.domain = domain
        self.run_id = f"run_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{os.urandom(3).hex()}"
        self.run_dir = f"ai/runs/{self.run_id}"

    def before_agent_run(self, task_description: str):
        """에이전트 실행 전, RUN_ID 폴더를 생성하고 기본 작업 명세와 컨텍스트를 패킹합니다."""
        os.makedirs(self.run_dir, exist_ok=True)

        # 1. task.md 기록
        with open(f"{self.run_dir}/task.md", "w", encoding="utf-8") as f:
            f.write(f"# Agent Run Task Specification ({self.run_id})\n\n")
            f.write(f"- **Agent**: {self.agent_name}\n")
            f.write(f"- **Domain**: {self.domain}\n")
            f.write(f"- **Timestamp**: {datetime.now().isoformat()}\n\n")
            f.write(f"## Task Description\n{task_description}\n")

        # 2. context-manifest.yaml 생성 (가상 YAML 구조)
        with open(f"{self.run_dir}/context-manifest.yaml", "w", encoding="utf-8") as f:
            f.write(f"run_id: {self.run_id}\n")
            f.write(f"base_standards: ai/context/coding-standards.md\n")
            f.write(f"domain_context: ai/context/{self.domain}.summary.md\n")

    def after_agent_run(self, success: bool, diff_content: str):
        """에이전트 수정 완료 후, diff 패치와 로컬 `make verify` 테스트 로그를 수집 보관합니다."""
        # 1. diff.patch 보관
        with open(f"{self.run_dir}/diff.patch", "w", encoding="utf-8") as f:
            f.write(diff_content)

        # 2. make verify 자동 구동 및 로그 캡처
        try:
            result = subprocess.run(["make", "verify"], capture_output=True, text=True, cwd="/home/jumasi/workstation")
            with open(f"{self.run_dir}/test.log", "w", encoding="utf-8") as f:
                f.write("=== Make Verify Execution Log ===\n")
                f.write(result.stdout)
                f.write("\n=== Errors (If Any) ===\n")
                f.write(result.stderr)

            if result.returncode != 0:
                print(f"[Observer] [주의] {self.run_id} 검증 오류 감지! 롤백 처리를 트리거합니다.")
                # 여기에 소스 코드 롤백 및 Fault Tagging 코드 가동
        except Exception as e:
            with open(f"{self.run_dir}/test.log", "w", encoding="utf-8") as f:
                f.write(f"테스트 검증 구동 중 예외 발생: {str(e)}")
```
