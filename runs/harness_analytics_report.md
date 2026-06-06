# Test Harness & Agent Runs Analytics Report

이 보고서는 프로젝트의 AI 에이전트 실행 품질 지표를 분석하고 수집된 7대 아티팩트의 무결성을 정량적으로 추적하는 관찰성 분석 리포트입니다.

- **리포트 분석 시간**: 2026-05-30 20:24:43
- **분석 대상 디렉터리**: `/home/jumasi/workstation/tests/temp_agent_runs`

---

## 1. 종합 핵심 성과 지표 (KPI)

| 지표 | 측정값 | 설명 |
| :--- | :--- | :--- |
| **총 에이전트 수행 횟수 (Total Runs)** | `1 회` | 수집된 총 고유 실행 세션 수 |
| **아티팩트 준수율 (Completeness)** | `100.0%` | 7대 핵심 아티팩트가 모두 보관되었는지 검증 비율 |
| **품질 관문 통과율 (Test Pass Rate)** | `100.0%` | 정적 구문 및 테스트 검증 통과 비율 |

---

## 2. 배포 리스크 수준 분포 (Risk Distribution)

에이전트 변경 사항에 대해 배포 가드가 할당한 위험도 통계입니다.

- **Low Risk**: `0` 건
- **Medium Risk**: `0` 건
- **High Risk**: `0` 건
- **Unknown**: `1` 건

---

## 3. 에이전트별 구문 검증 합격률 (Agent Performance)

| 에이전트 이름 | 실행 횟수 | 합격 횟수 | 합격률 |
| :--- | :---: | :---: | :---: |
| `MockPageBuilder` | 1 | 1 | `100.0%` |

---

## 4. 개별 에이전트 실행 타임라인 이력

최근 실행된 세션들의 아티팩트 수집 상세 상태 정보입니다.

| 실행 ID | 에이전트 | 도메인 | 테스트 통과 | 리스크 | 수집된 아티팩트 목록 |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `run_20260530_202442_dbd727` | `MockPageBuilder` | `iqm` | [통과] PASS | `Unknown` | Task, Manifest, Plan, Diff, TestLog, Review, Risk |
