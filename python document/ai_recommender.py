"""
AI 智能推荐模块 - 基于 Project 3 的推荐逻辑
使用 MiniMax API 生成个性化推荐文案
"""

import os
import json
from typing import List, Dict, Optional
from restaurant_data import Restaurant, search_restaurants, get_learning_context, restaurant_to_dict

class AIRecommender:
    """AI 智能推荐器"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("MINIMAX_API_KEY", "")
        self.base_url = os.getenv("MINIMAX_BASE_URL", "https://api.minimax.chat/v1")
        self.conversation_history: List[Dict[str, str]] = []
        
    def generate_ai_recommendation(self, 
                                   user_query: str,
                                   matched_restaurants: List[Restaurant],
                                   taste: Optional[str] = None,
                                   budget: Optional[int] = None,
                                   time_limit: Optional[int] = None) -> str:
        """
        使用 MiniMax API 生成个性化推荐文案
        """
        if not self.api_key:
            return self._generate_fallback_recommendation(matched_restaurants)
        
        try:
            # 构建餐厅信息上下文
            restaurants_info = "\n".join([
                f"- {r.name}（{r.location}）：{r.description} 人均{r.avg_price}元，特色：{', '.join(r.features)}，推荐：{', '.join(r.recommendations)}"
                for r in matched_restaurants[:5]
            ])
            
            # 构建系统提示
            system_prompt = f"""你是宁波诺丁汉大学的"爱干饭的前辈"，一个亲切的学姐/学长，专门给学弟学妹推荐校园美食。

你的特点：
1. 语气亲切、活泼，像真正的学长学姐给建议
2. 会添加校园梗，增加亲切感
3. 推荐具体、实用，包含位置和价格
4. 如果用户预算紧张，会推荐性价比高的
5. 如果用户赶时间，会推荐出餐快的

以下是你学习到的食堂信息：
{get_learning_context()}

根据筛选条件匹配到的餐厅：
{restaurants_info if restaurants_info else "暂无完全匹配的餐厅，但我会基于学习数据给你推荐"}

请基于以上信息，给用户一个亲切、个性化的推荐。

重要要求：
1. 每个餐厅只说一次，不要重复推荐同一个餐厅
2. 每个推荐理由只说一次，不要重复
3. 控制字数，简洁明了
4. 推荐 2-3 个最适合的选项
5. 结尾用亲切的语气"""

            # 构建用户提示
            user_prompt = f"用户需求：{user_query}"
            if taste:
                user_prompt += f"\n口味偏好：{taste}"
            if budget:
                user_prompt += f"\n预算：{budget}元以内"
            if time_limit:
                user_prompt += f"\n时间限制：{time_limit}分钟内"
            
            # 调用 MiniMax API
            import requests
            
            messages = []
            # 添加对话历史（限制最近5轮）
            for msg in self.conversation_history[-10:]:
                messages.append({
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}]
                })
            
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": user_prompt}]
            })
            
            payload = {
                "model": "MiniMax-M2.7",
                "max_tokens": 800,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.7
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            response = requests.post(
                f"{self.base_url}/messages",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "content" in data and isinstance(data["content"], list):
                    text_blocks = [block.get("text", "") for block in data["content"] if block.get("type") == "text"]
                    ai_response = "\n".join(text_blocks)
                    
                    # 更新对话历史
                    self.conversation_history.append({"role": "user", "content": user_query})
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # 限制历史长度
                    if len(self.conversation_history) > 20:
                        self.conversation_history = self.conversation_history[-20:]
                    
                    return ai_response
            
            # API 调用失败，使用 fallback
            return self._generate_fallback_recommendation(matched_restaurants)
            
        except Exception as e:
            print(f"AI 推荐生成失败: {e}")
            return self._generate_fallback_recommendation(matched_restaurants)
    
    def _generate_fallback_recommendation(self, restaurants: List[Restaurant]) -> str:
        """
        当 API 不可用时，生成简单的推荐文案
        """
        if not restaurants:
            return "抱歉，暂时没有找到完全符合你要求的餐厅。试试调整一下口味、预算或时间吧~"
        
        result = "为你推荐以下餐厅：\n\n"
        for i, r in enumerate(restaurants[:3], 1):
            result += f"{i}. **{r.name}** 📍{r.location}\n"
            result += f"   💰 人均：{r.avg_price}元\n"
            result += f"   🍽️ 特色：{', '.join(r.features[:3])}\n"
            result += f"   💡 推荐：{r.recommendations[0] if r.recommendations else '值得一试'}\n\n"
        
        result += "这些都是学姐学长们亲测好吃的，快去试试吧！🍜"
        return result
    
    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []


def get_dual_recommendations(user_query: str,
                             taste: Optional[str] = None,
                             budget: Optional[int] = None,
                             time_limit: Optional[int] = None,
                             api_key: Optional[str] = None) -> Dict:
    """
    获取双模式推荐结果
    
    返回：
    {
        "structured": [...],  # 结构化筛选结果
        "ai_recommendation": "...",  # AI 生成的推荐文案
        "matched_count": 0  # 匹配数量
    }
    """
    # 1. 结构化筛选
    matched_restaurants = search_restaurants(taste, budget, time_limit)
    
    # 2. AI 生成推荐
    recommender = AIRecommender(api_key)
    ai_recommendation = recommender.generate_ai_recommendation(
        user_query=user_query,
        matched_restaurants=matched_restaurants,
        taste=taste,
        budget=budget,
        time_limit=time_limit
    )
    
    return {
        "structured": [restaurant_to_dict(r) for r in matched_restaurants[:5]],
        "ai_recommendation": ai_recommendation,
        "matched_count": len(matched_restaurants)
    }
