import os
import requests
import json
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔐 100% 纯净云端架构：绝无明文密钥
# ==========================================
API_KEY = os.environ.get("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/generate_route', methods=['POST'])
def generate_route():
    # 🛡️ 拦截器
    if not API_KEY:
        return jsonify({"error": "未检测到 API 密钥。请在后台环境变量中配置 DEEPSEEK_API_KEY！"}), 500

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

    if not start_city or not destination:
        return jsonify({"error": "出发城市和目的地不能为空！"}), 400

    # 🧠 双轨提示词判定引擎
    if time_mode == 'exact':
        travel_date = data.get('travel_date', '')
        return_date = data.get('return_date', '')
        if not travel_date or not return_date:
            return jsonify({"error": "精确模式下，去程和返程日期不能为空！"}), 400
        try:
            d1 = datetime.strptime(travel_date, "%Y-%m-%d")
            d2 = datetime.strptime(return_date, "%Y-%m-%d")
            days = (d2 - d1).days + 1
            if days <= 0:
                return jsonify({"error": "返程日期必须在去程日期之后哦！"}), 400
        except:
            days = 3
            
        time_constraint = f"📅 日期：{travel_date} 至 {return_date} （共 {days} 天）"
        rules_constraint = f"""
1. 交通：极简给出真实航班号(如 JD5177)及起降时间，直接标总价。
2. 住宿：极简给出具体酒店全称、房型及实测总价。
3. 行程：每日行程必须浓缩为【一行字结构】（例如：Day1：机场 -> 酒店 -> 核心景区）。禁止长篇大论描述景点风景！"""
    else:
        approx_time = data.get('approx_time', '近期')
        days = data.get('days', '3')
        time_constraint = f"📅 大致时间：{approx_time} | ⏱️ 共 {days} 天"
        rules_constraint = f"""
1. 交通：一句话给出该时段平均航班/高铁估价。
2. 住宿：一句话推荐酒店类型、区域及均价。
3. 行程：每日行程必须浓缩为【一行字打卡流】。禁止长篇大论！"""

    # 🔥 核心防御：给 AI 戴上极度精简的“紧箍咒”
    system_prompt = f"""你是一位顶级旅游精算师。当前时间为2026年5月。
请针对以下需求，规划三套路书。

【用户需求】：🛫 {start_city} ➡️ 🎯 {destination} | {time_constraint} | 💰 预算：{budget}元 | 🎭 偏好：{tags}

【🚨 致命约束 - 绝不妥协】：
1. 你必须严格使用三个暗号分割方案，不准加空格或改大小写！
2. 你的输出额度极度有限！每个方案的字数必须极度压缩，废话全删！每日行程用 `A -> B -> C` 的箭头格式一笔带过。
3. 确保你能一口气把三个方案完整输出到底，绝对不准中途烂尾！格式必须严格如下：

---PLAN_MATCH---
# 🎯 方案一：【专属定制版】(≤ {budget} 元)
### 📊 极简账本：[用一句话写明总预算拆解]
### 🏨 机酒直达：[精炼的交通与住宿详情]
<div class="affiliate-card"><span>🧡 特惠：</span><a href="#" target="_blank">[抢特价房态]</a></div>
### 🗺️ 行程骨架：
[Day1: xxx -> xxx -> xxx]
[Day2: xxx -> xxx -> xxx]

---PLAN_SAVING---
# 🪙 方案二：【极限穷游版】(≤ {saving_budget} 元)
### 📊 极简账本：[用一句话写明总预算拆解]
### 🏨 极限省钱：[青旅/硬座直达]
<div class="affiliate-card"><span>🪙 特惠：</span><a href="#" target="_blank">[秒杀特价票]</a></div>
### 🗺️ 行程骨架：
[Day1: xxx -> xxx]
[Day2: xxx -> xxx]

---PLAN_LUXURY---
# 👑 方案三：【轻奢尊享版】(约 {luxury_budget} 元)
### 📊 极简账本：[用一句话写明总预算拆解]
### 🏨 尊享顶配：[五星/头等舱直达]
<div class="affiliate-card" style="border-color: #d97706; background-color: #fef3c7;"><span style="color: #b45309;">👑 黑金：</span><a href="#" target="_blank">[升舱预订]</a></div>
### 🗺️ 行程骨架：
[Day1: 专车 -> xxx -> 奢华晚餐]
[Day2: xxx -> xxx]
"""

    def generate_stream():
        try:
            response = requests.post(API_URL, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": system_prompt}],
                "temperature": 0.1,
                "stream": True,      
                "max_tokens": 4096   # 回归稳定的最大输出额度
            }, headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }, stream=True, timeout=60)

            if response.status_code != 200:
                yield f"data: {json.dumps({'error': f'大模型拒绝访问: {response.status_code}'})}\n\n"
                return

            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        if data_str.strip() == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            chunk = data_json['choices'][0]['delta'].get('content', '')
                            if chunk:
                                yield f"data: {json.dumps({'text': chunk})}\n\n"
                        except:
                            continue
        except Exception as e:
            yield f"data: {json.dumps({'error': f'网络阻断: {str(e)}'})}\n\n"

    return Response(generate_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5002), debug=True)
