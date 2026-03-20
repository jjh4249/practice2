import math
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# 기본 설정
# =========================================================
st.set_page_config(
    page_title="젤라티코 창업 분석 플랫폼",
    page_icon="🍦",
    layout="wide",
)

# =========================================================
# 한국어 표시용 스타일
# =========================================================
st.markdown(
    """
    <style>
    html, body, [class*="css"], [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        font-family: "Apple SD Gothic Neo", "Malgun Gothic", "Noto Sans KR",
                     "Nanum Gothic", Arial, sans-serif !important;
    }

    .main-title {
        font-size: 2.3rem;
        font-weight: 800;
        color: #1B3A6B;
        margin-bottom: 0.2rem;
    }

    .sub-title {
        font-size: 1.0rem;
        color: #475569;
        margin-bottom: 1.4rem;
    }

    .section-title {
        font-size: 1.35rem;
        font-weight: 700;
        color: #1B3A6B;
        margin-top: 0.5rem;
        margin-bottom: 0.8rem;
    }

    .card {
        padding: 1rem 1.1rem;
        border-radius: 16px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        margin-bottom: 0.8rem;
    }

    .highlight {
        color: #1B3A6B;
        font-weight: 700;
    }

    .small-note {
        font-size: 0.92rem;
        color: #64748B;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 파일 경로
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
# 공통 함수
# =========================================================
def show_header(title: str, subtitle: str = ""):
    st.markdown(f'<div class="main-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="sub-title">{subtitle}</div>', unsafe_allow_html=True)


def read_csv_safe(path: Path, file_label: str) -> pd.DataFrame:
    if not path.exists():
        st.error(f"파일이 없습니다: {file_label}")
        st.info(f"확인 경로: {path}")
        st.info("해결 방법: data 폴더 안에 해당 CSV 파일이 있는지 확인하세요.")
        st.stop()

    # utf-8-sig 우선, 실패 시 utf-8, 마지막 cp949 시도
    encodings = ["utf-8-sig", "utf-8", "cp949"]
    last_error = None

    for enc in encodings:
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception as e:
            last_error = e

    st.error(f"CSV를 읽을 수 없습니다: {file_label}")
    st.exception(last_error)
    st.stop()


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    return df


def extract_first_number(text):
    if pd.isna(text):
        return None

    if isinstance(text, (int, float)):
        return float(text)

    s = str(text).strip().replace(",", "")
    if s == "":
        return None

    # 범위값 처리 예: 2800~4500
    if "~" in s:
        left, right = s.split("~", 1)
        left_num = extract_first_number(left)
        right_num = extract_first_number(right)
        if left_num is not None and right_num is not None:
            return (left_num + right_num) / 2

    result = []
    dot_used = False
    found = False

    for ch in s:
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


def format_people(value) -> str:
    if value is None or pd.isna(value):
        return "-"
    return f"{int(round(value)):,}명"


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
        st.error("monthly_sales.csv에는 '년도-월' 컬럼이 반드시 있어야 합니다.")
        st.stop()

    sales_cols = [c for c in df.columns if c != "년도-월"]
    if not sales_cols:
        st.error("monthly_sales.csv에 매장별 매출 컬럼이 없습니다.")
        st.stop()

    for col in sales_cols:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_top_stores(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["매장명", "총매출(만원)", "월평균매출(만원)"]
    require_columns(df, required, "top_stores.csv")

    for col in ["총매출(만원)", "월평균매출(만원)"]:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_location_analysis(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
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
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_cost_structure(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["비교 항목", "소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]
    require_columns(df, required, "cost_structure.csv")

    for col in ["소형(10평)(만원)", "중형(15평)(만원)", "대형(20평)(만원)"]:
        df[col] = df[col].apply(extract_first_number)

    return df


def parse_marketing_effect(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)
    required = ["전략명", "월 예산(만원)", "유입 증가율", "매출 상승률", "추천 상권"]
    require_columns(df, required, "marketing_effect.csv")

    for col in ["월 예산(만원)", "유입 증가율", "매출 상승률"]:
        df[col] = df[col].apply(extract_first_number)

    return df


@st.cache_data
def load_all_data():
    store_df = parse_store_data(read_csv_safe(FILE_MAP["store_data"], "store_data.csv"))
    monthly_df = parse_monthly_sales(read_csv_safe(FILE_MAP["monthly_sales"], "monthly_sales.csv"))
    top_df = parse_top_stores(read_csv_safe(FILE_MAP["top_stores"], "top_stores.csv"))
    location_df = parse_location_analysis(read_csv_safe(FILE_MAP["location_analysis"], "location_analysis.csv"))
    cost_df = parse_cost_structure(read_csv_safe(FILE_MAP["cost_structure"], "cost_structure.csv"))
    marketing_df = parse_marketing_effect(read_csv_safe(FILE_MAP["marketing_effect"], "marketing_effect.csv"))

    return store_df, monthly_df, top_df, location_df, cost_df, marketing_df


# =========================================================
# 데이터 로드
# =========================================================
store_df, monthly_df, top_df, location_df, cost_df, marketing_df = load_all_data()

# KPI 계산
store_count = len(store_df)
avg_revenue = store_df["월매출(만원)"].mean()
max_revenue = monthly_df.drop(columns=["년도-월"]).max().max()

melted = monthly_df.melt(id_vars="년도-월", var_name="매장명", value_name="매출(만원)")
melted["매출(만원)"] = melted["매출(만원)"].apply(extract_first_number)
max_idx = melted["매출(만원)"].idxmax()
top_store_name = melted.loc[max_idx, "매장명"]
top_store_month = melted.loc[max_idx, "년도-월"]

# =========================================================
# 사이드바 네비게이션
# =========================================================
st.sidebar.title("Gelatico")
page = st.sidebar.radio(
    "페이지 선택",
    ["Home", "About", "Menu", "Process", "Dashboard", "Simulation"],
)

st.sidebar.markdown("---")
st.sidebar.markdown('<div class="small-note">젤라티코 창업 분석 플랫폼</div>', unsafe_allow_html=True)

# =========================================================
# 페이지 함수
# =========================================================
def render_home():
    show_header(
        "🍦 젤라티코 GELATICO",
        "감성 브랜딩 + 데이터 기반 창업 의사결정 플랫폼"
    )

    st.markdown(
        """
        <div class="card">
        <span class="highlight">이미 사랑받는 젤라또 브랜드, 이제 당신의 매장으로 이어집니다.</span><br>
        Gelatico는 예비 창업자가 브랜드를 이해하고, 상권과 수익성을 데이터로 검토할 수 있도록 설계된
        프랜차이즈 창업 안내 플랫폼입니다.
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    c1.metric("운영 매장 수", f"{store_count}개")
    c2.metric("평균 월매출", "7,449만원")
    c3.metric("최고 월매출", "12,482만원")

    st.markdown("### 핵심 강점")
    a, b, c = st.columns(3)

    with a:
        st.markdown(
            """
            <div class="card">
            <b>브랜드 신뢰</b><br>
            전국 18개 매장 운영과 누적 데이터를 기반으로 창업 판단을 돕습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with b:
        st.markdown(
            """
            <div class="card">
            <b>메뉴 경쟁력</b><br>
            시즌성과 프리미엄 포지셔닝이 가능한 젤라또 메뉴 구성을 제안합니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with c:
        st.markdown(
            """
            <div class="card">
            <b>데이터 기반 수익 분석</b><br>
            상권, 점포 규모, 마케팅 전략에 따라 예상 수익을 계산할 수 있습니다.
            </div>
            """,
            unsafe_allow_html=True,
        )

    col1, col2 = st.columns(2)
    with col1:
        st.info("창업 데이터를 보려면 Dashboard 페이지로 이동하세요.")
    with col2:
        st.info("예상 수익을 계산하려면 Simulation 페이지로 이동하세요.")


def render_about():
    show_header("About Gelatico", "브랜드 소개와 핵심 지표")

    st.markdown("### 브랜드 스토리")
    st.write(
        """
        Gelatico는 이탈리아 젤라또의 감성과 국내 상권 데이터 기반 운영 전략을 결합한 가상 프랜차이즈 브랜드입니다.
        단순한 디저트 판매를 넘어서, 상권별 수익 구조를 정량적으로 검토할 수 있도록 설계되었습니다.
        """
    )

    st.markdown("### 핵심 지표")
    c1, c2, c3 = st.columns(3)
    c1.metric("운영 매장", "18개")
    c2.metric("평균 월매출", "7,449만원")
    c3.metric("최고 월매출", "12,482만원")

    tourism_avg = store_df.loc[store_df["상권 유형"] == "관광", "월매출(만원)"].mean()
    st.metric("관광 상권 평균 월매출", format_manwon(tourism_avg))

    st.markdown("### 차별점")
    st.write("- 이탈리아 감성의 프리미엄 브랜드 톤")
    st.write("- 계절성을 반영한 제품 운영")
    st.write("- 상권별 데이터 기반 창업 의사결정")
    st.write("- 투자비와 회수 기간까지 고려한 분석 구조")


def render_menu():
    show_header("Menu", "대표 메뉴 및 시즌 메뉴")

    menu_items = [
        ("피스타치오 젤라또", "진한 견과 풍미와 부드러운 질감", "베스트셀러"),
        ("스트라치아텔라", "밀크 젤라또와 초콜릿 칩의 클래식 조합", "시그니처"),
        ("망고 소르베", "상큼한 과일 베이스의 여름 시즌 인기 메뉴", "여름 추천"),
        ("티라미수 젤라또", "디저트 감성을 강조한 프리미엄 메뉴", "프리미엄"),
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

    st.markdown("### 시즌 메뉴")
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
    show_header("Startup Process", "8단계 창업 절차")

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
                "온라인 또는 전화로 초기 문의 접수",
                "담당자와 1:1 상담 진행",
                "유동인구·상권·고객층 분석",
                "10평 / 15평 / 20평 기준 검토",
                "가맹 조건 검토 및 계약",
                "브랜드 가이드 기반 시공",
                "제품 제조·POS·CS 교육",
                "오픈 후 운영 지원",
            ],
            "소요 기간": ["1일", "1주", "2주", "1주", "1주", "4~6주", "2주", "지속"],
        }
    )

    st.dataframe(process_df, use_container_width=True)


def render_dashboard():
    show_header("Revenue Dashboard", "매출 데이터 기반 분석")

    st.markdown("### 필터")
    f1, f2, f3 = st.columns(3)

    region_options = ["전체"] + sorted(store_df["지역"].dropna().unique().tolist())
    type_options = ["전체"] + sorted(store_df["상권 유형"].dropna().unique().tolist())
    store_options = ["전체"] + sorted(store_df["매장명"].dropna().unique().tolist())

    selected_region = f1.selectbox("지역 선택", region_options)
    selected_type = f2.selectbox("상권 유형 선택", type_options)
    selected_store = f3.selectbox("매장 선택", store_options)

    filtered = store_df.copy()

    if selected_region != "전체":
        filtered = filtered[filtered["지역"] == selected_region]
    if selected_type != "전체":
        filtered = filtered[filtered["상권 유형"] == selected_type]
    if selected_store != "전체":
        filtered = filtered[filtered["매장명"] == selected_store]

    if filtered.empty:
        st.warning("선택한 조건에 맞는 데이터가 없습니다.")
        return

    st.markdown("### KPI")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("매장 수", len(filtered))
    k2.metric("평균 월매출", format_manwon(filtered["월매출(만원)"].mean()))
    k3.metric("최고 월매출", format_manwon(max_revenue))
    k4.metric("최고 매출 지점", f"{top_store_name} ({top_store_month})")

    tab1, tab2, tab3, tab4 = st.tabs(["매장별 비교", "상위 5개 추이", "비용 구조", "원본 데이터"])

    with tab1:
        bar_df = filtered.sort_values("월매출(만원)", ascending=False)
        fig_bar = px.bar(
            bar_df,
            x="매장명",
            y="월매출(만원)",
            color="상권 유형",
            text="월매출(만원)",
            title="매장별 월매출 비교",
        )
        fig_bar.update_layout(
            xaxis_title="매장명",
            yaxis_title="월매출(만원)",
            font=dict(family="Arial, sans-serif"),
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with tab2:
        top_names = top_df["매장명"].tolist()
        available_top_names = [x for x in top_names if x in monthly_df.columns]

        line_df = monthly_df[["년도-월"] + available_top_names].copy()
        long_df = line_df.melt(id_vars="년도-월", var_name="매장명", value_name="매출(만원)")

        fig_line = px.line(
            long_df,
            x="년도-월",
            y="매출(만원)",
            color="매장명",
            markers=True,
            title="상위 5개 매장 월별 매출 추이",
        )
        fig_line.update_layout(
            xaxis_title="년도-월",
            yaxis_title="매출(만원)",
            font=dict(family="Arial, sans-serif"),
        )
        st.plotly_chart(fig_line, use_container_width=True)
        st.caption("여름철(6~8월) 성수기 구간에서 매출 상승이 나타나도록 설계된 데이터입니다.")

    with tab3:
        size_option = st.selectbox("기준 점포 규모", ["소형(10평)", "중형(15평)", "대형(20평)"])

        size_col_map = {
            "소형(10평)": "소형(10평)(만원)",
            "중형(15평)": "중형(15평)(만원)",
            "대형(20평)": "대형(20평)(만원)",
        }
        selected_col = size_col_map[size_option]

        pie_df = cost_df[~cost_df["비교 항목"].isin(["총 초기 투자비", "예상 월매출", "예상 투자 회수"])].copy()
        pie_df = pie_df[["비교 항목", selected_col]].rename(columns={selected_col: "금액(만원)"})

        fig_pie = px.pie(
            pie_df,
            names="비교 항목",
            values="금액(만원)",
            title=f"{size_option} 기준 초기 비용 구조",
        )
        fig_pie.update_layout(font=dict(family="Arial, sans-serif"))
        st.plotly_chart(fig_pie, use_container_width=True)

    with tab4:
        st.dataframe(filtered, use_container_width=True)

    st.markdown("### 상위 매장 요약")
    st.dataframe(top_df, use_container_width=True)


def get_initial_investment(size: int) -> float:
    col_map = {
        10: "소형(10평)(만원)",
        15: "중형(15평)(만원)",
        20: "대형(20평)(만원)",
    }
    col = col_map[size]

    total_row = cost_df[cost_df["비교 항목"] == "총 초기 투자비"]
    if not total_row.empty:
        return float(total_row[col].iloc[0])

    temp = cost_df[~cost_df["비교 항목"].isin(["예상 월매출", "예상 투자 회수"])]
    return float(temp[col].sum())


def simulate(location_type: str, size: int, selected_marketing: list[str]) -> dict:
    loc_row = location_df[location_df["상권 유형"] == location_type]
    if loc_row.empty:
        return {
            "revenue": 0,
            "fixed_cost": 0,
            "net_profit": 0,
            "investment": 0,
            "payback": None,
        }

    base_revenue = float(loc_row["예상 월매출(만원)"].iloc[0])
    rent = float(loc_row["평균 임대료(만원)"].iloc[0])

    size_multiplier = {10: 0.82, 15: 1.00, 20: 1.18}[size]
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

    payback = None
    if net_profit > 0:
        payback = investment / net_profit

    return {
        "revenue": revenue,
        "fixed_cost": fixed_cost,
        "net_profit": net_profit,
        "investment": investment,
        "payback": payback,
    }


def render_simulation():
    show_header("Startup Simulation", "상권·규모·마케팅 전략 기반 수익 예측")

    s1, s2 = st.columns(2)

    with s1:
        location_type = st.selectbox("상권 유형", location_df["상권 유형"].dropna().unique().tolist())
        size = st.selectbox("점포 규모", [10, 15, 20], format_func=lambda x: f"{x}평")

    with s2:
        strategies = st.multiselect("마케팅 전략 선택", marketing_df["전략명"].dropna().unique().tolist())

    result = simulate(location_type, size, strategies)

    r1, r2, r3, r4, r5 = st.columns(5)
    r1.metric("예상 월매출", format_manwon(result["revenue"]))
    r2.metric("예상 고정비", format_manwon(result["fixed_cost"]))
    r3.metric("예상 순이익", format_manwon(result["net_profit"]))
    r4.metric("초기 투자비", format_manwon(result["investment"]))

    if result["payback"] is None:
        payback_text = "회수 불가"
    else:
        payback_text = f"{result['payback']:.1f}개월"

    r5.metric("투자 회수 기간", payback_text)

    st.markdown("### 계산 기준")
    st.write("- 상권별 예상 월매출을 기준값으로 사용")
    st.write("- 점포 규모에 따라 매출 배율 적용")
    st.write("- 선택한 마케팅 전략의 매출 상승률을 최대 45%까지 반영")
    st.write("- 고정비 = 임대료 + 인건비 + 재료비 + 기타 운영비 + 마케팅비")

    with st.expander("상권 분석 데이터"):
        st.dataframe(location_df, use_container_width=True)

    with st.expander("점포 규모별 초기 비용"):
        st.dataframe(cost_df, use_container_width=True)

    with st.expander("마케팅 전략 효과"):
        st.dataframe(marketing_df, use_container_width=True)


# =========================================================
# 라우팅
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
