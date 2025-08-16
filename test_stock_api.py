#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票API端点的脚本
"""

import requests
import json

def test_stock_api():
    """测试股票API端点"""
    base_url = "http://localhost:8888"
    
    print("🧪 测试股票API端点")
    print("=" * 40)
    
    # 测试1: 获取股票下载状态
    print("1. 测试股票下载状态API...")
    try:
        response = requests.get(f"{base_url}/api/stock_download_status")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 状态API正常: {data}")
        else:
            print(f"❌ 状态API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 状态API异常: {e}")
    
    print()
    
    # 测试2: 获取股票列表
    print("2. 测试获取股票列表API...")
    try:
        response = requests.get(f"{base_url}/api/stocks", params={
            'market_type': 'A',
            'industry': '',
            'limit': 10
        })
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                stocks = data['data']['stocks']
                print(f"✅ 股票列表API正常，获取到 {len(stocks)} 只股票")
                if stocks:
                    print("前3只股票:")
                    for i, stock in enumerate(stocks[:3]):
                        print(f"  {i+1}. {stock['code']} - {stock['name']} ({stock['industry']})")
                else:
                    print("⚠️ 股票列表为空，可能需要先下载数据")
            else:
                print(f"❌ 股票列表API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 股票列表API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 股票列表API异常: {e}")
    
    print()
    
    # 测试3: 测试行业筛选
    print("3. 测试行业筛选API...")
    try:
        response = requests.get(f"{base_url}/api/stocks", params={
            'market_type': 'A',
            'industry': '银行',
            'limit': 5
        })
        if response.status_code == 200:
            data = response.json()
            if data['success']:
                stocks = data['data']['stocks']
                print(f"✅ 行业筛选API正常，银行行业股票: {len(stocks)} 只")
                if stocks:
                    print("银行股票:")
                    for stock in stocks:
                        print(f"  {stock['code']} - {stock['name']}")
                else:
                    print("⚠️ 银行行业没有找到股票")
            else:
                print(f"❌ 行业筛选API返回错误: {data.get('message', '未知错误')}")
        else:
            print(f"❌ 行业筛选API失败: {response.status_code}")
    except Exception as e:
        print(f"❌ 行业筛选API异常: {e}")
    
    print()
    print("=" * 40)
    print("测试完成！")

if __name__ == "__main__":
    test_stock_api()

