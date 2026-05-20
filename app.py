import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔐 100% 大厂无痕规范：仅从系统环境变量读取
# ==========================================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate_route', methods=['POST'])
def generate_route():
    try:
        # 🛡️ 极其关键的安全拦截：如果没有配钥匙，立刻报错，防止前端死循环转圈！
        if not API_KEY:
            return jsonify({"error": "系统未检测到 API 密钥。请在 Render 的 Environment 环境变量中配置 DEEPSEEK_API_KEY！"}), 500

        data = request.json or {}
        start_city = data.get('start_city', '').strip()
        destination = data.get('destination', '').strip()
        travel_date = data.get('travel_date', '').strip()
        days = data.get('days', '').strip()
        
        try:
            budget = int(data.get('budget', 2000))
        except:
            budget = 2000
            
        tags = data.get('tags', '').strip()

        if not start_city or not destination or not travel_date:
            return jsonify({"error": "出发城市、目的地和出发日期为硬性约束，不能为空！"}), 400

        # 动态计算三个档位的预算锚定比例
        saving_budget = int(budget * 0.65)
        luxury_budget = int(budget * 1.8)

        system_prompt = f"""你是一位精通大数据精算与商业变现的顶级智慧旅游架构师。
当前时间线为2026年5月。请针对用户输入的时空约束，**同时并行规划三套不同档位的特制路书**。

【用户硬性输入】：
- 🛫 出发地：{start_city} | 🎯 目的地：{destination} | 📅 日期：{travel_date}
- 💰 用户核心预算：{budget} 元
- ⏱️ 天数：{days} 天 | 🎭 偏好：{tags}

【三方案精算矩阵要求】：
请严格按照以下三个标签页的数据结构输出 Markdown 格式，不要说任何客套话。每一个方案必须包含完整的“大交通+住宿+餐饮门票+10%备用金”闭环。

---PLAN_MATCH---
# 🎯 方案一：【用户专属定制版】（严格控价：≤ {budget} 元）
### 📊 核心预算大账本：
[列出明细，总和 <= {budget}]
### 🏨 极致对齐·住宿与交通推荐：
[在此处列出 1 家最合适的酒店/客栈和往返交通推荐]
<div class="affiliate-card">
    <span>🧡 FlexBudget 实时比价沙盒（匹配版专属特惠）：</span><br>
    您的出发时间为 {travel_date}，已为您锁定当前档位协议价。<a href="https://s.click.taobao.com/mock_match" target="_blank">[点击此处一键抢扣特价房态]</a>
</div>
### 🗺️ {days}天专属定制行程路书：
[按Day 1, Day 2列出契合偏好 {tags} 的路线]

---PLAN_SAVING---
# 🪙 方案二：【极限穷游节省版】（极限压榨：≤ {saving_budget} 元）
### 📊 穷游大账本总览：
[总和 <= {saving_budget}]
### 🏨 极限省钱·落脚点推荐：
[推荐1家极低成本的落旅/床位]
<div class="affiliate-card">
    <span>🪙 FlexBudget 特种兵穷游津贴抠门榜：</span><br>
    <a href="https://s.click.taobao.com/mock_saving" target="_blank">[点击此处秒杀青年旅舍/硬座特价票]</a>
</div>
### 🗺️ {days}天省钱流特种兵路书：
[列出极致省钱的免费打卡路线与地道街边摊]

---PLAN_LUXURY---
# 👑 方案三：【轻奢尊享豪华版】（品质升舱：约 {luxury_budget} 元）
### 📊 奢华大账本总览：
[总和约 {luxury_budget}]
### 🏨 尊享奢华·高奢酒店与度假村推荐：
[推荐 1 家当地极具声誉的高端奢华酒店或海景网红大床房]
<div class="affiliate-card" style="border-color: #d97706; background-color: #fef3c7;">
    <span style="color: #b45309;">👑 FlexBudget 黑金会员尊享高端通道：</span><br>
    检测到您在 {travel_date} 出行，该奢华客房支持免押金入住并赠送双人早餐。<a href="https://s.click.taobao.com/mock_luxury" target="_blank" style="color: #b45309;">[点击此处即刻升舱预订]</a>
</div>
### 🗺️ {days}天品质度假奢享路书：
[列出高品质、重体验的尊享度假行程]
"""

        response = requests.post(API_URL, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.3
        }, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, timeout=60)

        if response.status_code != 200:
            return jsonify({"error": f"精算大脑响应异常，错误码: {response.status_code}"}), 500

        return jsonify({"result": response.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"error": f"服务器内部精算错误: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
