import pandas as pd
import matplotlib.pyplot as plt

# === 1. 设置中文字体 (防止乱码) ===
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# === 2. 读取刚才抓到的数据 ===
print("📊 正在读取 review_data.csv ...")
try:
    df = pd.read_csv("review_data.csv")
except FileNotFoundError:
    print("❌ 找不到文件！请先运行 spider.py 抓数据。")
    exit()

# === 3. 数据清洗 (把 "$220.00" 变成数字 220.00) ===
# 这一步是数据分析的灵魂：把文字变成机器能算的数字
# 强制转成字符 -> 删掉 $ -> 删掉逗号 -> 转成数字
df['Price_Num'] = pd.to_numeric(df['价格'].astype(str).str.replace('$', '').str.replace(',', ''), errors='coerce')

# 删掉没抓到价格的产品 (即 202 报错的那行)
df = df.dropna(subset=['Price_Num'])

# === 4. 画图 (柱状图) ===
plt.figure(figsize=(10, 6))

# 定义颜色：给 Medicube 的产品用“品牌蓝”，其他的用灰色
colors = ['skyblue' if 'medicube' in name.lower() else 'lightgray' for name in df['标题']]

bars = plt.bar(df['ASIN'], df['Price_Num'], color=colors)

# === 5. 装饰图表 ===
plt.title('亚马逊竞品价格对比', fontsize=16)
plt.xlabel('产品 ASIN', fontsize=12)
plt.ylabel('价格 ($)', fontsize=12)
plt.grid(axis='y', linestyle='--', alpha=0.3)

# 在柱子头顶标上价格
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'${height}',
             ha='center', va='bottom', fontsize=10, fontweight='bold')

print("🎉 图表已生成！")
plt.tight_layout()
plt.show()