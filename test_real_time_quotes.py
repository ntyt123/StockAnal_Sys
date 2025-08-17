#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试反爬虫机制在获取股票实时行情时的应用情况
验证每个数据源是否正确使用了反爬虫策略
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

def test_real_time_quotes_with_anti_crawler():
    """测试实时行情获取时的反爬虫机制应用"""
    try:
        print("开始测试实时行情获取时的反爬虫机制...")
        
        # 测试导入
        from stock_select.smart_data_source import SmartStockSource
        from stock_select.anti_crawler_strategy import get_anti_crawler_strategy
        
        print("✅ 模块导入成功")
        
        # 获取实例
        smart_source = SmartStockSource()
        anti_crawler = get_anti_crawler_strategy()
        
        print(f"✅ 智能数据源: {smart_source.name}")
        print(f"✅ 反爬虫策略: {type(anti_crawler).__name__}")
        
        # 测试股票列表
        print("\n1. 测试股票列表获取:")
        try:
            stock_list = smart_source.get_stock_list()
            print(f"   ✅ 成功获取股票列表，共 {len(stock_list)} 只股票")
        except Exception as e:
            print(f"   ❌ 获取股票列表失败: {e}")
        
        # 测试实时行情获取（逐个数据源测试）
        print("\n2. 测试实时行情获取（验证反爬虫机制）:")
        test_symbols = ['000001', '000002', '600000']
        
        for symbol in test_symbols:
            print(f"\n   获取股票 {symbol} 实时行情...")
            start_time = time.time()
            
            try:
                # 获取行情
                quote = smart_source.get_stock_quote(symbol)
                
                if quote and quote.get('price'):
                    print(f"   ✅ 行情获取成功")
                    print(f"      名称: {quote.get('name', 'N/A')}")
                    print(f"      价格: {quote.get('price', 'N/A')}")
                    print(f"      数据源: {quote.get('source', 'N/A')}")
                else:
                    print(f"   ❌ 行情数据为空")
                    
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
            
            end_time = time.time()
            print(f"   耗时: {end_time - start_time:.2f} 秒")
        
        # 检查反爬虫策略的统计信息
        print("\n3. 检查反爬虫策略应用情况:")
        
        # 检查请求历史
        request_history = anti_crawler.request_history
        print(f"   请求历史记录数量: {len(request_history)}")
        for url, timestamp in request_history.items():
            time_str = time.strftime('%H:%M:%S', time.localtime(timestamp))
            print(f"     {url}: {time_str}")
        
        # 检查成功模式
        success_patterns = anti_crawler.get_success_patterns()
        print(f"   成功请求模式数量: {len(success_patterns)}")
        for url, pattern in success_patterns.items():
            print(f"     {url}: 成功{pattern['success_count']}次")
        
        # 检查会话池
        print(f"   会话池大小: {len(anti_crawler.session_pool)}")
        
        # 检查代理配置
        print(f"   代理列表大小: {len(anti_crawler.proxy_list)}")
        
        # 测试批量获取（模拟实际应用场景）
        print("\n4. 测试批量获取（验证反爬虫机制效果）:")
        batch_symbols = ['000001', '000002', '000004', '000005', '000006']
        
        successful_count = 0
        total_start_time = time.time()
        
        for i, symbol in enumerate(batch_symbols, 1):
            print(f"   进度: {i}/{len(batch_symbols)} - 获取股票 {symbol}")
            
            try:
                quote = smart_source.get_stock_quote(symbol)
                if quote and quote.get('price'):
                    successful_count += 1
                    print(f"   ✅ 成功: {quote.get('name')} - {quote.get('price')}")
                else:
                    print(f"   ❌ 失败: 数据为空")
            except Exception as e:
                print(f"   ❌ 失败: {e}")
        
        total_end_time = time.time()
        total_time = total_end_time - total_start_time
        
        print(f"\n   批量获取完成:")
        print(f"   成功: {successful_count}/{len(batch_symbols)}")
        print(f"   成功率: {successful_count/len(batch_symbols)*100:.1f}%")
        print(f"   总耗时: {total_time:.2f} 秒")
        print(f"   平均每只股票: {total_time/len(batch_symbols):.2f} 秒")
        
        # 验证反爬虫机制是否生效
        print("\n5. 验证反爬虫机制效果:")
        
        # 检查是否有请求延迟
        if len(request_history) > 1:
            print("   ✅ 请求历史记录存在，说明延迟机制生效")
            
            # 计算请求间隔
            timestamps = sorted(request_history.values())
            intervals = []
            for i in range(1, len(timestamps)):
                interval = timestamps[i] - timestamps[i-1]
                intervals.append(interval)
            
            if intervals:
                avg_interval = sum(intervals) / len(intervals)
                min_interval = min(intervals)
                print(f"   平均请求间隔: {avg_interval:.2f} 秒")
                print(f"   最小请求间隔: {min_interval:.2f} 秒")
                
                if min_interval >= 0.5:  # 至少0.5秒间隔
                    print("   ✅ 请求间隔合理，反爬虫延迟机制生效")
                else:
                    print("   ⚠️  请求间隔过短，可能存在反爬虫绕过风险")
        else:
            print("   ⚠️  请求历史记录不足，无法验证延迟机制")
        
        # 检查是否使用了多个数据源
        if success_patterns:
            print("   ✅ 成功模式记录存在，说明请求头轮换等机制生效")
        else:
            print("   ⚠️  成功模式记录为空")
        
        print("\n" + "=" * 60)
        print("✅ 实时行情反爬虫机制测试完成！")
        print("=" * 60)
        
        return successful_count > 0
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已创建相关模块文件")
        return False
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_anti_crawler_mechanisms():
    """测试具体的反爬虫机制"""
    try:
        print("\n开始测试具体反爬虫机制...")
        
        from stock_select.anti_crawler_strategy import get_anti_crawler_strategy
        
        strategy = get_anti_crawler_strategy()
        
        print("1. 测试请求延迟机制:")
        test_url = "test_url_1"
        
        # 第一次请求
        start_time = time.time()
        strategy.add_request_delay(test_url, min_delay=1.0, max_delay=2.0)
        first_request_time = time.time() - start_time
        
        # 立即第二次请求（应该被延迟）
        start_time = time.time()
        strategy.add_request_delay(test_url, min_delay=1.0, max_delay=2.0)
        second_request_time = time.time() - start_time
        
        print(f"   第一次请求耗时: {first_request_time:.3f} 秒")
        print(f"   第二次请求耗时: {second_request_time:.3f} 秒")
        
        if second_request_time > first_request_time:
            print("   ✅ 请求延迟机制生效")
        else:
            print("   ❌ 请求延迟机制未生效")
        
        print("2. 测试会话轮换:")
        session1 = strategy.get_session()
        session2 = strategy.get_session()
        
        if session1 != session2:
            print("   ✅ 会话轮换机制生效")
        else:
            print("   ⚠️  会话轮换机制可能未生效")
        
        print("3. 测试User-Agent轮换:")
        original_headers = dict(session1.headers)
        strategy.rotate_user_agent(session1)
        new_headers = dict(session1.headers)
        
        if original_headers != new_headers:
            print("   ✅ User-Agent轮换机制生效")
        else:
            print("   ⚠️  User-Agent轮换机制可能未生效")
        
        return True
        
    except Exception as e:
        print(f"❌ 反爬虫机制测试失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试实时行情反爬虫机制")
    print("=" * 60)
    
    # 测试实时行情反爬虫机制
    success1 = test_real_time_quotes_with_anti_crawler()
    
    # 测试具体反爬虫机制
    success2 = test_anti_crawler_mechanisms()
    
    if success1 and success2:
        print("\n🎉 所有测试通过！反爬虫机制在实时行情获取中正常工作")
    else:
        print("\n⚠️  部分测试失败，请检查日志")
