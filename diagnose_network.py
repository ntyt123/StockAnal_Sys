#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连接诊断工具
用于诊断股票分析系统的网络连接问题
"""

import requests
import time
import socket
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_basic_connectivity():
    """测试基本网络连接"""
    print("=" * 50)
    print("基本网络连接测试")
    print("=" * 50)
    
    # 测试DNS解析
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        print(f"✓ 本地主机名: {hostname}")
        print(f"✓ 本地IP地址: {ip}")
    except Exception as e:
        print(f"✗ DNS解析失败: {e}")
    
    # 测试外网连接
    test_urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.taobao.com"
    ]
    
    for url in test_urls:
        try:
            start_time = time.time()
            response = requests.get(url, timeout=10)
            end_time = time.time()
            if response.status_code == 200:
                print(f"✓ {url} - 连接成功 (响应时间: {end_time - start_time:.2f}秒)")
            else:
                print(f"⚠ {url} - 连接成功但状态码异常: {response.status_code}")
        except requests.exceptions.Timeout:
            print(f"✗ {url} - 连接超时")
        except requests.exceptions.ConnectionError:
            print(f"✗ {url} - 连接错误")
        except Exception as e:
            print(f"✗ {url} - 未知错误: {e}")

def test_akshare_connectivity():
    """测试AKShare相关数据源连接"""
    print("\n" + "=" * 50)
    print("AKShare数据源连接测试")
    print("=" * 50)
    
    try:
        import akshare as ak
        print("✓ AKShare库导入成功")
        
        # 测试东方财富数据源
        print("\n测试东方财富数据源...")
        try:
            start_time = time.time()
            # 尝试获取一个简单的数据
            stock_list = ak.stock_zh_a_spot_em()
            end_time = time.time()
            
            if not stock_list.empty:
                print(f"✓ 东方财富数据源连接成功 (响应时间: {end_time - start_time:.2f}秒)")
                print(f"  获取到 {len(stock_list)} 只股票数据")
            else:
                print("⚠ 东方财富数据源连接成功但数据为空")
        except Exception as e:
            print(f"✗ 东方财富数据源连接失败: {e}")
        
        # 测试其他数据源
        print("\n测试其他数据源...")
        try:
            start_time = time.time()
            # 测试股票基本信息
            stock_info = ak.stock_individual_info_em(symbol="000001")
            end_time = time.time()
            
            if not stock_info.empty:
                print(f"✓ 股票基本信息数据源连接成功 (响应时间: {end_time - start_time:.2f}秒)")
            else:
                print("⚠ 股票基本信息数据源连接成功但数据为空")
        except Exception as e:
            print(f"✗ 股票基本信息数据源连接失败: {e}")
            
    except ImportError:
        print("✗ AKShare库未安装")
    except Exception as e:
        print(f"✗ AKShare测试失败: {e}")

def test_proxy_settings():
    """测试代理设置"""
    print("\n" + "=" * 50)
    print("代理设置检查")
    print("=" * 50)
    
    # 检查环境变量中的代理设置
    import os
    proxy_vars = ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']
    
    for var in proxy_vars:
        value = os.environ.get(var)
        if value:
            print(f"⚠ 发现代理设置: {var}={value}")
        else:
            print(f"✓ 未设置代理: {var}")
    
    # 检查requests的代理设置
    try:
        session = requests.Session()
        if session.proxies:
            print(f"⚠ requests会话使用代理: {session.proxies}")
        else:
            print("✓ requests会话未使用代理")
    except Exception as e:
        print(f"✗ 检查requests代理设置失败: {e}")

def provide_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 50)
    print("问题解决方案建议")
    print("=" * 50)
    
    print("""
如果遇到网络连接问题，请尝试以下解决方案：

1. 网络连接问题：
   - 检查网络连接是否稳定
   - 尝试重启路由器或网络设备
   - 检查防火墙设置

2. AKShare连接问题：
   - 更新AKShare到最新版本: pip install --upgrade akshare
   - 检查网络是否被数据源限制
   - 尝试使用VPN或代理

3. 频率限制问题：
   - 减少请求频率，增加请求间隔
   - 使用缓存机制减少重复请求
   - 考虑使用付费API服务

4. 代码优化：
   - 添加重试机制
   - 实现请求超时设置
   - 使用连接池优化

5. 环境配置：
   - 检查.env文件中的网络相关配置
   - 确认Docker网络设置
   - 验证端口映射配置
""")

def main():
    """主函数"""
    print(f"网络连接诊断工具 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_basic_connectivity()
    test_akshare_connectivity()
    test_proxy_settings()
    provide_solutions()
    
    print("\n" + "=" * 50)
    print("诊断完成")
    print("=" * 50)

if __name__ == "__main__":
    main()
