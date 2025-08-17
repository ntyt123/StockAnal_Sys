#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
智能数据源
使用多种反爬虫策略获取股票数据
"""

import time
import random
import logging
import pandas as pd
from typing import Dict, Any, Optional
from .data_sources import DataSource
from .anti_crawler_strategy import get_anti_crawler_strategy

logger = logging.getLogger(__name__)

class SmartStockSource(DataSource):
    """智能股票数据源"""
    
    def __init__(self):
        """初始化智能数据源"""
        self.name = "智能数据源"
        self.anti_crawler = get_anti_crawler_strategy()
        self.cache = {}
        self.cache_ttl = 300  # 缓存5分钟
        
        # 数据源优先级（腾讯财经优先）
        self.data_sources = [
            self._try_tencent_finance,  # 腾讯财经放在首位
            self._try_sina_finance,
            self._try_akshare_spot,
            self._try_163_finance,
            self._try_akshare_individual
        ]
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            logger.info("使用智能数据源获取股票列表")
            
            # 尝试AKShare获取完整列表
            try:
                import akshare as ak
                result = ak.stock_info_a_code_name()
                if not result.empty:
                    logger.info(f"成功获取股票列表，共 {len(result)} 只")
                    return result
            except Exception as e:
                logger.warning(f"AKShare获取股票列表失败: {e}")
            
            # 如果AKShare失败，返回基础列表
            logger.info("使用基础股票列表")
            return self._get_basic_stock_list()
            
        except Exception as e:
            logger.error(f"获取股票列表失败: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息"""
        try:
            logger.info(f"使用智能数据源获取股票 {symbol} 信息")
            
            # 检查缓存
            cache_key = f"info_{symbol}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    logger.debug(f"从缓存获取股票 {symbol} 信息")
                    return cache_data
            
            # 尝试多个数据源
            for source_func in self.data_sources:
                try:
                    if source_func.__name__.endswith('_individual'):
                        result = source_func(symbol)
                        if result:
                            # 缓存结果
                            self.cache[cache_key] = (time.time(), result)
                            return result
                except Exception as e:
                    logger.debug(f"数据源 {source_func.__name__} 失败: {e}")
                    continue
            
            # 如果所有数据源都失败，返回基础信息
            logger.warning(f"所有数据源都无法获取股票 {symbol} 信息，返回基础信息")
            return self._get_basic_stock_info(symbol)
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 信息失败: {e}")
            raise
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        try:
            logger.info(f"使用智能数据源获取股票 {symbol} 行情")
            
            # 检查缓存
            cache_key = f"quote_{symbol}"
            if cache_key in self.cache:
                cache_time, cache_data = self.cache[cache_key]
                if time.time() - cache_time < self.cache_ttl:
                    logger.debug(f"从缓存获取股票 {symbol} 行情")
                    return cache_data
            
            # 尝试多个数据源
            for source_func in self.data_sources:
                try:
                    if not source_func.__name__.endswith('_individual'):
                        result = source_func(symbol)
                        if result and result.get('price'):
                            # 缓存结果
                            self.cache[cache_key] = (time.time(), result)
                            return result
                except Exception as e:
                    logger.debug(f"数据源 {source_func.__name__} 失败: {e}")
                    continue
            
            # 如果所有数据源都失败，返回空结果
            logger.warning(f"所有数据源都无法获取股票 {symbol} 行情")
            return {}
            
        except Exception as e:
            logger.error(f"获取股票 {symbol} 行情失败: {e}")
            raise
    
    def _try_akshare_spot(self, symbol: str) -> Optional[Dict[str, Any]]:
        """尝试使用AKShare获取实时行情"""
        try:
            import akshare as ak
            
            # 使用反爬虫策略（增加延迟）
            self.anti_crawler.add_request_delay(f"akshare_spot_{symbol}", min_delay=2.0, max_delay=4.0)
            
            result = ak.stock_zh_a_spot_em()
            if not result.empty:
                stock_data = result[result['代码'] == symbol]
                if not stock_data.empty:
                    row = stock_data.iloc[0]
                    return {
                        'symbol': symbol,
                        'name': row.get('名称', ''),
                        'price': row.get('最新价', 0),
                        'change': row.get('涨跌幅', 0),
                        'volume': row.get('成交量', 0),
                        'amount': row.get('成交额', 0),
                        'source': 'AKShare实时行情'
                    }
        except Exception as e:
            logger.debug(f"AKShare实时行情失败: {e}")
        
        return None
    
    def _try_akshare_individual(self, symbol: str) -> Optional[Dict[str, Any]]:
        """尝试使用AKShare获取个股信息"""
        try:
            import akshare as ak
            
            # 使用反爬虫策略（增加延迟）
            self.anti_crawler.add_request_delay(f"akshare_individual_{symbol}", min_delay=2.0, max_delay=4.0)
            
            result = ak.stock_individual_info_em(symbol=symbol)
            if not result.empty:
                info = {}
                for _, row in result.iterrows():
                    item = str(row['item']).strip()
                    value = str(row['value']).strip()
                    info[item] = value
                return info
        except Exception as e:
            logger.debug(f"AKShare个股信息失败: {e}")
        
        return None
    
    def _try_sina_finance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """尝试使用新浪财经"""
        try:
            if symbol.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            url = f"http://hq.sinajs.cn/list={market}{symbol}"
            
            # 使用反爬虫策略
            response = self.anti_crawler.make_request(url)
            
            data = response.text
            if 'var hq_str_' in data:
                parts = data.split('=')[1].strip('"').split(',')
                if len(parts) >= 32:
                    return {
                        'symbol': symbol,
                        'name': parts[0],
                        'price': float(parts[3]) if parts[3] else 0,
                        'change': 0,  # 新浪财经需要计算
                        'volume': int(parts[8]) if parts[8] else 0,
                        'amount': float(parts[9]) if parts[9] else 0,
                        'source': '新浪财经'
                    }
        except Exception as e:
            logger.debug(f"新浪财经失败: {e}")
        
        return None
    
    def _try_tencent_finance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """尝试使用腾讯财经（优化版）"""
        try:
            # 确定市场代码
            if symbol.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 构建URL
            full_symbol = f"{market}{symbol}"
            url = f"http://qt.gtimg.cn/q={full_symbol}"
            
            # 使用反爬虫策略，增加延迟
            self.anti_crawler.add_request_delay(f"tencent_finance_{symbol}", min_delay=1.0, max_delay=3.0)
            response = self.anti_crawler.make_request(url)
            
            # 解析数据
            data = response.text
            if 'v_' in data and '~' in data:
                # 提取数据部分
                data_part = data.split('=')[1].strip('";\n')
                parts = data_part.split('~')
                
                if len(parts) >= 40:
                    # 提取关键数据
                    try:
                        price = float(parts[3]) if parts[3] else 0
                        change_percent = float(parts[32]) if parts[32] else 0
                        volume = int(float(parts[6])) if parts[6] else 0
                        amount = float(parts[37]) if parts[37] else 0
                        
                        # 构建结果
                        result = {
                            'symbol': symbol,
                            'name': parts[1],
                            'price': price,
                            'change': change_percent,
                            'volume': volume,
                            'amount': amount,
                            'open': float(parts[5]) if parts[5] else 0,
                            'high': float(parts[33]) if parts[33] else 0,
                            'low': float(parts[34]) if parts[34] else 0,
                            'source': '腾讯财经'
                        }
                        
                        # 添加更多有用的信息
                        if len(parts) > 45:
                            try:
                                result['pe_ratio'] = float(parts[39]) if parts[39] and parts[39] != '-' else None
                                result['market_value'] = float(parts[45]) if parts[45] and parts[45] != '-' else None
                            except (ValueError, IndexError):
                                pass
                        
                        logger.info(f"腾讯财经获取 {symbol} 成功: 价格={price}, 涨跌幅={change_percent}%")
                        return result
                    except (ValueError, IndexError) as e:
                        logger.warning(f"腾讯财经数据解析错误: {e}")
                else:
                    logger.warning(f"腾讯财经返回数据格式不正确: {data[:100]}...")
            else:
                logger.warning(f"腾讯财经返回数据不包含预期格式: {data[:100]}...")
                
        except Exception as e:
            logger.debug(f"腾讯财经获取失败: {e}")
        
        return None
    
    def _try_163_finance(self, symbol: str) -> Optional[Dict[str, Any]]:
        """尝试使用网易财经"""
        try:
            url = f"http://api.money.126.net/data/feed/{symbol}/money.api"
            
            # 使用反爬虫策略
            response = self.anti_crawler.make_request(url)
            
            data = response.json()
            if symbol in data and data[symbol].get('price'):
                stock_data = data[symbol]
                return {
                    'symbol': symbol,
                    'name': stock_data.get('name', ''),
                    'price': stock_data.get('price', 0),
                    'change': stock_data.get('percent', 0),
                    'volume': stock_data.get('volume', 0),
                    'amount': stock_data.get('amount', 0),
                    'source': '网易财经'
                }
        except Exception as e:
            logger.debug(f"网易财经失败: {e}")
        
        return None
    
    def _get_basic_stock_list(self) -> pd.DataFrame:
        """获取基础股票列表"""
        basic_stocks = [
            {'code': '000001', 'name': '平安银行'},
            {'code': '000002', 'name': '万科A'},
            {'code': '600000', 'name': '浦发银行'},
            {'code': '600036', 'name': '招商银行'},
            {'code': '000858', 'name': '五粮液'},
            {'code': '000002', 'name': '万科A'},
            {'code': '600519', 'name': '贵州茅台'},
            {'code': '000001', 'name': '平安银行'},
        ]
        return pd.DataFrame(basic_stocks)
    
    def _get_basic_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取基础股票信息"""
        return {
            '股票代码': symbol,
            '股票简称': f'股票{symbol}',
            '总股本': '100000000',
            '流通股本': '80000000',
            '所属行业': '未知',
            '上市日期': '未知'
        }
    
    def clear_cache(self):
        """清空缓存"""
        self.cache.clear()
        logger.info("智能数据源缓存已清空")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """获取缓存统计"""
        return {
            'cache_size': len(self.cache),
            'cache_ttl': self.cache_ttl,
            'cached_symbols': list(self.cache.keys())
        }
