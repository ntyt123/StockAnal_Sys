#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的股票下载功能
"""

import os
import sys
import time
import logging

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def test_single_stock():
    """测试单只股票数据获取"""
    try:
        import akshare as ak
        
        print("测试单只股票数据获取...")
        
        # 测试A股实时行情
        print("1. 测试A股实时行情...")
        start_time = time.time()
        real_time_data = ak.stock_zh_a_spot_em()
        end_time = time.time()
        
        if not real_time_data.empty:
            print(f"✅ 成功获取实时行情数据，共 {len(real_time_data)} 只股票")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            
            # 显示前5只股票
            print("   前5只股票:")
            for i, (_, row) in enumerate(real_time_data.head().iterrows()):
                print(f"   {i+1}. {row['代码']} {row['名称']} 价格:{row['最新价']}")
        else:
            print("❌ 实时行情数据为空")
        
        # 测试个股信息
        print("\n2. 测试个股信息...")
        test_stock = "000001"  # 平安银行
        
        start_time = time.time()
        stock_info = ak.stock_individual_info_em(symbol=test_stock)
        end_time = time.time()
        
        if not stock_info.empty:
            print(f"✅ 成功获取股票 {test_stock} 信息")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            
            # 显示部分信息
            print("   基本信息:")
            for _, row in stock_info.head(3).iterrows():
                print(f"   {row['item']}: {row['value']}")
        else:
            print(f"❌ 获取股票 {test_stock} 信息失败")
        
        # 测试公司概况
        print("\n3. 测试公司概况...")
        start_time = time.time()
        profile_info = ak.stock_profile_cninfo(symbol=test_stock)
        end_time = time.time()
        
        if not profile_info.empty:
            print(f"✅ 成功获取股票 {test_stock} 公司概况")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            
            # 显示部分信息
            row = profile_info.iloc[0]
            print(f"   公司名称: {row.get('公司名称', 'N/A')}")
            print(f"   所属行业: {row.get('所属行业', 'N/A')}")
        else:
            print(f"❌ 获取股票 {test_stock} 公司概况失败")
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_batch_requests():
    """测试批量请求控制"""
    try:
        from stock_select.request_config import RequestConfig
        
        print("\n测试批量请求控制...")
        
        config = RequestConfig()
        
        # 测试频率限制
        print("1. 测试频率限制...")
        
        for i in range(3):
            start_time = time.time()
            config.should_wait('stock_zh_a_spot_em')
            config.record_request('stock_zh_a_spot_em')
            end_time = time.time()
            
            print(f"   第 {i+1} 次请求，耗时: {end_time - start_time:.2f} 秒")
        
        # 测试缓存
        print("\n2. 测试缓存功能...")
        
        test_data = {"test": "data"}
        config.set_cached_data("test_key", test_data)
        
        cached_data = config.get_cached_data("test_key", expiry=60)
        if cached_data == test_data:
            print("   ✅ 缓存功能正常")
        else:
            print("   ❌ 缓存功能异常")
            
    except Exception as e:
        print(f"❌ 批量请求控制测试失败: {e}")
        import traceback
        traceback.print_exc()

def test_optimized_downloader():
    """测试优化后的下载器"""
    try:
        from stock_select.get_stock_info import StockInfoDownloader
        
        print("\n测试优化后的下载器...")
        
        # 创建下载器实例
        downloader = StockInfoDownloader()
        
        # 测试批量获取实时数据
        print("1. 测试批量获取实时数据...")
        start_time = time.time()
        real_time_data = downloader._get_real_time_data_batch()
        end_time = time.time()
        
        if real_time_data is not None and not real_time_data.empty:
            print(f"✅ 批量获取成功，共 {len(real_time_data)} 只股票")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
        else:
            print("❌ 批量获取失败")
        
        # 测试小批量股票处理
        print("\n2. 测试小批量股票处理...")
        test_stocks = [
            {'stock_code': '000001', 'stock_name': '平安银行', 'market_type': 'A', 'exchange': 'SZ'},
            {'stock_code': '000002', 'stock_name': '万科A', 'market_type': 'A', 'exchange': 'SZ'},
            {'stock_code': '000858', 'stock_name': '五粮液', 'market_type': 'A', 'exchange': 'SZ'},
        ]
        
        start_time = time.time()
        detailed_stocks = downloader.download_stock_details(test_stocks)
        end_time = time.time()
        
        if detailed_stocks:
            print(f"✅ 小批量处理成功，共 {len(detailed_stocks)} 只股票")
            print(f"   耗时: {end_time - start_time:.2f} 秒")
            
            # 显示第一只股票的详细信息
            if detailed_stocks:
                first_stock = detailed_stocks[0]
                print(f"   第一只股票详情:")
                print(f"   代码: {first_stock.get('stock_code')}")
                print(f"   名称: {first_stock.get('stock_name')}")
                print(f"   当前价格: {first_stock.get('current_price')}")
                print(f"   市盈率: {first_stock.get('pe_ratio')}")
        else:
            print("❌ 小批量处理失败")
            
    except Exception as e:
        print(f"❌ 优化后下载器测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始测试优化后的股票下载功能...")
    print("=" * 50)
    
    # 测试单只股票
    test_single_stock()
    
    # 测试批量请求控制
    test_batch_requests()
    
    # 测试优化后的下载器
    test_optimized_downloader()
    
    print("\n" + "=" * 50)
    print("测试完成！")
