"""
餐厅数据模块 - 整合 Project 3 的学习数据
包含宁波诺丁汉大学及周边餐厅信息
"""

from dataclasses import dataclass, asdict
from typing import List, Optional

@dataclass
class Restaurant:
    """餐厅数据模型"""
    id: str
    name: str
    location: str
    price_range: str
    avg_price: int
    taste: str
    dishes: List[str]
    features: List[str]
    wait_time: int
    description: str
    recommendations: List[str]

# 从 Project 3 的 integrated_learning_data.json 导入的餐厅数据
RESTAURANTS = [
    Restaurant(
        id="R001",
        name="青海牛肉拉面",
        location="1食堂",
        price_range="10-15元",
        avg_price=12,
        taste="清淡",
        dishes=["牛肉拉面", "鸡丝拌面", "凉面"],
        features=["性价比高", "味道好", "热情的阿姨", "早上开得早"],
        wait_time=8,
        description="1食堂的老店，开很多年了，味道还不错。",
        recommendations=["早上可以来这里吃早餐", "鸡丝拌面是招牌"]
    ),
    Restaurant(
        id="R002",
        name="次坞打面",
        location="2食堂",
        price_range="12-18元",
        avg_price=15,
        taste="辣",
        dishes=["肉丝笋丁面", "汤面", "干拌面"],
        features=["性价比高", "分量足", "味道好", "加香菜绝配"],
        wait_time=10,
        description="2食堂的新宠，价格实惠满满一大碗，爱吃面的不二选择。",
        recommendations=["肉丝笋丁面加香菜是绝配", "有汤面和干拌面可选"]
    ),
    Restaurant(
        id="R003",
        name="淮南牛肉汤",
        location="小灶台",
        price_range="16-20元",
        avg_price=18,
        taste="清淡",
        dishes=["牛肉粉丝汤", "白切牛肉乌冬面", "虎皮凤爪"],
        features=["性价比高", "味道好", "分量足", "食材新鲜"],
        wait_time=12,
        description="量大，面条劲道，粉丝是粗粉，口感糯叽叽，佐以大量牛肉。",
        recommendations=["牛肉粉丝配饼很好吃", "汤底浓厚纯正"]
    ),
    Restaurant(
        id="R004",
        name="阿兰碧卡",
        location="行政楼-1层/图书馆",
        price_range="50-200元",
        avg_price=80,
        taste="西餐",
        dishes=["牛排", "披萨", "烤翅", "鸡肉卷", "奶昔"],
        features=["环境好", "白人饭", "拍照出片"],
        wait_time=20,
        description="校内的西餐厅，适合聚餐和约会。",
        recommendations=["钟楼店的烤翅强推", "图书馆店的鸡肉卷必吃", "奶昔很好喝"]
    ),
    Restaurant(
        id="R005",
        name="泰式打抛饭",
        location="宁诺后街",
        price_range="18-30元",
        avg_price=20,
        taste="辣",
        dishes=["双蛋打抛饭", "单蛋打抛饭", "泰式咖喱鸡肉饭", "牛杂饭"],
        features=["性价比高", "锅气香", "分量足", "现炒"],
        wait_time=15,
        description="宁诺后街的烟火气，猛火现炒满满的锅气香，一口穿越曼谷街头。",
        recommendations=["双蛋流心的快乐", "双蛋打抛饭20元性价比拉满", "配泰式奶红/奶绿更划算"]
    ),
    Restaurant(
        id="R006",
        name="喷泉牛杂六拼",
        location="小灶台",
        price_range="10-15元",
        avg_price=10,
        taste="清淡",
        dishes=["牛杂六拼", "牛心", "牛肠", "牛肺", "牛肚", "牛筋", "牛肉"],
        features=["性价比高", "味道好", "半价活动"],
        wait_time=8,
        description="满满一小碗，上面有花生、香菜、香葱、红辣椒粒点缀。",
        recommendations=["半价期间性价比超高", "牛筋超好吃", "适合当小吃"]
    ),
    Restaurant(
        id="R007",
        name="东北菜手工水饺",
        location="学府一号",
        price_range="30-40元",
        avg_price=35,
        taste="咸鲜",
        dishes=["锅包肉", "东北大拉皮", "地三鲜", "酸菜冻豆腐", "白菜猪肉饺子"],
        features=["性价比高", "味道正宗", "适合聚餐", "环境好"],
        wait_time=25,
        description="宁波大学生聚会必去的东北菜餐馆，8个人7个菜260r吃空盘。",
        recommendations=["锅包肉必点，外脆里嫩", "东北大拉皮每次必点", "人均30-40元"]
    ),
    Restaurant(
        id="R008",
        name="澳洲肉派",
        location="4食堂",
        price_range="25-35元",
        avg_price=30,
        taste="西餐",
        dishes=["鸡胸肉饭", "匈牙利牛肉饭", "洋葱肥牛饭"],
        features=["健康轻食", "少油少盐", "食材新鲜", "健身减脂"],
        wait_time=10,
        description="又健康又好吃的轻食，健身减脂人士可放心大胆冲。",
        recommendations=["鸡胸肉饭强推", "匈牙利牛肉饭很好吃", "洋葱肥牛饭推荐"]
    ),
    Restaurant(
        id="R009",
        name="麻辣香锅",
        location="2食堂",
        price_range="15-25元",
        avg_price=18,
        taste="辣",
        dishes=["麻辣香锅", "加油条版香锅"],
        features=["口感正宗", "物美价廉", "越吃越辣"],
        wait_time=12,
        description="2食堂的麻辣香锅比3食好吃，加油条超级好吃。",
        recommendations=["一定要加油条", "中辣越吃越辣很过瘾", "跟米饭绝配"]
    ),
    Restaurant(
        id="R010",
        name="章阿姨饺子店",
        location="4食堂",
        price_range="15-20元",
        avg_price=18,
        taste="清淡",
        dishes=["饺子", "南瓜粥"],
        features=["阿姨热情", "送饮料", "早上开得早"],
        wait_time=8,
        description="饺子味道还可以，南瓜粥超级好喝，招牌绝对是热情的阿姨。",
        recommendations=["南瓜粥超级好喝", "消费送饮料", "早上可以来喝粥"]
    ),
    Restaurant(
        id="R011",
        name="小辉烧烤",
        location="宁诺后街",
        price_range="20-40元",
        avg_price=30,
        taste="辣",
        dishes=["烤串", "鸡翅", "鸡腿", "掌中宝"],
        features=["老OG", "味道好", "入味"],
        wait_time=15,
        description="吃了三年还是喜欢他家的味道，非常入味。",
        recommendations=["吃了三年还是喜欢", "奥尔良蜜汁味好吃", "可以选择辣度"]
    ),
    Restaurant(
        id="R012",
        name="武汉黑鸭",
        location="宁诺后街",
        price_range="15-30元",
        avg_price=20,
        taste="辣",
        dishes=["热卤鸭货", "鸭脖", "鸭翅"],
        features=["干净", "入味", "阿姨人好"],
        wait_time=5,
        description="吃了后街所有的鸭货，这家是最好吃的。非常干净而且入味。",
        recommendations=["冬天可以加热后拌", "非常干净", "阿姨人超级好"]
    ),
]

# 小红书原始学习数据（用于 AI 生成推荐）
LEARNING_DATA = [
    "欢迎宁诺新生！1食堂就是很多大学都有的自选窗口，很普通味道中规中矩，一日三餐都有。价格都有标注，看自己的选择。我觉得不算贵，有时候10元不到就能吃一顿。",
    "2食堂的荣味盖浇饭（饭点很火的一家店），沙县小吃、次坞打面。除此之外还有黄焖鸡米饭、麻辣香锅、烧腊饭。",
    "3食堂有饺子米线店、轻食店、拉面店、煎饼店、里面还有一块可以自选称重的店叫'星期八'。",
    "4食堂有赛百味、焗饭店、煲仔饭店、米线店、章阿姨饺子店、砂锅店、日式拉面店、海南鸡饭、铁板饭、澳洲肉派（轻食）。",
    "阿兰碧卡：图书馆店鸡肉卷强推，太好吃了，去图书馆必吃。钟楼店薯条/德国香肠/鸡翅强推。",
    "小灶台：淮南牛肉粉丝汤配饼很好吃，做的很入味。西域烧烤是真羊肉，肥瘦相间。",
    "后街美食：泰式打抛饭猛火现炒满满的锅气香，销魂鸡翅奥尔良蜜汁味，武汉黑鸭干净入味。",
    "周边美食：学府一号东北菜手工水饺（锅包肉必点），万象汇厨创（锅包肉顶中之顶），南来北往粥底火锅。",
]

def get_restaurants_by_taste(taste: Optional[str] = None) -> List[Restaurant]:
    """根据口味筛选餐厅"""
    if not taste:
        return RESTAURANTS
    return [r for r in RESTAURANTS if taste in r.taste or any(taste in f for f in r.features)]

def get_restaurants_by_budget(budget: Optional[int] = None) -> List[Restaurant]:
    """根据预算筛选餐厅"""
    if not budget:
        return RESTAURANTS
    return [r for r in RESTAURANTS if r.avg_price <= budget]

def get_restaurants_by_time(time_limit: Optional[int] = None) -> List[Restaurant]:
    """根据时间筛选餐厅"""
    if not time_limit:
        return RESTAURANTS
    return [r for r in RESTAURANTS if r.wait_time <= time_limit]

def search_restaurants(taste: Optional[str] = None, 
                      budget: Optional[int] = None, 
                      time_limit: Optional[int] = None) -> List[Restaurant]:
    """综合筛选餐厅"""
    result = RESTAURANTS.copy()
    
    if taste:
        taste_lower = taste.lower()
        result = [r for r in result if 
                  (r.taste and taste_lower in r.taste.lower()) or 
                  (r.features and any(taste_lower in f.lower() for f in r.features)) or
                  (r.dishes and any(taste_lower in d.lower() for d in r.dishes))]
    if budget:
        result = [r for r in result if r.avg_price <= budget]
    if time_limit:
        result = [r for r in result if r.wait_time <= time_limit]
    
    return result

def get_learning_context() -> str:
    """获取学习数据上下文，用于 AI 推荐"""
    return "\n".join(LEARNING_DATA)

def restaurant_to_dict(r: Restaurant) -> dict:
    """将餐厅对象转换为字典"""
    return asdict(r)

# 在 restaurant_data.py 末尾添加

import json
import os

DATA_FILE = os.path.join(os.path.dirname(__file__), 'data', 'restaurants.json')
os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)

def save_restaurants_to_file():
    """将当前 RESTAURANTS 列表保存到文件"""
    try:
        data = [asdict(r) for r in RESTAURANTS]
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[INFO] 已保存 {len(data)} 家餐厅到 {DATA_FILE}")
    except Exception as e:
        print(f"[ERROR] 保存餐厅数据失败: {e}")

def load_restaurants_from_file():
    """从文件加载餐厅数据，合并到 RESTAURANTS（如果文件存在）"""
    global RESTAURANTS
    if not os.path.exists(DATA_FILE):
        print("[INFO] 未找到餐厅数据文件，使用默认数据")
        return
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 转换为 Restaurant 对象
        loaded = [Restaurant(**item) for item in data]
        # 合并：默认数据优先，文件数据追加（去重按 id）
        existing_ids = {r.id for r in RESTAURANTS}
        for r in loaded:
            if r.id not in existing_ids:
                RESTAURANTS.append(r)
        print(f"[INFO] 从文件加载了 {len(loaded)} 家餐厅，当前共 {len(RESTAURANTS)} 家")
    except Exception as e:
        print(f"[ERROR] 加载餐厅数据失败: {e}")