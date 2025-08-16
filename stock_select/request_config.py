#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
请求配置管理模块
用于控制API请求频率、缓存策略和错误处理
"""

import time
import logging
from typing import Optional, Any, Dict
from functools import wraps

logger = logging.getLogger(__name__)

class RequestConfig:
    """请求配置管理类"""
    
    def __init__(self):
        # 缓存设置
        self.cache = {}
        self.cache_timestamps = {}
        
        # 频率限制设置
        self.request_intervals = {
            'stock_zh_a_spot_em': 2.0,      # A股实时行情：2秒间隔
            'stock_individual_info_em': 1.0, # 个股信息：1秒间隔
            'stock_profile_cninfo': 1.5,     # 公司概况：1.5秒间隔
        }
        
        # 重试设置
        self.max_retries = 3
        self.retry_delays = [2, 5, 10]  # 递增延迟时间
        
        # 最后请求时间记录
        self.last_request_times = {}
    
    def get_cached_data(self, key: str, expiry: int = 60) -> Optional[Any]:
        """获取缓存数据"""
        if key in self.cache and key in self.cache_timestamps:
            current_time = time.time()
            if current_time - self.cache_timestamps[key] < expiry:
                logger.debug(f"使用缓存数据: {key}, 缓存时间: {current_time - self.cache_timestamps[key]:.1f}秒")
                return self.cache[key]
        return None
    
    def set_cached_data(self, key: str, data: Any):
        """设置缓存数据"""
        self.cache[key] = data
        self.cache_timestamps[key] = time.time()
        logger.debug(f"缓存数据更新: {key}")
    
    def should_wait(self, api_name: str) -> bool:
        """检查是否需要等待以避免频率限制"""
        if api_name not in self.last_request_times:
            return False
        
        current_time = time.time()
        interval = self.request_intervals.get(api_name, 1.0)
        time_since_last = current_time - self.last_request_times[api_name]
        
        if time_since_last < interval:
            wait_time = interval - time_since_last
            logger.debug(f"频率限制：等待 {wait_time:.1f} 秒")
            time.sleep(wait_time)
            return True
        return False
    
    def record_request(self, api_name: str):
        """记录请求时间"""
        self.last_request_times[api_name] = time.time()
    
    def clear_cache(self):
        """清理缓存"""
        self.cache.clear()
        self.cache_timestamps.clear()
        logger.info("缓存已清理")

def rate_limited(api_name: str):
    """频率限制装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            # 检查缓存
            cache_key = f"{api_name}_{hash(str(args) + str(kwargs))}"
            cached_result = self.request_config.get_cached_data(cache_key, expiry=60)
            if cached_result is not None:
                return cached_result
            
            # 检查频率限制
            self.request_config.should_wait(api_name)
            
            # 执行请求
            try:
                result = func(self, *args, **kwargs)
                # 缓存结果
                self.request_config.set_cached_data(cache_key, result)
                # 记录请求时间
                self.request_config.record_request(api_name)
                return result
            except Exception as e:
                logger.warning(f"API请求失败 {api_name}: {e}")
                raise
        return wrapper
    return decorator

def retry_on_failure(max_retries: int = 3, delays: list = None):
    """重试装饰器"""
    if delays is None:
        delays = [2, 5, 10]
    
    def decorator(func):
        @wraps(func)
        def wrapper(self, *args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(self, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        delay = delays[min(attempt, len(delays) - 1)]
                        logger.warning(f"请求失败，第 {attempt + 1} 次重试，等待 {delay} 秒: {e}")
                        time.sleep(delay)
                    else:
                        logger.error(f"请求最终失败: {e}")
                        raise last_exception
            
            return None
        return wrapper
    return decorator

# 全局配置实例
request_config = RequestConfig()
