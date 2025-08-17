#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
反爬虫策略模块
包含多种绕过反爬虫的技术和策略
"""

import time
import random
import logging
import requests
from typing import Dict, List, Optional
from .request_headers import header_rotator

logger = logging.getLogger(__name__)

class AntiCrawlerStrategy:
    """反爬虫策略管理器"""
    
    def __init__(self):
        """初始化反爬虫策略"""
        self.proxy_list = []
        self.session_pool = []
        self.request_history = {}
        self.blocked_ips = set()
        self.success_patterns = {}
        
        # 策略配置
        self.max_retries = 5
        self.base_delay = 1.0
        self.max_delay = 10.0
        self.jitter_factor = 0.3
        
        # 初始化会话池
        self._init_session_pool()
    
    def _init_session_pool(self):
        """初始化会话池"""
        for i in range(3):
            session = requests.Session()
            session.headers.update(header_rotator.get_headers('stock_data'))
            session.timeout = (5, 15)  # 连接超时5秒，读取超时15秒
            self.session_pool.append(session)
    
    def get_session(self) -> requests.Session:
        """获取一个会话"""
        return random.choice(self.session_pool)
    
    def add_proxy(self, proxy: str):
        """添加代理服务器"""
        if proxy not in self.proxy_list:
            self.proxy_list.append(proxy)
            logger.info(f"添加代理: {proxy}")
    
    def get_proxy(self) -> Optional[Dict[str, str]]:
        """获取一个代理"""
        if not self.proxy_list:
            return None
        proxy = random.choice(self.proxy_list)
        return {'http': proxy, 'https': proxy}
    
    def calculate_delay(self, attempt: int, base_delay: float = None) -> float:
        """计算延迟时间（指数退避 + 抖动）"""
        if base_delay is None:
            base_delay = self.base_delay
        
        # 指数退避
        delay = base_delay * (2 ** attempt)
        
        # 添加随机抖动
        jitter = random.uniform(1 - self.jitter_factor, 1 + self.jitter_factor)
        delay *= jitter
        
        # 限制最大延迟
        delay = min(delay, self.max_delay)
        
        return delay
    
    def should_retry(self, error: Exception, attempt: int) -> bool:
        """判断是否应该重试"""
        if attempt >= self.max_retries:
            return False
        
        # 网络错误通常可以重试
        if isinstance(error, (requests.ConnectionError, requests.Timeout)):
            return True
        
        # HTTP错误码判断
        if hasattr(error, 'response') and error.response is not None:
            status_code = error.response.status_code
            
            # 这些状态码通常可以重试
            if status_code in [429, 500, 502, 503, 504]:
                return True
            
            # 这些状态码通常不应该重试
            if status_code in [400, 401, 403, 404]:
                return False
        
        return True
    
    def handle_rate_limit(self, response: requests.Response):
        """处理速率限制"""
        if response.status_code == 429:
            # 从响应头获取重试时间
            retry_after = response.headers.get('Retry-After')
            if retry_after:
                try:
                    wait_time = int(retry_after)
                    logger.warning(f"遇到速率限制，等待 {wait_time} 秒")
                    time.sleep(wait_time)
                except ValueError:
                    pass
    
    def rotate_user_agent(self, session: requests.Session):
        """轮换User-Agent"""
        new_headers = header_rotator.get_headers('stock_data')
        session.headers.update(new_headers)
    
    def add_request_delay(self, url: str, min_delay: float = 2.0, max_delay: float = 5.0):
        """添加请求延迟（优化后的延迟策略）"""
        current_time = time.time()
        last_request = self.request_history.get(url, 0)
        
        # 增加最小延迟，避免请求过于频繁
        if current_time - last_request < min_delay:
            wait_time = random.uniform(min_delay, max_delay)
            logger.info(f"添加反爬虫延迟: {wait_time:.2f} 秒 (URL: {url})")
            time.sleep(wait_time)
        
        self.request_history[url] = current_time
    
    def make_request(self, url: str, method: str = 'GET', **kwargs) -> requests.Response:
        """执行HTTP请求（带反爬虫策略）"""
        session = self.get_session()
        proxy = self.get_proxy()
        
        for attempt in range(self.max_retries):
            try:
                # 添加请求延迟
                self.add_request_delay(url)
                
                # 轮换User-Agent
                self.rotate_user_agent(session)
                
                # 设置代理
                if proxy:
                    kwargs['proxies'] = proxy
                
                # 执行请求
                if method.upper() == 'GET':
                    response = session.get(url, **kwargs)
                elif method.upper() == 'POST':
                    response = session.post(url, **kwargs)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                # 处理速率限制
                self.handle_rate_limit(response)
                
                # 检查响应状态
                response.raise_for_status()
                
                # 记录成功模式
                self._record_success_pattern(url, response)
                
                return response
                
            except Exception as e:
                logger.warning(f"第{attempt + 1}次请求失败: {e}")
                
                if not self.should_retry(e, attempt):
                    raise e
                
                # 计算延迟时间
                delay = self.calculate_delay(attempt)
                logger.info(f"等待 {delay:.2f} 秒后重试")
                time.sleep(delay)
                
                # 如果是代理问题，移除代理
                if proxy and isinstance(e, requests.ProxyError):
                    logger.warning(f"代理 {proxy} 失败，移除代理")
                    self.proxy_list.remove(proxy.get('http', ''))
                    proxy = None
        
        raise Exception(f"请求失败，已重试 {self.max_retries} 次")
    
    def _record_success_pattern(self, url: str, response: requests.Response):
        """记录成功的请求模式"""
        if url not in self.success_patterns:
            self.success_patterns[url] = {
                'success_count': 0,
                'last_success': 0,
                'headers': dict(response.request.headers),
                'method': response.request.method
            }
        
        self.success_patterns[url]['success_count'] += 1
        self.success_patterns[url]['last_success'] = time.time()
    
    def get_success_patterns(self) -> Dict:
        """获取成功模式统计"""
        return self.success_patterns
    
    def reset_strategy(self):
        """重置策略状态"""
        self.request_history.clear()
        self.blocked_ips.clear()
        self.success_patterns.clear()
        logger.info("反爬虫策略已重置")

# 全局反爬虫策略实例
anti_crawler_strategy = AntiCrawlerStrategy()

def get_anti_crawler_strategy():
    """获取反爬虫策略实例"""
    return anti_crawler_strategy
