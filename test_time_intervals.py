#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试随机时间间隔功能
"""

import sys
import os
import time

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_time_intervals():
    """测试时间间隔功能"""
    try:
        print("开始测试随机时间间隔功能...")
        
        # 测试导入
        from stock_select.data_sources import data_source_manager, set_time_interval, get_request_stats
        print("✅ 数据源管理器导入成功")
        
        # 测试默认时间间隔
        print("\n1. 测试默认时间间隔设置:")
        stats = get_request_stats()
        print(f"   默认时间间隔: {stats['current_interval']}")
        
        # 测试设置时间间隔
        print("\n2. 测试设置时间间隔:")
        set_time_interval(1.0, 3.0)
        stats = get_request_stats()
        print(f"   新时间间隔: {stats['current_interval']}")
        
        # 测试连续请求的时间间隔
        print("\n3. 测试连续请求的时间间隔:")
        test_symbol = '000001'
        
        print("   第一次请求...")
        start_time = time.time()
        result1 = data_source_manager.get_stock_quote(test_symbol)
        end_time = time.time()
        print(f"   第一次请求耗时: {end_time - start_time:.2f} 秒")
        
        print("   第二次请求...")
        start_time = time.time()
        result2 = data_source_manager.get_stock_quote(test_symbol)
        end_time = time.time()
        print(f"   第二次请求耗时: {end_time - start_time:.2f} 秒")
        
        print("   第三次请求...")
        start_time = time.time()
        result3 = data_source_manager.get_stock_quote(test_symbol)
        end_time = time.time()
        print(f"   第三次请求耗时: {end_time - start_time:.2f} 秒")
        
        # 显示请求统计
        print("\n4. 请求统计信息:")
        stats = get_request_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 测试批量请求
        print("\n5. 测试批量请求的时间间隔:")
        test_symbols = ['000001', '000002', '600000']
        
        for i, symbol in enumerate(test_symbols, 1):
            print(f"   第{i}次请求股票 {symbol}...")
            start_time = time.time()
            result = data_source_manager.get_stock_quote(symbol)
            end_time = time.time()
            print(f"   请求耗时: {end_time - start_time:.2f} 秒")
            
            if result:
                print(f"   获取成功: {result.get('name', 'N/A')} - 价格: {result.get('price', 'N/A')}")
            else:
                print(f"   获取失败")
        
        print("\n" + "=" * 50)
        print("✅ 随机时间间隔功能测试完成！")
        print("=" * 50)
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已创建相关模块文件")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_time_intervals()
