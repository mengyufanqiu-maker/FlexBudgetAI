import os
import requests
import json
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ==========================================
# 🔐 100% 纯净云端架构：从环境变量读取密钥
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
    plan_type = data.get('plan_type', 'match') 
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
        accuracy_rule = f"你必须针对 {travel_date} 和 {return_date} 这两个真实日期的实际票态，进行多模态大交通测算。"
    else:
        approx_time = data.get('approx_time', '近期')
        days = data.get('days', '3')
        time_info = f"📅 大致出行时段：{approx_time} | 预计玩 {days} 天"
        accuracy_rule = "请基于该时段两地之间普遍的大交通规律进行智能方案推荐。"

    # 2. 三舱分流财务红线与偏好风格配置
    if plan_type == 'saving':
        target_budget = int(budget * 0.65)
        title_tag = f"🪙 方案二：【极限穷游节省版】（核心目标：严格压减在 {target_budget} 元以内）"
        style_rule = "极尽省钱之能事。交通优先推荐硬座、廉航、夜车；大交通中转优先考虑‘最省钱中转方案’（如跨站换乘、普快中转、红眼航班中转等）。住宿推荐青年旅舍大通铺或低价民宿；市内通勤‘100% 锁死公共交通’。"
        ad_card = '<div class="affiliate-card"><span>🪙 穷游特惠：</span><br><a href="#" target="_blank">[秒杀全网低价学生/特价学生中转联程票]</a></div>'
    elif plan_type == 'luxury':
        target_budget = int(budget * 1.8)
        title_tag = f"👑 方案三：【轻奢尊享豪华版】（目标范围：大约 {target_budget} 元左右）"
        style_rule = "不计较成本，主打假期尊享与无缝衔接。大交通优先推荐直飞头等舱/商务舱、高铁商务座。如果目的地无直达，则必须规划‘最省时、最舒适的智能中转’（如：空铁联运双商务舱，且中转留白换乘时间控制在 45-90 分钟内，避免长时滞留）。市内交通主打全程专车接送或核心景区直达包车，拒绝拥挤。"
        ad_card = '<div class="affiliate-card" style="border-color: #d97706; background-color: #fef3c7;"><span style="color: #b45309;">👑 黑金通道：</span><br><a href="#" target="_blank">[尊享高净值通道，点击即刻预订 VIP 专车接送与接机服务]</a></div>'
    else:
        target_budget = budget
        title_tag = f"🎯 方案一：【专属平衡定制版】（中轴红线：严格控制在 {target_budget} 元以内）"
        style_rule = "在出行效率与性价比之间寻找最优解。大交通智能计算：若直达票价高于中转30%且时间相差不大，主动推荐最优‘高性价比高铁/空铁中转方案’。住宿推荐市区高分舒适型酒店（如亚朵、美豪丽致等）；市内交通灵活组合，平衡打车与地铁。"
        ad_card = '<div class="affiliate-card"><span>🧡 核心特惠：</span><br><a href="#" target="_blank">[独家对齐，点击抢扣本航线中转优惠券与景区大通票]</a></div>'

    # 3. 注入“智能中转与多模态市内交通”提示词灵魂
    system_prompt = f"""你是一位精通全球12306、航司动态、市内高德/百度地图实时路况的高级智能出行调度总监。
当前时间为 2026 年 5 月。请针对用户的具体出行需求，输出一份**细节拉满、动线科学、具备智能交通调度的超级路书**。

【用户出行约束】：
- 🛫 出发城市：{start_city} ➡️ 🎯 目的地：{destination}
- {time_info}
- 🎨 用户偏好特征：{tags}

【你当前被指派单独输出的舱位】：
{title_tag}

【🚨 智能交通与中转精算核心规范】：
1. 🚊 大交通【直达 vs 智能中转】深度测算：
   - 请先评估 {start_city} 到 {destination} 是否有直达高铁/航班。
   - 如果“无直达”、“直达票价溢价严重”或“直达时间极差”，你必须激活【最优智能中转推荐】。中转方案必须详细写出：中转枢纽城市（如武汉/西安/昆明）、前段车次/航班（含预估价）、中转站内停留时间（必须留足 40 分钟以上防止误车，穷游版可适当拉长）、后段车次/航班。
   - 严禁模糊。必须给出一个明确、可执行的联程闭环动线。

2. 🚇 市内通勤【时间+路况智能最优解】：
   - 每日行程的动线必须符合地理逻辑，拒绝折返跑。
   - 必须细化到具体的交通工具！在【早晚高峰时段（07:30-09:30, 17:00-19:30）】或【核心拥堵景区周围】，必须智能推荐‘地铁/轻轨/公共交通换乘方案’，并写明具体线路（如：搭乘地铁1号线至大雁塔站C口出）。
   - 在平峰期、无地铁直达区域或深夜，推荐‘打车/网约车’，并写明预估费用（如：打车约18元，避开A路段改走高架快线）。

3. 🧮 财务总账本重构：
   - 必须单列出【大交通分段费用（或中转总费）】和【市内公共交通/网约车预估通勤专项基金】。大账本总额必须符合该舱位目标！

请直接输出 Markdown 格式。开头不要废话。在输出的内容中间，必须包含这一条商业合作广告代码：
{ad_card}
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
