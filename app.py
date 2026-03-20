import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# 기본 설정
# ---------------------------
st.set_page_config(page_title="젤라또 매출 대시보드", layout="wide")

st.title("🍦 젤라또 창업 매출 분석 대시보드")

# ---------------------------
# 데이터 로드
# ---------------------------
@st.cache_data
def load_data():
    store = pd.read_csv("store_full_dataset_updated.csv")
    monthly = pd.read_csv("monthly_sales_2023_2025_wide.csv")
    return store, monthly

store_df, monthly_df = load_data()

# ---------------------------
# KPI 영역
# ---------------------------
col1, col2, col3 = st.columns(3)

col1.metric("평균 월매출", f"{int(store_df['월매출(만원)'].mean())}만원")
col2.metric("최고 매출", f"{int(store_df['월매출(만원)'].max())}만원")
col3.metric("매장 수", len(store_df))

st.divider()

# ---------------------------
# 1. 매장별 매출 (Bar)
# ---------------------------
st.subheader("📊 매장별 월매출 비교")

bar_data = store_df.set_index("매장명")["월매출(만원)"]
st.bar_chart(bar_data)

st.divider()

# ---------------------------
# 2. 월별 매출 추이 (Line)
# ---------------------------
st.subheader("📈 월별 매출 추이")

monthly_df = monthly_df.set_index("년도-월")

selected_store = st.selectbox("매장 선택", monthly_df.columns)

st.line_chart(monthly_df[selected_store])

st.divider()

# ---------------------------
# 3. 상권별 매출 비중 (Pie)
# ---------------------------
st.subheader("🥧 상권별 매출 비중")

market_data = store_df.groupby("상권 유형")["월매출(만원)"].sum()

fig, ax = plt.subplots()
ax.pie(market_data, labels=market_data.index, autopct='%1.1f%%')
ax.set_title("상권별 매출 비중")

st.pyplot(fig)

st.divider()

# ---------------------------
# 4. 점포 규모 vs 매출 (Scatter)
# ---------------------------
st.subheader("📍 점포 규모 vs 매출")

fig2, ax2 = plt.subplots()
ax2.scatter(store_df["점포 규모(평수)"], store_df["월매출(만원)"])
ax2.set_xlabel("점포 규모(평수)")
ax2.set_ylabel("월매출(만원)")
ax2.set_title("점포 규모 vs 매출")

st.pyplot(fig2)
