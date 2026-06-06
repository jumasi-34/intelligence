# security-checklist.md (AI 하네스 보안 체크리스트)

AI-assisted 변경 또는 릴리즈 PR에서는 아래 항목을 확인합니다.

- [ ] `.env`, token, password, credential, secret key가 diff, 로그, run artifact에 포함되지 않았습니다.
- [ ] DB connection string과 운영 endpoint가 출력되지 않았습니다.
- [ ] Databricks/Oracle/SQLite 운영 DB를 대상으로 write 또는 destructive query를 실행하지 않았습니다.
- [ ] 사용자 입력을 raw SQL에 직접 concat하지 않았습니다.
- [ ] 개인정보, 사용자 로그, 세션 정보가 마스킹되었습니다.
- [ ] `db_client.py`, `login_page.py`, `.env`, 인증/권한 관련 변경은 High risk로 분류했습니다.
- [ ] High risk 변경은 `risk.md`와 PR 본문에 사람 승인 여부를 기록했습니다.
- [ ] AI-assisted PR은 실제 `ai/runs/run_*` 디렉터리와 7대 아티팩트를 포함합니다.
