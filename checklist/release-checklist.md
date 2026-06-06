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

## 4. 릴리즈 가드 에이전트 협업 수칙 (Ops Release Guard Collaboration)
- 본 릴리즈 체크리스트의 모든 관문과 검증 프로세스는 배포 시 [ops-release-guard.md](file:///home/jumasi/workstation/ai/agent/ops-release-guard.md) 에이전트가 가동되어 위배 사항을 상시 감시하고 제어해야 합니다. 릴리즈 가드는 체크리스트 전수 충족 여부를 확인한 후 최종 Sign-off 아티팩트를 발행합니다.
