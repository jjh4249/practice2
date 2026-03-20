import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st


# =========================================================
# Page config
# =========================================================
st.set_page_config(
    page_title="Gelatico Franchise Platform",
    page_icon="🍦",
    layout="wide",
)


# =========================================================
# Basic styling
# =========================================================
st.markdown(
    """
    <style>
    .main-title {
        font-size: 2.4rem;
        font-weight: 800;
        color: #1B3A6B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #4A5568;
        margin-bottom: 1.5rem;
    }
    .section-title {
        font-size: 1.45rem;
        font-weight: 700;
        color: #1B3A6B;
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
    }
    .card {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.8rem;
    }
    .highlight {
        color: #1B3A6B;
        font-weight: 700;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# Paths
# =========================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

FILE_MAP = {
    "store_data": DATA_DIR / "store_data.csv",
    "monthly_sales": DATA_DIR / "monthly_sales.csv",
    "top_stores": DATA_DIR / "top_stores.csv",
    "location_analysis": DATA_DIR / "location_analysis.csv",
    "cost_structure": DATA_DIR / "cost_structure.csv",
    "marketing_effect": DATA_DIR / "marketing_effect.csv",
}


# =========================================================
# Helpers
# =========================================================
def show_header(title: str, subtitle: str = "") -> None:
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)


def read_csv_safe(path: Path, file_label: str) -> pd.DataFrame:
    """Read CSV safely with friendly error messages."""
    if not path.exists():
        st.error(f"[파일 없음] {file_label}: {path}")
        st.info("data 폴더 안에 CSV가 있는지, 파일명이 정확한지 확인하세요.")
        st.stop()

    try:
        return pd.read_csv(path, encoding="utf-8-sig")
    except Exception as e:
        st.error(f"[읽기 실패] {file_label}: {e}")
        st.stop()


def normalize_text_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df


def clean_numeric_value(value):
    """
    Convert values like:
    '7,449만원', '80만원', '+12%', '15,000명', '약 14개월', '15~20평'
    into numeric when possible.
    """
    if pd.isna(value):
        return None

    if isinstance(value, (int, float)):
        return value

    text = str(value).strip()
    if text == "":
        return None

    # Range like "2800~4500" or "15~20평" -> use average
    if "~" in text:
        left, right = text.split("~", 1)
        left_num = extract_first_number(left)
        right_num = extract_first_number(right)
        if left_num is not None and right_num is not None:
            return (left_num + right_num) / 2

    num = extract_first_number(text)
    return num


def extract_first_number(text: str):
    chars = []
    dot_used = False
    found = False

    for ch in text.replace(",", ""):
        if ch.isdigit():
            chars.append(ch)
            found = True
        elif ch == "." and not dot_used:
            chars.append(ch)
            dot_used = True
            found = True
        elif found:
            break

    if not chars:
        return None

    try:
        return float("".join(chars))
    except ValueError:
        return None


def require_columns(df: pd.DataFrame, required: list[str], file_label: str) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(
            f"[컬럼 누락] {file_label}에 필요한 컬럼이 없습니다.\n\n"
            f"- 필요한 컬럼: {required}\n"
            f"- 누락 컬럼: {missing}\n"
            f"- 현재 컬럼: {list(df.columns)}"
        )
        st.stop()


def parse_store_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)

    required = [
        "매장ID",
        "매장명",
        "지역",
        "상권 유형",
        "점포 규모(평수)",
        "오픈일",
        "월매출(만원)",
        "객단가(원)",
        "재방문율(%)",
    ]
    require_columns(df, required, "store_data.csv")

    numeric_cols = ["점포 규모(평수)", "월매출(만원)", "객단가(원)", "재방문율(%)"]
    for col in numeric_cols:
        df[col] = df[col].apply(clean_numeric_value)

    df["오픈일"] = pd.to_datetime(df["오픈일"], errors="coerce")
    return df


def parse_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expected wide format:
    년도-월 | 젤라또 강남점 | 젤라또 여의도점 | ...
    """
    df = normalize_text_columns(df)

    if "년도-월" not in df.columns:
        st.error(
            "[컬럼 누락] monthly_sales.csv에는 첫 번째 컬럼으로 '년도-월'이 필요합니다."
        )
        st.stop()

    store_cols = [c for c in df.columns if c != "년도-월"]
    if not store_cols:
        st.error("[데이터 오류] monthly_sales.csv에 매장 컬럼이 없습니다.")
        st.stop()

    for col in store_cols:
        df[col] = df[col].apply(clean_numeric_value)

    return df


def parse_top_stores(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)
    required = ["매장명", "총매출(만원)", "월평균매출(만원)"]
    require_columns(df, required, "top_stores.csv")

    for col in ["총매출(만원)", "월평균매출(만원)"]:
        df[col] = df[col].apply(clean_numeric_value)
    return df


def parse_location_analysis(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)
    required = [
        "상권 유형",
        "일평균 유동인구(명)",
        "주 고객층",
        "경쟁 점포 수",
        "평균 임대료(만원)",
        "추천 규모",
        "예상 월매출(만원)",
    ]
    require_columns(df, required, "location_analysis.csv")

    for col in ["일평균 유동인구(명)", "평균 임대료(만원)", "예상 월매출(만원)"]:
        df[col] = df[col].apply(clean_numeric_value)

    return df


def parse_cost_structure(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)
    required = ["비교 항목", "소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]
    require_columns(df, required, "cost_structure.csv")

    value_cols = ["소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]
    for col in value_cols:
        df[col] = df[col].apply(clean_numeric_value)

    return df


def parse_marketing_effect(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_text_columns(df)
    required = ["전략명", "월 예산(만원)", "유입 증가율", "매출 상승률", "추천 상권"]
    require_columns(df, required, "marketing_effect.csv")

    df["월 예산(만원)"] = df["월 예산(만원)"].apply(clean_numeric_value)
    df["유입 증가율"] = df["유입 증가율"].apply(clean_numeric_value)
    df["매출 상승률"] = df["매출 상승률"].apply(clean_numeric_value)
    return df


@st.cache_data
def load_all_data():
    raw_store = read_csv_safe(FILE_MAP["store_data"], "store_data.csv")
    raw_monthly = read_csv_safe(FILE_MAP["monthly_sales"], "monthly_sales.csv")
    raw_top = read_csv_safe(FILE_MAP["top_stores"], "top_stores.csv")
    raw_location = read_csv_safe(FILE_MAP["location_analysis"], "location_analysis.csv")
    raw_cost = read_csv_safe(FILE_MAP["cost_structure"], "cost_structure.csv")
    raw_marketing = read_csv_safe(FILE_MAP["marketing_effect"], "marketing_effect.csv")

    store_df = parse_store_data(raw_store)
    monthly_df = parse_monthly_sales(raw_monthly)
    top_df = parse_top_stores(raw_top)
    location_df = parse_location_analysis(raw_location)
    cost_df = parse_cost_structure(raw_cost)
    marketing_df = parse_marketing_effect(raw_marketing)

    return store_df, monthly_df, top_df, location_df, cost_df, marketing_df


def format_manwon(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{int(round(value)):,}만원"


def format_people(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{int(round(value)):,}명"


def get_kpis(store_df: pd.DataFrame, monthly_df: pd.DataFrame) -> dict:
    store_count = len(store_df)
    avg_revenue = store_df["월매출(만원)"].mean()

    monthly_numeric = monthly_df.drop(columns=["년도-월"])
    max_revenue = monthly_numeric.max().max()

    # Identify top store and max point
    stacked = monthly_df.melt(id_vars="년도-월", var_name="매장명", value_name="매출(만원)")
    stacked["매출(만원)"] = stacked["매출(만원)"].apply(clean_numeric_value)
    idx = stacked["매출(만원)"].idxmax()
    top_record = stacked.loc[idx]

    return {
        "store_count": store_count,
        "avg_revenue": avg_revenue,
        "max_revenue": max_revenue,
        "max_store": top_record["매장명"],
        "max_month": top_record["년도-월"],
    }


def make_store_bar_chart(store_df: pd.DataFrame):
    sorted_df = store_df.sort_values("월매출(만원)", ascending=False)
    fig = px.bar(
        sorted_df,
        x="매장명",
        y="월매출(만원)",
        color="상권 유형",
        title="매장별 월매출 비교",
        text="월매출(만원)",
    )
    fig.update_layout(xaxis_title="", yaxis_title="월매출(만원)")
    return fig


def make_top_store_line_chart(monthly_df: pd.DataFrame, top_df: pd.DataFrame):
    top_store_names = top_df["매장명"].tolist()
    available_top_stores = [s for s in top_store_names if s in monthly_df.columns]

    line_df = monthly_df[["년도-월"] + available_top_stores].copy()
    line_long = line_df.melt(id_vars="년도-월", var_name="매장명", value_name="매출(만원)")

    fig = px.line(
        line_long,
        x="년도-월",
        y="매출(만원)",
        color="매장명",
        markers=True,
        title="상위 5개 매장 월별 매출 추이",
    )
    fig.update_layout(xaxis_title="년도-월", yaxis_title="매출(만원)")
    return fig


def make_cost_pie_chart(cost_df: pd.DataFrame, size_label: str):
    col_map = {
        "소형(10평)": "소형(10평)(만원)",
        "중형(15평)": "중형(15평)(만원)",
        "대형(20평)": "대형(20평)(만원)",
    }
    selected_col = col_map[size_label]

    pie_df = cost_df.copy()
    pie_df = pie_df[~pie_df["비교 항목"].isin(["총 초기 투자비", "예상 월매출", "예상 투자 회수"])]
    pie_df = pie_df[["비교 항목", selected_col]].rename(columns={selected_col: "금액(만원)"})

    fig = px.pie(
        pie_df,
        names="비교 항목",
        values="금액(만원)",
        title=f"{size_label} 기준 초기 비용 구조",
    )
    return fig


def get_initial_investment(cost_df: pd.DataFrame, size_value: int) -> float:
    col_map = {
        10: "소형(10평)(만원)",
        15: "중형(15평)(만원)",
        20: "대형(20평)(만원)",
    }
    selected_col = col_map[size_value]
    row = cost_df[cost_df["비교 항목"] == "총 초기 투자비"]

    if row.empty:
        # Fallback: sum item rows except summary rows
        temp = cost_df[~cost_df["비교 항목"].isin(["총 초기 투자비", "예상 월매출", "예상 투자 회수"])]
        return float(temp[selected_col].sum())

    return float(row[selected_col].iloc[0])


def simulate_business(
    location_df: pd.DataFrame,
    cost_df: pd.DataFrame,
    marketing_df: pd.DataFrame,
    location_type: str,
    store_size: int,
    selected_marketing: list[str],
) -> dict:
    """
    Realistic but simple business simulation.
    """
    row = location_df[location_df["상권 유형"] == location_type]
    if row.empty:
        return {
            "expected_revenue": 0,
            "fixed_cost": 0,
            "net_profit": 0,
            "initial_investment": 0,
            "payback_period": None,
        }

    base_revenue = float(row["예상 월매출(만원)"].iloc[0])
    rent = float(row["평균 임대료(만원)"].iloc[0])

    # Size multiplier
    size_multiplier = {
        10: 0.82,
        15: 1.00,
        20: 1.18,
    }[store_size]

    revenue = base_revenue * size_multiplier

    # Marketing effects (compound lift but capped)
    marketing_cost = 0.0
    total_revenue_lift = 0.0

    if selected_marketing:
        selected_rows = marketing_df[marketing_df["전략명"].isin(selected_marketing)]
        marketing_cost = selected_rows["월 예산(만원)"].sum()
        total_revenue_lift = selected_rows["매출 상승률"].sum() / 100.0
        total_revenue_lift = min(total_revenue_lift, 0.45)  # cap at +45%

    revenue *= (1 + total_revenue_lift)

    # Fixed cost model
    # rent + labor + ingredient + utilities + marketing
    labor_cost = {10: 380, 15: 520, 20: 700}[store_size]
    ingredient_cost = revenue * 0.32
    utilities_misc = {10: 120, 15: 160, 20: 220}[store_size]

    fixed_cost = rent + labor_cost + ingredient_cost + utilities_misc + marketing_cost
    net_profit = revenue - fixed_cost

    initial_investment = get_initial_investment(cost_df, store_size)

    if net_profit > 0:
        payback_period = initial_investment / net_profit
    else:
        payback_period = None

    return {
        "expected_revenue": revenue,
        "fixed_cost": fixed_cost,
        "net_profit": net_profit,
        "initial_investment": initial_investment,
        "payback_period": payback_period,
    }


# =========================================================
# Load data
# =========================================================
store_df, monthly_df, top_df, location_df, cost_df, marketing_df = load_all_data()
kpi = get_kpis(store_df, monthly_df)


# =========================================================
# Sidebar
# =========================================================
st.sidebar.title("Gelatico Navigation")
page = st.sidebar.radio(
    "페이지 선택",
    ["Home", "About", "Menu", "Process", "Dashboard", "Simulation"],
)

st.sidebar.markdown("---")
st.sidebar.caption("Gelatico Franchise Decision Platform")


# =========================================================
# Pages
# =========================================================
def render_home():
    show_header(
        "🍦 GELATICO",
        "Emotional branding + data-driven franchise decision platform",
    )

    st.markdown(
        """
        <div class="card">
        <span class="highlight">이미 사랑받는 젤라또 브랜드, 이제 당신의 매장으로 이어집니다.</span><br>
        Gelatico는 감성적인 브랜드 경험과 실제 가상 데이터 기반 수익 분석을 결합한
        프랜차이즈 창업 안내 플랫폼입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("운영 매장 수", f"{kpi['store_count']}개")
    c2.metric("평균 월매출", format_manwon(kpi["avg_revenue"]))
    c3.metric("최고 월매출", format_manwon(kpi["max_revenue"]))

    st.markdown("### Why Gelatico?")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(
            """
            <div class="card">
            <b>높은 브랜드 신뢰</b><br>
            전국 18개 매장 운영과 축적된 상권 데이터를 바탕으로 창업 판단을 지원합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card">
            <b>검증된 메뉴 경쟁력</b><br>
            시즌성과 프리미엄 포지셔닝이 가능한 젤라또 메뉴 구성으로 차별화를 만듭니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col3:
        st.markdown(
            """
            <div class="card">
            <b>데이터 기반 의사결정</b><br>
            상권, 규모, 마케팅 전략에 따라 예상 수익과 투자 회수 기간을 시뮬레이션합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("### Quick Actions")
    a1, a2 = st.columns(2)
    with a1:
        if st.button("창업 데이터 보기"):
            st.info("왼쪽 사이드바에서 Dashboard 페이지로 이동하세요.")
    with a2:
        if st.button("수익 시뮬레이션 해보기"):
            st.info("왼쪽 사이드바에서 Simulation 페이지로 이동하세요.")


def render_about():
    show_header("About Gelatico", "브랜드 스토리와 핵심 경쟁력")

    st.markdown("### 브랜드 소개")
    st.write(
        """
        Gelatico는 이탈리아 젤라또의 프리미엄 감성과 국내 상권 데이터 기반 운영 전략을 결합한
        가상의 프랜차이즈 브랜드입니다. 브랜드 목표는 단순한 디저트 판매가 아니라,
        입지와 계절성에 맞는 운영 전략으로 창업 성공 확률을 높이는 것입니다.
        """
    )

    st.markdown("### 핵심 지표")
    col1, col2, col3 = st.columns(3)
    col1.metric("운영 매장", "18개")
    col2.metric("평균 월매출", "7,449만원")
    col3.metric("최고 월매출", "12,482만원")

    tourism_avg = store_df.loc[store_df["상권 유형"] == "관광", "월매출(만원)"].mean()
    st.metric("관광 상권 평균 월매출", format_manwon(tourism_avg))

    st.markdown("### 차별점")
    st.write("- 이탈리아 감성의 프리미엄 브랜드 톤")
    st.write("- 계절성에 맞는 메뉴 운영 전략")
    st.write("- 상권별 수익성 데이터 기반 창업 판단")
    st.write("- 초기 투자비와 회수 기간까지 고려한 실전형 플랫폼")


def render_menu():
    show_header("Menu", "대표 메뉴와 시즌 구성")

    menu_items = [
        ("피스타치오 젤라또", "진한 견과 풍미와 부드러운 질감", "베스트셀러"),
        ("스트라치아텔라", "밀크 젤라또와 초콜릿 칩의 클래식 조합", "시그니처"),
        ("망고 소르베", "상큼한 과일 베이스의 여름 시즌 인기 메뉴", "여름 추천"),
        ("티라미수 젤라또", "디저트 감성을 강화한 프리미엄 메뉴", "프리미엄"),
        ("말차 라떼 젤라또", "쌉싸름한 풍미로 성인 고객 선호도 높음", "트렌디"),
    ]

    cols = st.columns(2)
    for i, (name, desc, badge) in enumerate(menu_items):
        with cols[i % 2]:
            st.markdown(
                f"""
                <div class="card">
                <b>{name}</b><br>
                {desc}<br><br>
                <span class="highlight">{badge}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.markdown("### 시즌 한정 메뉴")
    season_df = pd.DataFrame(
        {
            "시즌": ["봄", "여름", "가을", "겨울"],
            "대표 메뉴": ["딸기 요거트", "레몬 바질 소르베", "밤 티라미수", "초코 헤이즐넛"],
            "특징": [
                "산뜻하고 부드러운 맛",
                "청량감과 상큼함 강조",
                "깊은 풍미와 디저트 감성",
                "진한 단맛과 겨울 한정 테마",
            ],
        }
    )
    st.dataframe(season_df, use_container_width=True)


def render_process():
    show_header("Startup Process", "8-step franchise onboarding process")

    process_df = pd.DataFrame(
        {
            "단계": [1, 2, 3, 4, 5, 6, 7, 8],
            "단계명": [
                "창업 문의",
                "브랜드 상담",
                "상권 분석",
                "점포 규모 산정",
                "가맹 계약",
                "인테리어/설비",
                "교육/운영 준비",
                "오픈 및 사후관리",
            ],
            "주요 내용": [
                "온라인 폼 또는 전화로 초기 관심 접수",
                "담당자와 1:1 상담 및 방향성 협의",
                "유동인구·경쟁점포·고객층 분석",
                "10/15/20평 기준 비용 및 수익 구조 확정",
                "가맹 조건 검토 후 계약 체결",
                "브랜드 가이드에 따른 시공 및 설비 구축",
                "제조·POS·CS 교육 진행",
                "그랜드 오픈 후 밀착 운영 지원",
            ],
            "소요 기간": ["1일", "1주", "2주", "1주", "1주", "4~6주", "2주", "지속"],
        }
    )

    st.dataframe(process_df, use_container_width=True)


def render_dashboard():
    show_header("Revenue Dashboard", "매출 데이터 기반 핵심 분석")

    # -------------------------
    # Filters
    # -------------------------
    st.markdown("### 필터")
    f1, f2, f3 = st.columns(3)

    regions = ["전체"] + sorted(store_df["지역"].dropna().unique().tolist())
    categories = ["전체"] + sorted(store_df["상권 유형"].dropna().unique().tolist())
    stores = ["전체"] + sorted(store_df["매장명"].dropna().unique().tolist())

    selected_region = f1.selectbox("지역", regions)
    selected_category = f2.selectbox("상권 유형", categories)
    selected_store = f3.selectbox("매장", stores)

    filtered_store = store_df.copy()

    if selected_region != "전체":
        filtered_store = filtered_store[filtered_store["지역"] == selected_region]
    if selected_category != "전체":
        filtered_store = filtered_store[filtered_store["상권 유형"] == selected_category]
    if selected_store != "전체":
        filtered_store = filtered_store[filtered_store["매장명"] == selected_store]

    if filtered_store.empty:
        st.warning("선택한 조건에 해당하는 매장이 없습니다.")
        return

    # -------------------------
    # KPI
    # -------------------------
    st.markdown("### KPI")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("매장 수", len(filtered_store))
    c2.metric("평균 월매출", format_manwon(filtered_store["월매출(만원)"].mean()))
    c3.metric("최고 월매출", format_manwon(kpi["max_revenue"]))
    tourism_avg = store_df.loc[store_df["상권 유형"] == "관광", "월매출(만원)"].mean()
    c4.metric("관광 상권 평균", format_manwon(tourism_avg))

    # -------------------------
    # Charts
    # -------------------------
    st.markdown("### 차트")

    tab1, tab2, tab3, tab4 = st.tabs(
        ["매장별 비교", "상위 매장 추이", "비용 구조", "기본 데이터"]
    )

    with tab1:
        fig_bar = make_store_bar_chart(filtered_store)
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        fig_line = make_top_store_line_chart(monthly_df, top_df)
        st.plotly_chart(fig_line, use_container_width=True)
        st.caption("여름철(6~8월) 성수기 구간에서 상위권 매장의 매출 상승이 뚜렷하게 나타나도록 설계됨.")

    with tab3:
        size_option = st.selectbox("비용 구조 기준 규모 선택", ["소형(10평)", "중형(15평)", "대형(20평)"])
        fig_pie = make_cost_pie_chart(cost_df, size_option)
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab4:
        st.dataframe(filtered_store, use_container_width=True)

    st.markdown("### 상위 매장 요약")
    st.dataframe(top_df, use_container_width=True)


def render_simulation():
    show_header("Startup Simulation", "상권·규모·마케팅 전략에 따른 예상 수익 계산")

    st.write("아래 조건을 선택하면 예상 월매출, 고정비, 순이익, 초기 투자비, 회수 기간을 계산합니다.")

    col1, col2 = st.columns(2)

    with col1:
        location_type = st.selectbox(
            "상권 유형 선택",
            location_df["상권 유형"].dropna().unique().tolist(),
        )

        store_size = st.selectbox(
            "점포 규모 선택",
            [10, 15, 20],
            format_func=lambda x: f"{x}평",
        )

    with col2:
        marketing_options = marketing_df["전략명"].dropna().unique().tolist()
        selected_marketing = st.multiselect(
            "마케팅 전략 선택",
            marketing_options,
        )

    result = simulate_business(
        location_df=location_df,
        cost_df=cost_df,
        marketing_df=marketing_df,
        location_type=location_type,
        store_size=store_size,
        selected_marketing=selected_marketing,
    )

    st.markdown("### 시뮬레이션 결과")
    r1, r2, r3, r4, r5 = st.columns(5)

    r1.metric("예상 월매출", format_manwon(result["expected_revenue"]))
    r2.metric("예상 고정비", format_manwon(result["fixed_cost"]))
    r3.metric("예상 순이익", format_manwon(result["net_profit"]))
    r4.metric("초기 투자비", format_manwon(result["initial_investment"]))

    if result["payback_period"] is None:
        payback_text = "회수 불가"
    else:
        payback_text = f"{result['payback_period']:.1f}개월"
    r5.metric("예상 회수 기간", payback_text)

    st.markdown("### 계산 로직 요약")
    st.write("- 상권별 예상 월매출을 기준값으로 사용")
    st.write("- 점포 규모에 따라 매출 배율 적용")
    st.write("- 선택한 마케팅 전략의 매출 상승률을 합산 적용 (최대 45%)")
    st.write("- 고정비 = 임대료 + 인건비 + 재료비 + 공과잡비 + 마케팅 비용")
    st.write("- 순이익이 0 이하이면 투자 회수 기간은 계산하지 않음")

    # Supporting tables
    with st.expander("상권 분석 데이터 보기"):
        st.dataframe(location_df, use_container_width=True)

    with st.expander("점포 규모별 초기 비용 보기"):
        st.dataframe(cost_df, use_container_width=True)

    with st.expander("마케팅 전략별 효과 보기"):
        st.dataframe(marketing_df, use_container_width=True)


# =========================================================
# Router
# =========================================================
if page == "Home":
    render_home()
elif page == "About":
    render_about()
elif page == "Menu":
    render_menu()
elif page == "Process":
    render_process()
elif page == "Dashboard":
    render_dashboard()
elif page == "Simulation":
    render_simulation()
