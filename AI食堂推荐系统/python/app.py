#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Canteen Pilot - Flask API Service
基于新的数据爬取程序的API服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import os
import sys
import json
from datetime import datetime

# 添加src目录到Python路径
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from ai_canteen_pilot_chat import AICanteenPilot

app = Flask(__name__)
CORS(app)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'zzh061218',
    'database': 'canteen',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 全局变量
pilot = None

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def init_database():
    """初始化数据库表"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            # 创建食堂食物表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS canteen_foods (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    taste VARCHAR(50),
                    price INT,
                    wait_time INT,
                    location VARCHAR(100),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_taste (taste),
                    INDEX idx_price (price),
                    INDEX idx_wait_time (wait_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
            # 创建用户偏好表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    taste VARCHAR(50),
                    budget INT,
                    time INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            ''')
        connection.commit()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

def save_canteen_data(name, taste, price, wait_time, location, description):
    """保存抓取的数据到数据库"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = '''
                INSERT INTO canteen_foods (name, taste, price, wait_time, location, description)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                taste = VALUES(taste),
                price = VALUES(price),
                wait_time = VALUES(wait_time),
                location = VALUES(location),
                description = VALUES(description)
            '''
            cursor.execute(sql, (name, taste, price, wait_time, location, description))
        connection.commit()
        print(f"✅ Saved canteen data: {name}")
    except Exception as e:
        print(f"❌ Error saving canteen data: {e}")
    finally:
        if 'connection' in locals():
            connection.close()

def extract_and_store_canteen_info(learning_data):
    """从学习数据中提取并存储食堂信息"""
    print("🔄 Extracting and storing canteen information...")
    
    # 从学习数据中提取食堂信息
    canteen_data = []
    
    for data in learning_data:
        text = str(data).lower()
        
        # 提取食堂名称
        name = None
        if '食堂' in text:
            # 尝试提取食堂名称
            import re
            name_match = re.search(r'([^，。；；\n]*?食堂)', text)
            if name_match:
                name = name_match.group(1).strip()
            else:
                # 如果没有匹配到，使用默认名称
                name = "食堂"
        
        # 提取价格信息
        price = None
        price_match = re.search(r'(\d+)\s*[元块钱]', text)
        if price_match:
            price = int(price_match.group(1))
        
        # 提取口味信息
        taste = None
        taste_keywords = ['川菜', '粤菜', '鲁菜', '淮扬菜', '闽菜', '浙菜', '湘菜', '徽菜', '清真', '西餐', '中餐', '快餐', '辣', '清淡', '甜', '咸']
        for keyword in taste_keywords:
            if keyword in text:
                taste = keyword
                break
        
        # 提取等待时间
        wait_time = None
        time_match = re.search(r'(\d+)\s*[分钟分min]', text)
        if time_match:
            wait_time = int(time_match.group(1))
        
        # 提取位置信息
        location = None
        location_keywords = ['东区', '西区', '北区', '南区', '留学生公寓', '校园']
        for keyword in location_keywords:
            if keyword in text:
                location = keyword
                break
        
        # 如果提取到了有用的信息，就保存
        if name or price or taste:
            canteen_data.append({
                'name': name or '未知食堂',
                'taste': taste or '中餐',
                'price': price or 20,
                'wait_time': wait_time or 15,
                'location': location or '校园',
                'description': text[:100] if len(text) > 100 else text
            })
    
    # 如果没有提取到数据，使用示例数据
    if not canteen_data:
        print("⚠️  No canteen data extracted from learning data, using sample data")
        canteen_data = [
            {
                'name': '第一食堂',
                'taste': '中餐',
                'price': 15,
                'wait_time': 10,
                'location': '校园东区',
                'description': '经济实惠，种类丰富'
            },
            {
                'name': '第二食堂',
                'taste': '川菜',
                'price': 20,
                'wait_time': 15,
                'location': '校园西区',
                'description': '口味偏辣，特色菜丰富'
            },
            {
                'name': '清真食堂',
                'taste': '清真',
                'price': 18,
                'wait_time': 12,
                'location': '校园北区',
                'description': '清真风味，干净卫生'
            },
            {
                'name': '西餐厅',
                'taste': '西餐',
                'price': 35,
                'wait_time': 20,
                'location': '留学生公寓',
                'description': '西式料理，环境优雅'
            }
        ]
    
    # 保存到数据库
    for item in canteen_data:
        save_canteen_data(
            item['name'],
            item['taste'],
            item['price'],
            item['wait_time'],
            item['location'],
            item['description']
        )
    
    print(f"✅ Canteen data extraction and storage completed. Total items: {len(canteen_data)}")

def extract_and_store_ai_canteen_info(ai_content):
    """从AI生成的内容中提取并存储食堂信息"""
    print("🔄 Extracting and storing AI-generated canteen information...")
    
    # 从AI内容中提取食堂信息
    canteen_data = []
    
    # 分割AI内容为多个推荐项
    import re
    items = re.split(r'[0-9]+\.', ai_content)
    
    for item in items:
        text = item.strip()
        if not text:
            continue
        
        # 提取食堂名称
        name = None
        name_match = re.search(r'([^，。；；\n]*?食堂)', text)
        if not name_match:
            name_match = re.search(r'推荐：([^，。；；\n]+)', text)
        if name_match:
            name = name_match.group(1).strip()
        
        # 提取价格信息
        price = None
        price_match = re.search(r'(\d+)\s*[元块钱]', text)
        if price_match:
            price = int(price_match.group(1))
        
        # 提取口味信息
        taste = None
        taste_keywords = ['川菜', '粤菜', '鲁菜', '淮扬菜', '闽菜', '浙菜', '湘菜', '徽菜', '清真', '西餐', '中餐', '快餐', '辣', '清淡', '甜', '咸']
        for keyword in taste_keywords:
            if keyword in text:
                taste = keyword
                break
        
        # 提取等待时间
        wait_time = None
        time_match = re.search(r'(\d+)\s*[分钟分min]', text)
        if time_match:
            wait_time = int(time_match.group(1))
        
        # 提取位置信息
        location = None
        location_keywords = ['东区', '西区', '北区', '南区', '留学生公寓', '校园']
        for keyword in location_keywords:
            if keyword in text:
                location = keyword
                break
        
        # 如果提取到了有用的信息，就保存
        if name or price or taste:
            canteen_data.append({
                'name': name or '未知食堂',
                'taste': taste or '中餐',
                'price': price or 20,
                'wait_time': wait_time or 15,
                'location': location or '校园',
                'description': text[:100] if len(text) > 100 else text
            })
    
    # 保存到数据库
    for item in canteen_data:
        save_canteen_data(
            item['name'],
            item['taste'],
            item['price'],
            item['wait_time'],
            item['location'],
            item['description']
        )
    
    print(f"✅ AI-generated canteen data extraction and storage completed. Total items: {len(canteen_data)}")
    return len(canteen_data)

@app.route('/')
def index():
    """根路径"""
    return jsonify({
        'success': True,
        'message': 'AI Canteen Pilot API is running',
        'endpoints': {
            '/api/recommend': 'POST - Get food recommendations',
            '/api/crawl': 'POST - Crawl and store canteen data',
            '/api/health': 'GET - Health check'
        }
    })

@app.route('/api/health')
def health():
    """健康检查"""
    return jsonify({
        'success': True,
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/crawl', methods=['POST'])
def crawl_and_store():
    """爬取并存储食堂数据"""
    try:
        if pilot and pilot.learning_data:
            extract_and_store_canteen_info(pilot.learning_data)
        else:
            # 即使没有学习数据，也保存一些示例数据
            extract_and_store_canteen_info([])
        
        return jsonify({
            'success': True,
            'message': 'Data crawled and stored successfully'
        })
    except Exception as e:
        print(f"❌ Error in crawl_and_store: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/recommend', methods=['POST'])
def recommend():
    """获取推荐"""
    try:
        data = request.json
        user_input = data.get('user_input', '')
        
        print(f"📥 Received recommendation request: {user_input}")
        
        # 使用新的AI Canteen Pilot生成响应
        recommendation = "抱歉，AI服务暂时不可用"
        if pilot:
            recommendation = pilot.generate_response(user_input)
            print(f"🤖 AI Generated Content: {recommendation}")
            # 从AI生成的内容中提取并存储食堂信息
            count = extract_and_store_ai_canteen_info(recommendation)
            print(f"📊 Extracted and stored {count} items from AI content")
        
        # 同时从数据库获取基础推荐
        connection = get_db_connection()
        db_recommendations = []
        try:
            with connection.cursor() as cursor:
                # 先查询总记录数
                cursor.execute('SELECT COUNT(*) as total FROM canteen_foods')
                total = cursor.fetchone()['total']
                print(f"📊 Total records in database: {total}")
                
                # 按创建时间倒序获取最新的5条记录
                cursor.execute('SELECT * FROM canteen_foods ORDER BY created_at DESC LIMIT 5')
                db_recommendations = cursor.fetchall()
                print(f"📊 Retrieved {len(db_recommendations)} recommendations from database")
                for rec in db_recommendations:
                    print(f"  - {rec.get('name', 'Unknown')}: {rec.get('taste', 'Unknown')}, {rec.get('price', 0)}元")
        except Exception as e:
            print(f"❌ Error fetching from database: {e}")
        finally:
            connection.close()
        
        # 格式化数据库推荐结果
        formatted_recommendations = []
        for item in db_recommendations:
            formatted_recommendations.append({
                'name': item.get('name', ''),
                'taste': item.get('taste', ''),
                'price': item.get('price', 0),
                'waitTime': item.get('wait_time', 0),
                'location': item.get('location', ''),
                'description': item.get('description', '')
            })
        
        return jsonify({
            'success': True,
            'recommendation': recommendation,
            'recommendations': formatted_recommendations
        })
        
    except Exception as e:
        print(f"❌ Error in recommend: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'recommendation': '抱歉，处理您的请求时出现了错误'
        }), 500

def main():
    """主函数"""
    global pilot
    
    # 初始化数据库
    init_database()
    
    # 初始化AI Canteen Pilot
    print("🔧 Initializing AI Canteen Pilot...")
    api_key = "sk-cp-D8nMKAO11UQXliAaXe-SKjXW19VlCMZpskP8ggVSoQUhxYbJP3PT9FLVfR64cEH0fEhAOVIwPAZp5HDRI18ZVQPOi2nOVe1LT_nPXTMP0Urr9PnQEmVGvlM"
    
    try:
        pilot = AICanteenPilot(api_key=api_key)
        print("✅ AI Canteen Pilot initialized successfully")
    except Exception as e:
        print(f"❌ Error initializing AI Canteen Pilot: {e}")
        pilot = None
    
    # 爬取并存储数据
    print("🔄 Starting data crawling...")
    try:
        if pilot:
            # 搜索宁波诺丁汉大学食堂信息
            pilot.search_unnc_canteen_info()
            # 存储数据到数据库
            extract_and_store_canteen_info(pilot.learning_data)
        else:
            # 即使没有pilot，也存储一些示例数据
            extract_and_store_canteen_info([])
        print("✅ Data crawling and storage completed")
    except Exception as e:
        print(f"❌ Error during data crawling: {e}")
    
    # 启动Flask服务
    print("🚀 Starting Flask API server...")
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    main()
