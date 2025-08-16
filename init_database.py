#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建数据库和表结构
"""

import os
import sys

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def init_database():
    """初始化数据库"""
    print("🔧 开始初始化数据库...")
    
    try:
        # 确保data目录存在
        data_dir = os.path.join(project_root, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"✅ 创建数据目录: {data_dir}")
        
        # 设置环境变量
        os.environ['USE_DATABASE'] = 'True'
        os.environ['DATABASE_URL'] = 'sqlite:///data/stock_analyzer.db'
        
        # 导入数据库模块
        from database import init_db, get_session, StockInfo
        
        # 初始化数据库
        print("📊 创建数据库表...")
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
        db_path = os.path.join(data_dir, 'stock_analyzer.db')
        if os.path.exists(db_path):
            file_size = os.path.getsize(db_path)
            file_size_kb = file_size / 1024
            print(f"📁 数据库文件: {db_path}")
            print(f"📏 文件大小: {file_size_kb:.2f} KB")
            print(f"🕒 创建时间: {os.path.getctime(db_path)}")
        
        print("\n🎉 数据库初始化完成！")
        print("\n💡 下一步操作:")
        print("  1. 运行股票数据下载器获取A股数据")
        print("  2. 使用SQLite工具查看数据库内容")
        print("  3. 启动Web服务器使用股票筛选功能")
        
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        import traceback
        traceback.print_exc()

def check_database_status():
    """检查数据库状态"""
    print("\n🔍 检查数据库状态...")
    
    try:
        # 设置环境变量
        os.environ['USE_DATABASE'] = 'True'
        os.environ['DATABASE_URL'] = 'sqlite:///data/stock_analyzer.db'
        
        from database import get_session, StockInfo
        
        session = get_session()
        
        # 检查表是否存在
        from sqlalchemy import inspect
        inspector = inspect(session.bind)
        tables = inspector.get_table_names()
        
        print(f"📋 数据库中的表: {', '.join(tables)}")
        
        # 检查各表的记录数
        for table_name in tables:
            if table_name == 'stock_info':
                count = session.query(StockInfo).count()
                print(f"  - {table_name}: {count} 条记录")
        
        session.close()
        
    except Exception as e:
        print(f"❌ 检查数据库状态失败: {e}")

if __name__ == "__main__":
    print("🚀 股票分析系统 - 数据库初始化工具")
    print("=" * 50)
    
    # 初始化数据库
    init_database()
    
    # 检查状态
    check_database_status()
    
    print("\n" + "=" * 50)
    print("初始化完成！")

