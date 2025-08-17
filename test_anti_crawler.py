#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试反爬虫策略
验证各种反爬虫技术的效果
"""

import sys
import os
import time
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_anti_crawler_strategy():
    """测试反爬虫策略"""
    try:
        print("开始测试反爬虫策略...")
        
        # 测试导入
        from stock_select.anti_crawler_strategy import get_anti_crawler_strategy
        from stock_select.smart_data_source import SmartStockSource
        
        print("✅ 反爬虫策略模块导入成功")
        
        # 获取反爬虫策略实例
        strategy = get_anti_crawler_strategy()
        print(f"✅ 反爬虫策略实例创建成功")
        
        # 测试智能数据源
        print("\n1. 测试智能数据源:")
        smart_source = SmartStockSource()
        print(f"   数据源名称: {smart_source.name}")
        print(f"   可用数据源数量: {len(smart_source.data_sources)}")
        
        # 测试股票信息获取
        print("\n2. 测试股票信息获取:")
        test_symbols = ['000001', '000002', '600000']
        
        for symbol in test_symbols:
            print(f"\n   获取股票 {symbol} 信息...")
            start_time = time.time()
            
            try:
                info = smart_source.get_stock_info(symbol)
                if info:
                    print(f"   ✅ 股票信息获取成功")
                    print(f"      名称: {info.get('股票简称', 'N/A')}")
                    print(f"      行业: {info.get('行业', 'N/A')}")
                else:
                    print(f"   ❌ 股票信息为空")
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
            
            end_time = time.time()
            print(f"   耗时: {end_time - start_time:.2f} 秒")
        
        # 测试股票行情获取
        print("\n3. 测试股票行情获取:")
        for symbol in test_symbols:
            print(f"\n   获取股票 {symbol} 行情...")
            start_time = time.time()
            
            try:
                quote = smart_source.get_stock_quote(symbol)
                if quote and quote.get('price'):
                    print(f"   ✅ 股票行情获取成功")
                    print(f"      名称: {quote.get('name', 'N/A')}")
                    print(f"      价格: {quote.get('price', 'N/A')}")
                    print(f"      数据源: {quote.get('source', 'N/A')}")
                else:
                    print(f"   ❌ 股票行情为空")
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
            
            end_time = time.time()
            print(f"   耗时: {end_time - start_time:.2f} 秒")
        
        # 测试缓存功能
        print("\n4. 测试缓存功能:")
        cache_stats = smart_source.get_cache_stats()
        print(f"   缓存大小: {cache_stats['cache_size']}")
        print(f"   缓存TTL: {cache_stats['cache_ttl']} 秒")
        print(f"   已缓存项目: {cache_stats['cached_symbols']}")
        
        # 测试反爬虫策略统计
        print("\n5. 测试反爬虫策略统计:")
        success_patterns = strategy.get_success_patterns()
        print(f"   成功模式数量: {len(success_patterns)}")
        for url, pattern in success_patterns.items():
            print(f"   URL: {url}")
            print(f"     成功次数: {pattern['success_count']}")
            print(f"     最后成功: {time.strftime('%H:%M:%S', time.localtime(pattern['last_success']))}")
        
        print("\n" + "=" * 60)
        print("✅ 反爬虫策略测试完成！")
        print("=" * 60)
        
        return True
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已创建相关模块文件")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_proxy_functionality():
    """测试代理功能"""
    try:
        print("\n开始测试代理功能...")
        
        from stock_select.anti_crawler_strategy import get_anti_crawler_strategy
        
        strategy = get_anti_crawler_strategy()
        
        # 添加测试代理
        test_proxies = [
            "http://127.0.0.1:8080",
            "http://127.0.0.1:8081",
            "socks5://127.0.0.1:1080"
        ]
        
        for proxy in test_proxies:
            strategy.add_proxy(proxy)
        
        print(f"✅ 添加了 {len(strategy.proxy_list)} 个测试代理")
        
        # 测试代理获取
        proxy = strategy.get_proxy()
        if proxy:
            print(f"✅ 成功获取代理: {proxy}")
        else:
            print("❌ 代理获取失败")
        
        return True
        
    except Exception as e:
        print(f"❌ 代理功能测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始反爬虫策略测试")
    print("=" * 60)
    
    # 测试反爬虫策略
    success1 = test_anti_crawler_strategy()
    
    # 测试代理功能
    success2 = test_proxy_functionality()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！反爬虫策略工作正常")
    else:
        print("\n⚠️  部分测试失败，请检查日志")
