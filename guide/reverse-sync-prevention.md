# 역동기화 재발방지 및 자체 피드백 로그 (Reverse Sync Prevention Logs)

이 파일은 에이전트 구동 과정에서 지속/누적되는 오류를 감지하여, 하네스 자체 역동기화 훅이 수립한 **근본 원인 분석(RCA)** 및 **재발방지 조치 사항**을 아카이빙하는 문서입니다. 향후 에이전트는 본 로그를 최우선 참고하여 실수를 자가 정제해야 합니다.

| 발생 일시 | RUN ID | 에이전트 | 도메인 | 에러 분류 | 근본 원인 (RCA) | 재발방지 조치 사항 |
|---|---|---|---|---|---|---|
| 2026-05-30 20:44:46 | `run_20260530_204446_555553` | MockPageBuilder | IQM | **Layer_Boundary_Violation** | 3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생. | 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것. |
| 2026-05-30 20:45:05 | `run_20260530_204505_b6eced` | MockPageBuilder | IQM | **Layer_Boundary_Violation** | 3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생. | 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것. |
| 2026-05-30 20:45:55 | `run_20260530_204554_65899f` | MockPageBuilder | IQM | **Layer_Boundary_Violation** | 3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생. | 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것. |
| 2026-05-30 20:50:55 | `run_20260530_205055_871c3e` | MockPageBuilder | IQM | **Layer_Boundary_Violation** | 3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생. | 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것. |
| 2026-05-30 20:51:33 | `run_20260530_205133_5042cf` | MockPageBuilder | IQM | **Layer_Boundary_Violation** | 3-Layer 설계 구조 규칙을 어기고 UI 레이어(pages/)에서 queries/를 직접 부르거나, queries/가 DB 실행을 위임받는 등 모듈간 경계 오염 발생. | 경계 정적 테스트 규칙에 준수하여 pages/는 service/만 부르고, queries/는 쿼리 조립만 수행하게 제한하며, service/는 DataFrame 데이터 반환 규칙을 준수할 것. |
