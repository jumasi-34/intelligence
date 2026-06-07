# context-manual-setup.md (서비스 환경 수동 설정 및 배포 가이드라인)

본 문서는 `goeq_bi` 프로젝트의 개발 완료 후 **실서비스 환경(Ubuntu Production Server)**으로 이전 및 배포 시, AI(바이브코딩 등)가 직접 제어할 수 없는 시스템 설정 항목들을 사용자가 체계적이고 안전하게 **수동(Manual)으로 관리할 수 있도록 업무 목록을 정의하고 기록하는 전용 가이드라인**입니다.

> [!IMPORTANT]
> - **AI 환경 분리 안전장치**: AI 에이전트는 실서비스(Production) 환경의 핵심 자산(`.env`, `crontab`, `systemctl` 등)을 직접 수정하지 못합니다.
> - **수동 작업 및 기록 주의**: 본 가이드에 정의된 쉘 명령어를 활용하여 사용자가 직접 설정을 확인하고, 최종 세팅 내용을 본 문서 하단의 **[스냅샷 기록 관리 양식]**에 업데이트하여 동기화해야 합니다.

---

## 1. 수동 관리 대상 업무 목록 (업무 정의 및 체크리스트)

실서비스 가동 시 누락되기 쉬운 수동 핵심 설정 업무를 정의합니다. 개발 환경 변경 후 배포 시 아래 체크리스트를 점검하십시오.

### 📋 수동 배포/설정 체크리스트
- [ ] **1. `.env` 환경 변수 동기화 및 보안 점검**
  - 개발 환경의 `.env`와 서비스 환경의 `.env` 간 키/값 일치 여부 확인. (Snowflake, Oracle, Databricks, Streamlit Theme 등 총 39개 환경 변수 수동 확인)
- [ ] **2. `Crontab` 배치 자동화 등록 및 로그 점검**
  - SELLIN 집계(`agg_sellin.py`) 및 IQM PLUS 집계(`agg_iqm_plus.py`) 크론잡의 정상 작동 및 로그 적재 여부 확인.
  - ⚠️ **주의**: 실서비스 서버의 배치 스크립트 경로는 `/home/jumasi/workstation/_08_automation/`입니다. (개발 환경의 `automation/`과 폴더명 정합성 확인 필수)
- [ ] **3. `Streamlit` 서비스 프로세스 관리 및 포트 이중화**
  - 포트 8501(메인 서비스, `streamlit.service`) 및 포트 8502(예비/검증용 서비스, `streamlit2.service`) 백그라운드 구동 확인 및 systemd 서비스 기동 상태 점검.
- [ ] **4. Oracle Instant Client 시스템 라이브러리 및 쉘 바인딩**
  - `LD_LIBRARY_PATH` 경로 설정 및 DB 접근 활성화 상태 점검.

---

## 2. 수동 업무별 상세 설정 방법 및 명령어

### ① `.env` 파일 구성 및 관리
실서비스 환경에 배포된 애플리케이션의 엔트리포인트 디렉터리 `/home/jumasi/workstation/.env`에 총 39종의 환경 변수가 누락 없이 정상 구성되어 있는지 점검합니다.

- **설정 위치**: `/home/jumasi/workstation/.env`
- **보안 가이드**: `.env` 파일은 절대 Git 저장소에 노출되지 않도록 수동으로만 편집 및 보존되어야 합니다.
- **주요 환경 변수 분류**:
  ```ini
  # Snowflake 데이터웨어하우스 연동
  SNOWFLAKE_USER=...
  SNOWFLAKE_PASSWORD=...
  SNOWFLAKE_ACCOUNT=...
  ...

  # Oracle BI & MES 커넥션
  ORACLE_BI_USER=...
  ORACLE_BI_PASSWORD=...
  ORACLE_BI_HOST=...
  ...

  # Databricks OAuth Principal 커넥션
  DATABRICKS_SERVER_HOSTNAME=...
  DATABRICKS_HTTP_PATH=...
  DATABRICKS_OAUTH_CLIENT_ID=...
  ...

  # Streamlit UI 및 서버 테마 설정
  STREAMLIT_THEME_BASE=...
  STREAMLIT_THEME_PRIMARY_COLOR=...
  STREAMLIT_SERVER_PORT=8501
  ```

---

### ② `Crontab` 배치 작업 등록
자동 집계 스크립트 실행을 위해 서비스 환경의 시스템 크론(Cron) 서비스에 직접 스케줄을 추가해야 합니다.

- **설정 편집 명령어**:
  ```bash
  crontab -e
  ```
- **실서비스 환경 crontab 등록 내용**:
  ```bash
  # [메일 알림] 작업 결과나 에러 발생 시 수신할 이메일
  MAILTO="Jungman.Sim@hankookn.com"

  # 1. HOPE SELLIN 데이터 집계 자동화 (매일 KST 12:30 / UTC 03:30 실행)
  30 03 * * * /home/jumasi/miniconda3/bin/conda run -n goeq python /home/jumasi/workstation/_08_automation/agg_sellin.py >> /home/jumasi/workstation/logs/agg_sellin.log 2>&1

  # 2. IQM PLUS 데이터 집계 자동화 (매일 KST 12:40 / UTC 03:40 실행)
  40 03 * * * /home/jumasi/miniconda3/bin/conda run -n goeq python /home/jumasi/workstation/_08_automation/agg_iqm_plus.py >> /home/jumasi/workstation/logs/agg_iqm_plus.log 2>&1
  ```
- **배치 실행 결과 실시간 모니터링**:
  ```bash
  tail -f /home/jumasi/workstation/logs/agg_sellin.log
  tail -f /home/jumasi/workstation/logs/agg_iqm_plus.log
  ```

---

### ③ `Streamlit` 서비스 프로세스 관리 (Systemd)
Streamlit 애플리케이션이 터미널 세션이 종료된 후에도 가동을 계속하고, OS 재부팅 시 자동으로 복구될 수 있도록 Linux `systemd` 서비스로 관리됩니다.

- **메인 서비스 (Port 8501)**: `/etc/systemd/system/streamlit.service`
- **예비/검증용 서비스 (Port 8502)**: `/etc/systemd/system/streamlit2.service`

#### 🛠️ 주요 Systemd 제어 명령어 (수동 실행용)
```bash
# 메인 서비스 상태 확인
sudo systemctl status streamlit.service

# 예비 서비스 상태 확인
sudo systemctl status streamlit2.service

# 서비스 재시작 (코드 배포 후 반영 시 실행)
sudo systemctl restart streamlit.service
sudo systemctl restart streamlit2.service
```

---

### ④ Oracle Instant Client 환경 변수 영구 반영
애플리케이션 및 크론탭 내부에서 Oracle Client가 정상 구동될 수 있도록 환경 변수가 사용자 프로필에 등록되어 있는지 점검합니다.

- **사용자 배시 환경 설정 파일**: `~/.bashrc`
- **설정 내용**:
  ```bash
  export LD_LIBRARY_PATH=/opt/oracle/instantclient_23_8:$LD_LIBRARY_PATH
  ```

---

## 3. 실서비스 환경(Ubuntu) 설정 정보 가져오기 및 등록 가이드

실제 운영 환경의 세팅 상태를 체계적으로 기록하고 관리하기 위해, 사용자가 **직접 서비스 서버에 접속하여 아래의 명령어를 실행**하고, 그 출력 결과를 이 문서 하단의 스냅샷 섹션에 기록해 주셔야 합니다.

> [!TIP]
> **실서비스 터미널(Ubuntu)에 로그인 후, 아래 명령어 묶음을 한 번에 실행하여 결과를 복사하십시오.**

### 🔍 실서비스 설정 조회 명령어 묶음
```bash
echo "=== [1] 현재 가동 중인 Streamlit 프로세스 현황 ==="
ps aux | grep streamlit | grep -v grep

echo "=== [2] 현재 등록된 Crontab 설정 ==="
crontab -l

echo "=== [3] .env 템플릿 정보 (비밀번호 제외한 키 목록만 추출) ==="
grep -E '^[A-Za-z0-9_]+=' /home/jumasi/workstation/.env | sed 's/=.*$/=******/'

echo "=== [4] systemd 내 Streamlit 서비스 등록 유무 ==="
ls -la /etc/systemd/system/ | grep streamlit

echo "=== [5] Oracle 환경 변수 설정 현황 ==="
echo "LD_LIBRARY_PATH: $LD_LIBRARY_PATH"
echo "TNS_ADMIN: $TNS_ADMIN"
```

---

## 4. [기록 공간] 실서비스 환경 설정 스냅샷 (Production Snapshot)

본 영역은 사용자가 직접 수집해 온 실제 서비스 환경의 세팅 정보를 안전하게 보관 및 기록한 스냅샷입니다. 설정 변경 시 이 영역을 지속적으로 갱신해 주십시오.

### 📸 현재 설정 스냅샷 (최종 업데이트: 2026-06-06)

#### 1) 실서비스 환경의 `.env` 구성 상태 (보안을 위한 Key 패턴 복사)
```ini
SNOWFLAKE_USER=******
SNOWFLAKE_PASSWORD=******
SNOWFLAKE_ACCOUNT=******
SNOWFLAKE_WAREHOUSE=******
SNOWFLAKE_DATABASE=******
SNOWFLAKE_SCHEMA=******
ORACLE_BI_USER=******
ORACLE_BI_PASSWORD=******
ORACLE_BI_HOST=******
ORACLE_BI_PORT=******
ORACLE_BI_SERVICE_NAME=******
ORACLE_MES_USER=******
ORACLE_MES_PASSWORD=******
ORACLE_MES_HOST=******
ORACLE_MES_PORT=******
ORACLE_MES_SERVICE_NAME=******
DATABRICKS_SERVER_HOSTNAME=******
DATABRICKS_HTTP_PATH=******
DATABRICKS_OAUTH_CLIENT_ID=******
DATABRICKS_OAUTH_CLIENT_SECRET=******
DATABRICKS_PAT_TOKEN=******
STREAMLIT_THEME_BASE=******
STREAMLIT_THEME_PRIMARY_COLOR=******
STREAMLIT_THEME_BACKGROUND_COLOR=******
STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR=******
STREAMLIT_THEME_TEXT_COLOR=******
STREAMLIT_UI_LAYOUT=******
STREAMLIT_SERVER_PORT=******
STREAMLIT_SERVER_FILE_WATCHER_TYPE=******
STREAMLIT_SERVER_HEADLESS=******
STREAMLIT_SERVER_ENABLE_CORS=******
STREAMLIT_BROWSER_GATHER_USAGE_STATS=******
STREAMLIT_BROWSER_SERVER_ADDRESS=******
STREAMLIT_LOGGER_LEVEL=******
STREAMLIT_GLOBAL_DEVELOPMENT_MODE=******
STREAMLIT_CACHE_TTL=******
STREAMLIT_MAX_UPLOAD_SIZE=******
STREAMLIT_SERVER_ENABLE_STATIC_SERVING=******
STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=******
```

#### 2) 서비스 환경 실시간 `Crontab` 등록 상태
```bash
# [메일 알림] 작업 결과나 에러 발생 시 수신할 이메일
MAILTO="Jungman.Sim@hankookn.com"

# =================================================================
# 1. HOPE SELLIN 데이터 집계 자동화
# -----------------------------------------------------------------
# 실행 시간: 매일 12:30 (KST) / 03:30 (UTC)
# 주요 기능: SELLIN 관련 데이터 추출 및 집계
# =================================================================
30 03 * * * /home/jumasi/miniconda3/bin/conda run -n goeq python /home/jumasi/workstation/_08_automation/agg_sellin.py >> /home/jumasi/workstation/logs/agg_sellin.log 2>&1

# =================================================================
# 2. IQM PLUS 데이터 집계 자동화
# -----------------------------------------------------------------
# 실행 시간: 매일 12:40 (KST) / 03:40 (UTC)
# 주요 기능: IQM PLUS 대시보드용 데이터 업데이트
# =================================================================
40 03 * * * /home/jumasi/miniconda3/bin/conda run -n goeq python /home/jumasi/workstation/_08_automation/agg_iqm_plus.py >> /home/jumasi/workstation/logs/agg_iqm_plus.log 2>&1
```

#### 3) 가동 프로세스 및 `systemd` 서비스 관리 상태
```bash
# [Streamlit 백그라운드 프로세스]
jumasi    499147  0.0  4.1 3749936 661552 ?      Ssl  May19   2:37 /home/jumasi/miniconda3/envs/goeq/bin/python -m streamlit run app.py --server.port=8502 --server.address=0.0.0.0
jumasi    645694  0.3  2.0 5249340 336280 ?      Ssl  12:41   0:05 /home/jumasi/miniconda3/envs/goeq/bin/python -m streamlit run app.py --server.port=8501 --server.address=0.0.0.0

# [Systemd 서비스 파일 목록]
-rw-r--r--  1 root root  505 May 19 22:36 streamlit2.service  # Port 8502 매핑 서비스
-rw-r--r--  1 root root  440 Aug 19  2025 streamlit.service   # Port 8501 매핑 서비스
-rw-r--r--  1 root root  440 May 20 07:15 streamlit.service.save
```

#### 4) Oracle 인스턴트 클라이언트 환경 설정
```ini
LD_LIBRARY_PATH=/opt/oracle/instantclient_23_8:/opt/oracle/instantclient_23_8:/opt/instantclient_23_8
TNS_ADMIN=
```

---

## 5. AI 에이전트 서비스 배포/설정 대응 수칙
- **원격 직접 실행 금지**: AI 에이전트는 서비스 환경의 배포 및 시스템 구성에 연관된 동작을 직접 시도하지 않습니다.
- **가이드 우선 규칙**: 배포나 설정 변경에 관련된 요청을 받았을 때, AI는 본 `context-manual-setup.md` 문서를 인용하며 사용자에게 "직접 설정 및 3번 명령어 실행을 통한 스냅샷 기록"을 요구하고 가이드만 작성해야 합니다.
