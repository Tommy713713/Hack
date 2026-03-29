from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import logging
import os

load_dotenv()  # 统一加载环境变量

from db import insert_user_query, query_dishes
from minimax_client import extract_params_with_minimax
from ai_recommender import get_dual_recommendations
from recommendation_mode import process_recommendation_mode   # 新增导入
from restaurant_data import load_restaurants_from_file, save_restaurants_to_file  # 确保持久化函数存在

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
CORS(app)

# 获取 API Key
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")

# 启动时加载餐厅数据
load_restaurants_from_file()  # 如果文件存在则加载，否则保持默认

@app.route('/api/recommend', methods=['POST'])
def recommend():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "缺少 query 字段"}), 400

    user_query = data['query'].strip()
    if not user_query:
        return jsonify({"error": "query 不能为空"}), 400

    # 1. 检查是否进入推荐模式
    recommendation_result = process_recommendation_mode(user_query, MINIMAX_API_KEY)
    if recommendation_result:
        # 用户处于推荐模式，返回推荐模式的响应（前端需根据 is_recommendation_mode 处理）
        return jsonify({
            "is_recommendation_mode": True,
            "message": recommendation_result["message"],
            "restaurant_added": recommendation_result.get("restaurant_added", False),
            "restaurant_data": recommendation_result.get("restaurant_data"),
            "recommendations": [],
            "ai_recommendation": recommendation_result["message"],
            "matched_count": 0,
            "extracted_params": {}
        })

    # 2. 正常推荐流程
    try:
        params = extract_params_with_minimax(user_query)
    except Exception as e:
        app.logger.error(f"AI 提取失败: {e}")
        params = {"taste": None, "budget": None, "time": None, "people": None}

    taste = params.get('taste')
    budget = params.get('budget')
    time_limit = params.get('time')
    people = params.get('people')

    try:
        insert_user_query(taste, budget, time_limit, people)
    except Exception as e:
        app.logger.error(f"插入历史记录失败: {e}")

    try:
        result = get_dual_recommendations(
            user_query=user_query,
            taste=taste,
            budget=budget,
            time_limit=time_limit,
            api_key=MINIMAX_API_KEY
        )
        return jsonify({
            "is_recommendation_mode": False,
            "recommendations": result["structured"],
            "ai_recommendation": result["ai_recommendation"],
            "matched_count": result["matched_count"],
            "extracted_params": {
                "taste": taste,
                "budget": budget,
                "time": time_limit,
                "people": people
            }
        })
    except Exception as e:
        app.logger.error(f"推荐生成失败: {e}")
        return jsonify({"error": "推荐生成失败"}), 500


# 其他接口保持不变...
@app.route('/api/recommend/legacy', methods=['POST'])
def recommend_legacy():
    # ... 原有代码 ...
    pass

@app.route('/api/restaurants', methods=['GET'])
def get_all_restaurants():
    """获取所有餐厅数据"""
    from restaurant_data import RESTAURANTS, restaurant_to_dict
    
    return jsonify({
        "restaurants": [restaurant_to_dict(r) for r in RESTAURANTS],
        "total": len(RESTAURANTS)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)