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
    
    def search_xiaohongshu(self, query):
        """
        使用Playwright + 系统Chrome抓取小红书帖子
        """
        try:
            from playwright.sync_api import sync_playwright
            import time, random, os

            print(f"🔍 开始抓取小红书帖子: {query}")

            # 登录态存储文件
            state_file = os.path.join(os.path.dirname(__file__), "..", "data", "xiaohongshu_state.json")

            with sync_playwright() as p:
                # 自动检测操作系统并使用相应的Chrome路径
                import platform
                chrome_path = None
                
                if platform.system() == "Darwin":  # macOS
                    chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                elif platform.system() == "Windows":  # Windows
                    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
                
                browser = p.chromium.launch(
                    executable_path=chrome_path,
                    headless=False,  # 显示浏览器方便调试
                    slow_mo=100  # 模拟人类操作
                )

                if os.path.exists(state_file):
                    context = browser.new_context(storage_state=state_file)
                    print("✅ 使用已有登录态")
                else:
                    context = browser.new_context()
                    print("⚠️ 首次运行，请手动登录小红书页面后按回车继续")

                page = context.new_page()
                encoded_query = query.replace(" ", "%20")
                search_url = f"https://www.xiaohongshu.com/search_result?keyword={encoded_query}"
                page.goto(search_url, timeout=60000)
                page.wait_for_load_state("networkidle", timeout=60000)

                # 如果首次登录，保存登录态
                if not os.path.exists(state_file):
                    input("请在浏览器中完成登录，然后按回车保存登录态...")
                    context.storage_state(path=state_file)
                    print(f"✅ 登录态已保存: {state_file}")

                # 模拟滚动加载
                print("📜 模拟滚动加载更多内容...")
                for _ in range(5):
                    page.evaluate("window.scrollBy(0, document.body.scrollHeight)")
                    time.sleep(random.uniform(2, 4))

                # 提取帖子链接
                print("🔗 提取帖子链接...")
                links = page.query_selector_all("a")
                post_links = []
                for link in links:
                    href = link.get_attribute("href")
                    if href and "/explore/" in href:
                        full_url = f"https://www.xiaohongshu.com{href}"
                        post_links.append(full_url)
                post_links = list(set(post_links))
                print(f"✅ 找到 {len(post_links)} 个帖子链接")

                # 抓取前3个帖子内容
                valid_posts_count = 0
                for i, post_url in enumerate(post_links[:10]):  # 增加到前10个，提高找到有效内容的概率
                    if valid_posts_count >= 3:  # 只学习3个有效帖子
                        break
                        
                    print(f"📚 学习帖子 {i+1}: {post_url}")
                    page.goto(post_url, timeout=60000)
                    # 增加等待时间，确保页面完全加载
                    time.sleep(3)
                    page.wait_for_load_state("networkidle", timeout=60000)
                    # 再等待2秒，确保所有内容都加载完成
                    time.sleep(2)

                    # 尝试更多的选择器来提取标题
                    title_el = None
                    title_selectors = [
                        "h1", 
                        "div[class*='title']", 
                        "h1[class*='title']",
                        "div[class*='note-title']",
                        "div[class^='title']"
                    ]
                    for selector in title_selectors:
                        title_el = page.query_selector(selector)
                        if title_el:
                            break

                    # 尝试更多的选择器来提取内容
                    content_el = None
                    content_selectors = [
                        "div[class*='content']", 
                        "div[class*='note-content']", 
                        "div[class*='rich-text']",
                        "div[class*='desc']",
                        "div[class^='content']",
                        "article",
                        "div[class*='main-content']"
                    ]
                    for selector in content_selectors:
                        content_el = page.query_selector(selector)
                        if content_el:
                            break

                    post_info = []
                    if title_el:
                        title_text = title_el.inner_text().strip()
                        # 过滤无效标题
                        if "当前笔记暂时无法浏览" not in title_text and len(title_text) > 5:
                            post_info.append(f"小红书标题：{title_text}")
                    if content_el:
                        content_text = content_el.inner_text().strip()
                        # 过滤无效内容
                        if "当前笔记暂时无法浏览" not in content_text and len(content_text) > 30:  # 内容长度大于30，避免只抓取到导航栏
                            post_info.append(f"小红书内容：{content_text}")

                    # 如果没有找到标题和内容，尝试提取页面中的所有文本
                    if not post_info:
                        try:
                            # 提取页面中的所有文本
                            page_text = page.content()
                            # 过滤无效内容
                            if "当前笔记暂时无法浏览" not in page_text and len(page_text) > 1000:
                                # 使用BeautifulSoup提取文本
                                from bs4 import BeautifulSoup
                                soup = BeautifulSoup(page_text, 'html.parser')
                                # 提取所有文本
                                all_text = soup.get_text().strip()
                                # 截取前500个字符作为内容
                                content_text = all_text[:500]
                                post_info.append(f"小红书内容：{content_text}")
                                print(f"✅ 已提取页面文本内容")
                        except Exception as e:
                            print(f"❌ 提取页面文本失败: {e}")

                    # 保存到学习数据
                    if post_info:
                        self.learning_data.extend(post_info)
                        self.save_learning_data()
                        print(f"✅ 已学习帖子内容")
                        valid_posts_count += 1
                    else:
                        print(f"❌ 该帖子内容无效，跳过")

                    time.sleep(random.uniform(2, 4))  # 随机延迟

                browser.close()
                print("✅ 小红书抓取完成")

        except Exception as e:
            print(f"❌ 抓取小红书出错: {e}")
    
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
            "Origin": "https://www.dianping.com"
        }
        
        # 代理配置（可选）
        proxies = {
            # "http": "http://127.0.0.1:7890",
            # "https": "http://127.0.0.1:7890"
        }
        
        try:
            # 添加随机延迟
            import random
            time.sleep(random.uniform(2, 3))
            # 尝试使用代理
            response = requests.get(url, headers=headers, proxies=proxies, timeout=20)
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
                    if not content:
                        content = soup.find('div', class_='desc')
                    
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
                    # 尝试不同的标题选择器
                    title = soup.find('h1') or soup.find('h2') or soup.find('div', class_='shop-name')
                    # 尝试不同的评分选择器
                    rating = soup.find('div', class_='score') or soup.find('span', class_='rating') or soup.find('div', class_='star-wrapper')
                    # 尝试提取价格
                    price = soup.find('span', class_='price') or soup.find('div', class_='avg-price')
                    # 尝试提取地址
                    address = soup.find('div', class_='address') or soup.find('span', class_='addr')
                    
                    if title:
                        search_results.append(f"大众点评：{title.text.strip()}")
                    if rating:
                        search_results.append(f"评分：{rating.text.strip()}")
                    if price:
                        search_results.append(f"价格：{price.text.strip()}")
                    if address:
                        search_results.append(f"地址：{address.text.strip()}")
                
                # 检查是否是美团链接
                elif "meituan.com" in url:
                    # 提取美团信息
                    title = soup.find('h1') or soup.find('div', class_='shop-name')
                    rating = soup.find('div', class_='score') or soup.find('span', class_='star')
                    price = soup.find('span', class_='avg-price') or soup.find('div', class_='price')
                    address = soup.find('div', class_='address') or soup.find('span', class_='addr')
                    
                    if title:
                        search_results.append(f"美团：{title.text.strip()}")
                    if rating:
                        search_results.append(f"评分：{rating.text.strip()}")
                    if price:
                        search_results.append(f"价格：{price.text.strip()}")
                    if address:
                        search_results.append(f"地址：{address.text.strip()}")
                
                # 通用处理
                else:
                    # 提取标题和内容
                    title = soup.find('h1') or soup.find('h2') or soup.find('title')
                    content = soup.find('div', class_='content') or soup.find('div', class_='article') or soup.find('main')
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
        
        print("🤖 正在生成回应...")
        
        try:
            # 1. 异步处理链接学习，避免阻塞主流程
            import re
            urls = re.findall(r'https?://[^\s]+', user_input)
            if urls:
                # 检查用户是否有推荐意图
                recommend_keywords = ["推荐", "这家店", "这家餐厅", "好吃", "不错", "推荐一下", "分享"]
                has_recommend_intent = any(keyword in user_input for keyword in recommend_keywords)
                
                if has_recommend_intent:
                    print("🔍 检测到推荐意图，正在学习链接内容...")
                
                # 异步学习链接
                import threading
                def learn_url(url):
                    try:
                        self.learn_from_url(url)
                        if has_recommend_intent:
                            print("✅ 已学习推荐的店铺信息")
                    except Exception as e:
                        print(f"❌ 学习链接时出错: {e}")
                
                for url in urls:
                    thread = threading.Thread(target=learn_url, args=(url,))
                    thread.daemon = True
                    thread.start()
            else:
                # 检测用户是否有食堂相关问题，触发小红书搜索
                canteen_keywords = ["食堂", "餐厅", "饭", "吃", "美食", "推荐", "好吃", "东北菜", "unnc", "宁波诺丁汉"]
                has_canteen_intent = any(keyword in user_input for keyword in canteen_keywords)
                
                if has_canteen_intent:
                    print("🔍 检测到食堂相关问题，正在搜索小红书...")
                    # 异步搜索小红书
                    import threading
                    def search_and_learn():
                        try:
                            # 构建搜索关键词
                            search_query = "宁波诺丁汉大学 " + user_input
                            self.search_xiaohongshu(search_query)
                            print("✅ 小红书搜索学习完成")
                        except Exception as e:
                            print(f"❌ 搜索小红书时出错: {e}")
                    
                    thread = threading.Thread(target=search_and_learn)
                    thread.daemon = True
                    thread.start()
            
            # 2. 快速构建消息列表，只保留最近5轮对话
            messages = []
            recent_history = self.conversation_history[-5:]  # 只保留最近5轮对话
            for msg in recent_history:
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
            
            # 3. 优化系统提示，减少长度
            canteen_info = self.get_canteen_info()
            # 如果信息太长，只使用最近的部分
            if len(canteen_info) > 1500:
                # 只使用最近的信息
                info_lines = canteen_info.split("\n")
                canteen_info = "\n".join(info_lines[-20:])
            
            system_prompt = f"""你是宁诺的干饭学姐，对宁波诺丁汉大学的食堂和周边美食非常熟悉。你需要：
1. 理解学弟学妹的用餐需求
2. 基于以下学习到的食堂信息，为学弟学妹推荐合适的用餐选项：
{canteen_info}
3. 语言风格要亲切、活泼，像学姐给建议一样
4. 推荐餐厅时必须包含：人均价格、推荐菜品、排队时间、推荐理由
5. 如果有缺失的信息，要礼貌地询问学弟学妹
6. 每次回复都要保持多样性，不要重复之前的内容
7. 要能够理解对话上下文，保持对话的连贯性
8. 所有推荐必须基于学习到的信息，不要使用预设信息
9. 语气要友好、热情，像真正的学姐一样关心学弟学妹"""
            
            # 4. 优化API调用参数
            payload = {
                "model": "MiniMax-M2.7",
                "max_tokens": 800,  # 减少token数量
                "system": system_prompt,
                "messages": messages,
                "temperature": 0.6,  # 稍微降低温度，加快生成速度
                "stream": False  # 关闭流式输出
            }
            
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # 5. 发送API请求
            print("📡 正在调用AI服务...")
            import requests
            response = requests.post(
                "https://api.minimaxi.com/anthropic/v1/messages",
                json=payload,
                headers=headers,
                timeout=20  # 合理的超时时间
            )
            
            print(f"📡 AI服务响应状态: {response.status_code}")
            
            # 6. 快速处理响应
            data = response.json()
            
            # 提取响应内容
            if "content" in data and isinstance(data["content"], list):
                text_blocks = [block.get("text", "") for block in data["content"] if block.get("type") == "text"]
                ai_response = "\n".join(text_blocks)
                
                # 限制响应长度
                if len(ai_response) > 1200:
                    ai_response = ai_response[:1200] + "..."
                
                print(f"📝 AI响应: {ai_response[:80]}...")
                
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
            print(f"❌ 生成回应时出错: {e}")
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