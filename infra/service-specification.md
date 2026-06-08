# \[SERVICE\] service/ — 서비스 레이어 컨텍스트

> **LAYER:** `service/` · 서비스 레이어 — 원시 데이터 → 집계·변환 → DataFrame 생산.

---

## 역할

원시 데이터를 집계·변환해 UI가 바로 사용할 수 있는 DataFrame을 생산하는 중간 레이어.
`queries/`에서 SQL 문자열을 받아 DB를 실행하고, 결과를 가공·조합해 반환한다.
비즈니스 로직(필터링, 집계, 파생 컬럼 계산)은 이 레이어에 집중한다.

## 구조

`service/` 는 단일 레벨 플랫 구조다. 모든 모듈이 `service/` 직하에 위치한다.

```
service/
├── gmes_df.py    # GMES: NCF, Production, RR, UF, Weight, Spec Master
├── cqms_df.py    # CQMS: Quality Issue, 4M Change, Customer Audit
├── hope_df.py    # HOPE: OE App, Sell-in
├── hgws_df.py    # HGWS: 반품
├── ctms_df.py    # CTMS: CTL 데이터
├── qrs_df.py     # QRS: Worksheet
└── iqm_df.py     # IQM Plus: 집계·통합 지표 (WORKFLOW 포함)
```

## 네이밍 컨벤션

### 모듈

```
{system}_df.py
```

### 함수

```
preprocessing_{domain}_{purpose}_{unit}_{agg_or_condition}(params) -> pd.DataFrame
```

| 세그먼트 | 예시 |
|----------|------|
| `{domain}` | `ncf`, `production`, `rr`, `uf`, `qi`, `oeapp`, `4m`, `audit` |
| `{purpose}` | `rawdata`, `monthly_agg`, `plant_agg`, `dft_cd_agg`, `period_ppm_agg` |
| `{unit}` | 생략 가능 (단일 집계) |
| `{agg_or_condition}` | `only_fm`, `ongoing` 등 부가 조건 |

예:
- `preprocessing_ncf_rawdata(params)` — NCF 원시 데이터
- `preprocessing_ncf_monthly_agg(params)` — NCF 월별 집계 (새 스키마)
- `preprocessing_ncf_period_ppm_agg(params)` — NCF+Production 결합 PPM (옛 스키마)
- `preprocessing_qi_general_rawdata(params)` — 품질 이슈 원시 데이터

## 핵심 패턴

### 1) 파라미터 dataclass 수신

모든 서비스 함수는 파라미터를 개별 변수가 아닌 `core/params/parameters.py`에 정의된 dataclass 형태로 통일하여 전달받습니다. 이는 필터 확장성과 설계 일원화를 위해 강제되는 규칙입니다.

```python
from core.params.parameters import NonconformityParams
from service import gmes_df

df = gmes_df.preprocessing_ncf_rawdata(
    params=NonconformityParams(
        start_date="20250101",
        end_date="20251231",
        disposition_type="scrap",
    )
)
```

### 2) Pandas 전처리 메서드 체이닝 표준 (Method Chaining)

사이드 이펙트(부작용)를 최소화하고 선언적인 흐름을 유지하기 위해 데이터프레임 가공 시 기본적으로 메서드 체이닝을 사용합니다.

1. **가변(Mutation) 연산 지양**: `df['new_col'] = ...`와 같은 직접적인 inplace 값 할당 대신, `.assign()`을 사용하여 독립적인 새 복사본을 생성해 반환하도록 체이닝합니다. 이를 통해 Pandas의 고질적인 `SettingWithCopyWarning`을 예방합니다.
2. **Lambda 바인딩 활용**: 체인 중간 상태의 데이터프레임을 지칭할 때는 `lambda df: ...` (또는 `lambda d: ...`)를 사용해 체인을 끊지 않고 연속적인 가공을 수행합니다.
3. **체인 길이 제한 및 체크포인트 설정**: 연산의 흐름이 지나치게 길어지거나(대략 7~8단계 초과), 복잡한 분기 비즈니스 로직이 동반될 경우 체인을 강제로 연결하기보다 의미 있는 단위에서 체크포인트(임시 변수 선언, 예: `df_base`, `df_agg`)를 두어 분리합니다.
4. **로깅 파이프 사용**: 체인 진행 중에 데이터프레임의 로우(row) 크기나 중간 결과를 로깅하고 싶다면, 파이썬 데코레이터나 단순 로깅용 `.pipe(log_function)` 구조를 설계해 사용합니다.

```python
# 올바른 예시 (선언적 메서드 체이닝)
return (
    df_raw.pipe(lambda df: df.rename(columns=str.upper))
    .pipe(dataframe_helper.add_url_column, "SEQ", dataframe_config.URL_QUALITY_ISSUE)
    .assign(
        YYYY=lambda df: df["REG_DATE"].dt.year,
        STATUS=lambda df: df["STATUS"].fillna("UNKNOWN")
    )
)
```

### 3) view_mode 제거 원칙

서비스 함수 내부에 view_mode 분기 로직을 두지 않습니다.
각 함수는 하나의 집계 형태만 담당합니다.
동적 view_mode 분기가 필요한 경우 **pages/** 레이어에서 if/elif 로 처리합니다.

```python
# pages/ 레이어에서 분기
vm = params.step1_basic_view_by
if vm == "weekly":
    df = gmes_df.preprocessing_ncf_weekly_agg(ncf_p)
elif vm == "monthly":
    df = gmes_df.preprocessing_ncf_monthly_agg(ncf_p)
```

### 4) DB 클라이언트 호출

```python
from core.operate.db_client import get_client

df = get_client("databricks").execute(query)
df = get_client("oracle_bi").execute(query)
df = get_client("sqlite", sqlite_db_path="staging").execute(query)
```

### 5) 캐싱 규격 통일

Databricks 쿼리를 직접 감싸는 서비스 함수에는 `@st.cache_data(ttl=3600)`(1시간) 적용을 기본 규칙으로 일원화합니다.
인수로 받은 dataclass는 `frozen=True`여야 캐시 키로 사용 가능합니다.

---

## 스키마 구분

### NCF 새 스키마 (`PLT_CD, PRD_CD, SPEC_CD, DFT_CD, DFT_QTY, INS_DATE, CAT`)
- `preprocessing_ncf_rawdata`
- `preprocessing_ncf_dft_cd_agg`
- `preprocessing_ncf_daily_agg`, `weekly_agg`, `monthly_agg`, `yearly_agg`

### NCF 옛 스키마 (`PLANT, PERIOD_ID, NCF_QTY, PRDT_QTY, PPM`)
- `preprocessing_ncf_plant_agg` — 공장별
- `preprocessing_ncf_mcode_agg` — 규격별
- `preprocessing_ncf_period_ppm_agg` — 기간별 (monthly/yearly)
- `preprocessing_ncf_dft_cd_count_agg` — 불량코드별 (DFT_CD, DFT_DESC, NCF_QTY)

### Production 새 스키마 (`PLT_CD, PRD_CD, SPEC_CD, DATE, PRDT_QTY`)
- `preprocessing_production_spec_daily_agg`, `weekly_agg`, `monthly_agg`

### Production 옛 스키마 (`PLANT, PERIOD_ID, PRDT_QTY`)
- `preprocessing_production_plant_agg`, `mcode_agg`, `period_agg`

---

## 주요 함수 목록

| 함수 | 파일 | 설명 |
|------|------|------|
| `preprocessing_spec_master(params)` | `gmes_df.py` | 규격 마스터 |
| `preprocessing_ncf_rawdata(params)` | `gmes_df.py` | NCF 원시 데이터 (새 스키마) |
| `preprocessing_ncf_period_ppm_agg(params)` | `gmes_df.py` | 기간별 PPM (옛 스키마) |
| `preprocessing_ncf_plant_agg(params)` | `gmes_df.py` | 공장별 PPM (옛 스키마) |
| `preprocessing_production_weekly_agg(params)` | `gmes_df.py` | 주별 생산 (새 스키마) |
| `preprocessing_rr_rawdata(params)` | `gmes_df.py` | RR 원시 데이터 |
| `preprocessing_uf_weekly_agg(params)` | `gmes_df.py` | UF 주별 집계 |
| `preprocessing_weight_weekly_agg(params)` | `gmes_df.py` | 중량 주별 집계 |
| `preprocessing_qi_general_rawdata(params)` | `cqms_df.py` | 품질 이슈 원시 데이터 |
| `preprocessing_4m_rawdata(params)` | `cqms_df.py` | 4M 변경 원시 데이터 |
| `preprocessing_audit_rawdata(params)` | `cqms_df.py` | 고객 감사 원시 데이터 |
| `preprocessing_oeapp_general_rawdata(params)` | `hope_df.py` | OE App 일반 원시 데이터 (캐싱 탑재 표준) |
| `preprocessing_ctms_general_rawdata(params)` | `ctms_df.py` | CTMS 원시 데이터 |
| `preprocessing_cum_df(year)` | `iqm_df.py` | IQM Plus 누적 집계 |
| `run_iqm_aggregation()` | `iqm_df.py` | IQM Plus 전체 집계 실행 |

*주의: QRS 서비스(`qrs_df.py`)의 기존 비표준 낱개 파라미터 전처리 함수들은 추후 점진적으로 데이터클래스 파라미터 표준 수신 형태로 마이그레이션이 요구됩니다.*

---

## 주의 사항 및 강제 금지 규정 (Anti-Patterns)

1. **엄격한 3-레이어 아키텍처 준수**: `st` (Streamlit UI 라이브러리) 및 `st.column_config` 등을 서비스 레이어 내에서 절대로 호출하거나 상수로 선언하지 않습니다. 서비스 레이어는 데이터와 연산만 다루고, 표현(Presentation) 방식은 전적으로 UI/플롯 레이어에 일임합니다.
2. **파라미터 데이터클래스 필수 일원화**: 모든 신규 서비스 함수 및 전처리 함수는 낱개 파라미터(`start_date: str`, `end_date: str`)를 직접 바인딩하지 않고, 공통 파라미터 또는 전용 파라미터 데이터클래스(`DateFilterParams` 등)를 정의하여 상속 및 포팅해야 합니다.
3. **정의되지 않은 미임포트/참조 오류 제거 (Dead Code 예방)**: 로컬 혹은 타 패키지에 실재하지 않는 매개변수 클래스(`FourMChangeProcessingParams`)나 쿼리 함수(`direct_spec_revision`)를 임의 호출한 뒤 `# noqa` 주석 등으로 검사기만 통과시키는 행위를 엄격히 금지합니다.
4. **모듈 임포트 스타일의 일관성**: `queries` 패키지 하위의 파일들을 참조할 때, `from queries import xxx_query` 스타일의 패키지 레벨 임포트를 지향하여 쿼리 함수의 호출 출처를 코딩 상에서 명확하게 파악하도록 합니다.
5. **중복 전처리 함수 금지 (단일 진실 공급원 - SSOT)**: 완전히 동일한 쿼리를 수행하면서 캐싱 유무만 다른 여러 개의 독립된 함수(`preprocessing_oeapp_rawdata` vs `preprocessing_oeapp_general_rawdata`)의 불필요한 정의를 철저히 지양합니다.
6. **모듈 레벨 DB 클라이언트 금지**: 모듈 레벨에서 DB 클라이언트를 선언해놓지 않고, 개별 함수 내부에서 `get_client()`를 가져와 호출하도록 보장합니다.
7. **환경 조작 코드 방지**: `sys.path.append` 또는 `importlib.reload` 같은 런타임 환경 오염 스크립트를 서비스 모듈에 어떠한 이유로든 주입하지 않습니다.

