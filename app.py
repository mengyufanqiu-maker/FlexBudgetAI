import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# 你的专属密钥配置
# ==========================================
API_KEY = "sk-48bf10f821904382ae63972a30f5f6db"
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate_route', methods=['POST'])
def generate_route():
    try:
        data = request.json
        start_city = data.get('start_city', '').strip()
        destination = data.get('destination', '').strip()
        travel_date = data.get('travel_date', '').strip()
        days = data.get('days', '').strip()
        budget = int(data.get('budget', 2000))
        tags = data.get('tags', '').strip()

        # 动态计算三个档位的预算锚定
        saving_budget = int(budget * 0.65)
        luxury_budget = int(budget * 1.8)

        # 终极三方案流派提示词
        system_prompt = f"""你是一位精通大数据精算与商业变现的顶级智慧旅游架构师。
当前时间线为2026年5月。请针对用户输入的时空约束，**同时并行规划三套不同档位的特制路书**。

【用户硬性输入】：
- 🛫 出发地：{start_city} | 🎯 目的地：{destination} | 📅 日期：{travel_date}
- 💰 用户核心预算：{budget} 元
- ⏱️ 天数：{days} 天 | 🎭 偏好：{tags}

【三方案精算矩阵要求】：
请严格按照以下三个标签页的数据结构输出 Markdown 格式，不要说任何客套话。每一个方案必须包含完整的“大交通+住宿+餐饮门票+10%备用金”闭环，且通勤时间必须真实（拒绝瞬移）。

---PLAN_MATCH---
# 🎯 方案一：【用户专属定制版】（严格控价：≤ {budget} 元）
*这是最优先、最精准匹配用户预期的方案。大交通计算往返。*
### 📊 核心预算大账本：
[列出明细，总和 <= {budget}]
### 🏨 极致对齐·住宿与交通推荐：
[在此处列出 1 家最合适的酒店/客栈和往返交通推荐]
<div class="affiliate-card">
    <span>🧡 FlexBudget 实时比价沙盒（匹配版专属特惠）：</span><br>
    您的出发时间为 {travel_date}，已为您锁定当前档位协议价。<a href="https://s.click.taobao.com/mock_match" target="_blank">[点击此处一键抢扣特价房态]</a>
</div>
### 🗺️ {days}天专属定制行程路书：
[按Day 1, Day 2列出契合偏好 {tags} 的保姆级路线]

---PLAN_SAVING---
# 🪙 方案二：【极限穷游节省版】（极限压榨：≤ {saving_budget} 元）
*以极低的成本通关。大交通可能选择红眼航班、普快硬座或拼车，住宿锁死青年旅舍床位或远郊青旅。*
### 📊 穷游大账本总览：
[总和 <= {saving_budget}]
### 🏨 极限省钱·落脚点推荐：
[推荐1家极低成本的落旅/床位]
<div class="affiliate-card">
    <span>🪙 FlexBudget 特种兵穷游津贴抠门榜：</span><br>
    [点击此处秒杀青年旅舍/硬座特价票](https://s.click.taobao.com/mock_saving)
</div>
### 🗺️ {days}天省钱流特种兵路书：
[列出极致省钱的免费打卡路线与地道街边摊]

---PLAN_LUXURY---
# 👑 方案三：【轻奢尊享豪华版】（品质升舱：约 {luxury_budget} 元）
*打破预算天花板，展示如果预算充裕，能享受怎样的奢华体验（如：高铁一等座/商务舱、洱海绝美海景大床房、高端私房菜、VIP免排队门票）。*
### 📊 奢华大账本总览：
[总和约 {luxury_budget}]
### 🏨 尊享奢华·高奢酒店与度假村推荐：
[推荐 1 家当地极具声誉的高端奢华酒店或海景网红大床房，狠狠刺激用户]
<div class="affiliate-card" style="border-color: #d97706; bg-color: #fef3c7;">
    <span style="color: #b45309;">👑 FlexBudget 黑金会员尊享高端通道：</span><br>
    检测到您在 {travel_date} 出行，该奢华客房支持免押金入住并赠送双人早餐。<a href="https://s.click.taobao.com/mock_luxury" target="_blank" style="color: #b45309;">[点击此处即刻升舱预订]</a>
</div>
### 🗺️ {days}天品质度假奢享路书：
[列出高品质、重体验、绝不特种兵的尊享度假行程]
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
            return jsonify({"error": "精算大脑响应异常"}), 500

        return jsonify({"result": response.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
