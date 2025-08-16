#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
网络连接测试脚本
测试国内镜像源的连接性
"""

import requests
import time
import sys

def test_url(url, name, timeout=10):
    """测试URL连接性"""
    try:
        print(f"测试 {name}: {url}")
        start_time = time.time()
        response = requests.get(url, timeout=timeout)
        end_time = time.time()
        
        if response.status_code == 200:
            print(f"✅ {name} 连接成功 - 耗时: {end_time - start_time:.2f}秒")
            return True
        else:
            print(f"❌ {name} 连接失败 - 状态码: {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ {name} 连接超时")
        return False
    except requests.exceptions.ConnectionError:
        print(f"❌ {name} 连接错误")
        return False
    except Exception as e:
        print(f"❌ {name} 未知错误: {e}")
        return False

def test_pip_mirrors():
    """测试pip镜像源"""
    print("=" * 50)
    print("测试pip镜像源连接性")
    print("=" * 50)
    
    mirrors = [
        ("https://pypi.tuna.tsinghua.edu.cn/simple/", "清华大学镜像源"),
        ("https://pypi.douban.com/simple/", "豆瓣镜像源"),
        ("https://mirrors.aliyun.com/pypi/simple/", "阿里云镜像源"),
        ("https://pypi.mirrors.ustc.edu.cn/simple/", "中科大镜像源"),
    ]
    
    results = []
    for url, name in mirrors:
        result = test_url(url, name)
        results.append((name, result))
        time.sleep(1)  # 避免请求过快
    
    return results

def test_akshare_sources():
    """测试AKShare数据源"""
    print("\n" + "=" * 50)
    print("测试AKShare数据源连接性")
    print("=" * 50)
    
    sources = [
        ("https://www.akshare.xyz", "AKShare官网"),
        ("https://www.akshare.xyz/zh_CN/", "AKShare中文页面"),
    ]
    
    results = []
    for url, name in sources:
        result = test_url(url, name)
        results.append((name, result))
        time.sleep(1)
    
    return results

def test_debian_mirrors():
    """测试Debian镜像源"""
    print("\n" + "=" * 50)
    print("测试Debian镜像源连接性")
    print("=" * 50)
    
    mirrors = [
        ("https://mirrors.tuna.tsinghua.edu.cn/debian/", "清华大学Debian镜像"),
        ("https://mirrors.aliyun.com/debian/", "阿里云Debian镜像"),
        ("https://mirrors.ustc.edu.cn/debian/", "中科大Debian镜像"),
    ]
    
    results = []
    for url, name in mirrors:
        result = test_url(url, name)
        results.append((name, result))
        time.sleep(1)
    
    return results

def main():
    """主函数"""
    print("开始网络连接测试...")
    print("时间:", time.strftime("%Y-%m-%d %H:%M:%S"))
    
    # 测试pip镜像源
    pip_results = test_pip_mirrors()
    
    # 测试AKShare数据源
    akshare_results = test_akshare_sources()
    
    # 测试Debian镜像源
    debian_results = test_debian_mirrors()
    
    # 汇总结果
    print("\n" + "=" * 50)
    print("测试结果汇总")
    print("=" * 50)
    
    all_results = pip_results + akshare_results + debian_results
    success_count = sum(1 for _, result in all_results if result)
    total_count = len(all_results)
    
    print(f"总测试数: {total_count}")
    print(f"成功数: {success_count}")
    print(f"失败数: {total_count - success_count}")
    print(f"成功率: {success_count/total_count*100:.1f}%")
    
    # 显示失败的测试
    failed_tests = [name for name, result in all_results if not result]
    if failed_tests:
        print(f"\n❌ 失败的测试:")
        for name in failed_tests:
            print(f"  - {name}")
    
    # 给出建议
    print(f"\n💡 建议:")
    if success_count >= total_count * 0.8:
        print("  网络连接良好，可以正常使用")
    elif success_count >= total_count * 0.5:
        print("  网络连接一般，建议使用VPN或代理")
    else:
        print("  网络连接较差，强烈建议使用VPN或代理")
    
    return success_count >= total_count * 0.5

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        sys.exit(1)
