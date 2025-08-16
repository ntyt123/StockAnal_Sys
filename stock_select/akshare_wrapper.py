#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AKShare包装器
用于更好地控制请求头和网络请求，提高数据获取成功率
"""

import time
import random
import logging
from typing import Optional, Any, Dict
from request_headers import get_headers, header_rotator

logger = logging.getLogger(__name__)

class AKShareWrapper:
    """AKShare包装器，提供请求头控制和重试机制"""
    
    def __init__(self):
        """初始化包装器"""
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 0.5  # 最小请求间隔（秒）
        
    def _wait_if_needed(self):
        """如果需要，等待一段时间再发送请求"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        if time_since_last < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    def _get_request_headers(self, header_type='stock_data'):
        """获取请求头"""
        self.request_count += 1
        return header_rotator.get_headers(header_type)
    
    def _log_request(self, method_name, symbol=None):
        """记录请求日志"""
        headers = self._get_request_headers()
        user_agent = headers['User-Agent'][:50] + "..." if len(headers['User-Agent']) > 50 else headers['User-Agent']
        
        if symbol:
            logger.debug(f"请求 {method_name} - 股票: {symbol}, User-Agent: {user_agent}")
        else:
            logger.debug(f"请求 {method_name}, User-Agent: {user_agent}")
    
    def stock_info_a_code_name(self, **kwargs):
        """获取A股代码名称列表"""
        try:
            self._wait_if_needed()
            self._log_request("stock_info_a_code_name")
            
            # 导入akshare
            import akshare as ak
            
            # 设置请求头（如果支持）
            headers = self._get_request_headers()
            if hasattr(ak, 'set_headers'):
                ak.set_headers(headers)
            
            # 执行请求
            result = ak.stock_info_a_code_name(**kwargs)
            
            # 添加随机延迟
            time.sleep(random.uniform(0.1, 0.3))
            
            return result
            
        except Exception as e:
            logger.error(f"获取A股代码名称列表失败: {e}")
            raise
    
    def stock_individual_info_em(self, symbol: str, **kwargs):
        """获取个股信息"""
        try:
            self._wait_if_needed()
            self._log_request("stock_individual_info_em", symbol)
            
            # 导入akshare
            import akshare as ak
            
            # 设置请求头（如果支持）
            headers = self._get_request_headers()
            if hasattr(ak, 'set_headers'):
                ak.set_headers(headers)
            
            # 执行请求
            result = ak.stock_individual_info_em(symbol=symbol, **kwargs)
            
            # 添加随机延迟
            time.sleep(random.uniform(0.2, 0.5))
            
            return result
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 信息失败: {e}")
            raise
    
    def stock_profile_cninfo(self, symbol: str, **kwargs):
        """获取公司概况"""
        try:
            self._wait_if_needed()
            self._log_request("stock_profile_cninfo", symbol)
            
            # 导入akshare
            import akshare as ak
            
            # 设置请求头（如果支持）
            headers = self._get_request_headers()
            if hasattr(ak, 'set_headers'):
                ak.set_headers(headers)
            
            # 执行请求
            result = ak.stock_profile_cninfo(symbol=symbol, **kwargs)
            
            # 添加随机延迟
            time.sleep(random.uniform(0.3, 0.6))
            
            return result
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 公司概况失败: {e}")
            raise
    
    def stock_zh_a_spot_em(self, **kwargs):
        """获取A股实时行情"""
        try:
            self._wait_if_needed()
            self._log_request("stock_zh_a_spot_em")
            
            # 导入akshare
            import akshare as ak
            
            # 设置请求头（如果支持）
            headers = self._get_request_headers()
            if hasattr(ak, 'set_headers'):
                ak.set_headers(headers)
            
            # 执行请求
            result = ak.stock_zh_a_spot_em(**kwargs)
            
            # 添加随机延迟
            time.sleep(random.uniform(0.1, 0.3))
            
            return result
            
        except Exception as e:
            logger.error(f"获取A股实时行情失败: {e}")
            raise
    
    def set_request_interval(self, interval: float):
        """设置请求间隔"""
        self.min_request_interval = max(0.1, interval)
        logger.info(f"设置请求间隔为 {self.min_request_interval} 秒")
    
    def get_request_stats(self):
        """获取请求统计信息"""
        return {
            'total_requests': self.request_count,
            'last_request_time': self.last_request_time,
            'min_interval': self.min_request_interval
        }

# 全局AKShare包装器实例
ak_wrapper = AKShareWrapper()

# 便捷函数
def get_ak_wrapper():
    """获取AKShare包装器实例"""
    return ak_wrapper

def set_request_interval(interval: float):
    """设置请求间隔的便捷函数"""
    ak_wrapper.set_request_interval(interval)

def get_request_stats():
    """获取请求统计信息的便捷函数"""
    return ak_wrapper.get_request_stats()
