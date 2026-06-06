# AI Agent Orator: AGENT_MANIFEST.md

이 매니페스트는 프로젝트에 정의된 핵심 개발 에이전트들의 구동 트리거(Trigger), 역할(Role), 필수 참고 맥락(Required Context), 행위 한계(Allowed/Forbidden Actions), 그리고 검증 게이트(Verification)를 일원화하여 조망하고 라우팅하는 중앙 관리 매니페스트입니다.

---

## 1. 에이전트 라우팅 및 표준 매니페스트 (Central Routing Table)

현재 프로젝트는 복잡한 다중 에이전트 체계를 철폐하고, **역할의 명확한 분리와 아키텍처 결집**을 실현하기 위해 단 3개의 정예 전문 개발 에이전트로 단일화하여 운영됩니다.

| Trigger | Agent | Required Context | Allowed Actions | Forbidden Actions | Verification | Output |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **SQL 쿼리 설계 및<br>데이터 전처리 개발** | `dev-query-preprocessor` | `rule-architecture.md`<br>`context-common.md` | - `app/queries/` 내에 쿼리 함수 생성 및 수정<br>- `app/service/` 내에 데이터 전처리, 정제 및 `@st.cache_data` 부착 개발 | - `app/pages/` 내의 UI 파일이나 시각화(`_plots.py`) 직접 수정 금지<br>- 화면 컨트롤러 설계 개입 금지 | - `make verify` 구문/린트 검사<br>- Pandas 예외처리 및 방어 연산 검증 | `app/queries/*_query.py`<br>`app/service/*_df.py` |
| **Streamlit 화면 빌딩<br>및 Plotly 시각화** | `dev-page-plot-builder` | `rule-architecture.md`<br>`context-common.md` | - `app/pages/` 내에 Streamlit 레이아웃 구성 및 세션 상태 관리<br>- `app/pages/` 내에 프리미엄 Plotly Figure(`*_plots.py`) 설계 및 화면 배치<br>- `app/core/page/config_pages.py`에 네비게이션 매핑 및 자동 등록 | - `app/queries/` 및 `app/service/` 모듈 직접 수정 금지<br>- UI 레이어 내에서 직접 DB 쿼리 실행 또는 대규모 원천 가공 연산 수행 금지 | - 3-Layer 정합성 대조<br>- 차트 렌더링 검사<br>- 네비게이션 정상 등록 확인 | `app/pages/*_page.py`<br>`app/pages/*_plots.py`<br>`app/core/page/config_pages.py` |
| **신규 테이블 등록 시<br>사전 브리핑 및 EDA** | `dev-table-eda-analyst` | `rule-architecture.md`<br>`context-common.md` | - 본격 개발 착수 전, 사용자 및 개발 에이전트를 위한 충분하고 정교한 테이블 사전 브리핑 지원<br>- 데이터베이스의 Read-Only 메타데이터 및 통계 정보 수집<br>- `intelligence/context/` 내에 테이블의 비즈니스 현실 및 수치 특성을 융합한 EDA 가이드북 생성 및 영속 보존 | - **프로덕션 개발 코드(`.py`) 직접 작성 및 수정 금지** (No-Mutation Policy 준수)<br>- `INSERT`, `UPDATE`, `DELETE`, `DROP` 등 데이터 변조/변경 및 파괴적 쿼리 실행 금지<br>- 대용량 풀 스캔 쿼리 전송 금지 | - DDL/DML 쿼리 유무 검사 (Read-Only 여부)<br>- 보고서 산출물 내 결측치, 비즈니스 맥락 분석 유효성 대조 | `intelligence/context/context-eda-*.md`<br>`tests/eda_test_*.py` |

---

## 2. 예외 에스컬레이션 계약 (Escalation Protocol)

모든 에이전트는 다음 예외 조항 발생 시 즉시 자율 동작을 멈추고 사람(수동 관리자)에게 통제권을 인계해야 합니다.

1. **품질 검증 실패 (`make verify` 불합격)**: 자동 수정 중 타입 위반 또는 린트 오류 발견 시 즉시 작업을 중단하고 에러 로그를 보고합니다.
2. **보안 가이드라인 침해**: 코드 내 환경변수(DB 접속 정보, 비밀 토큰 등)가 하드코딩되거나 로그에 노출될 위험 감지 시 가차없이 실행을 중단합니다.
3. **리스크 위험도 최고 등급 (`Risk Level: High`)**: DB 마이그레이션이 수반되거나 권한 체계가 변동되는 패치는 절대 수동 검토 전 자동 승인 처리를 금지합니다.

---

## 3. PR 게이트 연결 규칙 (PR Gate Contract)

모든 AI 생성 및 조립 코드는 검증을 통과해야 하며, 다음의 병합 정책을 고정하여 준수합니다.

- **Low Risk**: 자동 검증 및 필수 유닛 테스트가 통과하면 승인 후 merge 가능.
- **Medium/High Risk**: 자동 검증 결과와 더불어 반드시 사람(Human Contributor)의 수동 소스 리뷰 및 롤백 플랜 확인 완료 후 병합 가능.
