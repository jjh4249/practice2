import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="Gelatico | 프리미엄 젤라또 프랜차이즈",
    page_icon="🍨",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =========================================================
# 경로 설정
# =========================================================
DATA_DIR = Path("data")

EXPECTED_FILES = {
    "store_data": DATA_DIR / "store_data.csv",
    "monthly_sales": DATA_DIR / "monthly_sales.csv",
    "top_stores": DATA_DIR / "top_store_data.csv",
    "location_analysis": DATA_DIR / "market_data.csv",
    "cost_structure": DATA_DIR / "store_size_cost.csv",
    "marketing_effect": DATA_DIR / "marketing_data.csv",
}

REQUIRED_COLUMNS = {
    "store_data": ["store_name", "region", "location_type", "store_size_pyeong", "opening_month"],
    "monthly_sales": ["month", "store_name", "region", "location_type", "revenue_million_krw"],
    "top_stores": ["store_name", "avg_revenue_million_krw", "rank"],
    "location_analysis": ["location_type", "avg_revenue_million_krw", "foot_traffic_index"],
    "cost_structure": ["cost_item", "percentage"],
    "marketing_effect": ["strategy", "revenue_uplift_pct", "monthly_cost_million_krw"],
}

LOCATION_ORDER = ["오피스", "대학가", "주거", "관광"]

MENU_ITEMS = [
    {
        "name": "시그니처 피스타치오 젤라또",
        "desc": "깊은 풍미와 고소함이 살아있는 프리미엄 시그니처 메뉴",
        "price": "6,500원",
        "tag": "BEST",
    },
    {
        "name": "제주 말차 젤라또",
        "desc": "제주산 말차의 쌉싸름함과 부드러운 질감의 조화",
        "price": "6,800원",
        "tag": "PREMIUM",
    },
    {
        "name": "딸기 마스카포네 컵",
        "desc": "상큼한 딸기와 진한 치즈 풍미를 담은 인기 디저트",
        "price": "7,200원",
        "tag": "NEW",
    },
    {
        "name": "바닐라 빈 아포가토",
        "desc": "젤라또와 에스프레소가 어우러진 디저트 커피",
        "price": "6,900원",
        "tag": "CAFE",
    },
    {
        "name": "솔티드 캐러멜 젤라또",
        "desc": "짭조름한 포인트가 매력적인 대중성 높은 메뉴",
        "price": "6,300원",
        "tag": "POPULAR",
    },
    {
        "name": "레몬 요거트 젤라또",
        "desc": "가볍고 산뜻한 맛으로 여름철 수요가 높은 메뉴",
        "price": "6,400원",
        "tag": "SUMMER",
    },
]

SEASONAL_ITEMS = [
    {"season": "봄", "menu": "체리 블라썸 젤라또", "note": "벚꽃 시즌 한정"},
    {"season": "여름", "menu": "망고 코코넛 젤라또", "note": "여름 피크 시즌 매출 견인"},
    {"season": "가을", "menu": "밤 티라미수 젤라또", "note": "디저트 수요 강화"},
    {"season": "겨울", "menu": "초코 헤이즐넛 핫 아포가토", "note": "동절기 객단가 상승"},
]

PROCESS_STEPS = [
    ("1", "창업 문의", "온라인 폼 / 전화 초기 관심 접수", "1일"),
    ("2", "브랜드 상담", "1:1 전담 상담 및 방향성·예산 협의", "1주"),
    ("3", "상권 분석", "유동인구·입지·경쟁 점포 분석", "2주"),
    ("4", "점포 규모 산정", "10/15/20평 기준 비용·수익 비교", "1주"),
    ("5", "가맹 계약", "계약 조건 검토 및 계약서 서명", "1주"),
    ("6", "인테리어/설비", "브랜드 가이드 시공 진행", "4~6주"),
    ("7", "교육/운영 준비", "제조·POS·CS 교육", "2주"),
    ("8", "오픈 & 사후관리", "그랜드 오픈 및 초기 운영 안정화 지원", "지속"),
]

# =========================================================
# 스타일
# =========================================================
def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"] {
            font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
                         "Malgun Gothic", "Segoe UI", sans-serif;
            background-color: #f6f1e3;
        }

        .stApp {
            background-color: #f6f1e3;
        }

        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1280px;
        }

        .hero-wrap {
            background: linear-gradient(135deg, #173b78 0%, #4b92df 100%);
            border-radius: 28px;
            padding: 34px 24px 48px 24px;
            text-align: center;
            color: white;
            margin-bottom: 28px;
            box-shadow: 0 10px 30px rgba(18, 53, 110, 0.18);
        }

        .hero-badge {
            display: inline-block;
            padding: 10px 22px;
            border-radius: 999px;
            background: rgba(255,255,255,0.18);
            font-size: 0.95rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            margin-bottom: 24px;
        }

        .hero-logo {
            font-size: 2.4rem;
            font-weight: 800;
            letter-spacing: 0.08em;
            margin-bottom: 8px;
        }

        .hero-sub {
            font-size: 1.15rem;
            opacity: 0.95;
            margin-bottom: 0;
        }

        .section-shell {
            background: #ffffff;
            border-radius: 24px;
            padding: 28px 28px 32px 28px;
            box-shadow: 0 8px 24px rgba(0,0,0,0.06);
            border: 1px solid rgba(20, 40, 80, 0.06);
        }

        .section-title {
            font-size: 1.5rem;
            font-weight: 800;
            color: #173b78;
            margin-bottom: 8px;
        }

        .section-desc {
            color: #6b7280;
            margin-bottom: 26px;
            font-size: 1rem;
        }

        .metric-card {
            background: linear-gradient(180deg, #f8fbff 0%, #eef5ff 100%);
            border: 1px solid #dbe7fb;
            border-radius: 20px;
            padding: 18px 16px;
            text-align: center;
            height: 100%;
        }

        .metric-label {
            font-size: 0.92rem;
            color: #5b6472;
            margin-bottom: 8px;
            font-weight: 600;
        }

        .metric-value {
            font-size: 1.75rem;
            font-weight: 800;
            color: #173b78;
        }

        .metric-sub {
            margin-top: 6px;
            color: #7b8390;
            font-size: 0.88rem;
        }

        .brand-card {
            background: #ffffff;
            border: 1px solid #e7ecf4;
            border-radius: 20px;
            padding: 20px;
            height: 100%;
            box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        }

        .brand-card h4 {
            margin-top: 0;
            color: #173b78;
            font-size: 1.08rem;
            margin-bottom: 12px;
        }

        .brand-card p {
            margin-bottom: 0;
            color: #586173;
            line-height: 1.65;
        }

        .menu-card {
            background: #ffffff;
            border: 1px solid #e8edf6;
            border-radius: 22px;
            padding: 20px;
            height: 100%;
            box-shadow: 0 5px 16px rgba(0,0,0,0.04);
        }

        .menu-tag {
            display: inline-block;
            padding: 6px 10px;
            border-radius: 999px;
            background: #eef4ff;
            color: #173b78;
            font-size: 0.78rem;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .menu-name {
            font-size: 1.12rem;
            font-weight: 800;
            color: #173b78;
            margin-bottom: 8px;
        }

        .menu-desc {
            color: #5f6a7b;
            min-height: 56px;
            margin-bottom: 12px;
            line-height: 1.55;
        }

        .menu-price {
            font-size: 1.05rem;
            font-weight: 800;
            color: #111827;
        }

        .process-card {
            background: #ffffff;
            border: 1px solid #e7ebf3;
            border-radius: 22px;
            padding: 22px 14px;
            text-align: center;
            box-shadow: 0 5px 16px rgba(0,0,0,0.04);
            height: 100%;
        }

        .process-num {
            width: 48px;
            height: 48px;
            border-radius: 999px;
            background: #173b78;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            margin: 0 auto 16px auto;
            font-weight: 800;
            font-size: 1.1rem;
        }

        .process-title {
            font-size: 1.06rem;
            font-weight: 800;
            color: #173b78;
            margin-bottom: 10px;
        }

        .process-desc {
            color: #687284;
            font-size: 0.95rem;
            line-height: 1.55;
            min-height: 60px;
        }

        .process-time {
            display: inline-block;
            margin-top: 12px;
            padding: 6px 12px;
            border-radius: 999px;
            background: #eef4ff;
            color: #173b78;
            font-size: 0.82rem;
            font-weight: 700;
        }

        .small-note {
            color: #6b7280;
            font-size: 0.92rem;
        }

        div[data-baseweb="tab-list"] {
            gap: 10px;
            background: #173b78;
            padding: 10px;
            border-radius: 18px;
            margin-bottom: 24px;
        }

        button[data-baseweb="tab"] {
            background: transparent;
            border-radius: 14px;
            color: white;
            font-weight: 700;
            padding: 12px 18px;
            border: none;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            background: #ffffff !important;
            color: #173b78 !important;
            box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        }

        div[data-testid="stMetric"] {
            background: #f9fbff;
            border: 1px solid #e1e9f8;
            padding: 14px;
            border-radius: 18px;
        }

        .footer-note {
            text-align: center;
            color: #7b8390;
            font-size: 0.9rem;
            margin-top: 18px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 유틸
# =========================================================
def safe_read_csv(file_path: Path) -> pd.DataFrame | None:
    if not file_path.exists():
        return None

    for enc in ["utf-8", "utf-8-sig", "cp949"]:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue
    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    column_map = {
        "매장명": "store_name",
        "점포명": "store_name",
        "지점명": "store_name",
        "store": "store_name",
        "지역": "region",
        "권역": "region",
        "시도": "region",
        "입지유형": "location_type",
        "상권유형": "location_type",
        "상권": "location_type",
        "입지": "location_type",
        "location": "location_type",
        "평수": "store_size_pyeong",
        "매장평수": "store_size_pyeong",
        "점포평수": "store_size_pyeong",
        "store_size": "store_size_pyeong",
        "오픈월": "opening_month",
        "개점월": "opening_month",
        "오픈일": "opening_month",
        "opening": "opening_month",
        "월": "month",
        "기준월": "month",
        "날짜": "month",
        "month_date": "month",
        "월매출": "revenue_million_krw",
        "매출": "revenue_million_krw",
        "매출액": "revenue_million_krw",
        "revenue": "revenue_million_krw",
        "평균매출": "avg_revenue_million_krw",
        "평균 월매출": "avg_revenue_million_krw",
        "평균월매출": "avg_revenue_million_krw",
        "순위": "rank",
        "유동인구지수": "foot_traffic_index",
        "유동인구": "foot_traffic_index",
        "비용항목": "cost_item",
        "항목": "cost_item",
        "비용비율": "percentage",
        "비율": "percentage",
        "구성비": "percentage",
        "전략": "strategy",
        "마케팅전략": "strategy",
        "매출상승률": "revenue_uplift_pct",
        "매출증가율": "revenue_uplift_pct",
        "상승률": "revenue_uplift_pct",
        "월마케팅비": "monthly_cost_million_krw",
        "마케팅비": "monthly_cost_million_krw",
    }

    return df.rename(columns=column_map)


def validate_columns(df: pd.DataFrame, required_cols: list[str]) -> list[str]:
    return [col for col in required_cols if col not in df.columns]


def format_million_krw(value: float) -> str:
    return f"{value:,.0f}만원"


def month_to_season(month_int: int) -> str:
    if month_int in [12, 1, 2]:
        return "겨울"
    if month_int in [3, 4, 5]:
        return "봄"
    if month_int in [6, 7, 8]:
        return "여름"
    return "가을"


def ensure_month_str(series: pd.Series) -> pd.Series:
    s = series.astype(str).str.strip()
    s = s.replace(r"^(\d{4})(\d{2})$", r"\1-\2", regex=True)
    s = s.str.replace("/", "-", regex=False)
    s = s.str.replace(".", "-", regex=False)
    return s

# =========================================================
# 데모 데이터
# =========================================================
def create_demo_data() -> dict[str, pd.DataFrame]:
    np.random.seed(42)

    store_names = [
        "강남점", "성수점", "홍대점", "잠실점", "판교점", "분당점",
        "수원점", "인천송도점", "대전둔산점", "천안점", "수원광교점", "안양점",
        "일산점", "건대점", "신촌점", "해운대점", "제주점", "광화문점"
    ]
    regions = [
        "서울", "서울", "서울", "서울", "경기", "경기",
        "경기", "인천", "대전", "충남", "경기", "경기",
        "경기", "서울", "서울", "부산", "제주", "서울"
    ]
    location_types = [
        "오피스", "주거", "대학가", "주거", "오피스", "주거",
        "주거", "관광", "오피스", "대학가", "주거", "주거",
        "주거", "대학가", "대학가", "관광", "관광", "오피스"
    ]
    store_sizes = [15, 15, 10, 20, 15, 15, 15, 20, 15, 10, 20, 15, 15, 10, 10, 20, 20, 15]
    opening_months = [
        "2023-01", "2023-02", "2023-03", "2023-04", "2023-05", "2023-06",
        "2023-07", "2023-08", "2023-09", "2023-10", "2024-01", "2024-02",
        "2024-03", "2024-04", "2024-05", "2024-06", "2024-07", "2024-08"
    ]

    base_by_location = {
        "오피스": 77.0,
        "대학가": 69.0,
        "주거": 71.0,
        "관광": 82.0,
    }
    store_bonus = {
        "제주점": 18.0,
        "해운대점": 10.0,
        "강남점": 8.0,
        "광화문점": 7.0,
        "성수점": 6.0,
        "판교점": 5.0,
    }

    store_data = pd.DataFrame({
        "store_name": store_names,
        "region": regions,
        "location_type": location_types,
        "store_size_pyeong": store_sizes,
        "opening_month": opening_months,
    })

    months = pd.date_range("2023-01-01", "2025-12-01", freq="MS")
    monthly_rows = []

    seasonality = {
        1: 0.92, 2: 0.95, 3: 1.00, 4: 1.03, 5: 1.05, 6: 1.12,
        7: 1.22, 8: 1.20, 9: 1.06, 10: 1.00, 11: 0.96, 12: 0.98
    }

    for _, store in store_data.iterrows():
        base = base_by_location[store["location_type"]] + store_bonus.get(store["store_name"], 0.0)

        for dt in months:
            trend_factor = 1 + ((dt.year - 2023) * 0.03)
            seasonal_factor = seasonality[dt.month]
            noise = np.random.normal(0, 4.5)

            revenue = base * trend_factor * seasonal_factor + noise
            revenue = max(revenue, 45.0)

            monthly_rows.append({
                "month": dt.strftime("%Y-%m"),
                "store_name": store["store_name"],
                "region": store["region"],
                "location_type": store["location_type"],
                "revenue_million_krw": round(revenue, 1),
            })

    monthly_sales = pd.DataFrame(monthly_rows)

    current_avg = monthly_sales["revenue_million_krw"].mean()
    target_avg = 74.49
    scaling = target_avg / current_avg
    monthly_sales["revenue_million_krw"] = (monthly_sales["revenue_million_krw"] * scaling).round(1)

    idx_jeju_peak = monthly_sales[
        (monthly_sales["store_name"] == "제주점") &
        (monthly_sales["month"] == "2025-08")
    ].index
    if len(idx_jeju_peak) > 0:
        monthly_sales.loc[idx_jeju_peak[0], "revenue_million_krw"] = 124.82

    top_stores = (
        monthly_sales.groupby("store_name", as_index=False)["revenue_million_krw"]
        .mean()
        .rename(columns={"revenue_million_krw": "avg_revenue_million_krw"})
        .sort_values("avg_revenue_million_krw", ascending=False)
        .reset_index(drop=True)
    )
    top_stores["rank"] = top_stores.index + 1
    top_stores = top_stores[["store_name", "avg_revenue_million_krw", "rank"]]

    location_analysis = (
        monthly_sales.groupby("location_type", as_index=False)["revenue_million_krw"]
        .mean()
        .rename(columns={"revenue_million_krw": "avg_revenue_million_krw"})
    )
    traffic_map = {"오피스": 88, "대학가": 82, "주거": 68, "관광": 91}
    location_analysis["foot_traffic_index"] = location_analysis["location_type"].map(traffic_map)

    cost_structure = pd.DataFrame({
        "cost_item": ["임대료", "인건비", "원재료비", "마케팅비", "공과금/기타"],
        "percentage": [22, 24, 28, 8, 18],
    })

    marketing_effect = pd.DataFrame({
        "strategy": ["인스타 광고", "배달앱 프로모션", "오픈 이벤트", "멤버십 적립", "지역 제휴 마케팅"],
        "revenue_uplift_pct": [4.0, 7.0, 6.0, 3.0, 5.0],
        "monthly_cost_million_krw": [1.2, 2.5, 1.8, 0.8, 1.0],
    })

    return {
        "store_data": store_data,
        "monthly_sales": monthly_sales,
        "top_stores": top_stores,
        "location_analysis": location_analysis,
        "cost_structure": cost_structure,
        "marketing_effect": marketing_effect,
    }

# =========================================================
# 전처리
# =========================================================
def preprocess_store_data(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["store_data"])
    if missing:
        return fallback_df.copy()

    df = df.copy()
    df["store_name"] = df["store_name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["location_type"] = df["location_type"].astype(str).str.strip()
    df["store_size_pyeong"] = pd.to_numeric(df["store_size_pyeong"], errors="coerce")
    df["opening_month"] = ensure_month_str(df["opening_month"])
    return df.dropna()


def preprocess_monthly_sales(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["monthly_sales"])
    if missing:
        return fallback_df.copy()

    df = df.copy()
    df["month"] = ensure_month_str(df["month"])
    df["store_name"] = df["store_name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["location_type"] = df["location_type"].astype(str).str.strip()
    df["revenue_million_krw"] = pd.to_numeric(df["revenue_million_krw"], errors="coerce")
    df["month_date"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["month_num"] = df["month_date"].dt.month
    df["season"] = df["month_num"].apply(lambda x: month_to_season(int(x)) if pd.notnull(x) else "기타")
    return df.dropna(subset=["month", "store_name", "region", "location_type", "revenue_million_krw"])


def preprocess_top_stores(df: pd.DataFrame, monthly_sales: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["top_stores"])
    if missing:
        if monthly_sales is not None and not monthly_sales.empty:
            rebuilt = (
                monthly_sales.groupby("store_name", as_index=False)["revenue_million_krw"]
                .mean()
                .rename(columns={"revenue_million_krw": "avg_revenue_million_krw"})
                .sort_values("avg_revenue_million_krw", ascending=False)
                .reset_index(drop=True)
            )
            rebuilt["rank"] = rebuilt.index + 1
            return rebuilt[["store_name", "avg_revenue_million_krw", "rank"]]
        return fallback_df.copy()

    df = df.copy()
    df["avg_revenue_million_krw"] = pd.to_numeric(df["avg_revenue_million_krw"], errors="coerce")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    return df.dropna(subset=["store_name", "avg_revenue_million_krw", "rank"])


def preprocess_location_analysis(df: pd.DataFrame, monthly_sales: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["location_analysis"])
    if missing:
        if monthly_sales is not None and not monthly_sales.empty:
            rebuilt = (
                monthly_sales.groupby("location_type", as_index=False)["revenue_million_krw"]
                .mean()
                .rename(columns={"revenue_million_krw": "avg_revenue_million_krw"})
            )
            traffic_map = {"오피스": 88, "대학가": 82, "주거": 68, "관광": 91}
            rebuilt["foot_traffic_index"] = rebuilt["location_type"].map(traffic_map).fillna(75)
            return rebuilt
        return fallback_df.copy()

    df = df.copy()
    df["avg_revenue_million_krw"] = pd.to_numeric(df["avg_revenue_million_krw"], errors="coerce")
    df["foot_traffic_index"] = pd.to_numeric(df["foot_traffic_index"], errors="coerce")
    return df.dropna(subset=["location_type", "avg_revenue_million_krw", "foot_traffic_index"])


def preprocess_cost_structure(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["cost_structure"])
    if missing:
        return fallback_df.copy()

    df = df.copy()
    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce")
    return df.dropna(subset=["cost_item", "percentage"])


def preprocess_marketing_effect(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    missing = validate_columns(df, REQUIRED_COLUMNS["marketing_effect"])
    if missing:
        return fallback_df.copy()

    df = df.copy()
    df["revenue_uplift_pct"] = pd.to_numeric(df["revenue_uplift_pct"], errors="coerce")
    df["monthly_cost_million_krw"] = pd.to_numeric(df["monthly_cost_million_krw"], errors="coerce")
    return df.dropna(subset=["strategy", "revenue_uplift_pct", "monthly_cost_million_krw"])

# =========================================================
# 로딩
# =========================================================
@st.cache_data
def load_data() -> tuple[dict[str, pd.DataFrame], list[str]]:
    demo = create_demo_data()
    raw_data = {}
    messages = []

    for key, path in EXPECTED_FILES.items():
        df = safe_read_csv(path)
        if df is None:
            raw_data[key] = demo[key]
            messages.append(f"{path.name}: 파일이 없어 데모 데이터를 사용합니다.")
        else:
            raw_data[key] = normalize_columns(df)
            messages.append(f"{path.name}: 로드 완료")

    store_data = preprocess_store_data(raw_data["store_data"], demo["store_data"])
    monthly_sales = preprocess_monthly_sales(raw_data["monthly_sales"], demo["monthly_sales"])
    top_stores = preprocess_top_stores(raw_data["top_stores"], monthly_sales, demo["top_stores"])
    location_analysis = preprocess_location_analysis(raw_data["location_analysis"], monthly_sales, demo["location_analysis"])
    cost_structure = preprocess_cost_structure(raw_data["cost_structure"], demo["cost_structure"])
    marketing_effect = preprocess_marketing_effect(raw_data["marketing_effect"], demo["marketing_effect"])

    return {
        "store_data": store_data,
        "monthly_sales": monthly_sales,
        "top_stores": top_stores,
        "location_analysis": location_analysis,
        "cost_structure": cost_structure,
        "marketing_effect": marketing_effect,
    }, messages


def compute_kpis(monthly_sales: pd.DataFrame) -> dict[str, float | str]:
    store_count = monthly_sales["store_name"].nunique()
    avg_revenue = float(monthly_sales["revenue_million_krw"].mean())
    max_revenue = float(monthly_sales["revenue_million_krw"].max())
    top_row = monthly_sales.loc[monthly_sales["revenue_million_krw"].idxmax()]
    top_store = str(top_row["store_name"])
    return {
        "store_count": store_count,
        "avg_revenue": avg_revenue,
        "max_revenue": max_revenue,
        "top_store": top_store,
    }

# =========================================================
# 시뮬레이션
# =========================================================
def run_simulation(
    location_type: str,
    store_size: int,
    selected_marketing: list[str],
    location_analysis: pd.DataFrame,
    marketing_effect: pd.DataFrame,
) -> dict[str, float]:
    row = location_analysis[location_analysis["location_type"] == location_type]
    base_revenue = float(row["avg_revenue_million_krw"].iloc[0]) if not row.empty else 74.49

    size_multiplier = {10: 0.88, 15: 1.00, 20: 1.16}.get(store_size, 1.00)
    expected_revenue = base_revenue * size_multiplier

    total_uplift_pct = 0.0
    marketing_cost = 0.0

    if selected_marketing:
        selected_df = marketing_effect[marketing_effect["strategy"].isin(selected_marketing)].copy()
        total_uplift_pct = min(selected_df["revenue_uplift_pct"].sum(), 18.0)
        marketing_cost = selected_df["monthly_cost_million_krw"].sum()

    expected_revenue *= (1 + total_uplift_pct / 100)

    cogs = expected_revenue * 0.28

    rent_by_size = {10: 11.0, 15: 14.0, 20: 18.0}
    labor_by_size = {10: 13.0, 15: 16.0, 20: 20.0}
    utilities_by_size = {10: 3.5, 15: 4.2, 20: 5.0}
    location_rent_multiplier = {
        "오피스": 1.18,
        "대학가": 1.05,
        "주거": 0.95,
        "관광": 1.12,
    }.get(location_type, 1.0)

    monthly_rent = rent_by_size[store_size] * location_rent_multiplier
    labor_cost = labor_by_size[store_size]
    utilities_cost = utilities_by_size[store_size]
    misc_fixed = 2.5
    fixed_cost = monthly_rent + labor_cost + utilities_cost + misc_fixed + marketing_cost

    net_profit = expected_revenue - cogs - fixed_cost

    fitout_per_pyeong = 2.6
    interior_cost = store_size * fitout_per_pyeong
    equipment_cost = {10: 32.0, 15: 38.0, 20: 45.0}[store_size]
    franchise_fee = 12.0
    training_fee = 4.0
    opening_inventory = 6.0

    initial_investment = interior_cost + equipment_cost + franchise_fee + training_fee + opening_inventory

    payback_period_months = math.inf if net_profit <= 0 else initial_investment / net_profit

    return {
        "expected_revenue": round(expected_revenue, 1),
        "fixed_cost": round(fixed_cost, 1),
        "net_profit": round(net_profit, 1),
        "initial_investment": round(initial_investment, 1),
        "payback_period_months": payback_period_months,
    }

# =========================================================
# UI 컴포넌트
# =========================================================
def render_hero():
    st.markdown(
        """
        <div class="hero-wrap">
            <div class="hero-badge">🍨 PREMIUM GELATO FRANCHISE</div>
            <div class="hero-logo">GELATICO</div>
            <p class="hero-sub">젤라티코 — 이탈리아의 맛, 당신의 매장에서</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(kpis):
    c1, c2, c3, c4 = st.columns(4)
    cards = [
        ("운영 매장 수", f"{kpis['store_count']}개", "전국 운영 네트워크"),
        ("평균 월매출", format_million_krw(kpis["avg_revenue"]), "전체 매장 평균 기준"),
        ("최대 월매출", format_million_krw(kpis["max_revenue"]), "최고 성과 월 기준"),
        ("최고 매장", str(kpis["top_store"]), "피크 성과 매장"),
    ]
    for col, (label, value, sub) in zip([c1, c2, c3, c4], cards):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-sub">{sub}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# =========================================================
# 탭 1: 젤라티코란?
# =========================================================
def render_brand_tab(kpis, store_data):
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🍨 젤라티코란?</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">감성 브랜딩과 프리미엄 디저트 경험을 결합한 젤라또 프랜차이즈 브랜드입니다.</div>',
        unsafe_allow_html=True,
    )

    render_metric_cards(kpis)
    st.write("")

    col1, col2 = st.columns([1.2, 1])
    with col1:
        st.markdown(
            """
            <div class="brand-card">
                <h4>브랜드 스토리</h4>
                <p>
                Gelatico는 단순히 디저트를 판매하는 브랜드가 아니라,
                감성적인 공간 경험과 시즌별 메뉴 기획을 통해
                '머물고 싶은 디저트 브랜드'를 지향합니다.
                젤라또의 신선함, 프리미엄 원재료, SNS 확산성이 높은 비주얼 요소를 중심으로
                재방문율과 브랜드 체류 경험을 함께 설계합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="brand-card">
                <h4>핵심 차별화 요소</h4>
                <p>
                1. 여름 성수기 매출 확장성이 높은 업종 구조<br>
                2. 시즌 메뉴 운영을 통한 이슈화와 재방문 유도<br>
                3. 상권/입지 데이터 기반 출점 판단 가능<br>
                4. 디저트 + 카페 경험을 결합한 객단가 설계
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.write("")
    st.subheader("대표 메뉴")
    cols = st.columns(3)
    for idx, item in enumerate(MENU_ITEMS[:6]):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="menu-card">
                    <div class="menu-tag">{item['tag']}</div>
                    <div class="menu-name">{item['name']}</div>
                    <div class="menu-desc">{item['desc']}</div>
                    <div class="menu-price">{item['price']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.subheader("지역별 매장 분포")
    region_counts = store_data["region"].value_counts().reset_index()
    region_counts.columns = ["region", "store_count"]

    fig = px.bar(
        region_counts,
        x="region",
        y="store_count",
        text="store_count",
        title="지역별 운영 매장 수",
    )
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 탭 2: 마케팅 전략
# =========================================================
def render_marketing_tab(marketing_effect, monthly_sales):
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📣 마케팅 전략</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">성수기 수요 확대와 비성수기 재방문 유도를 동시에 고려한 마케팅 구조입니다.</div>',
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1, 1])

    with c1:
        st.subheader("마케팅 효과 비교")
        fig = px.bar(
            marketing_effect,
            x="strategy",
            y="revenue_uplift_pct",
            text="revenue_uplift_pct",
            title="전략별 예상 매출 상승률",
            labels={"strategy": "전략", "revenue_uplift_pct": "매출 상승률(%)"},
        )
        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
        fig.update_layout(height=420, xaxis_tickangle=-20)
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("전략별 월 마케팅 비용")
        fig2 = px.bar(
            marketing_effect,
            x="strategy",
            y="monthly_cost_million_krw",
            text="monthly_cost_million_krw",
            title="전략별 월 비용",
            labels={"strategy": "전략", "monthly_cost_million_krw": "비용(만원)"},
        )
        fig2.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig2.update_layout(height=420, xaxis_tickangle=-20)
        st.plotly_chart(fig2, use_container_width=True)

    st.write("")
    st.subheader("시즌성 관점 마케팅 운영 방향")

    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            """
            <div class="brand-card">
                <h4>오픈 초기</h4>
                <p>
                오픈 이벤트와 지역 제휴 마케팅을 중심으로
                첫 방문 고객 유입과 지역 인지도를 확보합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            """
            <div class="brand-card">
                <h4>성수기 확장</h4>
                <p>
                인스타 광고와 계절 한정 메뉴 홍보를 통해
                여름 피크 시즌 매출을 극대화합니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            """
            <div class="brand-card">
                <h4>재방문 유도</h4>
                <p>
                멤버십 적립과 배달앱 프로모션을 통해
                반복 구매와 생활권 고객 유지율을 높입니다.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    season_df = (
        monthly_sales.groupby("season", as_index=False)["revenue_million_krw"]
        .mean()
    )
    season_order = ["봄", "여름", "가을", "겨울"]
    season_df["season"] = pd.Categorical(season_df["season"], categories=season_order, ordered=True)
    season_df = season_df.sort_values("season")

    st.write("")
    st.subheader("계절별 평균 매출")
    fig3 = px.line(
        season_df,
        x="season",
        y="revenue_million_krw",
        markers=True,
        title="계절별 평균 매출 흐름",
        labels={"season": "계절", "revenue_million_krw": "평균 매출(만원)"},
    )
    fig3.update_layout(height=380)
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 탭 3: 매출현황
# =========================================================
def render_sales_tab(monthly_sales, cost_structure):
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📊 매출현황</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">지역, 매장, 입지 유형별 매출 흐름과 비용 구조를 함께 확인할 수 있습니다.</div>',
        unsafe_allow_html=True,
    )

    f1, f2, f3 = st.columns(3)
    available_regions = ["전체"] + sorted(monthly_sales["region"].dropna().unique().tolist())
    available_stores = ["전체"] + sorted(monthly_sales["store_name"].dropna().unique().tolist())
    available_locations = ["전체"] + sorted(monthly_sales["location_type"].dropna().unique().tolist())

    selected_region = f1.selectbox("지역 선택", available_regions)
    selected_store = f2.selectbox("매장 선택", available_stores)
    selected_location = f3.selectbox("입지 유형 선택", available_locations)

    filtered = monthly_sales.copy()
    if selected_region != "전체":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_store != "전체":
        filtered = filtered[filtered["store_name"] == selected_store]
    if selected_location != "전체":
        filtered = filtered[filtered["location_type"] == selected_location]

    if filtered.empty:
        st.warning("선택한 조건에 해당하는 데이터가 없습니다.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 매장 수", f"{filtered['store_name'].nunique()}개")
    c2.metric("평균 월매출", format_million_krw(filtered["revenue_million_krw"].mean()))
    c3.metric("최대 월매출", format_million_krw(filtered["revenue_million_krw"].max()))
    c4.metric(
        "상위 매장",
        filtered.groupby("store_name")["revenue_million_krw"].mean().sort_values(ascending=False).index[0]
    )

    st.write("")
    col1, col2 = st.columns([1.1, 1])

    with col1:
        store_compare = (
            filtered.groupby("store_name", as_index=False)["revenue_million_krw"]
            .mean()
            .sort_values("revenue_million_krw", ascending=False)
        )

        fig_bar = px.bar(
            store_compare,
            x="store_name",
            y="revenue_million_krw",
            text="revenue_million_krw",
            title="매장별 평균 월매출",
            labels={"store_name": "매장", "revenue_million_krw": "평균 매출(만원)"},
        )
        fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_bar.update_layout(height=430, xaxis_tickangle=-25)
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        fig_pie = px.pie(
            cost_structure,
            names="cost_item",
            values="percentage",
            title="비용 구조",
            hole=0.45,
        )
        fig_pie.update_layout(height=430)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.write("")
    top5_stores = (
        filtered.groupby("store_name")["revenue_million_krw"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    line_df = filtered[filtered["store_name"].isin(top5_stores)].copy().sort_values("month_date")
    fig_line = px.line(
        line_df,
        x="month_date",
        y="revenue_million_krw",
        color="store_name",
        markers=True,
        title="상위 5개 매장 월별 매출 추이",
        labels={"month_date": "월", "revenue_million_krw": "매출(만원)", "store_name": "매장"},
    )
    fig_line.update_layout(height=500)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("데이터 미리보기")
    preview_cols = ["month", "store_name", "region", "location_type", "revenue_million_krw"]
    st.dataframe(
        filtered[preview_cols].sort_values(["month", "store_name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 탭 4: 창업안내
# =========================================================
def render_process_tab(location_analysis, marketing_effect):
    st.markdown('<div class="section-shell">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📋 창업안내</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-desc">문의부터 오픈까지 젤라티코 전담팀이 함께합니다.</div>',
        unsafe_allow_html=True,
    )

    cols = st.columns(8)
    for col, step in zip(cols, PROCESS_STEPS):
        num, title, desc, duration = step
        with col:
            st.markdown(
                f"""
                <div class="process-card">
                    <div class="process-num">{num}</div>
                    <div class="process-title">{title}</div>
                    <div class="process-desc">{desc}</div>
                    <div class="process-time">{duration}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.subheader("예상 수익 시뮬레이션")

    col1, col2 = st.columns([1, 1])

    with col1:
        location_options = sorted(location_analysis["location_type"].dropna().unique().tolist())
        if not location_options:
            location_options = LOCATION_ORDER

        location_type = st.selectbox("입지 유형", location_options, key="sim_location")
        store_size = st.selectbox("매장 평수", [10, 15, 20], index=1, key="sim_size")
        selected_marketing = st.multiselect(
            "적용할 마케팅 전략",
            options=marketing_effect["strategy"].tolist(),
            default=marketing_effect["strategy"].tolist()[:1],
            key="sim_marketing"
        )

    results = run_simulation(
        location_type=location_type,
        store_size=store_size,
        selected_marketing=selected_marketing,
        location_analysis=location_analysis,
        marketing_effect=marketing_effect,
    )

    with col2:
        st.metric("예상 월매출", format_million_krw(results["expected_revenue"]))
        st.metric("월 고정비", format_million_krw(results["fixed_cost"]))
        st.metric("예상 월순이익", format_million_krw(results["net_profit"]))
        st.metric("초기 투자비", format_million_krw(results["initial_investment"]))

        if math.isinf(results["payback_period_months"]):
            st.error("현재 조건에서는 투자금 회수기간 산정이 어렵습니다.")
        else:
            st.success(f"예상 투자금 회수기간: 약 {results['payback_period_months']:.1f}개월")

    if selected_marketing:
        st.write("")
        st.subheader("선택한 마케팅 전략")
        selected_df = marketing_effect[marketing_effect["strategy"].isin(selected_marketing)].copy()
        st.dataframe(selected_df, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

# =========================================================
# 메인
# =========================================================
def main():
    apply_custom_css()

    data, load_messages = load_data()
    store_data = data["store_data"]
    monthly_sales = data["monthly_sales"]
    cost_structure = data["cost_structure"]
    location_analysis = data["location_analysis"]
    marketing_effect = data["marketing_effect"]

    kpis = compute_kpis(monthly_sales)

    render_hero()

    with st.expander("데이터 로딩 상태", expanded=False):
        for msg in load_messages:
            st.write(f"- {msg}")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["🍨 젤라티코란?", "📣 마케팅 전략", "📊 매출현황", "📋 창업안내"]
    )

    with tab1:
        render_brand_tab(kpis, store_data)

    with tab2:
        render_marketing_tab(marketing_effect, monthly_sales)

    with tab3:
        render_sales_tab(monthly_sales, cost_structure)

    with tab4:
        render_process_tab(location_analysis, marketing_effect)

    st.markdown(
        '<div class="footer-note">Gelatico Franchise Decision Platform · 브랜드 이해 + 마케팅 + 매출현황 + 창업 시뮬레이션</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
