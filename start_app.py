#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速启动Flask应用的脚本
避免在启动时下载大量股票数据
"""

import os
import sys
from web_server import app

if __name__ == '__main__':
    print("正在启动股票分析系统...")
    print("访问地址: http://localhost:8888")
    print("按 Ctrl+C 停止应用")
    
    # 设置环境变量，禁用启动时的股票下载
    os.environ['SKIP_INITIAL_DOWNLOAD'] = 'true'
    
    # 启动Flask应用
    app.run(
        host='0.0.0.0', 
        port=8888, 
        debug=False,
        use_reloader=False  # 禁用自动重载，避免重复启动
    )
