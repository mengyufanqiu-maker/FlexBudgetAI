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
        destination = data.get('destination', '').strip()
        budget = data.get('budget', '').strip()
        days = data.get('days', '').strip()
        tags = data.get('tags', '').strip()

        if not destination or not budget:
            return jsonify({"error": "目的地和总预算是硬性条件，不能为空哦！"}), 400

        # 核心商业提示词工程：硬性锁价 + 动态植入返佣卡片
        system_prompt = f"""你是一位精通省钱通关流的顶级特种兵旅游规划师，擅长在大数据下进行极致的预算卡死与高性价比行程编排。

【用户硬性约束条件】：
- 🎯 目的地：{destination}
- 💰 硬核总预算：{budget} 元（必须严格卡死，总花费绝对不能超过这个数字！）
- 📅 游玩天数：{days} 天
- 🎭 风格偏好：{tags if tags else "经典打卡，极致性价比"}

【你的终极任务】：
请为用户量身定制一份保姆级路书行程单。不要说任何客套话，直接输出 Markdown 格式。

【商业变现规则（极其重要）】：
为了实现商业变现，你必须在行程单的【住宿推荐】和【大交通】区域，以特定的格式动态植入带有高亮效果的“分销返佣占位链接”（模拟淘宝联盟/携程分销）。
格式必须严格采用：
<div style="background-color: #fff7ed; border: 1px dashed #f97316; padding: 12px; border-radius: 12px; margin: 10px 0;">
    <span style="color: #ea580c; font-weight: bold;">🧡 FlexBudget 独家全网最低协议价特惠：</span><br>
    [点击此处前往特价预订/查看实时房态](https://s.click.taobao.com/mock_travel_affiliate_placeholder) 
</div>

【输出格式要求】：
1. 📊 预算大账本总览：
   - 拆分出：大交通预计、住宿预计、门票饮食预计、留白备用金。
   - 算一笔总账，证明总和 <= {budget} 元。
2. 🏨 极致性价比住宿推荐：
   - 推荐 1-2 家符合预算范围的青年旅舍、连锁酒店或高分民宿。
   - 必须在此处植入上述【商业变现规则】中的分销返佣卡片！
3. 🗺️ {days}天极限特种兵路书行程：
   - 按 Day 1, Day 2... 详细列出早、中、晚的路线图、推荐小吃、避坑指南。
   - 每一天的行程里，要融入用户提到的偏好：{tags}。
"""

        # 调教 DeepSeek 核心大脑
        response = requests.post(API_URL, json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": system_prompt}],
            "temperature": 0.4  # 降低随机性，让算账更严谨、卡预算更死
        }, headers={
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }, timeout=60)

        if response.status_code != 200:
            return jsonify({"error": f"精算大脑响应异常，状态码: {response.status_code}"}), 500

        res_data = response.json()
        route_markdown = res_data['choices'][0]['message']['content']

        return jsonify({"result": route_markdown})

    except Exception as e:
        return jsonify({"error": f"系统内部精算错误: {str(e)}"}), 500

if __name__ == '__main__':
    # 使用 5002 端口，完美避开之前的 5000 和 5001，绝不冲突！
    app.run(host='127.0.0.1', port=5002, debug=True)