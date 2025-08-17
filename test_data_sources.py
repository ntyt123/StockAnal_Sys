#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多数据源功能
"""

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def test_data_sources():
    """测试数据源功能"""
    try:
        print("开始测试多数据源功能...")
        
        # 测试导入
        from stock_select.data_sources import data_source_manager
        print("✅ 数据源管理器导入成功")
        
        # 测试可用数据源
        available_sources = data_source_manager.get_available_sources()
        print(f"✅ 可用数据源: {available_sources}")
        
        # 测试数据源
        for source_name in available_sources:
            print(f"\n测试数据源: {source_name}")
            try:
                if data_source_manager.test_source(source_name):
                    print(f"✅ {source_name} 测试成功")
                else:
                    print(f"❌ {source_name} 测试失败")
            except Exception as e:
                print(f"❌ {source_name} 测试异常: {e}")
        
        # 测试获取股票列表
        print("\n测试获取股票列表...")
        try:
            stock_list = data_source_manager.get_stock_list()
            if not stock_list.empty:
                print(f"✅ 获取股票列表成功，共 {len(stock_list)} 只股票")
                print(f"   数据列: {list(stock_list.columns)}")
                print(f"   前3只股票:")
                for i, (_, row) in enumerate(stock_list.head(3).iterrows()):
                    print(f"     {i+1}. {row.to_dict()}")
            else:
                print("❌ 获取股票列表为空")
        except Exception as e:
            print(f"❌ 获取股票列表失败: {e}")
        
        # 测试获取股票信息
        print("\n测试获取股票信息...")
        test_symbol = '000001'
        try:
            stock_info = data_source_manager.get_stock_info(test_symbol)
            if stock_info:
                print(f"✅ 获取股票 {test_symbol} 信息成功")
                print(f"   信息: {stock_info}")
            else:
                print(f"❌ 获取股票 {test_symbol} 信息为空")
        except Exception as e:
            print(f"❌ 获取股票 {test_symbol} 信息失败: {e}")
        
        # 测试获取股票行情
        print("\n测试获取股票行情...")
        try:
            stock_quote = data_source_manager.get_stock_quote(test_symbol)
            if stock_quote:
                print(f"✅ 获取股票 {test_symbol} 行情成功")
                print(f"   行情: {stock_quote}")
            else:
                print(f"❌ 获取股票 {test_symbol} 行情为空")
        except Exception as e:
            print(f"❌ 获取股票 {test_symbol} 行情失败: {e}")
        
        print("\n" + "=" * 50)
        print("✅ 多数据源功能测试完成！")
        print("=" * 50)
        
    except ImportError as e:
        print(f"❌ 模块导入失败: {e}")
        print("请确保已创建相关模块文件")
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_data_sources()
