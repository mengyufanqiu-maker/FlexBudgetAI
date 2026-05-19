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
        budget = data.get('budget', '').strip()
        tags = data.get('tags', '').strip()

        if not start_city or not destination or not travel_date or not budget:
            return jsonify({"error": "出发城市、目的地、出发日期和总预算为硬性约束，不能为空！"}), 400

        # 终极防幻觉、控实时性的商业提示词工程
        system_prompt = f"""你是一位精通省钱通关流、思维极其严谨的顶级特种兵旅游规划师。
你必须基于用户输入的【具体时间与空间约束】进行极致的预算扣减和路书编排。

【用户硬性约束条件】：
- 🛫 出发城市：{start_city}
- 🎯 目的地：{destination}
- 📅 出发具体日期：{travel_date} （请根据此日期判断该目的地属于淡季、旺季、还是节假日，并按当前时间线2026年5月的市场供需预估真实物价！）
- 💰 硬核总预算：{budget} 元（总花费必须包含往返大交通，绝对不能超支！）
- ⏱️ 游玩天数：{days} 天
- 🎭 风格偏好：{tags if tags else "经典打卡，极致性价比"}

【核心修正规则（强制执行）】：
1. 交通双程闭环：在账本里计算大交通花费时，必须同时计算从“{start_city} 到 {destination}”以及“从 {destination} 返回 {start_city}”的【双程】预计票价！
2. 真实时间轴拒绝瞬移：每个景点、酒店、大交通节点之间，必须留出至少 40-60 分钟的真实城市通勤时间。上午民宿/青旅通常无法办理入住，只能安排寄存行李。
3. 动态价格降维：由于出发日期是 {travel_date}，如果该日期处于法定节假日或旅游旺季，你必须在住宿预算上提高占比，并明确警告用户该时段物价会上涨，甚至需要削减门票和餐饮预算来强行对齐 {budget} 元的总预算。
4. 必须留出总预算的 10% 作为“突发事件备用金”。

【商业变现规则】：
必须在【大交通】和【住宿推荐】区域，动态植入以下高亮分销卡片（模拟携程/去哪儿实时比价占位符，用于解决大模型无法直接获取实时变动价格的痛点）：
<div style="background-color: #fff7ed; border: 1px dashed #f97316; padding: 14px; border-radius: 12px; margin: 12px 0; font-size: 13.5px; text-align: left;">
    <span style="color: #ea580c; font-weight: bold;">🧡 FlexBudget 动态数据链提示（实时锁定）：</span><br>
    当前大模型预估基于行业历史均价。由于您的出发时间为 {travel_date}，建议 
    <a href="https://s.click.taobao.com/mock_travel_affiliate_placeholder" target="_blank" style="color: #0284c7; text-decoration: underline; font-weight: bold;">[点击此处前往 FlexBudget 实时比价沙盒]</a> 
    一键比对今日全网最新秒杀价、抢扣实时特价房态，若从此处预订可直接锁定专属津贴。
</div>

【输出格式要求】：
请直接输出纯净的 Markdown 格式，包含：
# 一、FlexBudget 预算大账本总览（核算并证明总花费 <= {budget}元）
# 二、高性价比大交通与住宿落脚方案（必须包含上述变现卡片）
# 三、{days}天保姆级特种兵路书（按Day 1, Day 2划分，严格融入偏好并留足真实通勤时间）
"""

        response = requests.post(API_URL, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.3  # 进一步压低随机性，确保算账和逻辑高度严谨
        }, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, timeout=60)

        if response.status_code != 200:
            return jsonify({"error": f"后端大脑响应异常:
