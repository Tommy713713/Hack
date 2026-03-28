#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Canteen Pilot (智膳领航员)
基于MiniMax Token Plan的校园精准用餐决策助手
"""

import os
import json
import time
import requests
from dataclasses import dataclass
from typing import List, Dict, Optional
from bs4 import BeautifulSoup

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
    
    def __init__(self, school_name: str = "宁波诺丁汉大学", api_key: str = ""):
        self.school_name = school_name
        self.api_key = api_key or os.getenv("ANTHROPIC_API_KEY", "")
        self.learning_data = []  # 存储学习到的信息
        self.conversation_history: List[Dict[str, str]] = []
        self.data_file = "canteen_learning_data.json"  # 用于持久化存储学习数据
        
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
        
        # 加载之前学习的数据
        self.load_learning_data()
        
        self.initialize()
    
    def load_learning_data(self):
        """加载之前学习的数据"""
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.learning_data = data.get('learning_data', [])
                    print(f"✅ Loaded {len(self.learning_data)} items of learning data")
            except Exception as e:
                print(f"❌ Error loading learning data: {e}")
        else:
            print("ℹ️  No previous learning data found")
    
    def save_learning_data(self):
        """保存学习的数据"""
        try:
            data = {
                'learning_data': self.learning_data,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("✅ Learning data saved successfully")
        except Exception as e:
            print(f"❌ Error saving learning data: {e}")
    
    def initialize(self):
        """初始化"""
        print(f"🔧 Initializing AI Canteen Pilot for {self.school_name}...")
        
        # 初始学习：搜索学校食堂信息
        if any(keyword in self.school_name for keyword in ["宁波诺丁汉", "UNNC", "诺丁汉大学"]):
            self.learn_from_web("宁波诺丁汉大学食堂")
            # 直接学习小红书链接
            xiaohongshu_url = "https://www.xiaohongshu.com/explore/688c294100000000230206fa?xsec_token=AB9jEicQCuvZ_rXO1BrGENKyCvjfSBBmeVAziL2YPkgCU=&xsec_source=pc_search&source=web_search_result_notes"
            self.learn_from_url(xiaohongshu_url)
        
        print("✅ AI Canteen Pilot initialized successfully!")
    
    def learn_from_web(self, query):
        """从网上学习食堂数据"""
        print(f"📚 Learning from web about: {query}...")
        
        search_results = []
        
        # 增强的请求头
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0"
        }
        
        # 搜索百度相关信息（优先）
        try:
            url = f"https://www.baidu.com/s?wd={query}"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 提取相关信息
                results = soup.find_all('div', class_='result')
                for result in results[:10]:  # 增加结果数量
                    title = result.find('h3')
                    content = result.find('div', class_='c-abstract')
                    if title:
                        search_results.append(f"百度：{title.text.strip()}")
                    if content:
                        search_results.append(f"内容：{content.text.strip()}")
                print(f"✅ Baidu search completed successfully, found {len(results)} results")
            else:
                print(f"❌ Baidu returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error searching Baidu: {e}")
        
        # 搜索搜狗相关信息
        try:
            url = f"https://www.sogou.com/web?query={query}"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 提取相关信息
                results = soup.find_all('div', class_='vrwrap')
                for result in results[:5]:  # 只取前5个结果
                    title = result.find('h3')
                    content = result.find('p', class_='str_info')
                    if title:
                        search_results.append(f"搜狗：{title.text.strip()}")
                    if content:
                        search_results.append(f"内容：{content.text.strip()}")
                print(f"✅ Sogou search completed successfully, found {len(results)} results")
            else:
                print(f"❌ Sogou returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error searching Sogou: {e}")
        
        # 搜索360搜索相关信息
        try:
            url = f"https://www.so.com/s?q={query}"
            response = requests.get(url, headers=headers, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 提取相关信息
                results = soup.find_all('div', class_='res-list')
                for result in results[:5]:  # 只取前5个结果
                    title = result.find('h3')
                    content = result.find('p', class_='res-desc')
                    if title:
                        search_results.append(f"360搜索：{title.text.strip()}")
                    if content:
                        search_results.append(f"内容：{content.text.strip()}")
                print(f"✅ 360 search completed successfully, found {len(results)} results")
            else:
                print(f"❌ 360 search returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error searching 360: {e}")
        
        if search_results:
            print("✅ Learning completed successfully")
            # 存储学习到的信息
            self.learning_data.extend(search_results)
            # 保存学习数据
            self.save_learning_data()
            return "\n".join(search_results[:20])  # 限制结果数量
        else:
            print("❌ No information found")
            return f"未找到{query}的相关信息"
    
    def search_unnc_canteen_info(self):
        """搜索宁波诺丁汉大学食堂相关信息"""
        return self.learn_from_web("宁波诺丁汉大学食堂")
    
    def get_canteen_info(self):
        """获取食堂信息"""
        if self.learning_data:
            return "\n".join(self.learning_data)
        else:
            return "尚未学习到食堂信息，请输入学校名称以开始学习。"
    
    def learn_from_url(self, url):
        """从指定URL学习食堂数据"""
        print(f"📚 Learning from URL: {url}...")
        
        search_results = []
        
        # 增强的请求头，模拟真实浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.google.com/",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.xiaohongshu.com"
        }
        
        # 代理IP列表（可选）
        proxies = {
            # "http": "http://127.0.0.1:7890",
            # "https": "http://127.0.0.1:7890"
        }
        
        try:
            # 尝试使用代理
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 检查是否是小红书链接
                if "xiaohongshu.com" in url:
                    # 提取小红书帖子信息
                    title = soup.find('h1')
                    content = soup.find('div', class_='content')
                    
                    # 尝试其他选择器
                    if not title:
                        title = soup.find('h1', class_='title')
                    if not content:
                        content = soup.find('div', class_='note-content')
                    if not content:
                        content = soup.find('div', class_='rich-text')
                    
                    if title:
                        search_results.append(f"小红书标题：{title.text.strip()}")
                    if content:
                        search_results.append(f"小红书内容：{content.text.strip()}")
                    
                    # 提取标签
                    tags = soup.find_all('a', class_='tag')
                    if tags:
                        tag_texts = [tag.text.strip() for tag in tags]
                        search_results.append(f"小红书标签：{', '.join(tag_texts)}")
                
                # 检查是否是大众点评链接
                elif "dianping.com" in url:
                    # 提取大众点评信息
                    title = soup.find('h1')
                    rating = soup.find('div', class_='score')
                    if title:
                        search_results.append(f"大众点评：{title.text.strip()}")
                    if rating:
                        search_results.append(f"评分：{rating.text.strip()}")
                
                # 检查是否是美团链接
                elif "meituan.com" in url:
                    # 提取美团信息
                    title = soup.find('h1')
                    rating = soup.find('div', class_='score')
                    if title:
                        search_results.append(f"美团：{title.text.strip()}")
                    if rating:
                        search_results.append(f"评分：{rating.text.strip()}")
                
                # 通用处理
                else:
                    # 提取标题和内容
                    title = soup.find('h1')
                    content = soup.find('div', class_='content') or soup.find('div', class_='article')
                    if title:
                        search_results.append(f"标题：{title.text.strip()}")
                    if content:
                        search_results.append(f"内容：{content.text.strip()}")
            else:
                print(f"❌ URL returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error learning from URL: {e}")
        
        if search_results:
            print("✅ Learning from URL completed successfully")
            # 存储学习到的信息
            self.learning_data.extend(search_results)
            # 保存学习数据
            self.save_learning_data()
            return "\n".join(search_results)
        else:
            print("❌ No information found from URL")
            return "未从链接中找到相关信息"
    
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
            
            # 检查用户是否提供了链接
            import re
            urls = re.findall(r'https?://[^\s]+', user_input)
            if urls:
                for url in urls:
                    self.learn_from_url(url)
            
            # 检查用户是否提到学校名称，如果提到则学习相关食堂信息
            if any(keyword in user_input for keyword in ["宁波诺丁汉", "UNNC", "诺丁汉大学"]):
                self.learn_from_web("宁波诺丁汉大学食堂")
            
            # 构建系统提示
            system_prompt = f"""你是一个校园用餐决策助手，名叫智膳领航员。你需要：
1. 理解用户的用餐需求
2. 基于以下学习到的食堂信息，为用户推荐合适的用餐选项：
{self.get_canteen_info()}
3. 语言风格要亲切、活泼，像学长/学姐给建议一样
4. 可以添加一些校园梗，增加亲切感
5. 如果有缺失的信息，要礼貌地询问用户
6. 要包含具体的推荐理由和实用建议
7. 每次回复都要保持多样性，不要重复之前的内容
8. 要能够理解对话上下文，保持对话的连贯性
9. 要记住学习到的食堂信息，不断积累知识
10. 如果用户提到新的食堂信息，要学习并记住
11. 所有推荐必须基于学习到的信息，不要使用任何预设的信息
12. 如果学习到的信息不足，要明确告诉用户，并建议用户提供更多信息"""
            
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