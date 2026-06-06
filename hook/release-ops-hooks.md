# release-ops-hooks.md (운영 및 릴리즈 훅 아키텍처 상세 명세서)

이 문서는 배포 직후 시스템의 무결성을 고속 검증하고, 런타임 장애(Incident) 발생 시 최근 코드 변경점(`diff.patch`)과 연계 분석하여 롤백 대책을 도출하는 **운영/릴리즈 훅 및 장애 트리아지 시스템(Ops/Release Hooks & Incident Triage System)**의 설계 규격을 정의합니다.

본 운영 시스템의 모든 인텔리전스 훅은 운영 안정성을 위해 철저히 **읽기 전용(Read-Only Mode)**으로 제한 기동됩니다.

---

## 1. 운영 훅 아키텍처 및 라이프사이클

시스템 배포 및 런타임 운영 주기에 유기적으로 연결되어 작동하는 4대 운영 훅(Ops Hooks)을 탑재합니다.

```
       [배포 실행 완료]
              │
              ▼
   (1) smoke_test_hook      ──>  Streamlit 로컬 기동 여부 & 포트 200 OK 헤드리스 진단
              │
       [런타임 장애 발생]
              │
              ▼
   (2) incident_triage_hook  ──>  SQLite log.db 에러 수집 및 'Suspect Diff' 자동 추적
              │
              ▼
   (3) recent_diff_analyzer ──>  에러 추적과 최근 ai/runs/ 내 patch 코드 연관성 분석
              │
              ▼
   (4) rollback_generator   ──>  안전 롤백 체크리스트(rollback_checklist.md) 자동 빌드
```

---

## 2. 안전 격벽 필터 (Read-Only Guard Rails)

AI 에이전트가 운영 시스템과 실시간 훅에 개입할 때 유발할 수 있는 2차 사고를 원천 방지하기 위해 아래의 **엄격한 금지 행동**을 강제 필터링합니다.

> [!CAUTION]
> ### [주의] 운영 훅 에이전트 4대 금지령 (Hard Block Rules)
> 1. **자동 롤백 금지 (No Automated Rollback)**: 코드 롤백, git revert, 혹은 컨테이너 무단 재기동 등의 물리 변경은 에이전트가 단독으로 행하지 못하며, 오직 검증된 롤백 가이드 문서만 전달해야 합니다.
> 2. **프로덕션 DB 수정 금지 (No Prod-DB Write)**: 실시간 수집 대상 DB(Databricks, Oracle)에 에이전트가 임의의 DDL, DML을 인입하거나 SQLite 운영 계정을 변경하는 수정을 가해서는 안 됩니다.
> 3. **인프라 제어 금지 (No Infrastructure Mutation)**: VM 정지, 가상 서버 포트 변경, 또는 Docker 및 Miniconda 환경 설정을 임의로 소거/삭제할 수 없습니다.
> 4. **자격 증명 은닉 (No Secret Retrieval)**: 환경변수(`.env`) 내부의 민감 키 정보를 원격 API나 메일 본문에 마스킹 없이 외부로 중계 노출시키는 행위를 엄격히 차단합니다.

---

## 3. 4대 세부 훅 상세 사양

### 1) 배포 후 스모크 테스트 훅 (`smoke_test_hook`)
- **목적**: 빌드 및 소스 합치 완료 직후 Streamlit 웹서버가 온전히 가동되어 사용자 포트에서 유효 응답을 주는지 가상의 헤드리스 요청(HTTP Get)을 날려 최종 점검합니다.
- **동작**: `http://localhost:8501/` 진입 및 응답 본문 내에 `"OEquality BI"` 또는 `"Login"` 텍스트가 정상 렌더링되는지 10초 내에 체크하여, 500 Server Error나 순환 참조 다운 현상을 원천 방지합니다.

### 2) 장애 알림 및 인시던트 트리아지 훅 (`incident_triage_hook`)
- **목적**: 사용자 런타임 오류가 로컬 SQLite(`log.db`)에 누적되거나 SMTP 메일 발송 지연 에러가 감지되는 즉시 작동합니다.
- **동작**: 에러 Traceback 로그를 파싱하여 결함 함수명(예: `calculate_yield_rate`)을 도출합니다.

### 3) 최근 Diff 연관 분석 훅 (`recent_diff_analyzer`)
- **목적**: 트리아지 훅에서 추출된 에러 함수명과 최근 24시간 동안 `ai/runs/` 디렉터리에 기입된 에이전트들의 `diff.patch` 변경 소스 파일들을 전수 비교합니다.
- **동작**: 에러 유발 시점에 가장 인접하여 수정이 일어난 변경 코드를 "장애 원인 유발 후보(Suspect Patch)"로 격리 지정해 줍니다.

### 4) 롤백 체크리스트 자동 생성기 (`rollback_generator`)
- **목적**: 분석 완료된 Suspect Patch를 복구하기 위한 단계별 복구 시나리오 마크다운 가이드([rollback_checklist.md])를 자동 조립하여 어드민 메일 및 `ai/runs/`에 축적합니다.
- **출력 템플릿**:
  ```markdown
  ###  Incident Rollback Checklist (Run ID: run_xxx)
  - [ ] 1. 대상 위험 변경점 확인: `modified/service/iqm_df.py`
  - [ ] 2. 롤백 실행 명령어: `git apply -R ai/runs/run_xxx/diff.patch`
  - [ ] 3. 복구 후 영향성: SQLite 임시 세션 락의 수동 정제가 요구됨.
  ```

---

## 4. 릴리즈 훅 자동화 시뮬레이션 인터페이스 (Python Interface)

아래는 운영 및 릴리즈 장애 상황 시 트리아지를 가동하기 위해 탑재되는 로직 제어 표준 구조입니다.

```python
import os
import glob
import subprocess

class ReleaseOpsHooks:
    """배포 후 정적 진단 및 런타임 에러 캡처 시 최근 패치 연관성을 추적하는 읽기 전용 운영 훅 클래스입니다."""

    def __init__(self, run_archive_dir: str = "ai/runs"):
        self.archive_dir = run_archive_dir

    def run_smoke_test(self, port: int = 8501) -> bool:
        """배포 후 Streamlit 로컬 웹포트 응답 200 OK 여부를 초고속 검증합니다."""
        import urllib.request
        try:
            # 헤드리스 HTTP 요청을 통한 로컬 런타임 생존 진단 (10초 타임아웃)
            response = urllib.request.urlopen(f"http://localhost:{port}", timeout=5.0)
            status = response.getcode()
            if status == 200:
                print("[OpsHook] [통과] 배포 후 스모크 테스트 통과: Streamlit 가동 중")
                return True
        except Exception as e:
            print(f"[OpsHook] [주의] 배포 후 스모크 테스트 실패! 포트 {port} 응답 에러: {str(e)}")
        return False

    def triage_incident(self, traceback_err: str) -> dict:
        """장애 Traceback 인입 시 최근 24시간 내 ai/runs/ 패치들 중 연관 변경 파일을 격리 매핑합니다."""
        analysis_report = {
            "status": "No suspicious diff found",
            "suspect_run_id": None,
            "suspect_file": None
        }

        # 1. 에러 로그 상에서 파일 단서 색출 (예: iqm_df.py)
        suspect_file_clue = ""
        for file_pattern in ["iqm_df.py", "cqms_df.py", "gmes_df.py", "sqlite_utils.py"]:
            if file_pattern in traceback_err:
                suspect_file_clue = file_pattern
                break

        if not suspect_file_clue:
            return analysis_report

        # 2. ai/runs/* 아래의 최근 diff.patch 전수 검색
        runs_list = sorted(glob.glob(f"{self.archive_dir}/run_*"), reverse=True)
        for run_path in runs_list:
            diff_patch_path = f"{run_path}/diff.patch"
            if os.path.exists(diff_patch_path):
                with open(diff_patch_path, "r", encoding="utf-8") as f:
                    patch_content = f.read()
                    if suspect_file_clue in patch_content:
                        run_id = os.path.basename(run_path)
                        analysis_report.update({
                            "status": "[주의] SUSPECT DIFF DETECTED!",
                            "suspect_run_id": run_id,
                            "suspect_file": suspect_file_clue
                        })
                        self._generate_rollback_checklist(run_id, suspect_file_clue, run_path)
                        break

        return analysis_report

    def _generate_rollback_checklist(self, run_id: str, suspect_file: str, run_path: str):
        """장애 유발 의심 패치가 발견될 시 읽기 전용 복구 체크리스트를 자동 조합하여 보관합니다."""
        checklist_content = f"""# [주의] Incident Rollback Checklist ({run_id})

본 보고서는 최근 런타임 에러 추적 결과와 에이전트 수정 내역 간의 연관 분석을 통과해 자동 조립된 복구 가이드라인입니다.

## 1. 장애 분석 결과 요약
- **의심 유발 변경점**: `{suspect_file}`
- **장애 연계 Run ID**: `{run_id}`
- **분석 상태**: 최근 수정 영역과 에러 발생 Traceback 영역 일치율 초고위험

## 2. 안전 롤백 실행 가이드 (수동 수행용)
> [!IMPORTANT]
> 인프라 안정성을 위해 자동 롤백은 차단되어 있습니다. 관리자가 수동 검토 후 아래 절차를 직접 처리하십시오.

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
        with open(f"{run_path}/rollback_checklist.md", "w", encoding="utf-8") as f:
            f.write(checklist_content)
        print(f"[OpsHook]  {run_id} 복구용 롤백 체크리스트(rollback_checklist.md)가 안전하게 자동 빌드 완료되었습니다.")
```
