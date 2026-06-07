# context-governance.md (하네스 문서량 관리 원칙)

AI 하네스 문서는 역할을 분리해 컨텍스트 폭주를 막습니다.

| File Type | Responsibility | Size Guideline |
| :--- | :--- | :--- |
| `intelligence/context-common.md` | 모든 에이전트 공통 안전 원칙 | 짧게 유지, 정책 중심 |
| `intelligence/agent/AGENT_MANIFEST.md` | 에이전트 라우팅과 PR 게이트 | 라우팅 표와 정책만 유지 (SSOT 단일화) |
| `intelligence/context/*.summary.md` | 도메인 핵심 지식 | 1~2 화면 분량 |
| `intelligence/context/*.checklist.md` | 검증 항목 | 체크 가능한 항목 중심 |
| `intelligence/context/reverse_sync_prevention.md` | 누적 실패/재발방지 로그 | append-only 로그로 분리 |
| `intelligence/context/context-preprocessing-boundary.md` | 서비스 vs 시각화 전처리 경계 정의 가이드 | 아키텍처 및 샌드박스 경계 수칙 |
| `intelligence/evals/golden_tasks.yaml` | 벤치마크 태스크 | 측정 가능한 task/metric만 유지 |


문서가 커질 경우 원문 설명을 늘리기보다 summary와 checklist로 분리하고, 에이전트 실행 시에는 작업 도메인에 필요한 context pack만 로드합니다.

## Review Cadence

- `context-common.md`는 공통 정책만 남기고 세부 도메인 설명은 summary/checklist로 이동합니다.
- `AGENT_MANIFEST.md`는 라우팅, PR gate, merge policy만 담당합니다.
- `reverse_sync_prevention.md`는 누적 로그로 유지하고 에이전트 기본 컨텍스트에는 직접 포함하지 않습니다.

---

## 컨텍스트 문서 생성 위치 제약 및 명명 규제 (SSOT & Prefix 규칙)

* **[보관 위치 원칙]**: 모든 AI 하네스 문서 및 시스템/도메인 컨텍스트 문서는 **오직 `intelligence/` 폴더 및 그 하위인 `intelligence/context/` 디렉터리 내에만 보관**되어야 합니다.
* **[명명 prefix 규칙]**: 모든 공통/도메인 컨텍스트 문서는 컨텍스트 문서임을 한눈에 식별할 수 있도록 **파일명 시작 부분에 반드시 `context-` 접두사(prefix)를 부여**해야 합니다. (예: `context-common.md`, `context-queries.md`, `context-service.md`, `context-core.md`, `context-pages.md`)
* **[개별 생성 금지]**: 각 기능 레이어 디렉터리(`core/`, `pages/`, `service/`, `queries/` 등) 내부에 임의로 `CONTEXT.md` 파일을 생성하거나 방치하는 일체의 행위를 강력히 금지합니다.
* **[목적]**: 정보의 전역적이고 투명한 통합 관리 및 컨텍스트 폭주 방지, 그리고 소스 디렉터리의 본질적인 비즈니스 로직 보전을 위한 정책입니다. 만일 이외의 경로에서 발견 시 예외 없이 `intelligence/context/context-<도메인>.md` 명칭으로 이관 정리를 수행해야 합니다.


