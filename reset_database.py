#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
重置数据库脚本
删除现有数据库并重新创建
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def reset_database():
    """重置数据库"""
    print("🔧 开始重置数据库...")
    
    try:
        # 删除数据库文件
        db_path = os.path.join(project_root, 'data', 'stock_analyzer.db')
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ 已删除旧数据库文件: {db_path}")
        
        # 重新初始化数据库
        from database import init_db, get_session, StockInfo
        
        print("📊 重新创建数据库表...")
        init_db()
        print("✅ 数据库表创建成功！")
        
        # 检查数据库连接
        session = get_session()
        print("🔍 检查数据库连接...")
        
        # 测试查询
        stock_count = session.query(StockInfo).count()
        print(f"✅ 数据库连接正常，当前股票数量: {stock_count}")
        
        session.close()
        
        # 显示数据库文件信息
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            file_size_kb = file_size / 1024
            print(f"📁 数据库文件: {db_path}")
            print(f"📏 文件大小: {file_size_kb:.2f} KB")
        
        print("\n🎉 数据库重置完成！")
        
    except Exception as e:
        print(f"❌ 数据库重置失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 股票分析系统 - 数据库重置工具")
    print("=" * 50)
    
    reset_database()
    
    print("\n" + "=" * 50)
    print("重置完成！")
