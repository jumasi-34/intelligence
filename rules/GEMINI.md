# rules/ 규정

이 문서는 `intelligence/rules/` (표준 정책 및 행동 규칙 규정 레이어) 고유의 로컬 규칙과 파일 정보를 신속히 인지하기 위한 마이크로 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **절대 강제 규칙 (Absolute Rule enforcement)**: 본 폴더에 배치되는 `L1-*.md`, `L2-*.md`, `L3-*.md` 파일들은 에이전트와 소스 코드가 **예외 없이 100% 준수해야 하는 강제 규정(Must/Shall)**입니다. 어떠한 사적인 우회나 예외 적용도 허용하지 않습니다.
* **설명 및 코드 튜토리얼 배제 (No Tutorials)**: 문서 작성을 할 때는 장황한 설명, 환경설정 커맨드, 구체적인 파이썬 문법 등 교육 목적의 지침을 생략하고, 오로지 **"참/거짓", "수치적 제약", "허용/금지 조항"** 등 법률적 선언 형태로만 조항을 고도로 압축 기술하십시오. (설명과 구현 절차는 `guide/`로 이관)
* **가드레일 자동 검사 연동 (Automated Gate Link)**: 본 폴더에 등재되는 모든 표준 정책(Naming Convention, Git 규칙, 아키텍처 정합 수칙 등)은 신뢰성 확보를 위해 가능한 한 `guardrail/` 산하에 정적 분석 검사기 스크립트로 구현되어 배치 승인 파이프라인에 즉시 편입되어야 합니다.
* **WSL Markdown Link Constraint (WSL 환경 링크 제약)**: WSL(Windows Subsystem for Linux) 환경의 VS Code 터미널 및 채팅창, 마크다운 문서 내에서 절대 리눅스 경로(`file:///home/jumasi/...`)를 사용하면, 호스트 OS(Windows)가 해당 파일 링크를 로컬 윈도우 파일로 해석하여 `0x2` 에러가 발생합니다. 모든 마크다운 자산 내 하이퍼링크 및 AI 에이전트가 채팅창을 통해 제공하는 파일 링크는 반드시 워크스페이스 루트 기준의 평문 상대 경로(예: `[L2-architecture.md](intelligence/rules/L2-architecture.md)`) 또는 `./` 기반 상대 경로만을 사용해 에디터 내부에서 정상 열리도록 조치합니다.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `L1-git.md` | 커밋 메시지 머리말 태그 규정, 한국어 작성 표준 및 동시 푸시(Dual Push) 원칙 표준 |
| `L2-architecture.md` | UI - 비즈니스 서비스 - SQL 쿼리 간 결합도 제어 및 아키텍처 아웃라인 총괄 대원칙 |
| `L2-business-constants.md` | 물리 공장 코드(Plant Code), 핵심 비즈니스 상수 정적 매핑 및 이중화 방지 표준 |
| `L2-context-readability.md` | 문서 인덱스 자동화, 중복 명 접두사 배제 및 AI 컨텍스트 가독성 최적화 수칙 |
| `L2-naming-convention.md` | 물리 및 논리 계층의 파일명, 클래스명, 함수명 및 SQL 전처리 전반의 네이밍 표준 수칙 |
| `L2-sync-policy.md` | 로컬(WSL)과 원격(Ubuntu) 간의 자산 및 가동 데이터 Push/Pull 단방향 동기화 및 Rsync 제약 규정 |
| `L3-query.md` | SQL 디스플레이 한글 AS 하드코딩 전면 금지 및 영문 물리 컬럼명 유지 등 쿼리 레이어 개발 규칙 |
| `L3-service.md` | 데이터프레임 메서드 체이닝 표준 준수 및 비즈니스 전처리 전담 서비스 레이어 개발 규칙 |
| `L3-dashboard.md` | Streamlit 페이지 라우팅 제어, 이모지 전면 사용 금지 및 Google Material Symbols 채용 화면 UI 표준 규칙 |
| `L3-plot.md` | UI 레이어 1:1 시각화 격리 및 Plotly 차트 구현에 관한 렌더링 개발 규칙 |
| `table_naming_convention.json` | 데이터베이스 원천 테이블의 물리명과 한글 논리 도메인명의 공통 네이밍 정합용 사전 정의 파일 |

---

## 3. 변경 이력 (Changelog)

* **2026-06-14**:
  * [FIX] 마크다운 자산 내 절대 파일 경로(`file:///`)를 프로젝트 상대 경로로 일괄 변환(19개 파일)하고, 향후 재발 방지를 위해 WSL 하이퍼링크 제약 수칙을 로컬 규칙에 추가 영속화.
  * [REFACTOR] `rules/` 레이어 정의를 단순 가이드에서 예외 없는 '표준 정책 및 행동 규칙 규정 레이어'로 승격하고, 설명/튜토리얼 생략 및 법률적 압축 수칙을 명문화.
  * [Feat] 규정 폴더 전용 `GEMINI.md` 최초 비치.
