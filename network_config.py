# -*- coding: utf-8 -*-
"""
网络配置优化模块
用于改善AKShare等数据源的网络连接稳定性
"""

import requests
import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)

# 网络请求配置
REQUEST_TIMEOUT = 30  # 请求超时时间（秒）
MAX_RETRIES = 3      # 最大重试次数
RETRY_DELAY = 2      # 重试间隔（秒）

def configure_requests_session():
    """配置requests会话，优化网络连接"""
    session = requests.Session()
    
    # 设置请求头，模拟浏览器行为
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })
    
    # 设置连接池
    adapter = requests.adapters.HTTPAdapter(
        pool_connections=10,
        pool_maxsize=20,
        max_retries=3,
        pool_block=False
    )
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    return session

def retry_on_network_error(max_retries=MAX_RETRIES, delay=RETRY_DELAY):
    """网络错误重试装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except (requests.exceptions.ConnectionError, 
                        requests.exceptions.Timeout,
                        requests.exceptions.RequestException,
                        ConnectionAbortedError,
                        ConnectionResetError) as e:
                    last_exception = e
                    
                    if attempt < max_retries - 1:
                        logger.warning(f"网络请求失败，第 {attempt + 1} 次重试: {e}")
                        time.sleep(delay * (attempt + 1))  # 递增延迟
                    else:
                        logger.error(f"网络请求最终失败: {e}")
                        raise last_exception
            
            return None
        return wrapper
    return decorator

def safe_akshare_call(func, *args, **kwargs):
    """安全的AKShare函数调用，带重试机制"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            logger.debug(f"调用AKShare函数 {func.__name__}，第 {retry_count + 1} 次尝试")
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"AKShare函数 {func.__name__} 调用失败，第 {retry_count} 次重试: {e}")
                time.sleep(2 * retry_count)  # 递增延迟
            else:
                logger.error(f"AKShare函数 {func.__name__} 最终调用失败: {e}")
                raise e
    
    return None

# 网络状态检查
def check_network_connectivity():
    """检查网络连接状态"""
    try:
        response = requests.get('https://www.baidu.com', timeout=5)
        return response.status_code == 200
    except:
        return False

def get_network_info():
    """获取网络信息"""
    import socket
    try:
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return {
            'hostname': hostname,
            'ip_address': ip_address,
            'connectivity': check_network_connectivity()
        }
    except Exception as e:
        logger.error(f"获取网络信息失败: {e}")
        return {'error': str(e)}
