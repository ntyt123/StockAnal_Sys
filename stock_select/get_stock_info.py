#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股信息自动下载脚本
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
    """A股信息下载器"""
    
    def __init__(self):
        """初始化下载器"""
        self.session = None
        self.engine = None
        self.init_database()
    
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
            
            # 使用akshare获取A股列表
            stock_list = []
            
            # 获取沪深A股列表
            try:
                # 上海证券交易所A股
                sh_stocks = ak.stock_info_a_code_name()
                if not sh_stocks.empty:
                    for _, row in sh_stocks.iterrows():
                        stock_list.append({
                            'stock_code': str(row['code']),
                            'stock_name': str(row['name']),
                            'market_type': 'A',
                            'exchange': 'SH'
                        })
                    logger.info(f"获取上海A股 {len(sh_stocks)} 只")
            except Exception as e:
                logger.warning(f"获取上海A股失败: {e}")
            
            # 深圳证券交易所A股
            try:
                sz_stocks = ak.stock_info_a_code_name()
                if not sz_stocks.empty:
                    for _, row in sz_stocks.iterrows():
                        stock_list.append({
                            'stock_code': str(row['code']),
                            'stock_name': str(row['name']),
                            'market_type': 'A',
                            'exchange': 'SZ'
                        })
                    logger.info(f"获取深圳A股 {len(sz_stocks)} 只")
            except Exception as e:
                logger.warning(f"获取深圳A股失败: {e}")
            
            # 创业板
            try:
                cy_stocks = ak.stock_info_a_code_name()
                if not cy_stocks.empty:
                    for _, row in cy_stocks.iterrows():
                        stock_list.append({
                            'stock_code': str(row['code']),
                            'stock_name': str(row['name']),
                            'market_type': 'A',
                            'exchange': 'CY'
                        })
                    logger.info(f"获取创业板 {len(cy_stocks)} 只")
            except Exception as e:
                logger.warning(f"获取创业板失败: {e}")
            
            # 科创板
            try:
                kc_stocks = ak.stock_info_a_code_name()
                if not kc_stocks.empty:
                    for _, row in kc_stocks.iterrows():
                        stock_list.append({
                            'stock_code': str(row['code']),
                            'stock_name': str(row['name']),
                            'market_type': 'A',
                            'exchange': 'KC'
                        })
                    logger.info(f"获取科创板 {len(kc_stocks)} 只")
            except Exception as e:
                logger.warning(f"获取科创板失败: {e}")
            
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
                    # 获取股票实时信息
                    stock_info = ak.stock_individual_info_em(symbol=stock_code)
                    if not stock_info.empty:
                        # 提取股本信息
                        for _, row in stock_info.iterrows():
                            item = str(row['item']).strip()
                            value = str(row['value']).strip()
                            
                            if '总股本' in item:
                                try:
                                    stock['total_shares'] = int(float(value))
                                except:
                                    stock['total_shares'] = None
                            elif '流通股' in item:
                                try:
                                    stock['circulating_shocks'] = int(float(value))
                                except:
                                    stock['circulating_shocks'] = None
                        
                        stock['industry'] = "未知"
                        
                except Exception as e:
                    logger.debug(f"获取股票 {stock_code} 详细信息失败: {e}")
                    stock['industry'] = "未知"
                    stock['total_shares'] = None
                    stock['circulating_shocks'] = None
                
                # 获取股票实时行情信息
                try:
                    real_time_info = ak.stock_zh_a_spot_em()
                    if not real_time_info.empty:
                        # 找到对应的股票
                        stock_row = real_time_info[real_time_info['代码'] == stock_code]
                        if not stock_row.empty:
                            row = stock_row.iloc[0]
                            
                            # 提取财务指标
                            try:
                                stock['pe_ratio'] = float(row['市盈率-动态']) if row['市盈率-动态'] != '-' else None
                            except:
                                stock['pe_ratio'] = None
                            
                            try:
                                stock['pb_ratio'] = float(row['市净率']) if row['市净率'] != '-' else None
                            except:
                                stock['pb_ratio'] = None
                            
                            try:
                                stock['market_value'] = float(row['总市值']) if row['总市值'] != '-' else None
                            except:
                                stock['market_value'] = None
                            
                            try:
                                stock['circulating_value'] = float(row['流通市值']) if row['流通市值'] != '-' else None
                            except:
                                stock['circulating_value'] = None
                            
                            # 提取价格信息
                            try:
                                stock['current_price'] = float(row['最新价']) if row['最新价'] != '-' else None
                            except:
                                stock['current_price'] = None
                            
                            try:
                                stock['price_change'] = float(row['涨跌幅']) if row['涨跌幅'] != '-' else None
                            except:
                                stock['price_change'] = None
                            
                except Exception as e:
                    logger.debug(f"获取股票 {stock_code} 实时行情失败: {e}")
                    stock['pe_ratio'] = None
                    stock['pb_ratio'] = None
                    stock['market_value'] = None
                    stock['circulating_value'] = None
                    stock['current_price'] = None
                    stock['price_change'] = None
                
                # 获取公司概况信息
                try:
                    profile_info = ak.stock_profile_cninfo(symbol=stock_code)
                    if not profile_info.empty:
                        row = profile_info.iloc[0]
                        
                        # 提取公司信息
                        stock['company_name'] = str(row.get('公司名称', ''))
                        stock['english_name'] = str(row.get('英文名称', ''))
                        stock['former_name'] = str(row.get('曾用简称', ''))
                        stock['legal_representative'] = str(row.get('法人代表', ''))
                        stock['registered_capital'] = str(row.get('注册资金', ''))
                        stock['establishment_date'] = str(row.get('成立日期', ''))
                        stock['list_date'] = str(row.get('上市日期', ''))
                        stock['website'] = str(row.get('官方网站', ''))
                        stock['email'] = str(row.get('电子邮箱', ''))
                        stock['phone'] = str(row.get('联系电话', ''))
                        stock['fax'] = str(row.get('传真', ''))
                        stock['registered_address'] = str(row.get('注册地址', ''))
                        stock['office_address'] = str(row.get('办公地址', ''))
                        stock['postal_code'] = str(row.get('邮政编码', ''))
                        stock['main_business'] = str(row.get('主营业务', ''))
                        stock['business_scope'] = str(row.get('经营范围', ''))
                        stock['company_intro'] = str(row.get('机构简介', ''))
                        stock['selected_indices'] = str(row.get('入选指数', ''))
                        
                        # 更新行业信息
                        if row.get('所属行业'):
                            stock['industry'] = str(row['所属行业'])
                        
                except Exception as e:
                    logger.debug(f"获取股票 {stock_code} 公司概况失败: {e}")
                    # 设置默认值
                    stock['company_name'] = stock['stock_name']
                    stock['english_name'] = ''
                    stock['former_name'] = ''
                    stock['legal_representative'] = ''
                    stock['registered_capital'] = ''
                    stock['establishment_date'] = ''
                    stock['list_date'] = ''
                    stock['website'] = ''
                    stock['email'] = ''
                    stock['phone'] = ''
                    stock['fax'] = ''
                    stock['registered_address'] = ''
                    stock['office_address'] = ''
                    stock['postal_code'] = ''
                    stock['main_business'] = ''
                    stock['business_scope'] = ''
                    stock['company_intro'] = ''
                    stock['selected_indices'] = ''
                
                detailed_stocks.append(stock)
                
                # 避免请求过于频繁
                time.sleep(0.1)
                
            except Exception as e:
                logger.warning(f"处理股票 {stock_code} 时出错: {e}")
                continue
        
        logger.info(f"股票详细信息下载完成，共 {len(detailed_stocks)} 只")
        return detailed_stocks
    
    def save_to_database(self, stock_list: List[Dict]) -> bool:
        """保存股票信息到数据库"""
        try:
            session = self.get_session()
            
            # 清空现有数据
            session.execute(text("DELETE FROM stock_info WHERE market_type = 'A'"))
            logger.info("已清空现有A股数据")
            
            # 批量插入新数据
            for stock in stock_list:
                stock_info = StockInfo(
                    stock_code=stock['stock_code'],
                    stock_name=stock['stock_name'],
                    market_type=stock['market_type'],
                    industry=stock.get('industry', '未知'),
                    updated_at=datetime.now(),
                    
                    # 基础信息
                    exchange=stock.get('exchange', ''),
                    company_name=stock.get('company_name', ''),
                    english_name=stock.get('english_name', ''),
                    former_name=stock.get('former_name', ''),
                    
                    # 股本信息
                    total_shares=stock.get('total_shares'),
                    circulating_shares=stock.get('circulating_shocks'),
                    
                    # 财务指标
                    pe_ratio=stock.get('pe_ratio'),
                    pb_ratio=stock.get('pb_ratio'),
                    market_value=stock.get('market_value'),
                    circulating_value=stock.get('circulating_value'),
                    
                    # 公司信息
                    legal_representative=stock.get('legal_representative', ''),
                    registered_capital=stock.get('registered_capital', ''),
                    establishment_date=stock.get('establishment_date', ''),
                    list_date=stock.get('list_date', ''),
                    website=stock.get('website', ''),
                    email=stock.get('email', ''),
                    phone=stock.get('phone', ''),
                    fax=stock.get('fax', ''),
                    registered_address=stock.get('registered_address', ''),
                    office_address=stock.get('office_address', ''),
                    postal_code=stock.get('postal_code', ''),
                    main_business=stock.get('main_business', ''),
                    business_scope=stock.get('business_scope', ''),
                    company_intro=stock.get('company_intro', ''),
                    selected_indices=stock.get('selected_indices', '')
                )
                session.add(stock_info)
            
            # 提交事务
            session.commit()
            logger.info(f"成功保存 {len(stock_list)} 只A股信息到数据库")
            
            return True
            
        except SQLAlchemyError as e:
            logger.error(f"数据库操作失败: {e}")
            if session:
                session.rollback()
            return False
        except Exception as e:
            logger.error(f"保存数据失败: {e}")
            if session:
                session.rollback()
            return False
    
    def run_download(self) -> bool:
        """执行完整的下载流程"""
        start_time = datetime.now()
        logger.info("=" * 50)
        logger.info(f"开始执行A股信息下载任务 - {start_time}")
        logger.info("=" * 50)
        
        try:
            # 1. 下载A股列表
            stock_list = self.download_stock_list()
            if not stock_list:
                logger.error("下载A股列表失败，任务终止")
                return False
            
            # 2. 下载详细信息
            detailed_stocks = self.download_stock_details(stock_list)
            if not detailed_stocks:
                logger.error("下载股票详细信息失败，任务终止")
                return False
            
            # 3. 保存到数据库
            success = self.save_to_database(detailed_stocks)
            if not success:
                logger.error("保存到数据库失败，任务终止")
                return False
            
            end_time = datetime.now()
            duration = end_time - start_time
            
            logger.info("=" * 50)
            logger.info(f"A股信息下载任务完成 - {end_time}")
            logger.info(f"总耗时: {duration}")
            logger.info(f"成功处理: {len(detailed_stocks)} 只股票")
            logger.info("=" * 50)
            
            return True
            
        except Exception as e:
            logger.error(f"下载任务执行失败: {e}")
            logger.error(traceback.format_exc())
            return False
        finally:
            self.close_session()

def main():
    """主函数"""
    try:
        downloader = StockInfoDownloader()
        
        # 立即执行一次
        logger.info("执行首次下载...")
        success = downloader.run_download()
        
        if success:
            logger.info("首次下载完成，开始定时任务...")
            
            # 设置定时任务 - 每天16:00执行
            schedule.every().day.at("16:00").do(downloader.run_download)
            
            # 运行定时任务
            while True:
                schedule.run_pending()
                time.sleep(60)  # 每分钟检查一次
        else:
            logger.error("首次下载失败，程序退出")
            sys.exit(1)
            
    except KeyboardInterrupt:
        logger.info("收到中断信号，程序退出")
    except Exception as e:
        logger.error(f"程序运行出错: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main()
