import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# Streamlit 기본 설정
# =========================================================
st.set_page_config(
    page_title="Gelatico | 프랜차이즈 창업 의사결정 플랫폼",
    page_icon="🍨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 경로 / 파일명 설정
# 네 GitHub data 폴더 파일명 기준으로 수정함
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
    ("1단계", "브랜드 상담", "창업 목적, 예산, 희망 지역 기초 상담"),
    ("2단계", "상권 분석", "유동인구·경쟁 브랜드·입지 적합성 분석"),
    ("3단계", "가맹 신청", "가맹 의사 확정 및 서류 검토"),
    ("4단계", "점포 확정", "입지 선정, 임대 조건 검토, 출점 승인"),
    ("5단계", "인테리어 및 설비", "프리미엄 콘셉트 기준 시공 진행"),
    ("6단계", "교육", "운영, 메뉴 제조, 고객 응대, 위생 교육"),
    ("7단계", "오픈 마케팅", "지역 타깃 사전 홍보 및 오픈 이벤트"),
    ("8단계", "정식 오픈", "운영 시작 후 슈퍼바이징 및 성과 모니터링"),
]

# =========================================================
# CSS
# =========================================================
def apply_custom_css() -> None:
    st.markdown(
        """
        <style>
        html, body, [class*="css"]  {
            font-family: -apple-system, BlinkMacSystemFont, "Apple SD Gothic Neo",
                         "Malgun Gothic", "Segoe UI", sans-serif;
        }
        .main-title {
            font-size: 2.2rem;
            font-weight: 800;
            margin-bottom: 0.3rem;
        }
        .sub-title {
            font-size: 1.05rem;
            color: #666666;
            margin-bottom: 1.2rem;
        }
        .hero-box {
            padding: 1.5rem;
            border-radius: 18px;
            background: linear-gradient(135deg, #fffaf5, #f9f1e7);
            border: 1px solid #f0e0cd;
            margin-bottom: 1rem;
        }
        .card {
            padding: 1rem;
            border: 1px solid #e9e9e9;
            border-radius: 16px;
            background-color: white;
            box-shadow: 0 2px 8px rgba(0,0,0,0.04);
            height: 100%;
        }
        .small-muted {
            color: #777777;
            font-size: 0.92rem;
        }
        .cta-box {
            padding: 1rem;
            border-radius: 14px;
            background-color: #fcfcfc;
            border: 1px dashed #d9d9d9;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# =========================================================
# 유틸
# =========================================================
def safe_read_csv(file_path: Path) -> pd.DataFrame | None:
    """
    CSV 읽기
    utf-8, utf-8-sig, cp949 순서로 시도
    """
    if not file_path.exists():
        return None

    for enc in ["utf-8", "utf-8-sig", "cp949"]:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue
    return None


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    여러 형태의 컬럼명을 표준 컬럼명으로 통일
    """
    df = df.copy()
    df.columns = [str(col).strip() for col in df.columns]

    column_map = {
        # store_data 관련
        "매장명": "store_name",
        "점포명": "store_name",
        "지점명": "store_name",
        "store": "store_name",
        "store_name ": "store_name",

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

        # monthly_sales 관련
        "월": "month",
        "기준월": "month",
        "날짜": "month",
        "month_date": "month",

        "월매출": "revenue_million_krw",
        "매출": "revenue_million_krw",
        "매출액": "revenue_million_krw",
        "revenue": "revenue_million_krw",
        "월 평균 매출": "revenue_million_krw",

        # top_stores 관련
        "평균매출": "avg_revenue_million_krw",
        "평균 월매출": "avg_revenue_million_krw",
        "평균월매출": "avg_revenue_million_krw",
        "순위": "rank",

        # location_analysis 관련
        "유동인구지수": "foot_traffic_index",
        "유동인구": "foot_traffic_index",
        "평균매출(만원)": "avg_revenue_million_krw",

        # cost_structure 관련
        "비용항목": "cost_item",
        "항목": "cost_item",
        "비용비율": "percentage",
        "비율": "percentage",
        "구성비": "percentage",

        # marketing_effect 관련
        "전략": "strategy",
        "마케팅전략": "strategy",
        "매출상승률": "revenue_uplift_pct",
        "매출증가율": "revenue_uplift_pct",
        "상승률": "revenue_uplift_pct",
        "월마케팅비": "monthly_cost_million_krw",
        "마케팅비": "monthly_cost_million_krw",
    }

    df = df.rename(columns=column_map)
    return df


def validate_columns(df: pd.DataFrame, required_cols: list[str]) -> list[str]:
    """
    누락된 컬럼 목록 반환
    """
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
    """
    월 컬럼을 YYYY-MM 형태 문자열로 정리
    """
    s = series.astype(str).str.strip()

    # 202301 -> 2023-01 변환
    s = s.replace(r"^(\d{4})(\d{2})$", r"\1-\2", regex=True)
    # 2023/01 -> 2023-01
    s = s.str.replace("/", "-", regex=False)
    # 2023.01 -> 2023-01
    s = s.str.replace(".", "-", regex=False)

    return s

# =========================================================
# 데모 데이터 생성
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
# 데이터 후처리
# =========================================================
def preprocess_store_data(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    missing = validate_columns(df, REQUIRED_COLUMNS["store_data"])
    if missing:
        return fallback_df.copy()

    df["store_name"] = df["store_name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["location_type"] = df["location_type"].astype(str).str.strip()
    df["store_size_pyeong"] = pd.to_numeric(df["store_size_pyeong"], errors="coerce")
    df["opening_month"] = ensure_month_str(df["opening_month"])

    df = df.dropna(subset=["store_name", "region", "location_type", "store_size_pyeong", "opening_month"])
    return df


def preprocess_monthly_sales(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    missing = validate_columns(df, REQUIRED_COLUMNS["monthly_sales"])
    if missing:
        return fallback_df.copy()

    df["month"] = ensure_month_str(df["month"])
    df["store_name"] = df["store_name"].astype(str).str.strip()
    df["region"] = df["region"].astype(str).str.strip()
    df["location_type"] = df["location_type"].astype(str).str.strip()
    df["revenue_million_krw"] = pd.to_numeric(df["revenue_million_krw"], errors="coerce")

    df["month_date"] = pd.to_datetime(df["month"], format="%Y-%m", errors="coerce")
    df["month_num"] = df["month_date"].dt.month
    df["season"] = df["month_num"].apply(lambda x: month_to_season(int(x)) if pd.notnull(x) else "기타")

    df = df.dropna(subset=["month", "store_name", "region", "location_type", "revenue_million_krw"])
    return df


def preprocess_top_stores(df: pd.DataFrame, monthly_sales: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
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

    df["avg_revenue_million_krw"] = pd.to_numeric(df["avg_revenue_million_krw"], errors="coerce")
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce")
    df = df.dropna(subset=["store_name", "avg_revenue_million_krw", "rank"])
    return df


def preprocess_location_analysis(df: pd.DataFrame, monthly_sales: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
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

    df["avg_revenue_million_krw"] = pd.to_numeric(df["avg_revenue_million_krw"], errors="coerce")
    df["foot_traffic_index"] = pd.to_numeric(df["foot_traffic_index"], errors="coerce")
    df = df.dropna(subset=["location_type", "avg_revenue_million_krw", "foot_traffic_index"])
    return df


def preprocess_cost_structure(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    missing = validate_columns(df, REQUIRED_COLUMNS["cost_structure"])

    if missing:
        return fallback_df.copy()

    df["percentage"] = pd.to_numeric(df["percentage"], errors="coerce")
    df = df.dropna(subset=["cost_item", "percentage"])
    return df


def preprocess_marketing_effect(df: pd.DataFrame, fallback_df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    missing = validate_columns(df, REQUIRED_COLUMNS["marketing_effect"])

    if missing:
        return fallback_df.copy()

    df["revenue_uplift_pct"] = pd.to_numeric(df["revenue_uplift_pct"], errors="coerce")
    df["monthly_cost_million_krw"] = pd.to_numeric(df["monthly_cost_million_krw"], errors="coerce")
    df = df.dropna(subset=["strategy", "revenue_uplift_pct", "monthly_cost_million_krw"])
    return df

# =========================================================
# 데이터 로딩
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
            messages.append(f"{path.name}: 파일을 찾지 못해 데모 데이터를 사용합니다.")
            continue

        df = normalize_columns(df)
        raw_data[key] = df
        messages.append(f"{path.name}: 파일 로드는 성공했습니다.")

    # 각 데이터셋 후처리
    store_data_missing = validate_columns(raw_data["store_data"], REQUIRED_COLUMNS["store_data"])
    if store_data_missing:
        messages.append(f"store_data.csv: 필요한 컬럼이 부족하여 데모 데이터로 대체했습니다. 누락 컬럼: {store_data_missing}")
    store_data = preprocess_store_data(raw_data["store_data"], demo["store_data"])

    monthly_sales_missing = validate_columns(raw_data["monthly_sales"], REQUIRED_COLUMNS["monthly_sales"])
    if monthly_sales_missing:
        messages.append(f"monthly_sales.csv: 필요한 컬럼이 부족하여 데모 데이터로 대체했습니다. 누락 컬럼: {monthly_sales_missing}")
    monthly_sales = preprocess_monthly_sales(raw_data["monthly_sales"], demo["monthly_sales"])

    top_missing = validate_columns(raw_data["top_stores"], REQUIRED_COLUMNS["top_stores"])
    if top_missing:
        messages.append(f"top_store_data.csv: 일부 컬럼이 부족해 monthly_sales 기준으로 재생성하거나 데모 데이터를 사용했습니다. 누락 컬럼: {top_missing}")
    top_stores = preprocess_top_stores(raw_data["top_stores"], monthly_sales, demo["top_stores"])

    location_missing = validate_columns(raw_data["location_analysis"], REQUIRED_COLUMNS["location_analysis"])
    if location_missing:
        messages.append(f"market_data.csv: 일부 컬럼이 부족해 monthly_sales 기준으로 재생성하거나 데모 데이터를 사용했습니다. 누락 컬럼: {location_missing}")
    location_analysis = preprocess_location_analysis(raw_data["location_analysis"], monthly_sales, demo["location_analysis"])

    cost_missing = validate_columns(raw_data["cost_structure"], REQUIRED_COLUMNS["cost_structure"])
    if cost_missing:
        messages.append(f"store_size_cost.csv: 필요한 컬럼이 부족하여 데모 데이터를 사용했습니다. 누락 컬럼: {cost_missing}")
    cost_structure = preprocess_cost_structure(raw_data["cost_structure"], demo["cost_structure"])

    marketing_missing = validate_columns(raw_data["marketing_effect"], REQUIRED_COLUMNS["marketing_effect"])
    if marketing_missing:
        messages.append(f"marketing_data.csv: 필요한 컬럼이 부족하여 데모 데이터를 사용했습니다. 누락 컬럼: {marketing_missing}")
    marketing_effect = preprocess_marketing_effect(raw_data["marketing_effect"], demo["marketing_effect"])

    processed = {
        "store_data": store_data,
        "monthly_sales": monthly_sales,
        "top_stores": top_stores,
        "location_analysis": location_analysis,
        "cost_structure": cost_structure,
        "marketing_effect": marketing_effect,
    }

    return processed, messages


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
    if row.empty:
        base_revenue = 74.49
    else:
        base_revenue = float(row["avg_revenue_million_krw"].iloc[0])

    size_multiplier = {
        10: 0.88,
        15: 1.00,
        20: 1.16,
    }.get(store_size, 1.00)

    expected_revenue = base_revenue * size_multiplier

    total_uplift_pct = 0.0
    marketing_cost = 0.0

    if selected_marketing:
        selected_df = marketing_effect[marketing_effect["strategy"].isin(selected_marketing)].copy()
        total_uplift_pct = selected_df["revenue_uplift_pct"].sum()
        marketing_cost = selected_df["monthly_cost_million_krw"].sum()

    total_uplift_pct = min(total_uplift_pct, 18.0)
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

    if net_profit <= 0:
        payback_period_months = math.inf
    else:
        payback_period_months = initial_investment / net_profit

    return {
        "expected_revenue": round(expected_revenue, 1),
        "fixed_cost": round(fixed_cost, 1),
        "net_profit": round(net_profit, 1),
        "initial_investment": round(initial_investment, 1),
        "payback_period_months": payback_period_months,
    }

# =========================================================
# 페이지 렌더링
# =========================================================
def render_home(kpis: dict[str, float | str]) -> None:
    st.markdown('<div class="main-title">Gelatico</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">감성 브랜딩과 데이터 기반 수익 분석을 결합한 프리미엄 젤라또 프랜차이즈 플랫폼</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="hero-box">
            <h3 style="margin-top:0;">프리미엄 디저트 창업, 감이 아니라 데이터로 판단하세요.</h3>
            <p style="margin-bottom:0;">
                Gelatico는 브랜드 스토리, 메뉴 경쟁력, 상권 차이, 예상 수익성까지 한 번에 검토할 수 있는
                프랜차이즈 창업 의사결정 플랫폼입니다.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("운영 매장 수", f"{kpis['store_count']}개")
    c2.metric("평균 월매출", format_million_krw(kpis["avg_revenue"]))
    c3.metric("최대 월매출", format_million_krw(kpis["max_revenue"]))
    c4.metric("최고 매장", str(kpis["top_store"]))

    st.write("")
    col1, col2 = st.columns([1.5, 1])

    with col1:
        st.subheader("왜 Gelatico인가")
        st.write(
            """
            Gelatico는 단순한 아이스크림 매장이 아니라,
            계절성과 감성 소비를 동시에 공략하는 프리미엄 디저트 브랜드입니다.
            여름 성수기 수요 상승 구조와 지역별 수요 차이를 데이터로 확인할 수 있어,
            창업 검토 단계에서 더 설득력 있는 판단이 가능합니다.
            """
        )

        st.markdown(
            """
            <div class="cta-box">
                <b>추천 탐색 순서</b><br>
                1) About에서 브랜드 이해<br>
                2) Menu에서 상품 경쟁력 확인<br>
                3) Dashboard에서 실제 데이터 확인<br>
                4) Simulation에서 내 조건으로 수익 예측
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.subheader("핵심 포인트")
        st.write("- 18개 매장 운영 데이터 반영")
        st.write("- 36개월 매출 흐름 분석")
        st.write("- 여름 성수기 수요 상승 반영")
        st.write("- 지역/입지 유형별 매출 차이 분석")
        st.write("- 마케팅 전략 포함 수익 시뮬레이션")


def render_about(kpis: dict[str, float | str], store_data: pd.DataFrame) -> None:
    st.title("About Gelatico")

    st.subheader("브랜드 스토리")
    st.write(
        """
        Gelatico는 '매일의 작은 휴식도 충분히 프리미엄할 수 있다'는 관점에서 출발한 브랜드입니다.
        고품질 원재료, 감성적인 공간, 시즌별 메뉴 운영을 결합해
        단순한 디저트 소비를 넘어 일상 속 경험 소비로 확장하는 것을 목표로 합니다.
        """
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("총 매장 수", f"{kpis['store_count']}개")
    c2.metric("평균 월매출", format_million_krw(kpis["avg_revenue"]))
    c3.metric("최고 성과 매장", str(kpis["top_store"]))

    st.subheader("핵심 차별화 요소")
    d1, d2, d3 = st.columns(3)

    with d1:
        st.markdown(
            """
            <div class="card">
                <h4>감성 브랜딩</h4>
                <p>프리미엄 디저트 브랜드 톤앤매너, 공간 경험, 시즌 한정 메뉴 운영</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d2:
        st.markdown(
            """
            <div class="card">
                <h4>계절성 대응력</h4>
                <p>여름 성수기 고매출 구조를 기본으로, 비성수기 보완 메뉴 전략 운영</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with d3:
        st.markdown(
            """
            <div class="card">
                <h4>데이터 기반 창업 판단</h4>
                <p>지역, 입지, 평수, 마케팅 전략까지 수익 분석에 반영</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.subheader("운영 네트워크")
    region_counts = store_data["region"].value_counts().reset_index()
    region_counts.columns = ["region", "store_count"]

    fig = px.bar(
        region_counts,
        x="region",
        y="store_count",
        text="store_count",
        title="지역별 매장 분포",
    )
    fig.update_layout(height=420)
    st.plotly_chart(fig, use_container_width=True)


def render_menu() -> None:
    st.title("Menu")

    st.subheader("시그니처 메뉴")
    cols = st.columns(3)

    for idx, item in enumerate(MENU_ITEMS):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="card">
                    <h4 style="margin-bottom:0.3rem;">{item['name']}</h4>
                    <div class="small-muted" style="margin-bottom:0.7rem;">{item['tag']}</div>
                    <p>{item['desc']}</p>
                    <b>{item['price']}</b>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.write("")
    st.subheader("시즌 운영 메뉴")
    seasonal_df = pd.DataFrame(SEASONAL_ITEMS)
    st.dataframe(seasonal_df, use_container_width=True, hide_index=True)

    st.info("시즌 메뉴는 객단가 상승, SNS 화제성 확보, 재방문 유도 측면에서 중요한 역할을 합니다.")


def render_process() -> None:
    st.title("Startup Process")
    st.subheader("8단계 창업 프로세스")

    process_df = pd.DataFrame(PROCESS_STEPS, columns=["단계", "프로세스", "설명"])
    st.dataframe(process_df, use_container_width=True, hide_index=True)

    st.markdown(
        """
        <div class="cta-box">
            <b>포인트</b><br>
            Gelatico는 상권 분석과 오픈 마케팅 단계를 강조합니다.
            단순 출점이 아니라, 입지 타당성과 초기 수요 형성을 함께 관리하는 구조입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(monthly_sales: pd.DataFrame, cost_structure: pd.DataFrame) -> None:
    st.title("Dashboard")

    st.subheader("필터")
    f1, f2, f3 = st.columns(3)

    available_regions = ["전체"] + sorted(monthly_sales["region"].dropna().unique().tolist())
    available_stores = ["전체"] + sorted(monthly_sales["store_name"].dropna().unique().tolist())
    available_locations = ["전체"] + sorted(monthly_sales["location_type"].dropna().unique().tolist())

    selected_region = f1.selectbox("지역", available_regions)
    selected_store = f2.selectbox("매장", available_stores)
    selected_location = f3.selectbox("입지 유형", available_locations)

    filtered = monthly_sales.copy()

    if selected_region != "전체":
        filtered = filtered[filtered["region"] == selected_region]
    if selected_store != "전체":
        filtered = filtered[filtered["store_name"] == selected_store]
    if selected_location != "전체":
        filtered = filtered[filtered["location_type"] == selected_location]

    if filtered.empty:
        st.error("선택한 조건에 해당하는 데이터가 없습니다.")
        return

    kpi_store_count = filtered["store_name"].nunique()
    kpi_avg = filtered["revenue_million_krw"].mean()
    kpi_max = filtered["revenue_million_krw"].max()
    kpi_top_store = filtered.groupby("store_name")["revenue_million_krw"].mean().sort_values(ascending=False).index[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 대상 매장 수", f"{kpi_store_count}개")
    c2.metric("평균 월매출", format_million_krw(kpi_avg))
    c3.metric("최대 월매출", format_million_krw(kpi_max))
    c4.metric("상위 매장", kpi_top_store)

    st.subheader("매장별 평균 매출 비교")
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
        labels={"store_name": "매장", "revenue_million_krw": "평균 월매출(만원)"},
        title="매장별 평균 월매출",
    )
    fig_bar.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_bar.update_layout(height=450, xaxis_tickangle=-30)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("상위 5개 매장 월별 매출 추이")
    top5_stores = (
        filtered.groupby("store_name")["revenue_million_krw"]
        .mean()
        .sort_values(ascending=False)
        .head(5)
        .index.tolist()
    )

    line_df = filtered[filtered["store_name"].isin(top5_stores)].copy()
    line_df = line_df.sort_values("month_date")

    fig_line = px.line(
        line_df,
        x="month_date",
        y="revenue_million_krw",
        color="store_name",
        markers=True,
        labels={"month_date": "월", "revenue_million_krw": "매출(만원)", "store_name": "매장"},
        title="상위 5개 매장 월별 매출 추이",
    )
    fig_line.update_layout(height=500)
    st.plotly_chart(fig_line, use_container_width=True)

    st.subheader("계절성 분석")
    season_df = (
        filtered.groupby("season", as_index=False)["revenue_million_krw"]
        .mean()
    )

    season_order = ["봄", "여름", "가을", "겨울"]
    season_df["season"] = pd.Categorical(season_df["season"], categories=season_order, ordered=True)
    season_df = season_df.sort_values("season")

    fig_season = px.bar(
        season_df,
        x="season",
        y="revenue_million_krw",
        text="revenue_million_krw",
        title="계절별 평균 매출",
        labels={"season": "계절", "revenue_million_krw": "평균 매출(만원)"},
    )
    fig_season.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig_season.update_layout(height=400)
    st.plotly_chart(fig_season, use_container_width=True)

    st.subheader("비용 구조")
    fig_pie = px.pie(
        cost_structure,
        names="cost_item",
        values="percentage",
        title="표준 비용 구조 비중",
        hole=0.4,
    )
    fig_pie.update_layout(height=450)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.subheader("원본 데이터 미리보기")
    preview_cols = ["month", "store_name", "region", "location_type", "revenue_million_krw"]
    st.dataframe(
        filtered[preview_cols].sort_values(["month", "store_name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )


def render_simulation(location_analysis: pd.DataFrame, marketing_effect: pd.DataFrame) -> None:
    st.title("Simulation")
    st.write("입지 유형, 매장 규모, 마케팅 전략을 바탕으로 예상 수익성을 계산합니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        location_options = sorted(location_analysis["location_type"].dropna().unique().tolist())
        if not location_options:
            location_options = LOCATION_ORDER

        location_type = st.selectbox("입지 유형", location_options)
        store_size = st.selectbox("매장 평수", [10, 15, 20], index=1)
        selected_marketing = st.multiselect(
            "적용할 마케팅 전략",
            options=marketing_effect["strategy"].tolist(),
            default=marketing_effect["strategy"].tolist()[:1],
        )

    results = run_simulation(
        location_type=location_type,
        store_size=store_size,
        selected_marketing=selected_marketing,
        location_analysis=location_analysis,
        marketing_effect=marketing_effect,
    )

    with col2:
        st.subheader("예상 결과")
        m1, m2 = st.columns(2)
        m3, m4 = st.columns(2)

        m1.metric("예상 월매출", format_million_krw(results["expected_revenue"]))
        m2.metric("월 고정비", format_million_krw(results["fixed_cost"]))
        m3.metric("예상 월순이익", format_million_krw(results["net_profit"]))
        m4.metric("초기 투자비", format_million_krw(results["initial_investment"]))

        if math.isinf(results["payback_period_months"]):
            st.error("현재 조건에서는 순이익이 충분하지 않아 투자금 회수기간 산정이 어렵습니다.")
        else:
            st.success(f"예상 투자금 회수기간: 약 {results['payback_period_months']:.1f}개월")

    st.subheader("시뮬레이션 해석")
    st.write(
        f"""
        - 선택한 입지 유형: **{location_type}**
        - 선택한 평수: **{store_size}평**
        - 적용 마케팅 전략 수: **{len(selected_marketing)}개**
        """
    )

    if selected_marketing:
        selected_df = marketing_effect[marketing_effect["strategy"].isin(selected_marketing)].copy()
        st.dataframe(selected_df, use_container_width=True, hide_index=True)

    st.info(
        "이 시뮬레이션은 의사결정 보조용 추정 모델입니다. 실제 출점 시에는 권리금, 임대 조건, 상권 경쟁도, 인건비 구조를 추가 검토해야 합니다."
    )

# =========================================================
# 메인
# =========================================================
def main() -> None:
    apply_custom_css()

    data, load_messages = load_data()

    monthly_sales = data["monthly_sales"]
    store_data = data["store_data"]
    cost_structure = data["cost_structure"]
    location_analysis = data["location_analysis"]
    marketing_effect = data["marketing_effect"]

    kpis = compute_kpis(monthly_sales)

    st.sidebar.title("Gelatico")
    st.sidebar.caption("Franchise Decision Platform")

    page = st.sidebar.radio(
        "페이지 이동",
        ["Home", "About", "Menu", "Process", "Dashboard", "Simulation"],
        index=0,
    )

    with st.sidebar.expander("데이터 로딩 상태", expanded=False):
        for msg in load_messages:
            st.write(f"- {msg}")

    st.sidebar.markdown("---")
    st.sidebar.write("**기본 기준 데이터**")
    st.sidebar.write("- 18 stores")
    st.sidebar.write("- 36 months (2023-01 ~ 2025-12)")
    st.sidebar.write("- Avg revenue: 7,449만원")
    st.sidebar.write("- Max revenue: 12,482만원")
    st.sidebar.write("- Top store: 제주점")

    try:
        if page == "Home":
            render_home(kpis)
        elif page == "About":
            render_about(kpis, store_data)
        elif page == "Menu":
            render_menu()
        elif page == "Process":
            render_process()
        elif page == "Dashboard":
            render_dashboard(monthly_sales, cost_structure)
        elif page == "Simulation":
            render_simulation(location_analysis, marketing_effect)
    except Exception as e:
        st.error("앱 렌더링 중 오류가 발생했습니다.")
        st.exception(e)

    st.markdown("---")
    st.caption("Gelatico demo platform | 브랜드 이해 + 상권/매출/수익성 데이터 기반 창업 의사결정")


if __name__ == "__main__":
    main()
