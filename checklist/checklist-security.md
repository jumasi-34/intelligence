# checklist-security.md (릴리즈 및 에이전트 구동 보안 검토 체크리스트)

본 문서는 자율 품질 의사결정 시스템의 릴리즈 배포 및 AI 에이전트 구동 과정에서 컨텍스트, 시스템 데이터, 데이터베이스 자격 정보 등이 유출되는 것을 차단하고 안전 장치(Safety Guardrails)를 보장하기 위한 보안 지침서입니다.

---

## 1. 목적
- 소스 코드 및 인텔리전스 레이어의 민감 자산이 외부로 유출되거나 오염되는 것을 방지합니다.
- 데이터베이스 접근 시 최소 권한(Least Privilege) 원칙을 수립하고 준수하도록 강제합니다.
- 보안 위반 발생 시 즉각 추적할 수 있는 감사 추적(Audit Trail)을 유지합니다.

---

## 2. 조건
- 데이터베이스 및 외부 서비스와의 모든 커넥션은 환경 변수(`.env`) 및 Databricks DB 접속 표준 보안 키를 사용해야 합니다.
- 모든 스크립트 실행 및 스킬 구동은 명시적으로 부여된 로컬 환경 권한 하에 제한됩니다.

---

## 3. 제약
- **민감 정보 하드코딩 엄금 (No Hardcoding Secrets)**: API key, DB password, 비밀 토큰 등 일체의 인증 자산은 마크다운 문서 및 소스 코드에 평문(Plaintext)으로 작성할 수 없습니다.
- **AI Exclusion Zone 존중 (Uphold Exclusion Zone)**: 개인용 프라이빗 메모 공간인 `intelligence/note/` 및 그 하위 경로는 어떠한 경우에도 외부 AI에 노출되거나 참조 데이터로 활용되지 않아야 합니다. `.gitignore` 및 개별 이그노어 설정을 최신 상태로 유지하십시오.

---

## 4. 보안 검토 핵심 항목 (Security Checklist)

릴리즈 승인 및 빌드 단계에서 반드시 아래의 5대 핵심 보안 정합성 항목을 전수 확인해야 합니다.

### 항목 ①: 자격 정보 평문 보관 여부 검사
- [ ] `app/core/db/client.py` 및 관련 커넥터 설정 내에 물리 계정 정보가 하드코딩되지 않았는가?
- [ ] `intelligence/infra/` 의 시스템 명세서에 실서버의 IP나 패스워드가 하드코딩되지 않았는가?

### 항목 ②: AI 참조 차단 영역(note/) 관리 점검
- [ ] `.claudeignore`, `.copilotignore`, `.cursorignore` 파일에 `intelligence/note/` 하위 경로가 정상 등록되어 있는가?
- [ ] 실행 중인 에이전트가 `note/` 디렉터리에 대해 검색이나 파일 조회를 호출하지 않았는가?

### 항목 ③: 임시 작업 공간(runs/) 격리 상태 확인
- [ ] 에이전트가 세션 분석 계획 및 로컬 Diff 패치를 작성할 때 `guide/` 나 `infra/` 가 아닌 `runs/run_[session_id]/` 내에 안전하게 격리 저장하였는가?
- [ ] 작업 완료 후 찌꺼기 파일이 남아있지 않도록 정리를 끝마쳤는가?

### 항목 ④: Oracle 및 Databricks 최소 권한 계정 확인
- [ ] Streamlit UI 및 백엔드 쿼리에 바인딩된 계정이 DML(INSERT/UPDATE/DELETE)이나 DDL(DROP/ALTER) 권한이 제한된 조회 전용(READ-ONLY) 계정인가? (실제 DML 쓰기가 필요한 staging DB는 철저히 SQLite로 별도 격리하여 운영하고 있는지 확인)

### 항목 ⑤: 동적 컬럼 바인딩을 통한 SQL Injection 방지
- [ ] `QueryFilter` 및 `SQLConverter`를 활용하여 외부 유저 입력 매개변수가 원시 쿼리 문자열에 직접 하드코딩되어 결합(String Concatenation)되지 않고, 내부 파라미터 바인딩 및 타입 캐스팅을 정상적으로 거치도록 설계되었는가?
