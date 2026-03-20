import os
from pathlib import Path
import math
import numpy as np
import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# Streamlit Page Config
# =========================================================
st.set_page_config(
    page_title="Gelatico | 프랜차이즈 창업 의사결정 플랫폼",
    page_icon="🍨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# Global Constants
# =========================================================
DATA_DIR = Path("data")

EXPECTED_FILES = {
    "store_data": DATA_DIR / "store_data.csv",
    "monthly_sales": DATA_DIR / "monthly_sales.csv",
    "top_stores": DATA_DIR / "top_stores.csv",
    "location_analysis": DATA_DIR / "location_analysis.csv",
    "cost_structure": DATA_DIR / "cost_structure.csv",
    "marketing_effect": DATA_DIR / "marketing_effect.csv",
}

REQUIRED_COLUMNS = {
    "store_data": ["store_name", "region", "location_type", "store_size_pyeong", "opening_month"],
    "monthly_sales": ["month", "store_name", "region", "location_type", "revenue_million_krw"],
    "top_stores": ["store_name", "avg_revenue_million_krw", "rank"],
    "location_analysis": ["location_type", "avg_revenue_million_krw", "foot_traffic_index"],
    "cost_structure": ["cost_item", "percentage"],
    "marketing_effect": ["strategy", "revenue_uplift_pct", "monthly_cost_million_krw"],
}

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

LOCATION_ORDER = ["오피스", "대학가", "주거", "관광"]

# =========================================================
# Styling
# =========================================================
def apply_custom_css() -> None:
    """한글 폰트가 최대한 안정적으로 보이도록 간단한 CSS 적용"""
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
# Utility Functions
# =========================================================
def safe_read_csv(file_path: Path) -> pd.DataFrame | None:
    """
    CSV 파일 읽기.
    UTF-8, UTF-8-SIG, CP949 순서로 시도.
    """
    if not file_path.exists():
        return None

    encodings = ["utf-8", "utf-8-sig", "cp949"]
    for enc in encodings:
        try:
            return pd.read_csv(file_path, encoding=enc)
        except Exception:
            continue
    return None


def validate_columns(df: pd.DataFrame, required_cols: list[str], df_name: str) -> bool:
    """
    필수 컬럼 존재 여부 확인.
    누락되면 사용자에게 경고 표시.
    """
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.warning(
            f"'{df_name}' 데이터에 필요한 컬럼이 없습니다: {missing} "
            f"→ 데모 데이터 또는 일부 기능 제한으로 동작합니다."
        )
        return False
    return True


def format_million_krw(value: float) -> str:
    """백만원 단위 숫자를 보기 좋게 포맷"""
    return f"{value:,.0f}만원"


def month_to_season(month_int: int) -> str:
    if month_int in [12, 1, 2]:
        return "겨울"
    if month_int in [3, 4, 5]:
        return "봄"
    if month_int in [6, 7, 8]:
        return "여름"
    return "가을"

# =========================================================
# Demo Data
# =========================================================
def create_demo_data() -> dict[str, pd.DataFrame]:
    """
    실제 CSV가 없어도 앱이 바로 실행될 수 있도록
    18개 매장, 2023-01 ~ 2025-12 (36개월) 기준의 데모 데이터 생성
    """
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
        "제주점": 18.0,   # 최고 매장
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

    # 여름 성수기 반영
    seasonality = {
        1: 0.92, 2: 0.95, 3: 1.00, 4: 1.03, 5: 1.05, 6: 1.12,
        7: 1.22, 8: 1.20, 9: 1.06, 10: 1.00, 11: 0.96, 12: 0.98
    }

    for i, store in store_data.iterrows():
        base = base_by_location[store["location_type"]] + store_bonus.get(store["store_name"], 0.0)

        for dt in months:
            trend_factor = 1 + ((dt.year - 2023) * 0.03)  # 연 3% 성장
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

    # 평균 매출을 74.49에 맞추기 위해 스케일 조정
    current_avg = monthly_sales["revenue_million_krw"].mean()
    target_avg = 74.49
    scaling = target_avg / current_avg
    monthly_sales["revenue_million_krw"] = (monthly_sales["revenue_million_krw"] * scaling).round(1)

    # 최대 매출을 124.82 근처로 맞춤
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
# Data Loading
# =========================================================
@st.cache_data
def load_data() -> tuple[dict[str, pd.DataFrame], list[str]]:
    """
    CSV가 있으면 CSV 우선 사용.
    없거나 문제 있으면 데모 데이터 사용.
    반환:
        - 데이터 딕셔너리
        - 상태 메시지 리스트
    """
    demo_data = create_demo_data()
    loaded_data = {}
    messages = []

    for key, path in EXPECTED_FILES.items():
        df = safe_read_csv(path)
        if df is None:
            loaded_data[key] = demo_data[key]
            messages.append(f"{path.name}: 파일이 없어 데모 데이터를 사용합니다.")
            continue

        is_valid = validate_columns(df, REQUIRED_COLUMNS[key], path.name)
        if not is_valid:
            loaded_data[key] = demo_data[key]
            messages.append(f"{path.name}: 컬럼 문제로 데모 데이터를 사용합니다.")
            continue

        loaded_data[key] = df
        messages.append(f"{path.name}: 정상 로드 완료")

    # 타입 정리
    if "monthly_sales" in loaded_data:
        monthly = loaded_data["monthly_sales"].copy()
        monthly["revenue_million_krw"] = pd.to_numeric(monthly["revenue_million_krw"], errors="coerce")
        monthly["month_date"] = pd.to_datetime(monthly["month"], format="%Y-%m", errors="coerce")
        monthly["month_num"] = monthly["month_date"].dt.month
        monthly["season"] = monthly["month_num"].apply(lambda x: month_to_season(int(x)) if pd.notnull(x) else "기타")
        loaded_data["monthly_sales"] = monthly

    return loaded_data, messages


def compute_kpis(monthly_sales: pd.DataFrame) -> dict[str, float | str]:
    """
    핵심 KPI 계산
    """
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
# Simulation Logic
# =========================================================
def run_simulation(
    location_type: str,
    store_size: int,
    selected_marketing: list[str],
    location_analysis: pd.DataFrame,
    marketing_effect: pd.DataFrame,
) -> dict[str, float]:
    """
    창업 시뮬레이션 계산 로직
    단위:
      - 매출/비용/이익/투자비: 백만원(만원 단위 표기용)
    """
    # 1) 입지 평균 매출 기준
    row = location_analysis[location_analysis["location_type"] == location_type]
    if row.empty:
        base_revenue = 74.49
    else:
        base_revenue = float(row["avg_revenue_million_krw"].iloc[0])

    # 2) 평수별 보정
    size_multiplier = {
        10: 0.88,
        15: 1.00,
        20: 1.16,
    }.get(store_size, 1.00)

    expected_revenue = base_revenue * size_multiplier

    # 3) 마케팅 효과 합산
    total_uplift_pct = 0.0
    marketing_cost = 0.0

    if selected_marketing:
        selected_df = marketing_effect[marketing_effect["strategy"].isin(selected_marketing)].copy()
        total_uplift_pct = selected_df["revenue_uplift_pct"].sum()
        marketing_cost = selected_df["monthly_cost_million_krw"].sum()

    # 과도한 중첩 효과 방지
    total_uplift_pct = min(total_uplift_pct, 18.0)
    expected_revenue *= (1 + total_uplift_pct / 100)

    # 4) 비용 가정
    # 원재료비: 매출의 28%
    cogs = expected_revenue * 0.28

    # 고정비: 임대료 + 인건비 + 공과금 + 기타
    rent_by_size = {10: 11.0, 15: 14.0, 20: 18.0}
    labor_by_size = {10: 13.0, 15: 16.0, 20: 20.0}
    utilities_by_size = {10: 3.5, 15: 4.2, 20: 5.0}

    # 입지 유형에 따른 임대료 차등
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

    # 5) 순이익
    net_profit = expected_revenue - cogs - fixed_cost

    # 6) 초기 투자비
    # 평수 기반 + 설비 + 가맹/교육 + 초도물품
    fitout_per_pyeong = 2.6  # 평당 백만원
    interior_cost = store_size * fitout_per_pyeong
    equipment_cost = {10: 32.0, 15: 38.0, 20: 45.0}[store_size]
    franchise_fee = 12.0
    training_fee = 4.0
    opening_inventory = 6.0

    initial_investment = interior_cost + equipment_cost + franchise_fee + training_fee + opening_inventory

    # 7) 회수기간
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
# Page Render Functions
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
            여름 피크 시즌 매출 상승 구조와 지역별 수요 차이를 데이터로 확인할 수 있어,
            창업 검토 단계에서 훨씬 설득력 있는 판단이 가능합니다.
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
        st.write("- 2023-01 ~ 2025-12, 36개월 매출 흐름 분석")
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
    diff1, diff2, diff3 = st.columns(3)
    with diff1:
        st.markdown(
            """
            <div class="card">
                <h4>감성 브랜딩</h4>
                <p>프리미엄 디저트 브랜드 톤앤매너, 공간 경험, 시즌 한정 메뉴 운영</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with diff2:
        st.markdown(
            """
            <div class="card">
                <h4>계절성 대응력</h4>
                <p>여름 성수기 고매출 구조를 기본으로, 비성수기 보완 메뉴 전략 운영</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with diff3:
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

    st.write("")
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


def render_dashboard(
    monthly_sales: pd.DataFrame,
    cost_structure: pd.DataFrame,
) -> None:
    st.title("Dashboard")

    # -----------------------------------------------------
    # Filters
    # -----------------------------------------------------
    st.subheader("필터")
    f1, f2, f3 = st.columns(3)

    available_regions = ["전체"] + sorted(monthly_sales["region"].dropna().unique().tolist())
    available_stores = ["전체"] + sorted(monthly_sales["store_name"].dropna().unique().tolist())
    available_locations = ["전체"] + [x for x in LOCATION_ORDER if x in monthly_sales["location_type"].unique().tolist()]

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

    # -----------------------------------------------------
    # KPI
    # -----------------------------------------------------
    kpi_store_count = filtered["store_name"].nunique()
    kpi_avg = filtered["revenue_million_krw"].mean()
    kpi_max = filtered["revenue_million_krw"].max()
    kpi_top_store = filtered.groupby("store_name")["revenue_million_krw"].mean().sort_values(ascending=False).index[0]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("분석 대상 매장 수", f"{kpi_store_count}개")
    c2.metric("평균 월매출", format_million_krw(kpi_avg))
    c3.metric("최대 월매출", format_million_krw(kpi_max))
    c4.metric("상위 매장", kpi_top_store)

    # -----------------------------------------------------
    # Bar Chart: Store Comparison
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Line Chart: Monthly Revenue Trends (Top 5)
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Seasonality Insight
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Pie Chart: Cost Structure
    # -----------------------------------------------------
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

    # -----------------------------------------------------
    # Data Table
    # -----------------------------------------------------
    st.subheader("원본 데이터 미리보기")
    preview_cols = ["month", "store_name", "region", "location_type", "revenue_million_krw"]
    st.dataframe(
        filtered[preview_cols].sort_values(["month", "store_name"], ascending=[False, True]),
        use_container_width=True,
        hide_index=True,
    )


def render_simulation(
    location_analysis: pd.DataFrame,
    marketing_effect: pd.DataFrame,
) -> None:
    st.title("Simulation")
    st.write("입지 유형, 매장 규모, 마케팅 전략을 바탕으로 예상 수익성을 계산합니다.")

    col1, col2 = st.columns([1, 1])

    with col1:
        location_type = st.selectbox("입지 유형", LOCATION_ORDER, index=0)
        store_size = st.selectbox("매장 평수", [10, 15, 20], index=1)
        selected_marketing = st.multiselect(
            "적용할 마케팅 전략",
            options=marketing_effect["strategy"].tolist(),
            default=["인스타 광고"],
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

    st.write("")
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
# Main App
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

    # Sidebar
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

    # Page Routing
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

    # Footer
    st.markdown("---")
    st.caption(
        "Gelatico demo platform | 브랜드 이해 + 상권/매출/수익성 데이터 기반 창업 의사결정"
    )


if __name__ == "__main__":
    main()
