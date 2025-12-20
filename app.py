import streamlit as st
import pandas as pd

# === 1. 网页标题 ===
st.title("🛒 亚马逊竞品分析看板")
st.write("这是你用 Python 搭建的第一个交互式网页！")

# === 2. 读取数据 ===
# 使用缓存功能，避免每次点击都要重新读取文件
@st.cache_data
def load_data():
    # 确保文件名和你文件夹里的一致 (可能是 review_data.csv 或 review_data_v2.csv)
    try:
        df = pd.read_csv("review_data.csv") 
        # 数据清洗：把价格转成数字
        df['Price_Num'] = pd.to_numeric(df['价格'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')
        return df.dropna(subset=['Price_Num']) # 删掉没价格的
    except:
        return pd.DataFrame() # 如果找不到文件，返回空表

df = load_data()

if df.empty:
    st.error("❌ 找不到 review_data.csv，请先运行爬虫！")
else:
    # === 3. 侧边栏：交互控制器 ===
    st.sidebar.header("🔍 筛选工具")
    
    # 这是一个滑动条！控制价格显示范围
    max_price = st.sidebar.slider("最高价格限制 ($)", 0, 300, 200)
    
    # 根据滑动条筛选数据
    filtered_df = df[df['Price_Num'] <= max_price]

    # === 4. 展示关键指标 ===
    col1, col2 = st.columns(2)
    col1.metric("📦 展示产品数", f"{len(filtered_df)} 个")
    col2.metric("💰 平均价格", f"${filtered_df['Price_Num'].mean():.2f}")

    # === 5. 画图 (超级简单，一行代码) ===
    st.subheader("📊 价格柱状图")
    # Streamlit 自带图表，不需要 Matplotlib 那么复杂的设置
    st.bar_chart(filtered_df.set_index('标题')['Price_Num'])

    # === 6. 展示原始数据表 ===
    st.subheader("📋 详细数据表")
    st.dataframe(filtered_df)