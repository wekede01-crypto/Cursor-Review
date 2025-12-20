import requests
from bs4 import BeautifulSoup
import csv
import time
import random

# === 1. 🎯 目标清单 ===
asins = ["B0CWK6YQ7V", "B0FPQGLYK9", "B0DXZVNYKM", "B0FFF3757L"]

# === 2. 🎭 伪装升级：准备多个“身份证” ===
# 每次请求随机选一个，让亚马逊以为是不同的人在访问
user_agent_list = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

# === 3. 🛡️ 代理设置 ===
import os  # 记得在最上面加这一行

# ... 中间代码不变 ...

# === 改造：智能判断是否使用代理 ===
# 如果检测到是在 GitHub Actions 环境下运行，就不挂代理
if os.getenv("GITHUB_ACTIONS"):
    print("☁️ 检测到云端环境，不使用本地代理...")
    proxies = None 
else:
    # 在你自己电脑上，还是用 Clash
    proxies = {
        "http": "http://127.0.0.1:7890",
        "https": "http://127.0.0.1:7890"
    }

# ... 后面的 requests.get(..., proxies=proxies) 不用改，它会自动识别 ...

# === 4. 准备文件 ===
f = open("review_data.csv", mode="w", newline="", encoding="utf-8-sig")
writer = csv.writer(f)
writer.writerow(["ASIN", "标题", "价格", "链接"])

print(f"🚀 任务启动！准备抓取 {len(asins)} 个产品 (含自动重试)...")
print("--------------------------------------------------")

# === 5. 🔄 循环抓取 ===
for asin in asins:
    url = f"https://www.amazon.com/dp/{asin}"
    
    # --- ⭐ 新增：重试机制 ---
    max_retries = 3  # 最多试 3 次
    success = False  # 标记是否成功
    
    for attempt in range(1, max_retries + 1):
        print(f"🕵️ 正在侦察: {asin} (第 {attempt} 次尝试)...")
        
        try:
            # 每次随机换一个 User-Agent
            current_headers = {
                "User-Agent": random.choice(user_agent_list),
                "Accept-Language": "en-US,en;q=0.9"
            }
            
            resp = requests.get(url, headers=current_headers, proxies=proxies, timeout=10)
            
            # 如果状态码是 200，说明成功了！
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                
                title_tag = soup.find(id="productTitle")
                title = title_tag.get_text().strip() if title_tag else "无标题"
                short_title = title[:30] + "..."
                
                price_tag = soup.select_one('.a-price .a-offscreen')
                if not price_tag: price_tag = soup.find(class_="a-color-price")
                price = price_tag.get_text().strip() if price_tag else "无价格"
                
                writer.writerow([asin, title, price, url])
                print(f"✅ 成功锁定: {short_title} | 💰 {price}")
                
                success = True # 标记成功
                break # 成功了就跳出重试循环，不用再试了
            
            elif resp.status_code == 404:
                print("😭 404: 商品不存在，不再重试。")
                break # 404 是硬伤，重试也没用，直接跳过
                
            else:
                # 遇到 202 或 503，说明被挡了
                print(f"⚠️ 遇到阻碍 (状态码 {resp.status_code})，准备重试...")
        
        except Exception as e:
            print(f"❌ 出错: {e}")
            
        # 如果还没成功，稍微休息一下再重试
        if attempt < max_retries:
            time.sleep(random.randint(2, 4))
    
    # 如果试了 3 次还是没成功
    if not success:
        print(f"🚫 彻底失败: {asin} 放弃治疗。")
        writer.writerow([asin, "抓取失败", "N/A", url])

    print("--------------------------------------------------")
    # 抓下一个产品前，长休息
    time.sleep(random.randint(3, 6))

# === 6. 收尾 ===
f.close()
print("🎉 任务全部完成！")