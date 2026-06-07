# context-security-summary.md (AI 하네스 보안 요약)

이 문서는 AI 에이전트가 코드, 로그, PR, run archive를 생성할 때 반드시 지켜야 하는 보안 기준입니다.

## 절대 금지

- `.env`, 토큰, 비밀번호, DB 접속 문자열, 개인 인증 정보를 출력하거나 run artifact에 저장하지 않습니다.
- Databricks, Oracle, SQLite 운영 DB에 write, destructive query, 임의 마이그레이션을 실행하지 않습니다.
- 운영 데이터 샘플, 사용자 식별자, 세션 로그, 메일 주소를 마스킹 없이 PR 본문이나 로그에 남기지 않습니다.
- raw SQL string concatenation으로 사용자 입력을 직접 결합하지 않습니다.

## 필수 기준

- DB 조회는 가능한 `service/` 레이어와 기존 파라미터 dataclass를 경유합니다.
- 운영 DB 참조, 인증/권한, `.env`, `db_client.py`, `login_page.py` 변경은 High risk로 분류합니다.
- High risk 변경은 `risk.md`에 사유를 남기고 PR 본문에서 사람 승인을 받아야 합니다.
- AI-assisted PR은 `ai/runs/run_*` 아카이브와 `risk.md`의 Risk Level을 연결해야 합니다.

## 로그와 아티팩트

- `task.md`, `context-manifest.yaml`, `plan.md`, `diff.patch`, `test.log`, `review.md`, `risk.md`에는 재현에 필요한 정보만 남깁니다.
- 내부 추론 원문이나 민감 데이터 원문 대신, 실행 계획과 결정 근거를 요약합니다.
- 사고 대응용 traceback은 파일명과 함수명 중심으로 축약하고 credential-like 문자열은 제거합니다.
