from pathlib import Path
import pandas as pd
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="젤라티코 창업 분석 플랫폼",
    page_icon="🍦",
    layout="wide",
)

st.markdown(
    """
    <style>
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR",
                     "Nanum Gothic", Arial, sans-serif !important;
    }
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1B3A6B;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .card {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 경로 설정
# =========================================================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"

# 네 실제 파일명 기준
FILE_CANDIDATES = {
    "store_data": ["store_data.csv"],
    "monthly_sales": ["monthly_sales.csv"],
    "top_store_data": ["top_store_data.csv", "top_stores.csv"],
    "market_data": ["market_data.csv", "location_analysis.csv"],
    "store_size_cost": ["store_size_cost.csv", "cost_structure.csv"],
    "marketing_data": ["marketing_data.csv", "marketing_effect.csv"],
}


# =========================================================
# 공통 함수
# =========================================================
def show_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)


def find_file(possible_names: list[str]) -> Path | None:
    """
    아래 위치를 순서대로 탐색:
    1) app.py와 같은 폴더
    2) data 폴더
    """
    search_dirs = [BASE_DIR, DATA_DIR]

    for directory in search_dirs:
        for name in possible_names:
            candidate = directory / name
            if candidate.exists():
                return candidate
    return None


def read_csv_safe(file_key: str) -> pd.DataFrame:
    possible_names = FILE_CANDIDATES[file_key]
    found_path = find_file(possible_names)

    if found_path is None:
        st.error(f"파일을 찾을 수 없습니다: {possible_names[0]}")
        st.write("현재 찾는 위치:")
        st.write(f"- 루트 폴더: {BASE_DIR}")
        st.write(f"- data 폴더: {DATA_DIR}")
        st.write("현재 기대 파일명 후보:")
        for name in possible_names:
            st.write(f"- {name}")
        st.stop()

    encodings = ["utf-8-sig", "utf-8", "cp949"]
    last_error = None
    for enc in encodings:
        try:
            return pd.read_csv(found_path, encoding=enc)
        except Exception as e:
            last_error = e

    st.error(f"CSV 읽기 실패: {found_path.name}")
    st.exception(last_error)
    st.stop()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df


def extract_first_number(value):
    if pd.isna(value):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    text = str(value).strip().replace(",", "")
    if text == "":
        return None

    if "~" in text:
        left, right = text.split("~", 1)
        left_num = extract_first_number(left)
        right_num = extract_first_number(right)
        if left_num is not None and right_num is not None:
            return (left_num + right_num) / 2

    result = []
    dot_used = False
    found = False

    for ch in text:
        if ch.isdigit():
            result.append(ch)
            found = True
        elif ch == "." and not dot_used:
            result.append(ch)
            dot_used = True
            found = True
        elif found:
            break

    if not result:
        return None

    try:
        return float("".join(result))
    except ValueError:
        return None


def require_columns(df: pd.DataFrame, required_cols: list[str], file_label: str):
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        st.error(f"{file_label}에 필요한 컬럼이 없습니다.")
        st.write("누락 컬럼:", missing)
        st.write("현재 컬럼:", list(df.columns))
        st.stop()


def format_manwon(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{int(round(value)):,}만원"


# =========================================================
# 데이터 파싱
# =========================================================
def parse_store_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
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

    for col in ["점포 규모(평수)", "월매출(만원)", "객단가(원)", "재방문율(%)"]:
        df[col] = df[col].apply(extract_first_number)

    df["오픈일"] = pd.to_datetime(df["오픈일"], errors="coerce")
    return df


def parse_monthly_sales(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if "년도-월" not in df.columns:
        st.error("monthly_sales.csv에는 '년도-월' 컬럼이 필요합니다.")
        st.stop()

    value_cols = [c for c in df.columns if c != "년도-월"]
    for col in value_cols:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_top_store_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    # 둘 다 허용
    if "월평균매출(만원)" not in df.columns and "월매출 평균(만원)" in df.columns:
        df = df.rename(columns={"월매출 평균(만원)": "월평균매출(만원)"})

    required = ["매장명", "총매출(만원)", "월평균매출(만원)"]
    require_columns(df, required, "top_store_data.csv")

    for col in ["총매출(만원)", "월평균매출(만원)"]:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_market_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    # market_data.csv 실제 컬럼 기준
    required = [
        "상권 유형",
        "일평균 유동인구(명)",
        "주 고객층",
        "경쟁 점포 수",
        "평균 임대료(만원)",
        "추천 규모",
        "예상 월매출(만원)",
    ]
    require_columns(df, required, "market_data.csv")

    for col in ["일평균 유동인구(명)", "평균 임대료(만원)", "예상 월매출(만원)"]:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_store_size_cost(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["비교 항목", "소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]
    require_columns(df, required, "store_size_cost.csv")

    for col in ["소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_marketing_data(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["전략명", "월 예산(만원)", "유입 증가율", "매출 상승률", "추천 상권"]
    require_columns(df, required, "marketing_data.csv")

    for col in ["월 예산(만원)", "유입 증가율", "매출 상승률"]:
        df[col] = df[col].apply(extract_first_number)

    return df


@st.cache_data
def load_all_data():
    store_df = parse_store_data(read_csv_safe("store_data"))
    monthly_df = parse_monthly_sales(read_csv_safe("monthly_sales"))
    top_df = parse_top_store_data(read_csv_safe("top_store_data"))
    market_df = parse_market_data(read_csv_safe("market_data"))
    cost_df = parse_store_size_cost(read_csv_safe("store_size_cost"))
    marketing_df = parse_marketing_data(read_csv_safe("marketing_data"))
    return store_df, monthly_df, top_df, market_df, cost_df, marketing_df


# =========================================================
# 데이터 로드
# =========================================================
store_df, monthly_df, top_df, market_df, cost_df, marketing_df = load_all_data()

# KPI
store_count = len(store_df)
avg_revenue = store_df["월매출(만원)"].mean()
max_revenue = monthly_df.drop(columns=["년도-월"]).max().max()

# =========================================================
# 사이드바
# =========================================================
st.sidebar.title("Gelatico")
page = st.sidebar.radio(
    "페이지 선택",
    ["Home", "Dashboard", "Simulation"]
)

# =========================================================
# 페이지
# =========================================================
def render_home():
    show_header("🍦 젤라티코 GELATICO", "감성 브랜딩 + 데이터 기반 창업 분석")

    c1, c2, c3 = st.columns(3)
    c1.metric("운영 매장 수", f"{store_count}개")
    c2.metric("평균 월매출", "7,449만원")
    c3.metric("최고 월매출", "12,482만원")

    st.markdown(
        """
        <div class="card">
        젤라티코는 예비 창업자가 브랜드를 이해하고, 상권·점포 규모·마케팅 전략에 따른
        수익성을 데이터로 검토할 수 있도록 설계된 프랜차이즈 창업 분석 플랫폼입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard():
    show_header("Dashboard", "매출 핵심 데이터")

    st.markdown("### 매장별 월매출")
    st.bar_chart(store_df.set_index("매장명")["월매출(만원)"])

    st.markdown("### 상위 매장 월별 추이")
    top_names = [name for name in top_df["매장명"].tolist() if name in monthly_df.columns]
    if top_names:
        line_df = monthly_df.set_index("년도-월")[top_names]
        st.line_chart(line_df)
    else:
        st.warning("monthly_sales.csv 안의 매장명과 top_store_data.csv 안의 매장명이 일치하지 않습니다.")

    st.markdown("### 상권별 평균 월매출")
    market_avg = store_df.groupby("상권 유형")["월매출(만원)"].mean()
    st.bar_chart(market_avg)

    st.markdown("### 상위 매장 요약")
    st.dataframe(top_df, use_container_width=True)


def get_initial_investment(size: int) -> float:
    col_map = {
        10: "소형(10평)(만원)",
        15: "중형(15평)(만원)",
        20: "대형(20평)(만원)",
    }
    col = col_map[size]
    row = cost_df[cost_df["비교 항목"] == "총 초기 투자비"]
    if not row.empty:
        return float(row[col].iloc[0])

    fallback = cost_df[~cost_df["비교 항목"].isin(["예상 월매출", "예상 투자 회수"])]
    return float(fallback[col].sum())


def simulate(location_type: str, size: int, selected_marketing: list[str]) -> dict:
    loc = market_df[market_df["상권 유형"] == location_type]
    if loc.empty:
        return {"revenue": 0, "fixed_cost": 0, "net_profit": 0, "investment": 0, "payback": None}

    base_revenue = float(loc["예상 월매출(만원)"].iloc[0])
    rent = float(loc["평균 임대료(만원)"].iloc[0])

    size_multiplier = {10: 0.82, 15: 1.0, 20: 1.18}[size]
    revenue = base_revenue * size_multiplier

    selected_rows = marketing_df[marketing_df["전략명"].isin(selected_marketing)]
    marketing_cost = selected_rows["월 예산(만원)"].sum() if not selected_rows.empty else 0
    revenue_lift = selected_rows["매출 상승률"].sum() / 100 if not selected_rows.empty else 0
    revenue_lift = min(revenue_lift, 0.45)

    revenue = revenue * (1 + revenue_lift)

    labor_cost = {10: 380, 15: 520, 20: 700}[size]
    ingredient_cost = revenue * 0.32
    misc_cost = {10: 120, 15: 160, 20: 220}[size]

    fixed_cost = rent + labor_cost + ingredient_cost + misc_cost + marketing_cost
    net_profit = revenue - fixed_cost
    investment = get_initial_investment(size)
    payback = investment / net_profit if net_profit > 0 else None

    return {
        "revenue": revenue,
        "fixed_cost": fixed_cost,
        "net_profit": net_profit,
        "investment": investment,
        "payback": payback,
    }


def render_simulation():
    show_header("Simulation", "상권/규모/마케팅 전략별 수익 계산")

    c1, c2 = st.columns(2)
    with c1:
        location_type = st.selectbox("상권 유형", market_df["상권 유형"].dropna().unique().tolist())
        size = st.selectbox("점포 규모", [10, 15, 20], format_func=lambda x: f"{x}평")
    with c2:
        selected_marketing = st.multiselect("마케팅 전략", marketing_df["전략명"].dropna().unique().tolist())

    result = simulate(location_type, size, selected_marketing)

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("예상 월매출", format_manwon(result["revenue"]))
    r2.metric("예상 고정비", format_manwon(result["fixed_cost"]))
    r3.metric("예상 순이익", format_manwon(result["net_profit"]))
    r4.metric("초기 투자비", format_manwon(result["investment"]))
    r5.metric("투자 회수 기간", "회수 불가" if result["payback"] is None else f"{result['payback']:.1f}개월")


if page == "Home":
    render_home()
elif page == "Dashboard":
    render_dashboard()
elif page == "Simulation":
    render_simulation()
