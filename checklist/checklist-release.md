# release-checklist.md (생산 배포 전 필수 체크리스트 원장)

이 문서는 프로덕션 환경으로 코드를 최종 배포하기 직전, `Release Guard Agent`와 인간 릴리즈 매니저가 서비스 무중단성과 안전성을 담보하기 위해 반드시 상호 서명(Sign-off) 및 대조해야 하는 **최종 배포 전 공통 체크리스트**입니다.

---

## 1. 배포 즉각 차단 관문 (Pre-Deployment Blockers)

아래 항목 중 **단 하나라도 미완료(`[ ]`) 상태가 존재할 경우**, 배포 승인은 절대적으로 불허되며 전체 CI/CD 파이프라인 기동은 즉각 동결됩니다.

- [ ] **환경변수 일관성 확보 (`.env.template`)**
  - 신규 소스 코드 상에 선언된 모든 `os.getenv` 인자들이 `.env.template` 및 원격 서버 환경 설정(Production Config)에 철저히 동기화되어 주입되었는가?
- [ ] **정적 무결성 전수 검증 통과 (`make verify`)**
  - 배포 대상 커밋에 대한 문법 및 구문 구조 전수 정적 테스트(`verify_code.py`)가 100% 그린 패스를 획득했는가?
- [ ] **SQLite 무중단 마이그레이션 계획 수립**
  - 로컬 데이터베이스(`ops.db`, `staging.db`)의 스키마 스펙 변경(ALTER/CREATE TABLE 등)이 수반되는 경우, 기존 데이터 유실 없이 순차 갱신을 실행할 안전한 SQL 스크립트가 마련되어 있으며, 백업 원본이 영속화되었는가? (마이그레이션 대상이 없을 시에는 체크 완료로 간주)
- [ ] **공개 API 하위 호환성 (No Breaking Changes)**
  - 비즈니스 레이어(`service/`) 함수 및 데이터클래스의 파라미터 구조가 하위 호환성을 완벽히 만족하여, 기존 Streamlit 뷰 렌더링에 파괴적 오류를 전파하지 않음을 크로스 오디팅 완료했는가?

---

## 2. 긴급 복구 및 롤백 수칙 (Emergency Back-out Protocol)

배포 직후 라이브 대시보드가 불능 상태가 되거나 치명적 데이터 가공 오류가 발견되었을 때 기동할 **무중단 긴급 복구 절차**입니다.

- [ ] **Git Revert 절차 명문화**
  - 배포가 실패한 경우, 즉각적인 `git revert -m 1 [커밋ID]` 또는 특정 안전 안정화 릴리즈 브랜치로의 롤백 명령어가 준비되어 있는가?
- [ ] **SQLite 마이그레이션 백아웃(Back-out) 스크립트 확보**
  - 데이터 스키마 갱신에 오류가 났을 때, 이전 릴리즈 상태의 정상적인 데이터 백업 원본으로 1분 내 복구할 수 있는 물리 복제 스크립트나 이전 복원 지점이 보증되었는가?
- [ ] **Feature Flag 비활성화 장치 체크**
  - 신기능 가동 실패 시, 환경변수나 SQLite 관리 테이블에서 간단한 스위치 오프(Disable) 조치만으로 예전 해피 패스(Normal Path)가 즉시 재가동될 수 있게 격리 장치가 구성되었는가?

---

## 3. 배포 후 10분 밀착 관제 지점 (Post-Deployment Audit Points)

배포 개시 이후 시스템의 비정상적 요동을 포착하기 위해 **최초 10분 동안 집중 모니터링해야 하는 정밀 관제 포인트**입니다.

- [ ] **실시간 가상환경 시스템 로그 감시**
  - `/home/jumasi/workstation/logs/app.log` 파일을 실시간 테일링하여, 배포 후 사용자 트래픽 인입에 따른 신규 임포트 에러나 DB 커넥션 예외(`SQLException`, `oracledb.DatabaseError`)가 쏟아지지 않는지 확인합니다.
  ```bash
  tail -f /home/jumasi/workstation/logs/app.log
  ```
- [ ] **핵심 대시보드 뷰포트 Latency 측정**
  - CQMS(`oe_quality_issue_dashboard_page.py`), GMES 등 주요 화면 진입 시, `@st.cache_data`가 올바르게 트리거링되어 화면 로딩 소요 시간이 예전 대비 요동치지 않고 평균 수치를 유지하는지 모니터링합니다.
- [ ] **SQLite 로그인/트래픽 로깅 정합성 검증**
  - 사용자 접근 시 로그인 로깅이 `log.db`에 유실 없이 타임스탬프와 함께 완벽히 적재되고 있는지 DML 이력을 체크합니다.

---

## 4. 보안 및 AI 가드레일 필수 체크리스트 (Security & AI Harnessing Guardrails)

AI-assisted 변경 또는 릴리즈 PR 프로세스 상에서 아래 보안 게이트와 격리 규정을 반드시 자율 대조하고 준수해야 합니다.

- [ ] **민감 정보 누출 방지**: `.env`, token, password, credential, secret key 등 모든 비밀값(Secrets)이 diff, 런타임 로그, 또는 run artifact 상에 포함되거나 노출되지 않았는가?
- [ ] **접속 정보 출력 금지**: DB connection string과 내부 운영 API 엔드포인트 정보가 디버그 출력이나 표준 출력(stdout)으로 노출되지 않는지 점검했는가?
- [ ] **DB 안전 트랜잭션 수호**: Databricks, Oracle, SQLite 운영 DB를 대상으로 원치 않는 데이터 변형이나 삭제(DML Write / destructive query)를 실행하지 않는 무해한 조회(Read-Only) 성격임을 보증했는가?
- [ ] **SQL 인젝션 방지**: 사용자로부터 전달된 모든 필터 인자 및 사용자 입력을 raw SQL 문자열에 직접 결합(concat)하지 않고, 반드시 데이터클래스 파라미터 및 `QueryFilter` 헬퍼를 경유하여 안전하게 바인딩하였는가?
- [ ] **민감 데이터 마스킹**: 개인정보, 시스템 로그, DB 세션 정보 등 보안 민감 데이터가 마스킹되거나 난독화 처리되었는가?
- [ ] **고위험군 변경 통제 (High-Risk Sandbox)**: `db_client.py`, `login_page.py`, `.env`, 인증/권한 관련 파일의 변경은 고위험(High risk) 작업으로 격리 분류하고 특별한 검토 과정을 거쳤는가?
- [ ] **수동 승인 이력 기재**: 고위험군 변경이 수반된 경우, 해당 변경 사항에 대해 반드시 `risk.md` 기록과 PR 본문에 최종 관리자의 명시적 수동 승인 서명을 획득했는가?
- [ ] **임시 아티팩트 격리**: AI-assisted PR 또는 작업 중 생성된 계획서 및 임시 보고서는 절대 가이드/인프라에 남기지 않고, `intelligence/runs/run_*` 폴더에 완벽히 격리한 후 최종적으로 소거하였는가?

---

## 5. 릴리즈 가드 에이전트 협업 수칙 (Ops Release Guard Collaboration)
- 본 릴리즈 체크리스트의 모든 관문과 검증 프로세스는 배포 시 [quality-evaluator.md](intelligence/agent/quality-evaluator.md) 에이전트가 가동되어 위배 사항을 상시 감시하고 제어해야 합니다. 릴리즈 가드는 체크리스트 전수 충족 여부를 확인한 후 최종 Sign-off 아티팩트를 발행합니다.
