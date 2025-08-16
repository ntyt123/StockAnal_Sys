#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票数据获取测试脚本
用于诊断AKShare数据源连接问题
"""

import time
import traceback
from datetime import datetime

def test_basic_imports():
    """测试基本模块导入"""
    print("=" * 60)
    print("测试基本模块导入")
    print("=" * 60)
    
    try:
        import akshare as ak
        print("✓ AKShare导入成功")
        print(f"  AKShare版本: {ak.__version__}")
    except ImportError as e:
        print(f"✗ AKShare导入失败: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas导入成功")
        print(f"  Pandas版本: {pd.__version__}")
    except ImportError as e:
        print(f"✗ Pandas导入失败: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests导入成功")
        print(f"  Requests版本: {requests.__version__}")
    except ImportError as e:
        print(f"✗ Requests导入失败: {e}")
        return False
    
    return True

def test_network_connectivity():
    """测试网络连接"""
    print("\n" + "=" * 60)
    print("测试网络连接")
    print("=" * 60)
    
    import requests
    
    test_urls = [
        "https://www.baidu.com",
        "https://www.qq.com",
        "https://www.taobao.com",
        "https://www.eastmoney.com",  # 东方财富
        "https://www.akshare.xyz"    # AKShare官网
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
        except requests.exceptions.ConnectionError as e:
            print(f"✗ {url} - 连接错误: {e}")
        except Exception as e:
            print(f"✗ {url} - 未知错误: {e}")

def test_akshare_functions():
    """测试AKShare各个功能"""
    print("\n" + "=" * 60)
    print("测试AKShare功能")
    print("=" * 60)
    
    import akshare as ak
    
    # 测试股票列表获取
    print("1. 测试获取A股股票列表...")
    try:
        start_time = time.time()
        stock_list = ak.stock_zh_a_spot_em()
        end_time = time.time()
        
        if not stock_list.empty:
            print(f"✓ 获取A股股票列表成功 (响应时间: {end_time - start_time:.2f}秒)")
            print(f"  获取到 {len(stock_list)} 只股票数据")
            print(f"  数据列: {list(stock_list.columns)}")
        else:
            print("⚠ 获取A股股票列表成功但数据为空")
    except Exception as e:
        print(f"✗ 获取A股股票列表失败: {e}")
        print(f"  错误详情: {traceback.format_exc()}")
    
    # 测试单个股票信息
    print("\n2. 测试获取单个股票信息...")
    test_stocks = ["000001", "000002", "000017"]  # 包含您提到的000017
    
    for stock_code in test_stocks:
        try:
            print(f"  测试股票 {stock_code}...")
            start_time = time.time()
            
            # 测试实时行情
            stock_info = ak.stock_zh_a_spot_em()
            if not stock_info.empty:
                stock_row = stock_info[stock_info['代码'] == stock_code]
                if not stock_row.empty:
                    print(f"    ✓ 实时行情获取成功")
                    print(f"      股票名称: {stock_row.iloc[0]['名称']}")
                    print(f"      最新价: {stock_row.iloc[0]['最新价']}")
                else:
                    print(f"    ⚠ 未找到股票 {stock_code} 的实时行情")
            else:
                print(f"    ⚠ 实时行情数据为空")
            
            # 测试基本信息
            basic_info = ak.stock_individual_info_em(symbol=stock_code)
            if not basic_info.empty:
                print(f"    ✓ 基本信息获取成功")
                print(f"      数据行数: {len(basic_info)}")
            else:
                print(f"    ⚠ 基本信息数据为空")
            
            end_time = time.time()
            print(f"    总耗时: {end_time - start_time:.2f}秒")
            
        except Exception as e:
            print(f"    ✗ 获取股票 {stock_code} 信息失败: {e}")
            if "Connection aborted" in str(e) or "RemoteDisconnected" in str(e):
                print(f"      这是网络连接问题，可能是数据源限制或网络不稳定")
    
    # 测试其他数据源
    print("\n3. 测试其他数据源...")
    
    # 测试港股数据
    try:
        print("  测试港股数据...")
        hk_stocks = ak.stock_hk_spot_em()
        if not hk_stocks.empty:
            print(f"    ✓ 港股数据获取成功，共 {len(hk_stocks)} 只股票")
        else:
            print("    ⚠ 港股数据为空")
    except Exception as e:
        print(f"    ✗ 港股数据获取失败: {e}")
    
    # 测试美股数据
    # try:
    #     print("  测试美股数据...")
    #     us_stocks = ak.stock_us_spot_em()
    #     if not us_stocks.empty:
    #         print(f"    ✓ 美股数据获取成功，共 {len(us_stocks)} 只股票")
    #     else:
    #         print("    ⚠ 美股数据为空")
    # except Exception as e:
    #     print(f"    ✗ 美股数据获取失败: {e}")

def test_with_retry():
    """测试重试机制"""
    print("\n" + "=" * 60)
    print("测试重试机制")
    print("=" * 60)
    
    import akshare as ak
    
    def get_stock_data_with_retry(stock_code, max_retries=3):
        """带重试的股票数据获取"""
        for attempt in range(max_retries):
            try:
                print(f"  第 {attempt + 1} 次尝试获取股票 {stock_code} 数据...")
                start_time = time.time()
                
                stock_info = ak.stock_zh_a_spot_em()
                if not stock_info.empty:
                    stock_row = stock_info[stock_info['代码'] == stock_code]
                    if not stock_row.empty:
                        end_time = time.time()
                        print(f"    ✓ 成功！耗时: {end_time - start_time:.2f}秒")
                        return stock_row.iloc[0]
                
                print(f"    ⚠ 数据为空")
                return None
                
            except Exception as e:
                end_time = time.time()
                print(f"    ✗ 失败！耗时: {end_time - start_time:.2f}秒，错误: {e}")
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2
                    print(f"    ⏳ 等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                else:
                    print(f"    ❌ 所有重试都失败了")
                    return None
        
        return None
    
    # 测试重试机制
    test_stock = "000017"
    print(f"测试重试机制 - 股票代码: {test_stock}")
    
    result = get_stock_data_with_retry(test_stock)
    if result is not None:
        print(f"最终结果: {result['名称']} - {result['最新价']}")
    else:
        print("最终结果: 获取失败")

def provide_solutions():
    """提供解决方案建议"""
    print("\n" + "=" * 60)
    print("问题解决方案建议")
    print("=" * 60)
    
    print("""
基于测试结果，如果遇到网络连接问题，请尝试以下解决方案：

1. 网络连接问题：
   - 检查服务器网络连接是否稳定
   - 尝试重启网络服务: sudo systemctl restart networking
   - 检查防火墙设置: sudo ufw status
   - 检查DNS设置: cat /etc/resolv.conf

2. AKShare相关问题：
   - 更新AKShare到最新版本: pip install --upgrade akshare
   - 检查AKShare版本兼容性
   - 尝试使用不同的数据源

3. 频率限制问题：
   - 减少请求频率，增加请求间隔
   - 实现请求队列和限流机制
   - 考虑使用付费API服务

4. 代码优化：
   - 添加重试机制（已实现）
   - 实现请求超时设置
   - 使用连接池优化
   - 添加错误分类和处理

5. 环境配置：
   - 检查Python环境: python --version
   - 检查依赖版本: pip list
   - 确认网络代理设置
   - 验证服务器时间同步

6. 数据源备选方案：
   - 使用其他股票数据API
   - 实现数据缓存机制
   - 考虑离线数据更新
""")

def main():
    """主函数"""
    print(f"股票数据获取测试工具 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 测试基本导入
    if not test_basic_imports():
        print("基本模块导入失败，请检查环境配置")
        return
    
    # 测试网络连接
    test_network_connectivity()
    
    # 测试AKShare功能
    test_akshare_functions()
    
    # 测试重试机制
    test_with_retry()
    
    # 提供解决方案
    provide_solutions()
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()
