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
        # 使用绝对路径保存数据文件
        self.data_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data", "canteen_learning_data.json")
        self.data_file = os.path.normpath(self.data_file)  # 规范化路径
        
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
            # 确保data文件夹存在
            data_dir = os.path.dirname(self.data_file)
            if data_dir and not os.path.exists(data_dir):
                os.makedirs(data_dir)
                print(f"✅ Created directory: {data_dir}")
            
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
            # 直接学习用户提供的小红书链接
            xiaohongshu_urls = [
                "https://www.xiaohongshu.com/explore/69c0c555000000001d01e4a4?xsec_token=ABfr7Z_J4U8OLc4MzF8Ds3f-tEiJ0ScXW5A-BqGJWTleU=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/690b734c0000000007033917?xsec_token=ABOmrBdFYDxW39wMxAK4X2Ex6f4gH4RVBB6maeVb__ves=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/68b57732000000001d00e1c8?xsec_token=ABQ7uCTO6oBKjD-HoGteAsgrWjpdBkmPVfCwRMkbDVJCQ=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/68c3abf7000000001c011323?xsec_token=AB8jgb5QZRiIBHhVIhzLhwbtNADt72YlLGcJLfIraWCQs=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/69297248000000001e00777f?xsec_token=ABQT_nKGgE1ut12CTTWRWNKeaECNvi74WqFajxKwEwM28=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/66ffbb98000000002c029ea8?xsec_token=ABOH_DObctKKKQMyMqK6Zp3ykftPO1ADKB0acZyKN1jZc=&xsec_source=pc_search&source=web_explore_feed",
                "https://www.xiaohongshu.com/explore/670d43dc000000001b02ef4a?xsec_token=ABKW9BKYiKVxVPq9HO6Vaa6sbrYjFyE8-9BqHkbSvYDxU=&xsec_source=pc_search&source=web_search_result_notes",
                "https://www.xiaohongshu.com/explore/6933ac93000000001e03aea7?xsec_token=AB6bFu1J-vhUc3L0wqYbpUfcs3mTWCwbgm9dxpDHF5WZs=&xsec_source=pc_search&source=web_search_result_notes",
                "https://www.xiaohongshu.com/explore/6613c61a000000001a016fcc?xsec_token=ABRvql19wGla37v8D4yJVOB5OKKgl7o1Y1JZCeeIATWIg=&xsec_source=pc_search&source=web_search_result_notes",
                "https://www.xiaohongshu.com/explore/68f0d50f00000000050322a4?xsec_token=ABm1zD50k5kP-VMtNI-jLP0-HWNNBF-xiJNSX87umPTFM=&xsec_source=pc_search&source=web_search_result_notes"
            ]
            
            # 检查是否已经有足够的学习数据
            if len(self.learning_data) >= 50:
                print("✅ Already has enough learning data, skipping learning process")
            else:
                # 依次学习每个小红书链接
                for url in xiaohongshu_urls:
                    self.learn_from_url(url)
                    # 避免请求过快被封禁
                    time.sleep(3)
        
        print("✅ AI Canteen Pilot initialized successfully!")
    
    def learn_from_web(self, query):
        """从网上学习食堂数据"""
        print(f"📚 Learning from web about: {query}...")
        
        search_results = []
        
        # 更完整的请求头，模拟真实浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "DNT": "1",
            "Referer": "https://www.google.com/"
        }
        
        # 代理配置（可选）
        proxies = {
            # "http": "http://127.0.0.1:7890",
            # "https": "http://127.0.0.1:7890"
        }
        
        # 搜索百度相关信息（优先）
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.baidu.com/s?wd={encoded_query}"
            # 添加随机延迟
            import random
            time.sleep(random.uniform(1, 2))
            # 使用代理和完整请求头
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 尝试不同的选择器
                results = []
                # 尝试选择器1
                results1 = soup.find_all('div', class_='result')
                # 尝试选择器2
                results2 = soup.find_all('div', class_='c-container')
                # 尝试选择器3
                results3 = soup.find_all('div', class_='result-op')
                # 合并结果
                results = results1 + results2 + results3
                
                for result in results[:10]:  # 增加结果数量
                    # 尝试不同的标题选择器
                    title = result.find('h3') or result.find('a')
                    # 尝试不同的内容选择器
                    content = result.find('div', class_='c-abstract') or result.find('div', class_='abstract')
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
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.sogou.com/web?query={encoded_query}"
            # 添加随机延迟
            import random
            time.sleep(random.uniform(1, 2))
            # 使用代理和完整请求头
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 尝试不同的选择器
                results = []
                # 尝试选择器1
                results1 = soup.find_all('div', class_='vrwrap')
                # 尝试选择器2
                results2 = soup.find_all('div', class_='result')
                # 合并结果
                results = results1 + results2
                
                for result in results[:5]:  # 只取前5个结果
                    # 尝试不同的标题选择器
                    title = result.find('h3') or result.find('a')
                    # 尝试不同的内容选择器
                    content = result.find('p', class_='str_info') or result.find('div', class_='summary')
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
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.so.com/s?q={encoded_query}"
            # 添加随机延迟
            import random
            time.sleep(random.uniform(1, 2))
            # 使用代理和完整请求头
            response = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                # 尝试不同的选择器
                results = []
                # 尝试选择器1
                results1 = soup.find_all('div', class_='res-list')
                # 尝试选择器2
                results2 = soup.find_all('div', class_='result')
                # 合并结果
                results = results1 + results2
                
                for result in results[:5]:  # 只取前5个结果
                    # 尝试不同的标题选择器
                    title = result.find('h3') or result.find('a')
                    # 尝试不同的内容选择器
                    content = result.find('p', class_='res-desc') or result.find('div', class_='desc')
                    if title:
                        search_results.append(f"360搜索：{title.text.strip()}")
                    if content:
                        search_results.append(f"内容：{content.text.strip()}")
                print(f"✅ 360 search completed successfully, found {len(results)} results")
            else:
                print(f"❌ 360 search returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error searching 360: {e}")
        
        # 搜索小红书相关信息
        try:
            # 小红书搜索 - 使用百度搜索小红书链接
            import urllib.parse
            xiaohongshu_query = query
            encoded_query = urllib.parse.quote(f"{xiaohongshu_query} site:xiaohongshu.com")
            baidu_url = f"https://www.baidu.com/s?wd={encoded_query}"
            
            # 添加随机延迟
            import random
            time.sleep(random.uniform(1, 2))
            # 使用代理和完整请求头
            response = requests.get(baidu_url, headers=headers, proxies=proxies, timeout=15)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                links = soup.find_all('a', href=True)
                post_links = []
                
                for link in links:
                    href = link.get('href')
                    if href:
                        # 提取真实链接（处理百度跳转链接）
                        if 'http' in href:
                            # 检查是否包含小红书链接
                            if 'xiaohongshu.com' in href:
                                # 处理百度跳转链接
                                if 'baidu.com/link?' in href:
                                    # 尝试从href中提取真实链接
                                    try:
                                        import urllib.parse
                                        parsed_url = urllib.parse.urlparse(href)
                                        query_params = urllib.parse.parse_qs(parsed_url.query)
                                        if 'url' in query_params:
                                            real_url = query_params['url'][0]
                                            if 'xiaohongshu.com/explore/' in real_url:
                                                post_links.append(real_url)
                                    except:
                                        pass
                                else:
                                    # 直接的小红书链接
                                    if 'xiaohongshu.com/explore/' in href:
                                        post_links.append(href)
                
                # 去重
                post_links = list(set(post_links))
                
                print(f"✅ Baidu search for Xiaohongshu completed successfully, found {len(post_links)} posts")
                for i, post_url in enumerate(post_links[:3]):
                    print(f"📚 Learning from Xiaohongshu post {i+1}: {post_url}")
                    self.learn_from_url(post_url)
                    time.sleep(2)
            else:
                print(f"❌ Baidu search for Xiaohongshu returned status code: {response.status_code}")
        except Exception as e:
            print(f"❌ Error searching Xiaohongshu: {e}")
        
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
        
        # 更完整的请求头，模拟真实浏览器
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Cache-Control": "max-age=0",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "cross-site",
            "Sec-Fetch-User": "?1",
            "DNT": "1",
            "Referer": "https://www.google.com/",
            "X-Requested-With": "XMLHttpRequest",
            "Origin": "https://www.xiaohongshu.com"
        }
        
        # 代理配置（可选）
        proxies = {
            # "http": "http://127.0.0.1:7890",
            # "https": "http://127.0.0.1:7890"
        }
        
        try:
            # 添加随机延迟
            import random
            time.sleep(random.uniform(1, 2))
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
            system_prompt = f"""你是宁诺的干饭学姐，在宁波诺丁汉大学读了几年书，对学校的食堂和周边美食非常熟悉。你需要：
1. 理解学弟学妹的用餐需求
2. 基于以下学习到的食堂信息，为学弟学妹推荐合适的用餐选项：
{self.get_canteen_info()}
3. 语言风格要亲切、活泼，像学姐给建议一样，使用校园梗增加亲切感
4. 推荐餐厅时必须包含以下信息：
   - 人均价格
   - 推荐菜品
   - 一般的排队时间
   - 为什么推荐这家店
5. 如果有缺失的信息，要礼貌地询问学弟学妹
6. 每次回复都要保持多样性，不要重复之前的内容
7. 要能够理解对话上下文，保持对话的连贯性
8. 要记住学习到的食堂信息，不断积累知识
9. 如果学弟学妹提到新的食堂信息，要学习并记住
10. 所有推荐必须基于学习到的信息，不要使用任何预设的信息
11. 如果学习到的信息不足，要明确告诉学弟学妹，并建议提供更多信息
12. 语气要友好、热情，像真正的学姐一样关心学弟学妹"""
            
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
        print(f"👩‍🎓 宁诺干饭学姐已上线！为{self.school_name}的学弟学妹服务。")
        print("💡 有什么想吃的？学姐帮你推荐～输入'退出'结束对话。")
        
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