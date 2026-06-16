# GEMINI.md (scripts/ 로컬 가이드라인 및 인덱스)

이 문서는 `intelligence/scripts/` (인텔리전스 콘솔 빌드 및 웹서버 구동 레이어) 고유의 로컬 규칙과 파일 정보를 신속히 인지하기 위한 가이드라인입니다.

---

## 1. 로컬 핵심 제약 (Local Rules)

* **보안 차단 및 Exclusion Zone (Strict Safety)**: `build_dashboard.py` 컴파일러는 어떠한 경우에도 사적 메모 공간인 `intelligence/note/` 하위 폴더를 스캔하거나 읽어서는 안 되며, 정적 데이터 수집 시 완벽하게 제외해야 합니다.
* **CORS 및 캐시 차단 (No Cache Control)**: `server.py` 플라스크 백엔드는 브라우저 캐시로 인한 구버전 리소스 노출을 예방하기 위해 모든 HTTP 응답 헤더에 캐시 차단(`Cache-Control: no-cache, no-store, must-revalidate`) 설정을 상시 주입해야 합니다.
* **민감 정보 스캔 (Secret Scanner)**: 마크다운 파싱 시 정규식을 통한 API 키, 비밀번호 등의 민감 패턴을 모니터링하여 공공 대시보드 배포 시 유출되지 않도록 방어 기작을 설계해야 합니다.

---

## 2. 활성 파일 목록 인덱스 (Active Files)

| 파일명 | 파일의 본질적 역할 및 책임 (1줄 요약) |
| :--- | :--- |
| `build_dashboard.py` | 마크다운 문서 파싱, 에이전트 레지스트리 및 실행 이력 정적 컴파일링을 총괄하는 컴파일러 스크립트 |
| `server.py` | 로컬 static 서빙 및 실시간 리빌드 API(/api/build) 포트를 가동하는 Flask 웹 백엔드 서버 스크립트 |

---

## 3. 변경 이력 (Changelog)

* **2026-06-16 (Antigravity)**:
  * [FEAT] 로컬 Flask 백엔드 서버(`server.py`) 및 마크다운 파일 통합 파서(`build_dashboard.py`) 설계 및 탑재 완료.
