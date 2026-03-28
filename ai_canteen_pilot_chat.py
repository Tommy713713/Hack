#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Canteen Pilot (智膳领航员)
基于MiniMax Token Plan的校园精准用餐决策助手
"""

import os
import json
import time
from dataclasses import dataclass
from typing import List, Dict, Optional

# 导入anthropic SDK
import anthropic

@dataclass
class CanteenOption:
    """食堂选项"""
    name: str  # 食堂名称
    waiting_time: int  # 等待时间（分钟）
    price: float  # 价格（元）
    taste_match: float  # 口味匹配度（0-1）
    cost_performance: float  # 性价比（0-1）

class AICanteenPilot:
    """AI Canteen Pilot 核心类"""
    
    def __init__(self, school_name: str = "北京大学", api_key: str = ""):
        self.school_name = school_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.canteen_options: List[CanteenOption] = []
        self.conversation_history: List[Dict[str, str]] = []
        
        # 初始化anthropic客户端
        try:
            self.client = anthropic.Anthropic(
                api_key=self.api_key,
                base_url="https://api.minimaxi.com/anthropic"
            )
            print("✅ Anthropic client initialized successfully!")
        except Exception as e:
            print(f"❌ Error initializing Anthropic client: {e}")
            self.client = None
        
        self.initialize()
    
    def initialize(self):
        """初始化食堂数据"""
        print(f"🔧 Initializing AI Canteen Pilot for {self.school_name}...")
        
        # 模拟食堂数据
        self.canteen_options = [
            CanteenOption(name="一食堂一楼拉面", waiting_time=5, price=18, taste_match=0.8, cost_performance=0.9),
            CanteenOption(name="二食堂二楼套餐", waiting_time=10, price=25, taste_match=0.7, cost_performance=0.8),
            CanteenOption(name="三食堂二楼冒菜", waiting_time=8, price=28, taste_match=0.9, cost_performance=0.7),
            CanteenOption(name="四食堂一楼烤肉饭", waiting_time=7, price=22, taste_match=0.8, cost_performance=0.85),
            CanteenOption(name="五食堂三楼麻辣烫", waiting_time=12, price=30, taste_match=0.85, cost_performance=0.75)
        ]
        
        print(f"✅ Canteen data initialized successfully! Total canteens: {len(self.canteen_options)}")
    
    def get_canteen_info(self):
        """获取食堂信息"""
        canteen_info = []
        for option in self.canteen_options:
            canteen_info.append(f"{option.name}：等待时间{option.waiting_time}分钟，价格{option.price}元")
        return "\n".join(canteen_info)
    
    def generate_response(self, user_input: str) -> str:
        """
        使用MiniMax API生成响应
        """
        if not self.client:
            # 简单的响应生成作为 fallback
            return "抱歉，AI服务暂时不可用，请稍后再试。"
        
        print("🤖 Using MiniMax API for response generation...")
        
        try:
            # 构建消息列表
            messages = []
            
            # 添加对话历史
            for msg in self.conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": [{"type": "text", "text": msg["content"]}
                ]
                })
            
            # 添加当前用户输入
            messages.append({
                "role": "user",
                "content": [{"type": "text", "text": user_input}
            ]
            })
            
            # 构建系统提示
            system_prompt = f"""你是一个校园用餐决策助手，名叫智膳领航员。你需要：
1. 理解用户的用餐需求
2. 基于以下食堂信息，为用户推荐合适的用餐选项：
{self.get_canteen_info()}
3. 语言风格要亲切、活泼，像学长/学姐给建议一样
4. 可以添加一些校园梗，增加亲切感
5. 如果有缺失的信息，要礼貌地询问用户
6. 要包含具体的推荐理由和实用建议
7. 每次回复都要保持多样性，不要重复之前的内容
8. 要能够理解对话上下文，保持对话的连贯性"""
            
            # 构建请求数据
            payload = {
                "model": "MiniMax-M2.7",
                "max_tokens": 1000,
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.7
            }
            
            # 构建请求头
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 发送请求
            import requests
            response = requests.post(
                "https://api.minimaxi.com/anthropic/v1/messages",
                json=payload,
                headers=headers,
                timeout=30  # 增加超时时间
            )
            
            print(f"📡 API response status: {response.status_code}")
            
            # 解析响应
            data = response.json()
            
            # 提取响应内容
            if "content" in data and isinstance(data["content"], list):
                text_blocks = [block.get("text", "") for block in data["content"] if block.get("type") == "text"]
                ai_response = "\n".join(text_blocks)
                print(f"📝 MiniMax API response: {ai_response}")
                
                # 更新对话历史
                self.conversation_history.append({"role": "user", "content": user_input})
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                # 限制对话历史长度
                if len(self.conversation_history) > 10:
                    self.conversation_history = self.conversation_history[-10:]
                
                return ai_response
            else:
                # 如果响应格式不正确，使用默认生成
                return "抱歉，我没有理解你的意思，请再说一遍。"
                
        except Exception as e:
            print(f"❌ Error calling MiniMax API: {e}")
            # 出错时使用默认生成
            return "抱歉，AI服务暂时不可用，请稍后再试。"
    
    def run(self):
        """
        运行主程序
        """
        print(f"🎓 智膳领航员已启动！为{self.school_name}的同学服务。")
        print("💡 请输入你的用餐需求，输入'退出'结束对话。")
        
        while True:
            try:
                user_input = input("\n你: ")
                
                if user_input.strip() == "退出":
                    print("👋 对话已结束，再见！")
                    break
                
                response = self.generate_response(user_input)
                print(f"\n智膳领航员: {response}")
                
            except KeyboardInterrupt:
                print("\n👋 对话已结束，再见！")
                break
            except Exception as e:
                print(f"❌ 发生错误: {e}")
                print("🔄 请重新输入你的用餐需求。")

if __name__ == "__main__":
    import sys
    
    # 直接在代码中设置API key
    # 请将下面的API key替换为你自己的MiniMax Token Plan API key
    api_key = "sk-cp-D8nMKAO11UQXliAaXe-SKjXW19VlCMZpskP8ggVSoQUhxYbJP3PT9FLVfR64cEH0fEhAOVIwPAZp5HDRI18ZVQPOi2nOVe1LT_nPXTMP0Urr9PnQEmVGvlM"
    
    # 如果没有设置API key，提示用户输入
    if not api_key:
        api_key = input("请输入MiniMax Token Plan API key: ").strip()
    
    if not api_key:
        print("⚠️ 警告: API key 未设置")
        print("\n使用默认模式运行...")
    
    # 启动程序
    pilot = AICanteenPilot(api_key=api_key)
    pilot.run()