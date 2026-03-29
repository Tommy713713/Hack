import pymysql
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

# 模拟菜品数据（当数据库不可用时使用）
MOCK_DISHES = [
    {"sid": "D001", "sname": "水煮鱼", "staste": "辣,川菜", "sprice": "28", "stime": "15"},
    {"sid": "D002", "sname": "番茄鸡蛋面", "staste": "清淡", "sprice": "12", "stime": "8"},
    {"sid": "D003", "sname": "麻辣香锅", "staste": "辣", "sprice": "18", "stime": "12"},
    {"sid": "D004", "sname": "清蒸鲈鱼", "staste": "清淡", "sprice": "35", "stime": "20"},
    {"sid": "D005", "sname": "宫保鸡丁", "staste": "辣", "sprice": "22", "stime": "10"},
    {"sid": "D006", "sname": "蒜蓉西兰花", "staste": "清淡", "sprice": "10", "stime": "5"},
    {"sid": "D007", "sname": "麻婆豆腐", "staste": "辣", "sprice": "12", "stime": "7"},
    {"sid": "D008", "sname": "红烧肉", "staste": "咸鲜", "sprice": "25", "stime": "18"},
    {"sid": "D009", "sname": "酸辣土豆丝", "staste": "辣,酸", "sprice": "8", "stime": "6"},
    {"sid": "D010", "sname": "白切鸡", "staste": "清淡,粤菜", "sprice": "30", "stime": "15"},
]

# 内存中的查询记录
query_history = []

def get_db_connection():
    """获取 MySQL 数据库连接"""
    return pymysql.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'ai_canteen'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

def insert_user_query(taste, budget, time_limit, people):
    """
    将提取的参数存入 ai_canteen_assistant 表
    sno 使用 UUID 前20位作为主键
    """
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 生成主键：UUID 前20位（去掉横线）
            sno = uuid.uuid4().hex[:20]
            sql = """
                INSERT INTO ai_canteen_assistant 
                (sno, staste, sbudget, stime, speople) 
                VALUES (%s, %s, %s, %s, %s)
            """
            # 将数字转为字符串存储（表字段为 varchar）
            budget_str = str(budget) if budget is not None else None
            time_str = str(time_limit) if time_limit is not None else None
            people_str = str(people) if people is not None else None
            cursor.execute(sql, (sno, taste, budget_str, time_str, people_str))
        conn.commit()
        conn.close()
    except Exception as e:
        # 数据库不可用时，保存到内存
        query_history.append({
            "sno": uuid.uuid4().hex[:20],
            "staste": taste,
            "sbudget": budget,
            "stime": time_limit,
            "speople": people
        })
        print(f"[MOCK] 保存查询记录到内存: taste={taste}, budget={budget}")

def query_dishes(taste=None, budget=None, time_limit=None):
    """查询菜品，优先使用数据库，不可用时使用模拟数据"""
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT * FROM dish WHERE 1=1"
            params = []

            if taste:
                sql += " AND staste LIKE %s"
                params.append(f'%{taste}%')
            if budget is not None:
                sql += " AND CAST(sprice AS DECIMAL(10,2)) <= %s"
                params.append(budget)
            if time_limit is not None:
                sql += " AND CAST(stime AS SIGNED) <= %s"
                params.append(time_limit)

            sql += " ORDER BY sid LIMIT 5"
            cursor.execute(sql, params)
            result = cursor.fetchall()
        conn.close()
        return result
    except Exception as e:
        # 数据库不可用时，使用内存中的模拟数据
        print(f"[MOCK] 使用模拟数据查询: taste={taste}, budget={budget}, time={time_limit}")
        result = MOCK_DISHES.copy()
        
        # 应用筛选条件
        if taste:
            result = [d for d in result if taste in d['staste']]
        if budget is not None:
            result = [d for d in result if float(d['sprice']) <= budget]
        if time_limit is not None:
            result = [d for d in result if int(d['stime']) <= time_limit]
        
        return result[:5]
