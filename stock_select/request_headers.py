#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
请求头配置文件
包含各种伪造的浏览器请求头，用于模拟真实浏览器访问
"""

import random

# 常见的User-Agent列表
USER_AGENTS = [
    # Chrome浏览器
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    
    # Firefox浏览器
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    
    # Safari浏览器
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15",
    
    # Edge浏览器
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]

# 基础请求头
BASE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}

# 移动端请求头
MOBILE_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

# 股票数据专用请求头
STOCK_DATA_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Referer': 'https://www.akshare.xyz/',
    'Origin': 'https://www.akshare.xyz',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
}

def get_random_user_agent():
    """获取随机的User-Agent"""
    return random.choice(USER_AGENTS)

def get_desktop_headers():
    """获取桌面端请求头"""
    headers = BASE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    return headers

def get_mobile_headers():
    """获取移动端请求头"""
    headers = MOBILE_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    return headers

def get_stock_data_headers():
    """获取股票数据专用请求头"""
    headers = STOCK_DATA_HEADERS.copy()
    headers['User-Agent'] = get_random_user_agent()
    return headers

def get_custom_headers(custom_headers=None):
    """获取自定义请求头"""
    headers = get_desktop_headers()
    if custom_headers:
        headers.update(custom_headers)
    return headers

def rotate_user_agent():
    """轮换User-Agent"""
    return get_random_user_agent()

# 请求头轮换器类
class HeaderRotator:
    """请求头轮换器，用于避免被反爬虫机制检测"""
    
    def __init__(self):
        self.user_agents = USER_AGENTS.copy()
        self.current_index = 0
        self.request_count = 0
        self.rotation_interval = 10  # 每10次请求轮换一次
    
    def get_headers(self, header_type='desktop'):
        """获取请求头"""
        self.request_count += 1
        
        # 定期轮换User-Agent
        if self.request_count % self.rotation_interval == 0:
            self.current_index = (self.current_index + 1) % len(self.user_agents)
        
        if header_type == 'mobile':
            headers = get_mobile_headers()
        elif header_type == 'stock_data':
            headers = get_stock_data_headers()
        else:
            headers = get_desktop_headers()
        
        # 使用当前轮换的User-Agent
        headers['User-Agent'] = self.user_agents[self.current_index]
        
        return headers
    
    def add_custom_headers(self, headers, custom_headers):
        """添加自定义请求头"""
        if custom_headers:
            headers.update(custom_headers)
        return headers

# 全局请求头轮换器实例
header_rotator = HeaderRotator()

# 便捷函数
def get_headers(header_type='desktop', custom_headers=None):
    """获取请求头的便捷函数"""
    headers = header_rotator.get_headers(header_type)
    if custom_headers:
        headers.update(custom_headers)
    return headers
