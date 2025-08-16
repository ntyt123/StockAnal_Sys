import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# 读取配置
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///data/stock_analyzer.db')
USE_DATABASE = os.getenv('USE_DATABASE', 'False').lower() == 'true'

# 创建引擎
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# 定义模型
class StockInfo(Base):
    __tablename__ = 'stock_info'

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10), nullable=False, index=True)
    stock_name = Column(String(50))
    market_type = Column(String(5))
    industry = Column(String(50))
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    # 新增字段 - 基础信息
    exchange = Column(String(10))  # 交易所
    company_name = Column(String(200))  # 完整公司名称
    english_name = Column(String(200))  # 英文名称
    former_name = Column(String(200))  # 曾用简称
    
    # 新增字段 - 股本信息
    total_shares = Column(BigInteger)  # 总股本
    circulating_shares = Column(BigInteger)  # 流通股
    
    # 新增字段 - 财务指标
    pe_ratio = Column(Float)  # 市盈率
    pb_ratio = Column(Float)  # 市净率
    market_value = Column(Float)  # 总市值
    circulating_value = Column(Float)  # 流通市值
    
    # 新增字段 - 公司信息
    legal_representative = Column(String(100))  # 法人代表
    registered_capital = Column(String(100))  # 注册资金
    establishment_date = Column(String(50))  # 成立日期
    list_date = Column(String(50))  # 上市日期
    website = Column(String(200))  # 官方网站
    email = Column(String(100))  # 电子邮箱
    phone = Column(String(50))  # 联系电话
    fax = Column(String(50))  # 传真
    registered_address = Column(Text)  # 注册地址
    office_address = Column(Text)  # 办公地址
    postal_code = Column(String(20))  # 邮政编码
    main_business = Column(Text)  # 主营业务
    business_scope = Column(Text)  # 经营范围
    company_intro = Column(Text)  # 机构简介
    selected_indices = Column(Text)  # 入选指数

    def to_dict(self):
        return {
            'stock_code': self.stock_code,
            'stock_name': self.stock_name,
            'market_type': self.market_type,
            'industry': self.industry,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'exchange': self.exchange,
            'company_name': self.company_name,
            'english_name': self.english_name,
            'former_name': self.former_name,
            'total_shares': self.total_shares,
            'circulating_shares': self.circulating_shares,
            'pe_ratio': self.pe_ratio,
            'pb_ratio': self.pb_ratio,
            'market_value': self.market_value,
            'circulating_value': self.circulating_value,
            'legal_representative': self.legal_representative,
            'registered_capital': self.registered_capital,
            'establishment_date': self.establishment_date,
            'list_date': self.list_date,
            'website': self.website,
            'email': self.email,
            'phone': self.phone,
            'fax': self.fax,
            'registered_address': self.registered_address,
            'office_address': self.office_address,
            'postal_code': self.postal_code,
            'main_business': self.main_business,
            'business_scope': self.business_scope,
            'company_intro': self.company_intro,
            'selected_indices': self.selected_indices
        }


class AnalysisResult(Base):
    __tablename__ = 'analysis_results'

    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10), nullable=False, index=True)
    market_type = Column(String(5))
    analysis_date = Column(DateTime, default=datetime.now)
    score = Column(Float)
    recommendation = Column(String(100))
    technical_data = Column(JSON)
    fundamental_data = Column(JSON)
    capital_flow_data = Column(JSON)
    ai_analysis = Column(Text)

    def to_dict(self):
        return {
            'stock_code': self.stock_code,
            'market_type': self.market_type,
            'analysis_date': self.analysis_date.strftime('%Y-%m-%d %H:%M:%S') if self.analysis_date else None,
            'score': self.score,
            'recommendation': self.recommendation,
            'technical_data': self.technical_data,
            'fundamental_data': self.fundamental_data,
            'capital_flow_data': self.capital_flow_data,
            'ai_analysis': self.ai_analysis
        }


class Portfolio(Base):
    __tablename__ = 'portfolios'

    id = Column(Integer, primary_key=True)
    user_id = Column(String(50), nullable=False, index=True)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    stocks = Column(JSON)  # 存储股票列表的JSON

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'stocks': self.stocks
        }


# 创建会话工厂
Session = sessionmaker(bind=engine)


# 初始化数据库
def init_db():
    Base.metadata.create_all(engine)


# 获取数据库会话
def get_session():
    return Session()


# 如果启用数据库，则初始化
if USE_DATABASE:
    init_db()