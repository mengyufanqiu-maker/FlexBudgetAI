import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime  # 🚀 新增：时间计算引擎

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔐 100% 纯净云端架构
# ==========================================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate_route', methods=['POST'])
def generate_route():
    try:
        if not API_KEY:
            return jsonify({"error": "未检测到 API 密钥。请在 Render 配置 DEEPSEEK_API_KEY！"}), 500

        data = request.json or {}
        start_city = data.get('start_city', '').strip()
        destination = data.get('destination', '').strip()
        travel_date = data.get('travel_date', '').strip() # 去程日期
        return_date = data.get('return_date', '').strip() # 返程日期
        
        try:
            budget = int(data.get('budget', 2000))
        except:
            budget = 2000
            
        tags = data.get('tags', '').strip()

        if not start_city or not destination or not travel_date or not return_date:
            return jsonify({"error": "出发地、目的地、去程和返程日期为硬性约束，不能为空！"}), 400

        # 📅 自动计算游玩天数（用于规范 AI 的路书天数排布）
        try:
            d1 = datetime.strptime(travel_date, "%Y-%m-%d")
            d2 = datetime.strptime(return_date, "%Y-%m-%d")
            days = (d2 - d1).days + 1
            if days <= 0:
                return jsonify({"error": "时光倒流啦！返程日期必须在去程日期之后哦！"}), 400
        except:
            days = 3 # 容错保底

        saving_budget = int(budget * 0.65)
        luxury_budget = int(budget * 1.8)

        # 🧠 动态时空智算提示词：打破月份限制，完全基于用户双日期
        system_prompt = f"""你是一位具备 100% 真实数据采集能力的 AI 旅游精算师。
请针对用户以下精确的时间与空间约束，进行三方案精算。

【用户精准时空输入】：
- 🛫 出发地：{start_city} | 🎯 目的地：{destination}
- 📅 去程日期：{travel_date} | 🔙 返程日期：{return_date} （共计 {days} 天）
- 💰 用户预算：{budget} 元 | 🎭 偏好：{tags}

【极致真实性输出要求 - 绝不妥协】：
1. 航班班次：必须基于 {travel_date} 的去程和 {return_date} 的返程，给出具体的航班号（如 JD5177, MU5712 等）及精确的起降时间（HH:MM）。票价必须包含基准价及机建燃油。
2. 酒店细节：禁止使用模糊推荐。必须给出具体酒店全称及其具体房型和对应日期的实测价格。
3. 行程排布：必须严格按照 {days} 天的跨度输出每天的详细打卡点与真实通勤时间。
4. 格式死命令：你必须严格使用以下三个暗号来分割方案，绝对不准加空格或改变大小写，否则系统将崩溃！

---PLAN_MATCH---
# 🎯 方案一：【用户专属定制版】（严格控价：≤ {budget} 元）
### 📊 核心大账本：[明细，总和 <= {budget}]
### 🏨 极致对齐推荐：[具体航班与酒店]
<div class="affiliate-card"><span>🧡 FlexBudget 特惠：</span><br><a href="https://s.click.taobao.com/mock_match" target="_blank">[点击抢扣特价房态]</a></div>
### 🗺️ {days}天行程路书：[每日路线]

---PLAN_SAVING---
# 🪙 方案二：【极限穷游节省版】（极限压榨：≤ {saving_budget} 元）
### 📊 穷游大账本：[明细，总和 <= {saving_budget}]
### 🏨 极限省钱推荐：[青旅或硬座]
<div class="affiliate-card"><span>🪙 FlexBudget 特惠：</span><br><a href="https://s.click.taobao.com/mock_saving" target="_blank">[点击秒杀特价票]</a></div>
### 🗺️ {days}天穷游路书：[穷游路线]

---PLAN_LUXURY---
# 👑 方案三：【轻奢尊享豪华版】（品质升舱：约 {luxury_budget} 元）
### 📊 奢华大账本：[明细，总和约 {luxury_budget}]
### 🏨 尊享奢华推荐：[高端酒店与头等舱]
<div class="affiliate-card" style="border-color: #d97706; background-color: #fef3c7;"><span style="color: #b45309;">👑 黑金通道：</span><br><a href="https://s.click.taobao.com/mock_luxury" target="_blank">[即刻升舱预订]</a></div>
### 🗺️ {days}天尊享路书：[尊享路线]
"""

        response = requests.post(API_URL, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.1 
        }, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, timeout=60)

        if response.status_code != 200:
            return jsonify({"error": f"接口异常: {response.status_code}"}), 500

        return jsonify({"result": response.json()['choices'][0]['message']['content']})

    except Exception as e:
        return jsonify({"error": f"服务器精算错误: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5002, debug=True)
