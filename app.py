import os
import requests
import json
from flask import Flask, request, jsonify, render_template, Response
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
    if not API_KEY:
        return jsonify({"error": "未检测到 API 密钥。请在云端后台环境变量中配置 DEEPSEEK_API_KEY！"}), 500

    data = request.json or {}
    time_mode = data.get('time_mode', 'exact')
    start_city = data.get('start_city', '').strip()
    destination = data.get('destination', '').strip()
    
    try:
        budget = int(data.get('budget', 2000))
    except:
        budget = 2000
        
    tags = data.get('tags', '').strip()

    if not start_city or not destination:
        return jsonify({"error": "出发城市和目的地不能为空！"}), 400

    # 1. 动态时间线测算
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
        time_info = f"📅 去程日期：{travel_date} | 返程日期：{return_date} （共 {days} 天）"
    else:
        approx_time = data.get('approx_time', '近期')
        days = data.get('days', '3')
        time_info = f"📅 大致出行时段：{approx_time} | 预计玩 {days} 天"

    # 2. 空间距离就近算法提示词注入
    system_prompt = f"""你是一位精通全球12306、航司动态、地理空间距离、大城市轨道交通动线的高级智能出行调度总监。
当前时间为 2026 年 5 月。请输出一份**具备多车站智能择优、细节拉满、动线科学的专属平衡定制路书**。

【用户出行约束】：
- 🛫 出发城市：{start_city} ➡️ 🎯 目的地：{destination}
- {time_info}
- 💰 预算中轴红线：严格控制在 {budget} 元以内
- 🎨 用户偏好特征：{tags}

【🚨 核心精算：目的地多车站智能就近匹配规范】：
1. 🚊 大交通【市中心就近车站精选】：
   - 请首先识别目的地 {destination} 的传统市中心/核心商圈（例如：北京的王府井、上海的人民广场、成都的春熙路、重庆的解放碑等）。
   - 如果目的地有多个高铁/火车站（如北京南/北京西/北京丰台，重庆北/重庆西），**你必须智能选择“通过地铁或公共交通前往该市中心/核心酒店区用时最短、换乘最少”的那一个车站作为终点站**。
   - 严禁盲目分配偏远车站（如除非逼不得已，否则去重庆市中心不优先选无地铁直达、离市区极远的车站）。在路书中必须明确写出选择该特定车站的理由（如：“*特选【XX南站】作为终点，因其可搭乘地铁X号线直达市中心，比选择【XX西站】可节省约40分钟市内通勤时间*”）。

2. 🚊 智能中转与联程：
   - 若两地无直达或直达票面极差，启动中转推荐。中转枢纽站（如武汉/西安等）同样需要注意换乘是“同站换乘”还是“跨站换乘”，若是同站换乘，预留时间 40-60 分钟；若是跨站换乘，必须算入市内地铁转场时间并预留 2 小时以上。

3. 🚇 市内交通与时间戳：
   - 每日行程必须包含具体的时间戳（如 09:00 - 10:30），且动线严禁折返跑。
   - 早晚高峰（07:30-09:30, 17:00-19:30）及核心拥堵景区，锁死公共交通，必须写出具体的地铁线路（如：搭乘地铁2号线至XX站）。平峰期可推荐打车并预估费用。

4. 🧮 财务总账本：
   - 必须将总预算精确拆解到【大交通分段及中转费、住宿总费、市内交通专项基金、景点门票、餐饮】。

请直接输出 Markdown 格式。开头不要废话。在输出的内容中间，必须包含这一条商业合作广告代码：
<div class="affiliate-card"><span>🧡 FlexBudget 核心特惠：</span><br><a href="#" target="_blank">[独家对齐，点击抢扣本航线最优就近车站特价票、特价房态与景区大通票]</a></div>
"""

    def generate_stream():
        try:
            response = requests.post(API_URL, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": system_prompt}],
                "temperature": 0.2,
                "stream": True,      
                "max_tokens": 4096   
            }, headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            }, stream=True, timeout=60)

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
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return Response(generate_stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 5002), debug=True)
