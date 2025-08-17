#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试增强后的数据源管理器功能
包括随机时间间隔、重试机制等
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

def test_enhanced_data_sources():
    """测试增强后的数据源管理器"""
    try:
        print("开始测试增强后的数据源管理器...")
        
        # 测试导入
        from stock_select.data_sources import (
            data_source_manager, 
            set_time_interval, 
            get_request_stats,
            get_stock_quote,
            get_stock_info
        )
        print("✅ 数据源管理器导入成功")
        
        # 设置更保守的时间间隔
        print("\n1. 设置时间间隔:")
        set_time_interval(1.5, 3.0)  # 最小1.5秒，最大3秒
        stats = get_request_stats()
        print(f"   时间间隔: {stats['current_interval']}")
        
        # 测试单个股票获取
        print("\n2. 测试单个股票获取:")
        test_symbols = ['000001', '000002', '600000']
        
        for symbol in test_symbols:
            print(f"\n   获取股票 {symbol} 信息...")
            start_time = time.time()
            
            try:
                # 获取股票信息
                info = get_stock_info(symbol)
                if info:
                    print(f"   ✅ 股票信息获取成功")
                    print(f"      名称: {info.get('股票简称', 'N/A')}")
                    print(f"      行业: {info.get('行业', 'N/A')}")
                else:
                    print(f"   ❌ 股票信息为空")
                
                # 获取股票行情
                quote = get_stock_quote(symbol)
                if quote:
                    print(f"   ✅ 股票行情获取成功")
                    print(f"      名称: {quote.get('name', 'N/A')}")
                    print(f"      价格: {quote.get('price', 'N/A')}")
                    print(f"      涨跌幅: {quote.get('change', 'N/A')}%")
                else:
                    print(f"   ❌ 股票行情为空")
                    
            except Exception as e:
                print(f"   ❌ 获取失败: {e}")
            
            end_time = time.time()
            print(f"   总耗时: {end_time - start_time:.2f} 秒")
        
        # 显示请求统计
        print("\n3. 请求统计信息:")
        stats = get_request_stats()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        
        # 测试批量获取（模拟实际应用场景）
        print("\n4. 测试批量获取（模拟实际应用场景）:")
        batch_symbols = ['000001', '000002', '000004', '000005', '000006']
        
        successful_count = 0
        total_start_time = time.time()
        
        for i, symbol in enumerate(batch_symbols, 1):
            print(f"   进度: {i}/{len(batch_symbols)} - 获取股票 {symbol}")
            
            try:
                quote = get_stock_quote(symbol)
                if quote and quote.get('name'):
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
        
        print("\n" + "=" * 60)
        print("✅ 增强后的数据源管理器测试完成！")
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

if __name__ == "__main__":
    success = test_enhanced_data_sources()
    if success:
        print("\n🎉 测试成功！数据源管理器工作正常")
    else:
        print("\n⚠️  测试存在问题，请检查日志")
