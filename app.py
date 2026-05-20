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

    # 2. 注入地狱级商业硬核真实性提示词
    system_prompt = f"""你是一位精通12306实时中转、民航订票系统、携程/美团同程酒店库、高德地图空间动线的终极智能出行精算总监。
当前时间为 2026 年 5 月。请输出一份**大交通、市内动线换乘、真实酒店品牌及价格完全对齐现实世界事实**的专属平衡定制路书。

【用户出行约束】：
- 🛫 出发城市：{start_city} ➡️ 🎯 目的地：{destination}
- {time_info}
- 💰 预算中轴红线：严格控制在 {budget} 元以内
- 🎨 用户偏好特征：{tags}

【🚨 商业级 100% 真实性硬核校验规范（严禁捏造）】：
1. ✈️ 真实大交通及中转精算：
   - 必须给出 {start_city} 到 {destination} 真实存在的航班或高铁二等座车次（如 G102, D3522 等真实车次编号）。
   - 如果选择特定火车站（如北京南站、重庆北站、成都东站），必须明确写出选择该站的真实原因：因为它距离目的地市中心核心区或第一晚酒店在地理空间上最近、且有真实开通的地铁/公共交通工具。
   - 若无直达，推荐的高铁中转方案必须保证中转枢纽站（如武汉站、西安北站、郑州东站）有同站便捷换乘通道，且换乘时间真实合理（留足 45-60 分钟）。

2. 🏨 真实酒店及价格精算：
   - 严禁模糊描述（如‘入住市区快捷酒店’、‘入住某舒适型客栈’，这是严重违规）。
   - 你必须给出目的地真实存在的具体酒店全称（例如：亚朵酒店、全季酒店、美豪丽致酒店、华住汉庭酒店、或是洲际/喜来登等高端品牌）。
   - 酒店地理位置必须邻近你规划的行程路线或核心商圈（例如去重庆必须具体到：‘亚朵酒店(重庆解放碑步行街中心店)’）。
   - 必须标明契合该日期与预算的**真实房型**（如：高级大床房、舒适双床房）以及真实的携程/美团**当季参考每晚价格（元）**，并将其计入总账本。

3. 🚌 真实市内通勤（全面封杀虚假地铁）：
   - 必须伴随精准的时间戳（如 08:30 - 09:15）。
   - ⚠️ 针对目的地城市真实的公共交通网络编写：如果目的地（如丽江、大理、三亚、阳朔、九寨沟）现实中**没有城市地铁**，绝对不准捏造任何‘地铁X号线’！必须写出真实的‘景区直通车、机场巴士X号线、当地常规公交车、或是网约车/出租车（并给出高德地图真实的预估打车费）’。
   - 如果大城市有地铁（如北京、上海、广州、成都、杭州），必须写明真实运营的地铁线路编号和真实的换乘站点（如：搭乘地铁1号线至天府广场站，转2号线至春熙路站）。

4. 🧮 财务分毫不差总账本：
   - 在路书结尾，用表格或列表形式列出绝对真实的账目明细：大交通费用（含中转费）、酒店住宿费（单价*晚数）、景点门票费、市内实际通勤（地铁/打车）专项预算、餐饮预算，总和必须完美咬合预算红线。

请直接输出 Markdown 格式。开头不要一句废话，直接出干货。在输出的内容中间，必须包含这一条商业合作广告代码：
<div class="affiliate-card"><span>🧡 FlexBudget 核心特惠：</span><br><a href="#" target="_blank">[独家对齐，点击抢扣本航线最优就近车站特价票、真实房态与景区大通票]</a></div>
"""

    def generate_stream():
        try:
            response = requests.post(API_URL, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": system_prompt}],
                "temperature": 0.0,  # 🔥 降到绝对 0 度！彻底锁死 AI 的自由创造力，逼迫其100%采用最板正的、现实中存在的检索记忆与事实。
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
