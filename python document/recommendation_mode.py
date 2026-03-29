"""
推荐模式模块 - 处理用户推荐餐厅并学习
当用户输入"推荐模式"时，AI进入学习状态，提取餐厅信息
"""

import os
import json
import re
from typing import Dict, Optional

from restaurant_data import Restaurant, RESTAURANTS, save_restaurants_to_file

# 用户推荐保存文件
USER_RECOMMENDATIONS_FILE = os.path.join(os.path.dirname(__file__), 'data', 'user_recommendations.json')
os.makedirs(os.path.dirname(USER_RECOMMENDATIONS_FILE), exist_ok=True)


class RecommendationModeManager:
    """推荐模式管理器 - 单例模式，管理状态和餐厅添加"""
    _instance = None
    _is_active = False

    def __new__(cls, api_key=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
            cls._instance.base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.us/v1")
        return cls._instance

    @classmethod
    def get_instance(cls, api_key=None):
        if cls._instance is None:
            cls._instance = cls(api_key)
        return cls._instance

    @classmethod
    def is_active(cls):
        return cls._is_active

    @classmethod
    def set_active(cls, active):
        cls._is_active = active

    def check_activation(self, user_input: str) -> bool:
        activation_keywords = ["推荐模式"]
        user_input_lower = user_input.lower()
        for kw in activation_keywords:
            if kw in user_input_lower:
                return True
        return False

    def get_activation_message(self) -> str:
        return """🎉 进入推荐模式！

我是爱干饭的前辈，现在你可以向我推荐好吃的餐厅啦～

请告诉我：
1️⃣ 餐厅名称
2️⃣ 位置（在哪个食堂/后街/校外）
3️⃣ 人均价格
4️⃣ 推荐菜品
5️⃣ 特色/推荐理由

你可以像聊天一样说：
"我想推荐2食堂的麻辣香锅，人均18块，加油条特别好吃，越吃越辣很过瘾"

我会自动提取信息并记录下来，帮更多学弟学妹发现美食！🍜

输入"退出"可以随时离开推荐模式～"""

    def extract_restaurant_info(self, user_input: str) -> Optional[Dict]:
        """提取餐厅信息 - 规则优先，AI兜底"""
        # 检查是否是激活或退出关键词
        if self.check_activation(user_input) or self.check_exit(user_input):
            return None
            
        rule_result = self._extract_by_rules(user_input)
        if rule_result and rule_result.get("name"):
            print(f"[规则提取成功] {rule_result['name']}")
            return rule_result

        if self.api_key:
            ai_result = self._extract_by_ai(user_input)
            if ai_result:
                return ai_result

        return rule_result

    def _extract_by_rules(self, user_input: str) -> Optional[Dict]:
        user_input = user_input.strip()
        name = None

        # 提取名称
        name_match = re.search(r'推荐[了]?(?:一家|个)?(.+?)(?:，|,|\.|。|$|\s)', user_input)
        if name_match:
            name = name_match.group(1).strip()
        if not name:
            name_match = re.search(r'^(.+?)(?:（|\()(.+?)(?:）|\))[:：]', user_input)
            if name_match:
                name = name_match.group(1).strip()
        if not name:
            first_sentence = re.split(r'[。！？\n]', user_input)[0]
            if len(first_sentence) < 20:
                name = first_sentence.strip()

        if not name or len(name) < 2:
            return None

        # 位置
        location = "未知"
        location_patterns = [
            r'(?:位于|在|地址[:：]?)\s*(.+?)(?:，|,|\.|。|$|\s)',
            r'[（(](.+?)[）)]',
            r'(1食堂|一食堂|2食堂|二食堂|3食堂|三食堂|4食堂|四食堂|后街|校外|图书馆|行政楼|学府壹号|学府一号|万象汇|天一广场)',
        ]
        for pattern in location_patterns:
            match = re.search(pattern, user_input)
            if match:
                location = match.group(1).strip() if match.lastindex else match.group(1).strip()
                break

        # 价格
        avg_price = 20
        price_match = re.search(r'(?:人均[:：]?)?\s*(\d+)[元块]', user_input)
        if price_match:
            avg_price = int(price_match.group(1))

        # 口味
        taste = "未知"
        taste_map = {'辣': '辣', '麻辣': '辣', '清淡': '清淡', '西餐': '西餐', '甜': '甜', '酸': '酸', '咸': '咸鲜', '鲜': '咸鲜'}
        for kw, val in taste_map.items():
            if kw in user_input:
                taste = val
                break

        # 菜品
        dishes = []
        dish_match = re.search(r'(?:推荐|特色|招牌)[:：]?(.+?)(?:，|,|\.|。|$)', user_input)
        if dish_match:
            dishes_text = dish_match.group(1)
            dishes = [d.strip() for d in re.split(r'[、，,]', dishes_text) if d.strip()][:3]

        # 特色
        features = []
        feature_keywords = ['性价比高', '味道好', '分量足', '环境好', '服务好', '食材新鲜', '烟火气', '正宗']
        for kw in feature_keywords:
            if kw in user_input:
                features.append(kw)

        # 描述
        description = f"用户推荐的餐厅：{name}"
        desc_match = re.search(r'[:：](.+?)(?:人均|价格|地址|$)', user_input)
        if desc_match:
            desc_text = desc_match.group(1).strip()[:50]
            if len(desc_text) > 10:
                description = desc_text

        return {
            "name": name,
            "location": location,
            "price_range": f"{avg_price-5}-{avg_price+5}元",
            "avg_price": avg_price,
            "taste": taste,
            "dishes": dishes,
            "features": features,
            "wait_time": 10,
            "description": description,
            "recommendations": ["用户推荐"]
        }

    def _extract_by_ai(self, user_input: str) -> Optional[Dict]:
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.minimax.chat/v1"   # 确保此 URL 正确
            )

            system_prompt = """你是一个餐厅信息提取助手。从用户输入中提取餐厅信息，返回JSON。

字段：
- name: 餐厅名称
- location: 位置（1食堂/2食堂/3食堂/4食堂/后街/校外等）
- avg_price: 人均价格（数字）
- taste: 口味（辣/清淡/西餐等）
- dishes: 推荐菜品（数组）
- features: 特色（数组）
- description: 描述

返回格式示例：
{"name": "麻辣香锅", "location": "2食堂", "avg_price": 18, "taste": "辣", "dishes": ["油条"], "features": ["性价比高"], "description": "2食堂的麻辣香锅"}

如果有多个餐厅，请返回JSON数组：
[{"name": "餐厅1", ...}, {"name": "餐厅2", ...}]

只返回JSON，不要其他文字。"""

            user_prompt = f"用户输入：{user_input}"

            response = client.chat.completions.create(
                model="MiniMax-M2.7",  # 或 "abab6.5s-chat"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1,
                max_tokens=500
            )

            reply = response.choices[0].message.content
            print(f"[AI提取] 返回: {reply}")

            # 提取 JSON
            import json, re
            
            # 尝试提取 JSON 数组或对象
            json_str = reply.strip()
            
            # 移除可能的 markdown 代码块
            if json_str.startswith('```json'):
                json_str = json_str[7:]
            if json_str.endswith('```'):
                json_str = json_str[:-3]
            json_str = json_str.strip()
            
            try:
                # 尝试解析 JSON
                data = json.loads(json_str)
                
                # 检查是否是数组
                if isinstance(data, list):
                    # 处理多个餐厅
                    if len(data) > 0:
                        # 处理第一个餐厅
                        restaurant_data = data[0]
                        # 处理剩余餐厅
                        for i in range(1, len(data)):
                            next_restaurant = data[i]
                            if next_restaurant.get("name"):
                                # 数据清洗
                                if isinstance(next_restaurant.get("avg_price"), str):
                                    try:
                                        next_restaurant["avg_price"] = int(re.findall(r'\d+', next_restaurant["avg_price"])[0])
                                    except:
                                        next_restaurant["avg_price"] = 20
                                elif not isinstance(next_restaurant.get("avg_price"), int):
                                    next_restaurant["avg_price"] = 20
                                
                                next_restaurant.setdefault("price_range", f"{next_restaurant['avg_price']-5}-{next_restaurant['avg_price']+5}元")
                                next_restaurant.setdefault("wait_time", 10)
                                next_restaurant.setdefault("description", f"{next_restaurant.get('location', '未知')}的{next_restaurant['name']}")
                                next_restaurant.setdefault("recommendations", ["用户推荐"])
                                
                                for field in ["dishes", "features", "recommendations"]:
                                    if field not in next_restaurant or not isinstance(next_restaurant[field], list):
                                        next_restaurant[field] = []
                                
                                # 添加餐厅
                                self.add_restaurant(next_restaurant)
                    else:
                        return None
                else:
                    # 处理单个餐厅
                    restaurant_data = data
            except json.JSONDecodeError:
                # 如果解析失败，尝试提取第一个 JSON 对象
                json_match = re.search(r'\{[\s\S]*?\}', reply)
                if not json_match:
                    return None
                json_str = json_match.group(0)
                try:
                    restaurant_data = json.loads(json_str)
                except:
                    return None

            if not restaurant_data.get("name"):
                return None

            # 数据清洗
            if isinstance(restaurant_data.get("avg_price"), str):
                try:
                    restaurant_data["avg_price"] = int(re.findall(r'\d+', restaurant_data["avg_price"])[0])
                except:
                    restaurant_data["avg_price"] = 20
            elif not isinstance(restaurant_data.get("avg_price"), int):
                restaurant_data["avg_price"] = 20

            restaurant_data.setdefault("price_range", f"{restaurant_data['avg_price']-5}-{restaurant_data['avg_price']+5}元")
            restaurant_data.setdefault("wait_time", 10)
            restaurant_data.setdefault("description", f"{restaurant_data.get('location', '未知')}的{restaurant_data['name']}")
            restaurant_data.setdefault("recommendations", ["用户推荐"])

            for field in ["dishes", "features", "recommendations"]:
                if field not in restaurant_data or not isinstance(restaurant_data[field], list):
                    restaurant_data[field] = []

            return restaurant_data

        except Exception as e:
            print(f"[AI提取异常] {e}")
            return None

    def add_restaurant(self, restaurant_data: Dict) -> bool:
        try:
            existing_ids = [int(r.id[1:]) for r in RESTAURANTS if r.id.startswith('R')]
            new_id = f"R{max(existing_ids) + 1 if existing_ids else 1:03d}"
            new_restaurant = Restaurant(
                id=new_id,
                name=restaurant_data.get("name", "未知餐厅"),
                location=restaurant_data.get("location", "未知位置"),
                price_range=restaurant_data.get("price_range", "未知"),
                avg_price=restaurant_data.get("avg_price", 20),
                taste=restaurant_data.get("taste", "未知"),
                dishes=restaurant_data.get("dishes", []),
                features=restaurant_data.get("features", []),
                wait_time=restaurant_data.get("wait_time", 10),
                description=restaurant_data.get("description", ""),
                recommendations=restaurant_data.get("recommendations", [])
            )
            RESTAURANTS.append(new_restaurant)
            save_restaurants_to_file()  # 持久化完整列表
            # 单独保存用户推荐记录（可选）
            self._save_user_recommendation(restaurant_data)
            print(f"✅ 成功添加餐厅: {new_restaurant.name} (ID: {new_id})")
            return True
        except Exception as e:
            print(f"❌ 添加餐厅失败: {e}")
            return False

    def _save_user_recommendation(self, restaurant_data: Dict):
        try:
            existing = []
            if os.path.exists(USER_RECOMMENDATIONS_FILE):
                with open(USER_RECOMMENDATIONS_FILE, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            existing.append(restaurant_data)
            with open(USER_RECOMMENDATIONS_FILE, 'w', encoding='utf-8') as f:
                json.dump(existing, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[警告] 保存用户推荐失败: {e}")

    def check_exit(self, user_input: str) -> bool:
        exit_keywords = ["退出", "结束", "离开", "拜拜", "再见", "谢谢", "不推荐了", "先这样"]
        return any(kw in user_input.lower() for kw in exit_keywords)

    def _is_query_intent(self, user_input: str) -> bool:
        """判断用户输入是否是查询意图（而不是推荐餐厅）"""
        query_patterns = [
            "有没有", "哪里有", "在哪", "附近", "推荐", "什么好吃",
            "好吃吗", "味道", "怎么样", "评价", "价格", "人均",
            "营业时间", "开门", "几点", "怎么去", "多远"
        ]
        user_lower = user_input.lower()
        return any(pattern in user_lower for pattern in query_patterns)

    def get_exit_message(self) -> str:
        self.set_active(False)
        return "👋 已退出推荐模式！感谢你的分享，学弟学妹们会感谢你的～\n\n现在可以正常询问餐厅推荐啦！"


def process_recommendation_mode(user_input: str, api_key: str = None) -> Optional[Dict]:
    """处理推荐模式的主函数，返回 { is_recommendation_mode, message, restaurant_added, restaurant_data }"""
    manager = RecommendationModeManager.get_instance(api_key)

    # 激活推荐模式
    if not manager.is_active() and manager.check_activation(user_input):
        manager.set_active(True)
        return {
            "is_recommendation_mode": True,
            "message": manager.get_activation_message(),
            "restaurant_added": False
        }

    # 不在推荐模式
    if not manager.is_active():
        return None

    # 检查退出
    if manager.check_exit(user_input):
        return {
            "is_recommendation_mode": True,
            "message": manager.get_exit_message(),
            "restaurant_added": False
        }

    # 检查是否是查询意图
    if manager._is_query_intent(user_input):
        manager.set_active(False)  # 自动退出推荐模式
        return None  # 让主流程处理该查询

    # 提取餐厅信息
    restaurant_data = manager.extract_restaurant_info(user_input)

    if restaurant_data and restaurant_data.get("name"):
        success = manager.add_restaurant(restaurant_data)
        if success:
            return {
                "is_recommendation_mode": True,
                "message": f"🎉 太棒了！成功记录下 **{restaurant_data['name']}** ！\n\n📍 位置：{restaurant_data['location']}\n💰 人均：{restaurant_data['avg_price']}元\n🍽️ 菜品：{', '.join(restaurant_data['dishes'][:3]) if restaurant_data['dishes'] else '待补充'}\n\n还有其他餐厅想推荐吗？继续告诉我，或者输入 退出 离开推荐模式～",
                "restaurant_added": True,
                "restaurant_data": restaurant_data
            }
        else:
            return {
                "is_recommendation_mode": True,
                "message": "抱歉，记录餐厅信息时出了点问题。请再试一次，或者换个方式描述～",
                "restaurant_added": False
            }
    else:
        return {
            "is_recommendation_mode": True,
            "message": "我没太听懂呢～请告诉我餐厅名称和位置，比如：\n我想推荐2食堂的麻辣香锅，人均18块，加油条特别好吃",
            "restaurant_added": False
        }