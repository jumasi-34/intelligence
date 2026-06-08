# sysops-db-checklist.md (SQLite 세션 및 운영 로그 도메인 안전 체크리스트)

이 체크리스트는 SysOps 및 SQLite 로그 제어 모듈 관련 파일(`core/db/sqlite_utils.py`, `sqlite_management_page.py` 등)의 인프라 개선 및 쿼리 수정 시, 전수 정합성을 확보하기 위한 **보안성 체크리스트**입니다.

---

## 1. 동시성 제어 및 파일 Lock 회피 (Concurrency & WAL Mode)
- [ ] SQLite 파일 커넥터 인스턴스 취득 시, WAL(Write-Ahead Logging) 모드를 명시적으로 개방하여 동시 읽기/쓰기 성능 저하를 방지했는가?
- [ ] 데이터베이스 커넥션 타임아웃 옵션(예: `timeout=30.0`초 이상)이 안전하게 지정되어 일시적 경합 발생 시 즉시 뻗는 에러를 극복하고 있는가?
- [ ] 트랜잭션 수정을 사용하는 쿼리(`INSERT`, `UPDATE`, `DELETE`) 실행 후 `conn.commit()`이 실행 완료되었으며 `finally` 구문을 통한 커넥션 온전 반환 처리가 이루어졌는가?

---

## 2. 인증 및 어드민 패널 보안성 (Authentication & Access Control)
- [ ] SQLite 원시 테이블을 들여다볼 수 있는 `sqlite_management_page.py` 페이지 내부 진입 시점에 유저 세션 역할이 `Admin`인지의 물리적 차단문(`if role != 'Admin': return`)이 선제 작동하는가?
- [ ] 유저 암호화 검증 시 SHA-256 이상의 최신 단방향 솔팅(Salted) 해싱 해시 방식을 관철하여 평문 암호 유출 위험을 물리 차단하고 있는가?

---

## 3. 디스크 용량 관리 및 디버깅 (Disk Capacity & Diagnostics)
- [ ] 오디팅 로그가 무한히 증식하여 로컬 가상서버 디스크(SSD)를 가득 채우는 현상을 사전에 방지하도록 3개월 혹은 6개월 이상 된 초구버전 이력의 로그 회전(Log Rotation) 자동 정리 로직이 설계되었는가?
- [ ] 개발 도중 SQLite 접속 디버깅 코드를 주입한 흔적(`print()`, 로컬 절대 경로 하드코딩 등)이 온전히 정제되었는가?
