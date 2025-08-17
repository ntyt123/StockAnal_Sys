#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股信息自动下载脚本（多数据源版本）
每天16:00定时启动，下载全部A股信息并保存到数据库
"""

import os
import sys
import logging
import schedule
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import traceback

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    import akshare as ak
    import pandas as pd
    from sqlalchemy import create_engine, text
    from sqlalchemy.exc import SQLAlchemyError
    from database import StockInfo, get_session, init_db
    from request_headers import get_headers, header_rotator
    from data_sources import data_source_manager
except ImportError as e:
    print(f"导入依赖库失败: {e}")
    print("请确保已安装所需依赖: pip install akshare pandas sqlalchemy")
    sys.exit(1)

# 配置日志
def setup_logging():
    """设置日志配置"""
    log_dir = os.path.join(project_root, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    log_file = os.path.join(log_dir, 'stock_info_download.log')
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    return logging.getLogger(__name__)

logger = setup_logging()

class StockInfoDownloader:
    """A股信息下载器（多数据源版本）"""
    
    def __init__(self):
        """初始化下载器"""
        self.session = None
        self.engine = None
        self.init_database()
        self.setup_data_sources()
    
    def setup_data_sources(self):
        """设置数据源"""
        try:
            logger.info("初始化多数据源管理器...")
            
            # 测试各个数据源
            available_sources = data_source_manager.get_available_sources()
            logger.info(f"可用数据源: {available_sources}")
            
            for source_name in available_sources:
                if data_source_manager.test_source(source_name):
                    logger.info(f"数据源 {source_name} 测试成功")
                else:
                    logger.warning(f"数据源 {source_name} 测试失败")
                    
        except Exception as e:
            logger.warning(f"设置数据源失败: {e}")
    
    def init_database(self):
        """初始化数据库连接"""
        try:
            # 从环境变量获取数据库配置
            database_url = os.getenv('DATABASE_URL', 'sqlite:///data/stock_analyzer.db')
            self.engine = create_engine(database_url)
            
            # 确保数据库表存在
            init_db()
            
            logger.info("数据库初始化成功")
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            raise
    
    def get_session(self):
        """获取数据库会话"""
        if not self.session:
            self.session = get_session()
        return self.session
    
    def close_session(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
            self.session = None
    
    def download_stock_list(self) -> List[Dict]:
        """下载A股列表"""
        try:
            logger.info("开始下载A股列表...")
            
            # 使用多数据源管理器获取股票列表
            stock_list = []
            
            try:
                logger.info("使用多数据源管理器获取股票列表")
                all_stocks = data_source_manager.get_stock_list()
                
                # 处理股票数据
                if not all_stocks.empty:
                    for _, row in all_stocks.iterrows():
                        # 根据数据源格式处理
                        if 'code' in all_stocks.columns:
                            # 新浪财经格式
                            stock_list.append({
                                'stock_code': str(row['code']),
                                'stock_name': str(row['name']),
                                'market_type': 'A',
                                'exchange': row.get('market', 'SH')
                            })
                        elif 'code' in all_stocks.columns:
                            # AKShare格式
                            stock_list.append({
                                'stock_code': str(row['code']),
                                'stock_name': str(row['name']),
                                'market_type': 'A',
                                'exchange': 'SH' if str(row['code']).startswith('6') else 'SZ'
                            })
                    
                    logger.info(f"获取A股列表成功，共 {len(stock_list)} 只股票")
                else:
                    logger.warning("获取到的股票列表为空")
                    
            except Exception as e:
                logger.error(f"获取A股列表失败: {e}")
                return []
            
            # 去重
            unique_stocks = {}
            for stock in stock_list:
                code = stock['stock_code']
                if code not in unique_stocks:
                    unique_stocks[code] = stock
            
            final_stocks = list(unique_stocks.values())
            logger.info(f"A股列表下载完成，共 {len(final_stocks)} 只股票")
            
            return final_stocks
            
        except Exception as e:
            logger.error(f"下载A股列表失败: {e}")
            logger.error(traceback.format_exc())
            return []
    
    def download_stock_details(self, stock_list: List[Dict]) -> List[Dict]:
        """下载股票详细信息"""
        logger.info("开始下载股票详细信息...")
        
        detailed_stocks = []
        total = len(stock_list)
        
        for i, stock in enumerate(stock_list, 1):
            try:
                if i % 100 == 0:
                    logger.info(f"进度: {i}/{total} ({i/total*100:.1f}%)")
                
                stock_code = stock['stock_code']
                
                # 获取股票基本信息
                try:
                    # 使用多数据源管理器获取股票信息
                    logger.debug(f"获取股票 {stock_code} 信息，使用数据源: {data_source_manager.get_current_source()}")
                    
                    stock_info = data_source_manager.get_stock_info(stock_code)
                    if stock_info:
                        # 提取股本信息
                        for item, value in stock_info.items():
                            if '总股本' in item:
                                try:
                                    stock['total_shares'] = float(value.replace(',', ''))
                                except:
                                    stock['total_shares'] = 0
                            elif '流通股本' in item:
                                try:
                                    stock['circulating_shares'] = float(value.replace(',', ''))
                                except:
                                    stock['circulating_shares'] = 0
                            elif '所属行业' in item:
                                stock['industry'] = value
                            elif '上市日期' in item:
                                stock['listing_date'] = value
                        
                        # 获取股票行情
                        try:
                            quote_info = data_source_manager.get_stock_quote(stock_code)
                            if quote_info:
                                stock['current_price'] = quote_info.get('price', 0)
                                stock['change_percent'] = quote_info.get('change', 0)
                                stock['volume'] = quote_info.get('volume', 0)
                                stock['amount'] = quote_info.get('amount', 0)
                        except Exception as e:
                            logger.debug(f"获取股票 {stock_code} 行情失败: {e}")
                        
                        detailed_stocks.append(stock)
                    else:
                        logger.warning(f"股票 {stock_code} 信息为空")
                        
                except Exception as e:
                    logger.warning(f"获取股票 {stock_code} 信息失败: {e}")
                    continue
                
                # 使用数据源管理器的随机时间间隔机制
                # 注意：data_source_manager 已经内置了随机时间间隔控制
                
            except Exception as e:
                logger.error(f"处理股票 {stock_code} 时出错: {e}")
                continue
        
        logger.info(f"股票详细信息下载完成，成功获取 {len(detailed_stocks)} 只股票信息")
        return detailed_stocks
    
    def save_stock_info(self, stock_list: List[Dict]) -> bool:
        """保存股票信息到数据库"""
        try:
            logger.info("开始保存股票信息到数据库...")
            
            session = self.get_session()
            
            # 清空现有数据
            session.query(StockInfo).delete()
            session.commit()
            
            # 插入新数据
            for stock_data in stock_list:
                stock_info = StockInfo(
                    stock_code=stock_data['stock_code'],
                    stock_name=stock_data['stock_name'],
                    market_type=stock_data['market_type'],
                    exchange=stock_data['exchange'],
                    total_shares=stock_data.get('total_shares', 0),
                    circulating_shares=stock_data.get('circulating_shares', 0),
                    industry=stock_data.get('industry', ''),
                    listing_date=stock_data.get('listing_date', ''),
                    current_price=stock_data.get('current_price', 0),
                    change_percent=stock_data.get('change_percent', 0),
                    volume=stock_data.get('volume', 0),
                    amount=stock_data.get('amount', 0),
                    update_time=datetime.now()
                )
                session.add(stock_info)
            
            session.commit()
            logger.info(f"成功保存 {len(stock_list)} 只股票信息到数据库")
            return True
            
        except Exception as e:
            logger.error(f"保存股票信息失败: {e}")
            if session:
                session.rollback()
            return False
        finally:
            self.close_session()
    
    def download_and_save(self) -> bool:
        """下载并保存股票信息"""
        try:
            logger.info("开始下载并保存股票信息...")
            
            # 下载股票列表
            stock_list = self.download_stock_list()
            if not stock_list:
                logger.error("获取股票列表失败")
                return False
            
            # 下载股票详细信息
            detailed_stocks = self.download_stock_details(stock_list)
            if not detailed_stocks:
                logger.error("获取股票详细信息失败")
                return False
            
            # 保存到数据库
            success = self.save_stock_info(detailed_stocks)
            if success:
                logger.info("股票信息下载并保存完成")
                return True
            else:
                logger.error("保存股票信息失败")
                return False
                
        except Exception as e:
            logger.error(f"下载并保存股票信息失败: {e}")
            logger.error(traceback.format_exc())
            return False

def download_stock_info():
    """下载股票信息的主函数"""
    try:
        downloader = StockInfoDownloader()
        success = downloader.download_and_save()
        
        if success:
            logger.info("股票信息下载任务完成")
        else:
            logger.error("股票信息下载任务失败")
            
    except Exception as e:
        logger.error(f"股票信息下载任务异常: {e}")
        logger.error(traceback.format_exc())

def start_stock_download_scheduler():
    """启动股票信息下载定时任务"""
    try:
        logger.info("启动股票信息下载定时任务...")
        
        # 设置每天16:00执行
        schedule.every().day.at("16:00").do(download_stock_info)
        
        # 立即执行一次（可选）
        # download_stock_info()
        
        logger.info("股票信息下载定时任务已启动，每天16:00执行")
        
        # 保持调度器运行
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
            
    except Exception as e:
        logger.error(f"启动股票信息下载定时任务失败: {e}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    try:
        # 设置日志
        logger = setup_logging()
        
        # 启动下载任务
        download_stock_info()
        
    except Exception as e:
        print(f"程序执行失败: {e}")
        sys.exit(1)
