#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试akshare能获取到的股票信息字段
"""

import akshare as ak
import pandas as pd
import sys

def test_stock_list_info():
    """测试股票列表信息"""
    print("=" * 60)
    print("1. 测试股票列表信息 (ak.stock_info_a_code_name)")
    print("=" * 60)
    
    try:
        stocks = ak.stock_info_a_code_name()
        print(f"获取成功，共 {len(stocks)} 只股票")
        print(f"列名: {stocks.columns.tolist()}")
        print(f"前3行数据:")
        print(stocks.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()

def test_stock_individual_info():
    """测试个股详细信息"""
    print("=" * 60)
    print("2. 测试个股详细信息 (ak.stock_individual_info_em)")
    print("=" * 60)
    
    # 测试几个不同的股票代码
    test_codes = ['000001', '600000', '300001']
    
    for code in test_codes:
        try:
            print(f"\n股票代码: {code}")
            info = ak.stock_individual_info_em(symbol=code)
            print(f"列名: {info.columns.tolist()}")
            print(f"数据行数: {len(info)}")
            print("前5行数据:")
            print(info.head())
            print("-" * 40)
        except Exception as e:
            print(f"获取 {code} 失败: {e}")

def test_stock_real_time_info():
    """测试股票实时信息"""
    print("=" * 60)
    print("3. 测试股票实时信息 (ak.stock_zh_a_spot_em)")
    print("=" * 60)
    
    try:
        real_time = ak.stock_zh_a_spot_em()
        print(f"获取成功，共 {len(real_time)} 只股票")
        print(f"列名: {real_time.columns.tolist()}")
        print(f"前3行数据:")
        print(real_time.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()

def test_stock_financial_info():
    """测试股票财务信息"""
    print("=" * 60)
    print("4. 测试股票财务信息 (ak.stock_financial_analysis_indicator)")
    print("=" * 60)
    
    try:
        # 测试平安银行的财务指标
        financial = ak.stock_financial_analysis_indicator(symbol="000001")
        print(f"获取成功，共 {len(financial)} 条记录")
        print(f"列名: {financial.columns.tolist()}")
        print(f"前3行数据:")
        print(financial.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()

def test_stock_industry_info():
    """测试股票行业信息"""
    print("=" * 60)
    print("5. 测试股票行业信息 (ak.stock_board_industry_cons_em)")
    print("=" * 60)
    
    try:
        # 测试银行行业成分股
        industry_stocks = ak.stock_board_industry_cons_em(symbol="银行")
        print(f"获取成功，共 {len(industry_stocks)} 只股票")
        print(f"列名: {industry_stocks.columns.tolist()}")
        print(f"前3行数据:")
        print(industry_stocks.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()

def test_stock_profile_info():
    """测试股票概况信息"""
    print("=" * 60)
    print("6. 测试股票概况信息 (ak.stock_profile_cninfo)")
    print("=" * 60)
    
    try:
        # 测试平安银行的概况信息
        profile = ak.stock_profile_cninfo(symbol="000001")
        print(f"获取成功，共 {len(profile)} 条记录")
        print(f"列名: {profile.columns.tolist()}")
        print(f"前3行数据:")
        print(profile.head(3))
        print()
    except Exception as e:
        print(f"获取失败: {e}")
        print()

def main():
    """主函数"""
    print("🚀 测试akshare股票信息获取功能")
    print("=" * 60)
    
    try:
        # 测试各种信息获取
        test_stock_list_info()
        test_stock_individual_info()
        test_stock_real_time_info()
        test_stock_financial_info()
        test_stock_industry_info()
        test_stock_profile_info()
        
        print("✅ 所有测试完成！")
        
    except Exception as e:
        print(f"❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
