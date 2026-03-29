import os
import json
import re
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 是否使用模拟模式（不调用真实 API）
USE_MOCK = os.getenv('USE_MOCK', 'True').lower() == 'true'

def extract_params_with_minimax(query):
    if USE_MOCK:
        return _mock_extract(query)
    else:
        return _real_minimax_extract(query)

def _mock_extract(query):
    # ... 模拟提取逻辑（不变）...
    taste = None
    budget = None
    time_limit = None
    people = None

    taste_keywords = {
        '辣': '辣', '清淡': '清淡', '川菜': '川菜', '粤菜': '粤菜'
    }
    for kw, val in taste_keywords.items():
        if kw in query:
            taste = val
            break

    budget_match = re.search(r'(\d+)\s*[元块]', query)
    if budget_match:
        budget = int(budget_match.group(1))

    time_match = re.search(r'(\d+)\s*分钟', query)
    if time_match:
        time_limit = int(time_match.group(1))

    people_match = re.search(r'(\d+)\s*[人位]', query)
    if people_match:
        people = int(people_match.group(1))
    if people is None:
        if '一个人' in query or '1人' in query:
            people = 1
        elif '两个人' in query or '2人' in query:
            people = 2

    return {
        "taste": taste,
        "budget": budget,
        "time": time_limit,
        "people": people
    }

def _real_minimax_extract(query):
    """真实调用 MiniMax-M2.7 模型（OpenAI 兼容接口）"""
    api_key = os.getenv('MINIMAX_API_KEY')
    base_url = os.getenv('MINIMAX_BASE_URL', 'https://api.minimax.chat/v1')

    if not api_key:
        raise ValueError("未设置 MINIMAX_API_KEY 环境变量")

    try:
        from openai import OpenAI
    except ImportError:
        raise ImportError("未安装 openai 库，请执行: pip install openai")

    client = OpenAI(api_key=api_key, base_url=base_url)

    system_prompt = """你是一个参数提取助手。从用户的用餐需求中提取以下字段：
- taste: 口味偏好（如：辣、清淡、川菜、粤菜等）
- budget: 预算金额（整数，单位元）
- time: 可接受的等待时间（整数，单位分钟）
- people: 用餐人数（整数）

如果某个字段未提及，设为 null。
只返回 JSON 格式，不要添加任何解释文字。"""

    user_prompt = f"用户需求：{query}"

    try:
        response = client.chat.completions.create(
            model="MiniMax-M2.7",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            max_tokens=500
        )

        reply = response.choices[0].message.content
        print(f"MiniMax 返回原始内容: {reply}")

        # ---------- 提取 JSON ----------
        # 1. 尝试匹配 ```json ... ``` 代码块
        json_match = re.search(r'```json\s*(\{.*?\})\s*```', reply, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 2. 尝试直接匹配最外层的 {} 对象
            json_match = re.search(r'(\{.*\})', reply, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
            else:
                raise ValueError("未找到 JSON 对象")
        # ---------------------------------

        result = json.loads(json_str)
        return {
            "taste": result.get('taste'),
            "budget": result.get('budget'),
            "time": result.get('time'),
            "people": result.get('people')
        }

    except Exception as e:
        print(f"MiniMax API 调用失败: {e}")
        return {"taste": None, "budget": None, "time": None, "people": None}