# gmes-checklist.md (제조 공정 및 생산 품질 도메인 안전 체크리스트)

이 체크리스트는 GMES 제조 공정 도메인 관련 파일(`service/gmes_df.py`, `queries/gmes_query.py` 등)의 개발 및 패치 시, 변경 사항을 실 배포 브랜치에 머지하기 전에 전수 충족해야 하는 **오퍼레이션 진단 리스트**입니다.

---

## 1. 0 분모 및 수식 무결성 (Zero Division & Floating Point Guard)
- [ ] 생산 수량(`PROD_QTY` 또는 `TOTAL_QTY`)이 0일 때 발생할 수 있는 `ZeroDivisionError`를 방지하기 위해 `np.where` 또는 방어적 분기문이 탑재되었는가?
- [ ] 백분율 불량률 연산에서 분자 분모의 타입 변환 시 `errors="coerce"`가 지정되어 수치 유실 시 `0` 또는 `None`으로 부드럽게 무결성 처리되는가?
- [ ] 극소수점의 품질 편차나 규격 Cpk 분석 연산 수행 시 소수점 4째 자리 정밀도를 보존하도록 소수 연산이 보호되고 있는가?

---

## 2. 공장 파티션 격리 및 성능 (Partitioning & Query Optimization)
- [ ] 대용량 설비 테이블 스캔 시, 속도 지연을 차단하기 위해 `PLANT_CODE`와 발생 기간(`WORK_DT`) 조건이 쿼리의 WHERE 절에 선점 바인딩되었는가?
- [ ] 공장별 고유 캘린더나 교대조(Shift) 수식 가공 시 특정 공장의 규칙이 타 공장 데이터 가공 로직에 간섭(Side-Effect)을 유발할 여지가 차단되었는가?

---

## 3. 차트 렌더링 및 규격 선 표현 (Visual Specs & Controls)
- [ ] `pages/_60_workplace/` 차트 컴포넌트에 상한선(USL), 하한선(LSL) 및 이상치 감지 임계 영역(Outlier Threshold)이 시각적으로 명확하고 은은하게 표현되고 있는가?
- [ ] 차트가 빈 데이터프레임을 전달받았을 때, 공정 이상 경고 및 데이터 누락 안내 알림(`st.warning`)이 대시보드 구조를 깨뜨리지 않고 정갈하게 노출되는가?
- [ ] 수만 건의 공정 시계열 계측 좌표를 그릴 때 성능 지연을 경감시키기 위해 `plotly.graph_objects.Scattergl` (WebGL 기반) 등의 고속 렌더링을 적용했는가?

---

## 4. 테스트 하네스 검증 연계 (Test Harness Verification)
- 본 체크리스트에서 규정하는 0분모 방어, 공장 격리 바인딩 및 Outlier Threshold 시각화 조건은 테스트 하네스 검증 도구(예: `tests/test_layer_boundary.py` 등) 및 개별 인메모리 회귀/골든 테스트 코드를 구성하여 빌드 전 오류가 발생하지 않음을 자동으로 보증해야 합니다.
