#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多数据源管理器
包含多个股票数据获取接口，避免单一数据源依赖
"""

import time
import random
import logging
import requests
import pandas as pd
from typing import Optional, Dict, List, Any
from abc import ABC, abstractmethod
from .request_headers import get_headers, header_rotator

logger = logging.getLogger(__name__)

class DataSource(ABC):
    """数据源基类"""
    
    @abstractmethod
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        pass
    
    @abstractmethod
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息"""
        pass
    
    @abstractmethod
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        pass

class AKShareSource(DataSource):
    """AKShare数据源"""
    
    def __init__(self):
        self.name = "AKShare"
        self.success_rate = 0.8
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        try:
            import akshare as ak
            headers = header_rotator.get_headers('stock_data')
            logger.info(f"使用 {self.name} 获取股票列表")
            
            result = ak.stock_info_a_code_name()
            time.sleep(random.uniform(0.1, 0.3))
            return result
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票列表失败: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息"""
        try:
            import akshare as ak
            headers = header_rotator.get_headers('stock_data')
            logger.info(f"使用 {self.name} 获取股票 {symbol} 信息")
            
            result = ak.stock_individual_info_em(symbol=symbol)
            time.sleep(random.uniform(0.2, 0.5))
            
            info = {}
            if not result.empty:
                for _, row in result.iterrows():
                    item = str(row['item']).strip()
                    value = str(row['value']).strip()
                    info[item] = value
            
            return info
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 信息失败: {e}")
            raise
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        try:
            import akshare as ak
            headers = header_rotator.get_headers('stock_data')
            logger.info(f"使用 {self.name} 获取股票 {symbol} 行情")
            
            result = ak.stock_zh_a_spot_em()
            time.sleep(random.uniform(0.1, 0.3))
            
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
                        'amount': row.get('成交额', 0)
                    }
            
            return {}
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 行情失败: {e}")
            raise

class TencentFinanceSource(DataSource):
    """腾讯财经数据源"""
    
    def __init__(self):
        self.name = "腾讯财经"
        self.base_url = "http://qt.gtimg.cn"
        self.success_rate = 0.9  # 腾讯财经成功率高
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表（模拟数据）"""
        try:
            logger.info(f"使用 {self.name} 获取股票列表")
            
            # 腾讯财经没有提供完整股票列表API，返回基础列表
            sample_stocks = [
                {'code': '000001', 'name': '平安银行'},
                {'code': '000002', 'name': '万科A'},
                {'code': '600000', 'name': '浦发银行'},
                {'code': '600036', 'name': '招商银行'},
                {'code': '600519', 'name': '贵州茅台'},
            ]
            
            return pd.DataFrame(sample_stocks)
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票列表失败: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息"""
        try:
            logger.info(f"使用 {self.name} 获取股票 {symbol} 信息")
            
            # 确定市场代码
            if symbol.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 构建URL
            url = f"{self.base_url}/q={market}{symbol}"
            headers = header_rotator.get_headers('stock_data')
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.text
            if 'v_' in data and '~' in data:
                # 提取数据部分
                data_part = data.split('=')[1].strip('";\n')
                parts = data_part.split('~')
                
                if len(parts) >= 45:
                    # 提取基本信息
                    info = {
                        '股票代码': symbol,
                        '股票简称': parts[1],
                        '所属行业': parts[44] if len(parts) > 44 else '未知',
                        '总股本': parts[45] if len(parts) > 45 else '未知',
                        '流通股本': parts[46] if len(parts) > 46 else '未知',
                    }
                    
                    # 添加更多信息
                    if len(parts) > 45:
                        info['市盈率'] = parts[39] if parts[39] and parts[39] != '-' else '未知'
                        info['市净率'] = parts[46] if len(parts) > 46 and parts[46] and parts[46] != '-' else '未知'
                    
                    time.sleep(random.uniform(0.1, 0.3))
                    return info
            
            # 如果无法获取详细信息，返回基础信息
            return {
                '股票代码': symbol,
                '股票简称': f'股票{symbol}',
                '总股本': '未知',
                '流通股本': '未知',
                '所属行业': '未知',
            }
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 信息失败: {e}")
            raise
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        try:
            logger.info(f"使用 {self.name} 获取股票 {symbol} 行情")
            
            # 确定市场代码
            if symbol.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            # 构建URL
            url = f"{self.base_url}/q={market}{symbol}"
            headers = header_rotator.get_headers('stock_data')
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
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
                        
                        return result
                    except (ValueError, IndexError) as e:
                        logger.warning(f"腾讯财经数据解析错误: {e}")
            
            time.sleep(random.uniform(0.1, 0.3))
            return {}
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 行情失败: {e}")
            raise

class SinaFinanceSource(DataSource):
    """新浪财经数据源"""
    
    def __init__(self):
        self.name = "新浪财经"
        self.base_url = "http://hq.sinajs.cn"
        self.success_rate = 0.7
    
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表（模拟数据）"""
        try:
            logger.info(f"使用 {self.name} 获取股票列表")
            
            sample_stocks = [
                {'code': '000001', 'name': '平安银行', 'market': 'SZ'},
                {'code': '000002', 'name': '万科A', 'market': 'SZ'},
                {'code': '600000', 'name': '浦发银行', 'market': 'SH'},
                {'code': '600036', 'name': '招商银行', 'market': 'SH'},
            ]
            
            return pd.DataFrame(sample_stocks)
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票列表失败: {e}")
            raise
    
    def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """获取股票信息（模拟数据）"""
        try:
            logger.info(f"使用 {self.name} 获取股票 {symbol} 信息")
            
            info = {
                '股票代码': symbol,
                '股票名称': f'股票{symbol}',
                '总股本': '100000000',
                '流通股本': '80000000',
                '所属行业': '金融',
                '上市日期': '2020-01-01'
            }
            
            time.sleep(random.uniform(0.1, 0.3))
            return info
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 信息失败: {e}")
            raise
    
    def get_stock_quote(self, symbol: str) -> Dict[str, Any]:
        """获取股票行情"""
        try:
            logger.info(f"使用 {self.name} 获取股票 {symbol} 行情")
            
            if symbol.startswith('6'):
                market = 'sh'
            else:
                market = 'sz'
            
            url = f"{self.base_url}/list={market}{symbol}"
            headers = header_rotator.get_headers('stock_data')
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            data = response.text
            if 'var hq_str_' in data:
                parts = data.split('=')[1].strip('"').split(',')
                if len(parts) >= 32:
                    return {
                        'symbol': symbol,
                        'name': parts[0],
                        'open': float(parts[1]) if parts[1] else 0,
                        'close': float(parts[3]) if parts[3] else 0,
                        'price': float(parts[3]) if parts[3] else 0,
                        'high': float(parts[4]) if parts[4] else 0,
                        'low': float(parts[5]) if parts[5] else 0,
                        'volume': int(parts[8]) if parts[8] else 0,
                        'amount': float(parts[9]) if parts[9] else 0,
                        'date': parts[30],
                        'time': parts[31]
                    }
            
            time.sleep(random.uniform(0.1, 0.3))
            return {}
            
        except Exception as e:
            logger.error(f"{self.name} 获取股票 {symbol} 行情失败: {e}")
            raise

class DataSourceManager:
    """数据源管理器"""
    
    def __init__(self):
        """初始化数据源管理器（优先使用腾讯财经）"""
        try:
            from .smart_data_source import SmartStockSource
            smart_source = SmartStockSource()
            self.sources = {
                'smart': smart_source,
                'tencent': TencentFinanceSource(),  # 添加腾讯财经数据源
                'sina': SinaFinanceSource(),
                'akshare': AKShareSource(),
            }
            self.current_source = 'smart'
            # 调整优先级顺序，腾讯财经优先
            self.fallback_order = ['smart', 'tencent', 'sina', 'akshare']
        except ImportError:
            # 如果智能数据源导入失败，使用基础数据源
            self.sources = {
                'tencent': TencentFinanceSource(),  # 腾讯财经优先
                'sina': SinaFinanceSource(),
                'akshare': AKShareSource(),
            }
            self.current_source = 'tencent'  # 默认使用腾讯财经
            self.fallback_order = ['tencent', 'sina', 'akshare']
        
        # 时间间隔配置
        self.min_interval = 0.5      # 最小间隔（秒）
        self.max_interval = 2.0      # 最大间隔（秒）
        self.last_request_time = 0   # 上次请求时间
        self.request_count = 0       # 请求计数器
    
    def get_source(self, name: str) -> Optional[DataSource]:
        """获取指定数据源"""
        return self.sources.get(name)
    
    def get_stock_list(self, source_name: str = None) -> pd.DataFrame:
        """获取股票列表，支持指定数据源"""
        if source_name and source_name in self.sources:
            # 等待随机时间间隔
            self._wait_random_interval()
            return self.sources[source_name].get_stock_list()
        
        # 尝试多个数据源
        for source_name in self.fallback_order:
            try:
                # 等待随机时间间隔
                self._wait_random_interval()
                
                source = self.sources[source_name]
                logger.info(f"尝试使用 {source.name} 获取股票列表")
                result = source.get_stock_list()
                if not result.empty:
                    self.current_source = source_name
                    logger.info(f"成功使用 {source.name} 获取股票列表")
                    return result
            except Exception as e:
                logger.warning(f"{source.name} 获取股票列表失败: {e}")
                continue
        
        raise Exception("所有数据源都无法获取股票列表")
    
    def get_stock_info(self, symbol: str, source_name: str = None) -> Dict[str, Any]:
        """获取股票信息，支持指定数据源"""
        if source_name and source_name in self.sources:
            # 等待随机时间间隔
            self._wait_random_interval()
            return self._retry_with_backoff(
                self.sources[source_name].get_stock_info, 
                symbol
            )
        
        # 尝试多个数据源
        for source_name in self.fallback_order:
            try:
                # 等待随机时间间隔
                self._wait_random_interval()
                
                source = self.sources[source_name]
                logger.info(f"尝试使用 {source.name} 获取股票 {symbol} 信息")
                result = self._retry_with_backoff(
                    source.get_stock_info, 
                    symbol
                )
                if result:
                    self.current_source = source_name
                    logger.info(f"成功使用 {source.name} 获取股票 {symbol} 信息")
                    return result
            except Exception as e:
                logger.warning(f"{source.name} 获取股票 {symbol} 信息失败: {e}")
                continue
        
        raise Exception(f"所有数据源都无法获取股票 {symbol} 信息")
    
    def get_stock_quote(self, symbol: str, source_name: str = None) -> Dict[str, Any]:
        """获取股票行情，支持指定数据源"""
        if source_name and source_name in self.sources:
            # 等待随机时间间隔
            self._wait_random_interval()
            return self._retry_with_backoff(
                self.sources[source_name].get_stock_quote, 
                symbol
            )
        
        # 尝试多个数据源
        for source_name in self.fallback_order:
            try:
                # 等待随机时间间隔
                self._wait_random_interval()
                
                source = self.sources[source_name]
                logger.info(f"尝试使用 {source.name} 获取股票 {symbol} 行情")
                result = self._retry_with_backoff(
                    source.get_stock_quote, 
                    symbol
                )
                if result:
                    self.current_source = source_name
                    logger.info(f"成功使用 {source.name} 获取股票 {symbol} 行情")
                    return result
            except Exception as e:
                logger.warning(f"{source_name} 获取股票 {symbol} 行情失败: {e}")
                continue
        
        raise Exception(f"所有数据源都无法获取股票 {symbol} 行情")
    
    def get_available_sources(self) -> List[str]:
        """获取可用的数据源列表"""
        return list(self.sources.keys())
    
    def get_current_source(self) -> str:
        """获取当前使用的数据源"""
        return self.current_source
    
    def _wait_random_interval(self):
        """等待随机时间间隔"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # 计算需要等待的时间
        if time_since_last < self.min_interval:
            wait_time = random.uniform(self.min_interval, self.max_interval)
            logger.debug(f"等待随机时间间隔: {wait_time:.2f} 秒")
            time.sleep(wait_time)
        
        self.last_request_time = time.time()
        self.request_count += 1
    
    def _retry_with_backoff(self, func, *args, max_retries=3, **kwargs):
        """带指数退避的重试机制"""
        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if attempt == max_retries - 1:
                    raise e
                
                # 指数退避：等待时间随重试次数增加
                wait_time = (2 ** attempt) * random.uniform(0.5, 1.5)
                logger.warning(f"第{attempt + 1}次重试失败，等待 {wait_time:.2f} 秒后重试: {e}")
                time.sleep(wait_time)
    
    def set_time_interval(self, min_interval: float = 0.5, max_interval: float = 2.0):
        """设置时间间隔范围"""
        self.min_interval = max(0.1, min_interval)
        self.max_interval = max(self.min_interval, max_interval)
        logger.info(f"设置时间间隔: {self.min_interval}-{self.max_interval} 秒")
    
    def get_request_stats(self):
        """获取请求统计信息"""
        return {
            'total_requests': self.request_count,
            'last_request_time': self.last_request_time,
            'current_interval': f"{self.min_interval}-{self.max_interval}秒"
        }
    
    def test_source(self, source_name: str) -> bool:
        """测试数据源是否可用"""
        try:
            # 等待随机时间间隔
            self._wait_random_interval()
            
            source = self.sources[source_name]
            result = source.get_stock_quote('000001')
            return bool(result)
        except Exception as e:
            logger.warning(f"数据源 {source_name} 测试失败: {e}")
            return False

# 全局数据源管理器实例
data_source_manager = DataSourceManager()

# 便捷函数
def get_data_source_manager():
    """获取数据源管理器实例"""
    return data_source_manager

def get_stock_list(source_name: str = None):
    """获取股票列表的便捷函数"""
    return data_source_manager.get_stock_list(source_name)

def get_stock_info(symbol: str, source_name: str = None):
    """获取股票信息的便捷函数"""
    return data_source_manager.get_stock_info(symbol, source_name)

def get_stock_quote(symbol: str, source_name: str = None):
    """获取股票行情的便捷函数"""
    return data_source_manager.get_stock_quote(symbol, source_name)

def set_time_interval(min_interval: float = 0.5, max_interval: float = 2.0):
    """设置时间间隔的便捷函数"""
    data_source_manager.set_time_interval(min_interval, max_interval)

def get_request_stats():
    """获取请求统计信息的便捷函数"""
    return data_source_manager.get_request_stats()
