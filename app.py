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
        return jsonify({"error": "未检测到 API 密钥。请在环境变量中配置 DEEPSEEK_API_KEY！"}), 500

    data = request.json or {}
    time_mode = data.get('time_mode', 'exact')
    plan_type = data.get('plan_type', 'match') # 🚀 新增：接收前端传来的具体档位 (match/saving/luxury)
    start_city = data.get('start_city', '').strip()
    destination = data.get('destination', '').strip()
    
    try:
        budget = int(data.get('budget', 2000))
    except:
        budget = 2000
        
    tags = data.get('tags', '').strip()

    if not start_city or not destination:
        return jsonify({"error": "出发城市和目的地不能为空！"}), 400

    # 1. 动态时间逻辑
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
        accuracy_rule = f"你必须针对 {travel_date} 和 {return_date} 这两个真实的日子，给出具体的航班号（如 CA1831, MU5712）、具体的起降时间、具体的酒店名称及该日期的真实房型价格。"
    else:
        approx_time = data.get('approx_time', '近期')
        days = data.get('days', '3')
        time_info = f"📅 大致出行时段：{approx_time} | 预计玩 {days} 天"
        accuracy_rule = "请给出该时段目的地普遍的往返大交通、住宿的均价估算及推荐区域。"

    # 2. 根据前端点击的 Tab，针对性分配大账本预算红线
    if plan_type == 'saving':
        target_budget = int(budget * 0.65)
        title_tag = f"🪙 方案二：【极限穷游节省版】（预算上限：严格控制在 {target_budget} 元以内）"
        style_rule = "极尽省钱之能事。交通优先推荐硬座、廉航、夜车；住宿优先推荐青年旅舍大通铺、廉价民宿；餐饮主打 local 苍蝇馆子和地道街头小吃，把门票开销压到最低。"
        ad_card = '<div class="affiliate-card"><span>🪙 FlexBudget 特惠：</span><br><a href="#" target="_blank">[点击秒杀全网低价学生/穷游特价票]</a></div>'
    elif plan_type == 'luxury':
        target_budget = int(budget * 1.8)
        title_tag = f"👑 方案三：【轻奢尊享豪华版】（预算范围：大约 {target_budget} 元左右）"
        style_rule = "不计较成本，主打度假品质和奢华享受。交通优先推荐高端航司头等舱/商务舱、高铁商务座、景区包车接送；住宿必须是当地五星级奢华酒店或高分网红高档Villa（注明具体房型，如：全海景大床房）；餐饮推荐高分大众点评必吃榜或黑珍珠餐厅。"
        ad_card = '<div class="affiliate-card" style="border-color: #d97706; background-color: #fef3c7;"><span style="color: #b45309;">👑 黑金通道：</span><br><a href="#" target="_blank">[尊享高净值通道，点击即刻升舱预订]</a></div>'
    else:
        target_budget = budget
        title_tag = f"🎯 方案一：【专属平衡定制版】（预算中轴：严格控制在 {target_budget} 元以内）"
        style_rule = "在品质与价格之间寻找完美平衡。大交通推荐时间段优秀的经济舱或高铁二等座；住宿推荐市区交通便利的高分舒适型/高档型酒店（如亚朵、美豪丽致等）；行程丰富，松弛有度。"
        ad_card = '<div class="affiliate-card"><span>🧡 FlexBudget 特惠：</span><br><a href="#" target="_blank">[核心对齐，点击抢扣特价房态与独家门票优惠]</a></div>'

    # 3. 终极细节化 Prompts：取消字数限制，逼出 AI 的全部细节
    system_prompt = f"""你是一位精通大数据精算与深度旅行体验的顶级旅游规划总监。
当前时间为 2026 年 5 月。请针对用户的出行需求，输出一份**细节炸裂、内容极度充实、绝不敷衍**的高清路书。

【用户硬性约束】：
- 🛫 出发地：{start_city} ➡️ 🎯 目的地：{destination}
- {time_info}
- 🎨 用户风格偏好：{tags}

【你现在唯一需要输出的方案档位】：
{title_tag}

【输出规范 - 细节必须拉满】：
1. 🧮 极其详细的财务大账本：必须将总预算精确拆解到【大交通、住宿、本地通勤、各景点门票、餐饮、预备金】。每一笔钱都要写明算账过程。总额必须符合预算目标！
2. 🏨 具体的机酒数据：{accuracy_rule} {style_rule}
3. 🗺️ 逐日细节化行程表：每一天必须包含【具体的时间戳（如 09:00 - 10:30）】。严禁写空洞的地点，必须写明【具体的通勤交通方式（如：坐地铁2号线、滴滴打车约15元）】、【具体的游玩内容/避坑指南（如：建议走西门进，少排队30分钟）】和【每顿饭推荐的具体餐馆名称】。

请直接输出 Markdown 格式。开头不要废话。在输出的内容中间，必须包含这一条广告代码：
{ad_card}
"""

    def generate_stream():
        try:
            response = requests.post(API_URL, json={
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": system_prompt}],
                "temperature": 0.2,
                "stream": True,      
                "max_tokens": 4096   # 4096 令牌现在服务于单一个方案，细节丰富度翻了三倍！
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
