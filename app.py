import os
import requests
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime

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
        time_mode = data.get('time_mode', 'exact')
        start_city = data.get('start_city', '').strip()
        destination = data.get('destination', '').strip()
        
        try:
            budget = int(data.get('budget', 2000))
        except:
            budget = 2000
            
        tags = data.get('tags', '').strip()
        saving_budget = int(budget * 0.65)
        luxury_budget = int(budget * 1.8)

        # 🧠 双轨引擎逻辑：根据用户选择的模式构建约束条件
        if time_mode == 'exact':
            travel_date = data.get('travel_date', '')
            return_date = data.get('return_date', '')
            if not travel_date or not return_date:
                return jsonify({"error": "精确模式下，去程和返程日期不能为空！"}), 400
                
            try:
                d1 = datetime.strptime(travel_date, "%Y-%m-%d")
                d2 = datetime.strptime(return_date, "%Y-%m-%d")
                days = (d2 - d1).days + 1
            except:
                days = 3
                
            time_constraint = f"📅 去程：{travel_date} | 🔙 返程：{return_date} （精确共计 {days} 天）"
            rules_constraint = f"""
1. 航班班次：因为用户给定了具体日期，必须查出真实的航班号（如 JD5177, MU5712 等）及起降时间（HH:MM）。
2. 酒店细节：必须给出具体酒店全称及其具体房型和该指定日期的精确价格。
3. 行程排布：严格按照指定的这 {days} 天跨度写每天路书。"""

        else:
            # 模糊模式
            approx_time = data.get('approx_time', '近期')
            days = data.get('days', '3')
            time_constraint = f"📅 大致时间：{approx_time} | ⏱️ 游玩天数：{days} 天"
            rules_constraint = f"""
1. 交通估价：因为用户时间灵活，请给出该季节/月份的平均航班/高铁估价范围即可，无需指定特定班次。
2. 酒店建议：推荐适合此季节的酒店类型和区域（如：古城内特色客栈），给出均价范围。
3. 行程排布：给出一份非常丝滑灵活的 {days} 天打卡路线参考。"""

        # 统合终极提示词
        system_prompt = f"""你是一位精通数据采集与商业变现的顶级旅游架构师。
当前时间为 2026 年 5 月。请针对以下用户需求，规划三套特制路书。

【用户需求】：
- 🛫 出发地：{start_city} | 🎯 目的地：{destination}
- {time_constraint}
- 💰 用户预算：{budget} 元 | 🎭 偏好：{tags}

【极致真实性输出要求 - 绝不妥协】：{rules_constraint}

4. 格式死命令：你必须严格使用以下三个暗号来分割方案，绝对不准加空格或改变大小写，否则系统将崩溃！

---PLAN_MATCH---
# 🎯 方案一：【用户专属定制版】（严格控价：≤ {budget} 元）
### 📊 核心大账本：[明细，总和 <= {budget}]
### 🏨 对齐推荐：[交通与住宿详情]
<div class="affiliate-card"><span>🧡 FlexBudget 特惠：</span><br><a href="https://s.click.taobao.com/mock_match" target="_blank">[点击抢扣特价房态]</a></div>
### 🗺️ {days}天行程路书：[每日路线]

---PLAN_SAVING---
# 🪙 方案二：【极限穷游节省版】（极限压榨：≤ {saving_budget} 元）
### 📊 穷游大账本：[明细，总和 <= {saving_budget}]
### 🏨 省钱推荐：[青旅或硬座详情]
<div class="affiliate-card"><span>🪙 FlexBudget 特惠：</span><br><a href="https://s.click.taobao.com/mock_saving" target="_blank">[点击秒杀特价票]</a></div>
### 🗺️ {days}天穷游路书：[穷游路线]

---PLAN_LUXURY---
# 👑 方案三：【轻奢尊享豪华版】（品质升舱：约 {luxury_budget} 元）
### 📊 奢华大账本：[明细，总和约 {luxury_budget}]
### 🏨 奢华推荐：[高端酒店与头等舱详情]
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
