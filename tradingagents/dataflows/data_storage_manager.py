# -*- coding: utf-8 -*-
"""
A股数据存储和管理系统
提供数据库管理、数据清洗、数据验证、数据导出等功能
建立健全的A股数据库系统
"""

import os
import sqlite3
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Tuple
import logging
from pathlib import Path
from dataclasses import dataclass
from enum import Enum

import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.sqlite import insert
import jieba
import jieba.analyse

logger = logging.getLogger(__name__)

Base = declarative_base()

class DataQuality(Enum):
    """数据质量等级"""
    EXCELLENT = "excellent"  # 优秀
    GOOD = "good"           # 良好
    AVERAGE = "average"     # 一般
    POOR = "poor"           # 较差
    INVALID = "invalid"     # 无效

@dataclass
class DataValidationRule:
    """数据验证规则"""
    field_name: str
    rule_type: str  # required, format, length, range
    rule_value: Any
    error_message: str

class StockBasicInfo(Base):
    """股票基本信息表"""
    __tablename__ = 'stock_basic_info'
    
    id = Column(Integer, primary_key=True)
    stock_code = Column(String(10), unique=True, nullable=False, index=True)
    stock_name = Column(String(50), nullable=False)
    market = Column(String(10), nullable=False)  # SSE, SZSE
    board = Column(String(20))  # main, sme, gem, star
    industry = Column(String(50))
    is_active = Column(Boolean, default=True)
    listed_date = Column(DateTime)
    delisted_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

class NewsData(Base):
    """新闻数据表"""
    __tablename__ = 'news_data'
    
    id = Column(Integer, primary_key=True)
    news_id = Column(String(64), unique=True, nullable=False, index=True)  # MD5哈希
    stock_code = Column(String(10), index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(50), nullable=False)
    author = Column(String(100))  
    url = Column(String(500))
    publish_time = Column(DateTime, index=True)
    crawl_time = Column(DateTime, default=datetime.now)
    data_quality = Column(String(20), default=DataQuality.AVERAGE.value)
    sentiment_score = Column(Float)  # 情感分析得分
    keywords = Column(JSON)  # 关键词列表
    category = Column(String(50))  # 新闻分类
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    metadata = Column(JSON)  # 额外元数据

class AnnouncementData(Base):
    """公告数据表"""
    __tablename__ = 'announcement_data'
    
    id = Column(Integer, primary_key=True)
    announcement_id = Column(String(64), unique=True, nullable=False, index=True)
    stock_code = Column(String(10), index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    announcement_type = Column(String(50))  # 定期报告、临时公告等
    source = Column(String(50), nullable=False)
    url = Column(String(500))
    publish_time = Column(DateTime, index=True)
    crawl_time = Column(DateTime, default=datetime.now)
    data_quality = Column(String(20), default=DataQuality.AVERAGE.value)
    importance_score = Column(Float)  # 重要性评分
    keywords = Column(JSON)
    affected_stocks = Column(JSON)  # 影响的股票列表
    metadata = Column(JSON)

class InteractionData(Base):
    """互动数据表（如深交所互动易）"""
    __tablename__ = 'interaction_data'
    
    id = Column(Integer, primary_key=True)
    interaction_id = Column(String(64), unique=True, nullable=False, index=True)
    stock_code = Column(String(10), index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text)
    question_time = Column(DateTime, index=True)
    answer_time = Column(DateTime)
    questioner = Column(String(100))
    answerer = Column(String(100))
    source = Column(String(50), nullable=False)
    status = Column(String(20), default='answered')  # pending, answered, ignored
    data_quality = Column(String(20), default=DataQuality.AVERAGE.value)
    keywords = Column(JSON)
    sentiment_score = Column(Float)
    metadata = Column(JSON)

class ResearchData(Base):
    """研究报告数据表"""
    __tablename__ = 'research_data'
    
    id = Column(Integer, primary_key=True)
    report_id = Column(String(64), unique=True, nullable=False, index=True)
    stock_code = Column(String(10), index=True)
    title = Column(String(200), nullable=False)
    content = Column(Text)
    summary = Column(Text)
    source = Column(String(50), nullable=False)
    author = Column(String(100))
    institution = Column(String(100))  # 研究机构
    report_type = Column(String(50))  # 首次覆盖、深度报告、跟踪报告等
    rating = Column(String(20))  # 买入、持有、卖出
    target_price = Column(Float)  # 目标价
    url = Column(String(500))
    publish_time = Column(DateTime, index=True)
    crawl_time = Column(DateTime, default=datetime.now)
    data_quality = Column(String(20), default=DataQuality.AVERAGE.value)
    keywords = Column(JSON)
    metadata = Column(JSON)

class DataQualityLog(Base):
    """数据质量日志表"""
    __tablename__ = 'data_quality_log'
    
    id = Column(Integer, primary_key=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(String(64), nullable=False)
    quality_score = Column(Float, nullable=False)
    quality_level = Column(String(20), nullable=False)
    validation_results = Column(JSON)  # 验证结果详情
    created_at = Column(DateTime, default=datetime.now)

class DataStorageManager:
    """数据存储管理器"""
    
    def __init__(self, db_path: str = "ashare_comprehensive_data.db"):
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # 创建表
        Base.metadata.create_all(bind=self.engine)
        
        # 初始化文本分析工具
        self._init_text_analysis()
        
        # 数据验证规则
        self.validation_rules = self._init_validation_rules()
        
        logger.info(f"数据存储管理器初始化完成，数据库: {db_path}")
    
    def _init_text_analysis(self):
        """初始化文本分析工具"""
        try:
            # 添加自定义词典
            jieba.load_userdict(self._get_stock_dict_path())
        except:
            logger.warning("自定义词典加载失败，使用默认分词")
    
    def _get_stock_dict_path(self) -> str:
        """获取股票词典路径"""
        dict_path = Path(__file__).parent / "stock_dict.txt"
        if not dict_path.exists():
            # 创建基础股票词典
            stock_terms = [
                "涨停", "跌停", "停牌", "复牌", "分红", "配股", "增发", "重组",
                "并购", "IPO", "借壳", "退市", "ST", "PT", "主力", "游资",
                "机构", "散户", "北向资金", "南向资金", "沪深港通", "科创板",
                "创业板", "中小板", "主板", "新三板", "A股", "B股", "H股"
            ]
            with open(dict_path, 'w', encoding='utf-8') as f:
                for term in stock_terms:
                    f.write(f"{term}\n")
        return str(dict_path)
    
    def _init_validation_rules(self) -> Dict[str, List[DataValidationRule]]:
        """初始化数据验证规则"""
        return {
            'news': [
                DataValidationRule('title', 'required', True, '标题不能为空'),
                DataValidationRule('title', 'length', {'min': 5, 'max': 200}, '标题长度应在5-200字符之间'),
                DataValidationRule('source', 'required', True, '来源不能为空'),
                DataValidationRule('publish_time', 'format', r'\d{4}-\d{2}-\d{2}', '发布时间格式不正确'),
            ],
            'announcement': [
                DataValidationRule('title', 'required', True, '公告标题不能为空'),
                DataValidationRule('announcement_type', 'required', True, '公告类型不能为空'),
                DataValidationRule('stock_code', 'format', r'\d{6}', '股票代码格式不正确'),
            ],
            'interaction': [
                DataValidationRule('question', 'required', True, '问题内容不能为空'),
                DataValidationRule('question', 'length', {'min': 10}, '问题内容过短'),
            ]
        }
    
    def generate_content_hash(self, content: str) -> str:
        """生成内容哈希值用于去重"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def validate_data(self, data: Dict[str, Any], data_type: str) -> Tuple[bool, Dict[str, str]]:
        """验证数据质量"""
        rules = self.validation_rules.get(data_type, [])
        errors = {}
        
        for rule in rules:
            field_value = data.get(rule.field_name)
            
            if rule.rule_type == 'required' and rule.rule_value:
                if not field_value:
                    errors[rule.field_name] = rule.error_message
            
            elif rule.rule_type == 'length' and field_value:
                length = len(str(field_value))
                if isinstance(rule.rule_value, dict):
                    min_len = rule.rule_value.get('min', 0)
                    max_len = rule.rule_value.get('max', float('inf'))
                    if not (min_len <= length <= max_len):
                        errors[rule.field_name] = rule.error_message
            
            elif rule.rule_type == 'format' and field_value:
                if not re.match(rule.rule_value, str(field_value)):
                    errors[rule.field_name] = rule.error_message
        
        return len(errors) == 0, errors
    
    def calculate_quality_score(self, data: Dict[str, Any], data_type: str) -> float:
        """计算数据质量分数"""
        score = 100.0
        
        # 基础字段完整性检查
        required_fields = {
            'news': ['title', 'source', 'publish_time'],
            'announcement': ['title', 'announcement_type', 'stock_code'],
            'interaction': ['question', 'stock_code']
        }.get(data_type, [])
        
        for field in required_fields:
            if not data.get(field):
                score -= 20
        
        # 内容质量检查
        title = data.get('title', '')
        content = data.get('content', '')
        
        # 标题质量
        if len(title) < 10:
            score -= 10
        elif len(title) > 100:
            score -= 5
        
        # 内容质量
        if content:
            if len(content) < 50:
                score -= 15
            elif len(content) > 10000:
                score -= 5
            
            # 检查是否包含垃圾内容
            spam_keywords = ['广告', '推广', '加微信', '加QQ', '联系我们']
            for keyword in spam_keywords:
                if keyword in content:
                    score -= 25
                    break
        else:
            score -= 20
        
        # 时间合理性检查
        publish_time = data.get('publish_time')
        if publish_time:
            try:
                if isinstance(publish_time, str):
                    pub_date = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                else:
                    pub_date = publish_time
                
                # 检查是否为未来时间
                if pub_date > datetime.now():
                    score -= 30
                
                # 检查是否过于久远
                if pub_date < datetime.now() - timedelta(days=3650):  # 10年前
                    score -= 10
                    
            except:
                score -= 15
        
        return max(0, min(100, score))
    
    def determine_quality_level(self, score: float) -> DataQuality:
        """根据分数确定质量等级"""
        if score >= 90:
            return DataQuality.EXCELLENT
        elif score >= 75:
            return DataQuality.GOOD
        elif score >= 60:
            return DataQuality.AVERAGE
        elif score >= 40:
            return DataQuality.POOR
        else:
            return DataQuality.INVALID
    
    def extract_keywords(self, text: str, top_k: int = 10) -> List[str]:
        """提取关键词"""
        try:
            # 使用TF-IDF提取关键词
            keywords = jieba.analyse.extract_tags(text, topK=top_k, withWeight=False)
            return keywords
        except Exception as e:
            logger.error(f"关键词提取失败: {str(e)}")
            return []
    
    def clean_text(self, text: str) -> str:
        """清洗文本内容"""
        if not text:
            return ""
        
        # 去除多余空白字符
        text = re.sub(r'\s+', ' ', text.strip())
        
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 去除特殊字符但保留中文标点
        text = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\s\.\,\!\?\;\:\-\(\)（）\[\]【】\{\}""''《》「」]', '', text)
        
        return text
    
    def save_news_data(self, news_list: List[Dict[str, Any]]) -> int:
        """保存新闻数据"""
        saved_count = 0
        
        with self.SessionLocal() as session:
            for news_item in news_list:
                try:
                    # 数据清洗
                    title = self.clean_text(news_item.get('title', ''))
                    content = self.clean_text(news_item.get('content', ''))
                    
                    # 生成唯一ID
                    news_id = self.generate_content_hash(f"{title}{content}")
                    
                    # 检查是否已存在
                    existing = session.query(NewsData).filter_by(news_id=news_id).first()
                    if existing:
                        continue
                    
                    # 数据验证
                    is_valid, errors = self.validate_data(news_item, 'news')
                    
                    # 计算质量分数
                    quality_score = self.calculate_quality_score(news_item, 'news')
                    quality_level = self.determine_quality_level(quality_score)
                    
                    # 跳过低质量数据
                    if quality_level == DataQuality.INVALID:
                        logger.warning(f"跳过无效数据: {title[:50]}")
                        continue
                    
                    # 提取关键词
                    keywords = self.extract_keywords(f"{title} {content}")
                    
                    # 处理发布时间
                    publish_time = news_item.get('publish_time')
                    if isinstance(publish_time, str):
                        try:
                            publish_time = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                        except:
                            try:
                                publish_time = datetime.strptime(publish_time, '%Y-%m-%d')
                            except:
                                publish_time = None
                    
                    # 创建新闻记录
                    news_record = NewsData(
                        news_id=news_id,
                        stock_code=news_item.get('stock_code', ''),
                        title=title,
                        content=content,
                        source=news_item.get('source', ''),
                        author=news_item.get('author', ''),
                        url=news_item.get('url', ''),
                        publish_time=publish_time,
                        data_quality=quality_level.value,
                        keywords=keywords,
                        metadata=news_item
                    )
                    
                    session.add(news_record)
                    
                    # 记录质量日志
                    quality_log = DataQualityLog(
                        table_name='news_data',
                        record_id=news_id,
                        quality_score=quality_score,
                        quality_level=quality_level.value,
                        validation_results={'errors': errors, 'is_valid': is_valid}
                    )
                    session.add(quality_log)
                    
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存新闻数据失败: {str(e)}")
                    continue
            
            session.commit()
        
        logger.info(f"成功保存 {saved_count} 条新闻数据")
        return saved_count
    
    def save_announcement_data(self, announcement_list: List[Dict[str, Any]]) -> int:
        """保存公告数据"""
        saved_count = 0
        
        with self.SessionLocal() as session:
            for item in announcement_list:
                try:
                    title = self.clean_text(item.get('title', ''))
                    content = self.clean_text(item.get('content', ''))
                    
                    announcement_id = self.generate_content_hash(f"{title}{content}")
                    
                    # 检查重复
                    existing = session.query(AnnouncementData).filter_by(announcement_id=announcement_id).first()
                    if existing:
                        continue
                    
                    # 质量评估
                    quality_score = self.calculate_quality_score(item, 'announcement')
                    quality_level = self.determine_quality_level(quality_score)
                    
                    if quality_level == DataQuality.INVALID:
                        continue
                    
                    keywords = self.extract_keywords(f"{title} {content}")
                    
                    publish_time = item.get('publish_time')
                    if isinstance(publish_time, str):
                        try:
                            publish_time = datetime.strptime(publish_time, '%Y-%m-%d %H:%M:%S')
                        except:
                            publish_time = None
                    
                    announcement_record = AnnouncementData(
                        announcement_id=announcement_id,
                        stock_code=item.get('stock_code', ''),
                        title=title,
                        content=content,
                        announcement_type=item.get('type', ''),
                        source=item.get('source', ''),
                        url=item.get('url', ''),
                        publish_time=publish_time,
                        data_quality=quality_level.value,
                        keywords=keywords,
                        metadata=item
                    )
                    
                    session.add(announcement_record)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存公告数据失败: {str(e)}")
                    continue
            
            session.commit()
        
        logger.info(f"成功保存 {saved_count} 条公告数据")
        return saved_count
    
    def save_interaction_data(self, interaction_list: List[Dict[str, Any]]) -> int:
        """保存互动数据"""
        saved_count = 0
        
        with self.SessionLocal() as session:
            for item in interaction_list:
                try:
                    question = self.clean_text(item.get('question', ''))
                    answer = self.clean_text(item.get('answer', ''))
                    
                    interaction_id = self.generate_content_hash(f"{question}{answer}")
                    
                    # 检查重复
                    existing = session.query(InteractionData).filter_by(interaction_id=interaction_id).first()
                    if existing:
                        continue
                    
                    quality_score = self.calculate_quality_score(item, 'interaction')
                    quality_level = self.determine_quality_level(quality_score)
                    
                    if quality_level == DataQuality.INVALID:
                        continue
                    
                    keywords = self.extract_keywords(f"{question} {answer}")
                    
                    # 处理时间
                    question_time = item.get('question_time')
                    answer_time = item.get('answer_time')
                    
                    if isinstance(question_time, str):
                        try:
                            question_time = datetime.strptime(question_time, '%Y-%m-%d %H:%M:%S')
                        except:
                            question_time = None
                    
                    if isinstance(answer_time, str):
                        try:
                            answer_time = datetime.strptime(answer_time, '%Y-%m-%d %H:%M:%S')
                        except:
                            answer_time = None
                    
                    interaction_record = InteractionData(
                        interaction_id=interaction_id,
                        stock_code=item.get('stock_code', ''),
                        question=question,
                        answer=answer,
                        question_time=question_time,
                        answer_time=answer_time,
                        questioner=item.get('questioner', ''),
                        answerer=item.get('answerer', ''),
                        source=item.get('source', ''),
                        data_quality=quality_level.value,
                        keywords=keywords,
                        metadata=item
                    )
                    
                    session.add(interaction_record)
                    saved_count += 1
                    
                except Exception as e:
                    logger.error(f"保存互动数据失败: {str(e)}")
                    continue
            
            session.commit()
        
        logger.info(f"成功保存 {saved_count} 条互动数据")
        return saved_count
    
    def get_data_statistics(self) -> Dict[str, Any]:
        """获取数据统计信息"""
        with self.SessionLocal() as session:
            stats = {
                'news_count': session.query(NewsData).count(),
                'announcement_count': session.query(AnnouncementData).count(),
                'interaction_count': session.query(InteractionData).count(),
                'research_count': session.query(ResearchData).count(),
                'quality_distribution': {}
            }
            
            # 质量分布统计
            for quality in DataQuality:
                news_count = session.query(NewsData).filter_by(data_quality=quality.value).count()
                announcement_count = session.query(AnnouncementData).filter_by(data_quality=quality.value).count()
                interaction_count = session.query(InteractionData).filter_by(data_quality=quality.value).count()
                
                stats['quality_distribution'][quality.value] = {
                    'news': news_count,
                    'announcement': announcement_count,
                    'interaction': interaction_count,
                    'total': news_count + announcement_count + interaction_count
                }
            
            # 最近数据统计
            recent_date = datetime.now() - timedelta(days=7)
            stats['recent_data'] = {
                'news_count': session.query(NewsData).filter(NewsData.crawl_time >= recent_date).count(),
                'announcement_count': session.query(AnnouncementData).filter(AnnouncementData.crawl_time >= recent_date).count(),
                'interaction_count': session.query(InteractionData).filter(InteractionData.crawl_time >= recent_date).count()
            }
            
            return stats
    
    def export_data_to_excel(self, output_path: str = "ashare_data_export.xlsx"):
        """导出数据到Excel"""
        try:
            with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
                # 导出新闻数据
                news_df = pd.read_sql_query(
                    "SELECT stock_code, title, source, publish_time, data_quality FROM news_data ORDER BY publish_time DESC LIMIT 1000",
                    self.engine
                )
                news_df.to_excel(writer, sheet_name='新闻数据', index=False)
                
                # 导出公告数据
                announcement_df = pd.read_sql_query(
                    "SELECT stock_code, title, announcement_type, source, publish_time, data_quality FROM announcement_data ORDER BY publish_time DESC LIMIT 1000",
                    self.engine
                )
                announcement_df.to_excel(writer, sheet_name='公告数据', index=False)
                
                # 导出互动数据
                interaction_df = pd.read_sql_query(
                    "SELECT stock_code, question, answer, question_time, answer_time, source, data_quality FROM interaction_data ORDER BY question_time DESC LIMIT 1000",
                    self.engine
                )
                interaction_df.to_excel(writer, sheet_name='互动数据', index=False)
                
                # 导出统计数据
                stats = self.get_data_statistics()
                stats_df = pd.DataFrame([stats])
                stats_df.to_excel(writer, sheet_name='统计信息', index=False)
            
            logger.info(f"数据导出完成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            return False
    
    def search_data(self, keyword: str, data_types: List[str] = None, limit: int = 50) -> Dict[str, List[Dict]]:
        """搜索数据"""
        if data_types is None:
            data_types = ['news', 'announcement', 'interaction']
        
        results = {}
        
        with self.SessionLocal() as session:
            if 'news' in data_types:
                news_results = session.query(NewsData).filter(
                    NewsData.title.contains(keyword) | NewsData.content.contains(keyword)
                ).order_by(NewsData.publish_time.desc()).limit(limit).all()
                
                results['news'] = [
                    {
                        'id': item.news_id,
                        'title': item.title,
                        'source': item.source,
                        'publish_time': item.publish_time.strftime('%Y-%m-%d %H:%M:%S') if item.publish_time else '',
                        'url': item.url,
                        'quality': item.data_quality
                    }
                    for item in news_results
                ]
            
            if 'announcement' in data_types:
                announcement_results = session.query(AnnouncementData).filter(
                    AnnouncementData.title.contains(keyword) | AnnouncementData.content.contains(keyword)
                ).order_by(AnnouncementData.publish_time.desc()).limit(limit).all()
                
                results['announcement'] = [
                    {
                        'id': item.announcement_id,
                        'title': item.title,
                        'type': item.announcement_type,
                        'source': item.source,
                        'publish_time': item.publish_time.strftime('%Y-%m-%d %H:%M:%S') if item.publish_time else '',
                        'url': item.url,
                        'quality': item.data_quality
                    }
                    for item in announcement_results
                ]
            
            if 'interaction' in data_types:
                interaction_results = session.query(InteractionData).filter(
                    InteractionData.question.contains(keyword) | InteractionData.answer.contains(keyword)
                ).order_by(InteractionData.question_time.desc()).limit(limit).all()
                
                results['interaction'] = [
                    {
                        'id': item.interaction_id,
                        'question': item.question[:100] + '...' if len(item.question) > 100 else item.question,
                        'answer': item.answer[:100] + '...' if len(item.answer) > 100 else item.answer,
                        'question_time': item.question_time.strftime('%Y-%m-%d %H:%M:%S') if item.question_time else '',
                        'source': item.source,
                        'quality': item.data_quality
                    }
                    for item in interaction_results
                ]
        
        return results

def create_data_storage_manager(db_path: str = "ashare_comprehensive_data.db") -> DataStorageManager:
    """创建数据存储管理器"""
    return DataStorageManager(db_path)