# context-cqms-checklist.md (고객 품질 및 필드 클레임 도메인 안전 체크리스트)

이 체크리스트는 CQMS 도메인 관련 파일(`service/cqms_df.py`, `queries/cqms_query.py` 등)의 기능 개선 및 버그 수정 작업이 수행될 때, 머지 및 배포 전 반드시 충족해야 하는 **안전성 자가진단표**입니다.

---

## 1. 데이터 파싱 및 시간 정합성 (Date & Value Consistency)
- [ ] 수집된 원시 데이터의 접수 날짜(`RECEIPT_DT`) 컬럼이 `pd.to_datetime`을 통해 일관된 Datetime 포맷으로 강제 변환되었는가?
- [ ] 주차별(Weekly) 집계 시, 데이터가 존재하지 않는 빈 주차(Week Gap) 영역에 임의의 공백이 생기지 않도록 빈 주차 데이터 보완(축 채우기) 연산이 정상 탑재되었는가?
- [ ] 필터 파라미터가 비어 있거나 `None`일 때, 디폴트 날짜 범위(예: 최근 30일)를 할당하는 방어 코드가 작동하는가?

---

## 2. 개인정보 및 민감 데이터 유출 가드 (Security & Privacy Guard)
- [ ] 대시보드 및 상세 테이블 출력에 포함되는 고객 담당자명, 고객 이메일, 혹은 기술 협력처의 연락처 등 민감한 식별 정보가 마스킹(`***`) 처리되어 은폐되었는가?
- [ ] SQL 쿼리 조립 단에서 고객 명칭이나 불만 유형 텍스트의 동적 결합 시 SQL Injection 취약점이 존재하지 않는 형태로 `QueryFilter`가 적용되었는가?

---

## 3. 통계 지표 및 차트 일관성 (Statistical Visualization Guard)
- [ ] 필드 클레임 분석 차트(`weekly_cqms_monitor_plots.py`) 내에 통계적 이상치를 파악할 수 있도록 평균선(Mean Line)과 상/하한 관리선(UCL/LCL)이 얇은 점선으로 렌더링되고 있는가?
- [ ] 사용자가 임의로 지정한 기간의 상한값과 하한값에 대한 축(Axis) 범위가 데이터에 맞추어 자동 보정(Auto-scaling)되고 있는가?
- [ ] 전월 및 당월 누적 불량 트렌드 라인이 꼬이지 않고 시간 시퀀스에 따라 온전히 오름차순 정렬되어 노출되는가?

---

## 4. 테스트 하네스 검증 연계 (Test Harness Verification)
- 본 체크리스트에서 규정하는 데이터 변환, 마스킹 보안 및 UCL/LCL 통계 한계선 정합성 조건은 [qa-test-writer.md](file:///home/jumasi/workstation/intelligence/agent/qa-test-writer.md) 에이전트가 `tests/test_cqms_regression.py` 등의 완전한 인메모리 회귀/골든 테스트 코드를 생성하여 자동으로 보증해야 합니다.
