# -*- coding: utf-8 -*-
"""
增强版A股数据智能体
集成多数据源采集系统到现有A股交易框架
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Annotated
import json

from langchain_core.language_models import BaseLanguageModel
from langchain.tools import Tool

from .data_collector_agent import DataCollectorAgent, DataCollectionTask, DataSourceType
from ..dataflows.data_source_crawlers import CrawlerFactory
from ..dataflows.data_storage_manager import DataStorageManager
from ..ashare_config import get_ashare_config

logger = logging.getLogger(__name__)

class EnhancedAShareDataAgent:
    """增强版A股数据智能体
    
    集成了强大的数据采集功能，支持：
    - 巨潮信息网
    - 新浪财经
    - 东方财富网
    - 中国证券网
    - 深交所互动易
    - 第一财经
    - 韭研公社
    """
    
    def __init__(self, llm: BaseLanguageModel):
        self.llm = llm
        self.config = get_ashare_config()
        
        # 初始化数据采集器和存储管理器
        self.data_collector = DataCollectorAgent(llm)
        self.storage_manager = DataStorageManager()
        
        # 数据源映射
        self.data_source_map = {
            "巨潮信息网": DataSourceType.JUCHAO,
            "新浪财经": DataSourceType.SINA,
            "东方财富网": DataSourceType.EASTMONEY,
            "中国证券网": DataSourceType.CNS,
            "深交所互动易": DataSourceType.SZSE_INTERACT,
            "第一财经": DataSourceType.YICAI,
            "韭研公社": DataSourceType.JIUYAN
        }
        
        logger.info("增强版A股数据智能体初始化完成")
    
    def create_langchain_tools(self) -> List[Tool]:
        """创建LangChain工具集"""
        tools = [
            Tool(
                name="get_comprehensive_stock_news",
                description="获取A股股票的全面新闻数据，整合多个数据源",
                func=self.get_comprehensive_stock_news
            ),
            Tool(
                name="get_stock_announcements",
                description="获取A股股票的公告信息，来源于巨潮信息网等官方渠道",
                func=self.get_stock_announcements
            ),
            Tool(
                name="get_interactive_qa",
                description="获取深交所互动易的投资者问答数据",
                func=self.get_interactive_qa
            ),
            Tool(
                name="get_market_sentiment_analysis",
                description="获取市场情绪分析，整合各大财经媒体观点",
                func=self.get_market_sentiment_analysis
            ),
            Tool(
                name="get_industry_analysis",
                description="获取行业分析报告和相关新闻",
                func=self.get_industry_analysis
            ),
            Tool(
                name="search_stock_data",
                description="搜索股票相关的所有类型数据（新闻、公告、互动等）",
                func=self.search_stock_data
            ),
            Tool(
                name="get_data_quality_report",
                description="获取数据质量报告和统计信息",
                func=self.get_data_quality_report
            )
        ]
        
        return tools
    
    def get_comprehensive_stock_news(
        self,
        stock_code: Annotated[str, "A股股票代码，如'000001'或'600036'"],
        days_back: Annotated[int, "回看天数，默认7天"] = 7
    ) -> str:
        """获取综合股票新闻"""
        try:
            logger.info(f"开始获取 {stock_code} 的综合新闻数据")
            
            # 创建多个采集任务
            tasks = []
            for source_name, source_type in self.data_source_map.items():
                if source_type in [DataSourceType.SINA, DataSourceType.EASTMONEY, 
                                 DataSourceType.CNS, DataSourceType.YICAI]:
                    task = DataCollectionTask(
                        source_type=source_type,
                        target=stock_code,
                        data_type="news",
                        priority=1 if source_type == DataSourceType.SINA else 2
                    )
                    tasks.append(task)
            
            # 添加任务到采集队列
            for task in tasks:
                self.data_collector.add_collection_task(task)
            
            # 运行采集
            asyncio.run(self.data_collector.run_collection_pipeline())
            
            # 从数据库获取结果
            search_results = self.storage_manager.search_data(
                keyword=stock_code,
                data_types=['news'],
                limit=50
            )
            
            # 格式化结果
            news_data = search_results.get('news', [])
            if not news_data:
                return f"未找到股票 {stock_code} 的新闻数据"
            
            # 按来源和时间整理
            report = f"## {stock_code} 综合新闻汇总（近{days_back}天）\n\n"
            
            # 按来源分组
            source_groups = {}
            for news in news_data:
                source = news['source']
                if source not in source_groups:
                    source_groups[source] = []
                source_groups[source].append(news)
            
            for source, news_list in source_groups.items():
                report += f"### {source} ({len(news_list)}条)\n\n"
                for i, news in enumerate(news_list[:5], 1):  # 每个来源最多5条
                    report += f"**{i}. {news['title']}**\n"
                    report += f"时间: {news['publish_time']} | 质量: {news['quality']}\n"
                    if news.get('url'):
                        report += f"链接: {news['url']}\n"
                    report += "\n"
                report += "---\n\n"
            
            # 添加数据质量统计
            total_news = len(news_data)
            high_quality = len([n for n in news_data if n['quality'] in ['excellent', 'good']])
            report += f"### 数据质量统计\n"
            report += f"- 总新闻数: {total_news}\n"
            report += f"- 高质量新闻: {high_quality} ({high_quality/total_news*100:.1f}%)\n"
            report += f"- 数据源覆盖: {len(source_groups)}个\n"
            
            return report
            
        except Exception as e:
            logger.error(f"获取综合新闻失败: {str(e)}")
            return f"获取股票 {stock_code} 新闻数据失败: {str(e)}"
    
    def get_stock_announcements(
        self,
        stock_code: Annotated[str, "A股股票代码"],
        days_back: Annotated[int, "回看天数"] = 30
    ) -> str:
        """获取股票公告"""
        try:
            logger.info(f"开始获取 {stock_code} 的公告数据")
            
            # 创建公告采集任务
            task = DataCollectionTask(
                source_type=DataSourceType.JUCHAO,
                target=stock_code,
                data_type="announcement",
                priority=1
            )
            
            self.data_collector.add_collection_task(task)
            asyncio.run(self.data_collector.run_collection_pipeline())
            
            # 获取结果
            search_results = self.storage_manager.search_data(
                keyword=stock_code,
                data_types=['announcement'],
                limit=30
            )
            
            announcements = search_results.get('announcement', [])
            if not announcements:
                return f"未找到股票 {stock_code} 的公告数据"
            
            report = f"## {stock_code} 公告汇总（近{days_back}天）\n\n"
            
            for i, ann in enumerate(announcements, 1):
                report += f"### {i}. {ann['title']}\n"
                report += f"**类型**: {ann.get('type', '未知')} | **发布时间**: {ann['publish_time']}\n"
                report += f"**来源**: {ann['source']} | **质量**: {ann['quality']}\n"
                if ann.get('url'):
                    report += f"**链接**: {ann['url']}\n"
                report += "\n---\n\n"
            
            return report
            
        except Exception as e:
            logger.error(f"获取公告失败: {str(e)}")
            return f"获取股票 {stock_code} 公告数据失败: {str(e)}"
    
    def get_interactive_qa(
        self,
        stock_code: Annotated[str, "A股股票代码"],
        days_back: Annotated[int, "回看天数"] = 30
    ) -> str:
        """获取互动问答"""
        try:
            logger.info(f"开始获取 {stock_code} 的互动问答数据")
            
            # 创建互动易采集任务
            task = DataCollectionTask(
                source_type=DataSourceType.SZSE_INTERACT,
                target=stock_code,
                data_type="interaction",
                priority=1
            )
            
            self.data_collector.add_collection_task(task)
            asyncio.run(self.data_collector.run_collection_pipeline())
            
            # 获取结果
            search_results = self.storage_manager.search_data(
                keyword=stock_code,
                data_types=['interaction'],
                limit=20
            )
            
            interactions = search_results.get('interaction', [])
            if not interactions:
                return f"未找到股票 {stock_code} 的互动问答数据"
            
            report = f"## {stock_code} 投资者互动问答（近{days_back}天）\n\n"
            
            for i, qa in enumerate(interactions, 1):
                report += f"### 问答 {i}\n"
                report += f"**问题时间**: {qa['question_time']}\n"
                report += f"**问题**: {qa['question']}\n\n"
                report += f"**回答**: {qa['answer']}\n"
                report += f"**来源**: {qa['source']} | **质量**: {qa['quality']}\n"
                report += "\n---\n\n"
            
            return report
            
        except Exception as e:
            logger.error(f"获取互动问答失败: {str(e)}")
            return f"获取股票 {stock_code} 互动问答失败: {str(e)}"
    
    def get_market_sentiment_analysis(
        self,
        keyword: Annotated[str, "搜索关键词，如股票代码、行业名称等"],
        days_back: Annotated[int, "回看天数"] = 7
    ) -> str:
        """获取市场情绪分析"""
        try:
            logger.info(f"开始获取 {keyword} 的市场情绪分析")
            
            # 从多个数据源获取相关数据
            all_data = self.storage_manager.search_data(
                keyword=keyword,
                data_types=['news', 'announcement', 'interaction'],
                limit=100
            )
            
            if not any(all_data.values()):
                return f"未找到关于 {keyword} 的相关数据进行情绪分析"
            
            report = f"## {keyword} 市场情绪分析报告\n\n"
            
            # 统计各类数据数量
            news_count = len(all_data.get('news', []))
            ann_count = len(all_data.get('announcement', []))
            qa_count = len(all_data.get('interaction', []))
            
            report += f"### 数据概览\n"
            report += f"- 新闻数据: {news_count}条\n"
            report += f"- 公告数据: {ann_count}条\n"
            report += f"- 互动问答: {qa_count}条\n"
            report += f"- 数据时间范围: 近{days_back}天\n\n"
            
            # 数据源分布
            all_sources = set()
            for data_type in all_data.values():
                for item in data_type:
                    all_sources.add(item.get('source', ''))
            
            report += f"### 数据源覆盖\n"
            report += f"覆盖数据源: {', '.join(sorted(all_sources))}\n\n"
            
            # 质量分析
            all_items = []
            for data_type in all_data.values():
                all_items.extend(data_type)
            
            quality_dist = {}
            for item in all_items:
                quality = item.get('quality', 'unknown')
                quality_dist[quality] = quality_dist.get(quality, 0) + 1
            
            report += f"### 数据质量分布\n"
            for quality, count in sorted(quality_dist.items()):
                percentage = count / len(all_items) * 100
                report += f"- {quality}: {count}条 ({percentage:.1f}%)\n"
            
            # 时间趋势分析
            report += f"\n### 热度趋势\n"
            report += f"基于近{days_back}天的数据，{keyword}相关信息总计{len(all_items)}条，"
            
            if len(all_items) > 50:
                report += "信息量较大，市场关注度较高。\n"
            elif len(all_items) > 20:
                report += "信息量适中，有一定市场关注。\n"
            else:
                report += "信息量较少，市场关注度一般。\n"
            
            return report
            
        except Exception as e:
            logger.error(f"市场情绪分析失败: {str(e)}")
            return f"获取 {keyword} 市场情绪分析失败: {str(e)}"
    
    def get_industry_analysis(
        self,
        industry: Annotated[str, "行业名称，如'银行'、'科技'、'医药'等"],
        days_back: Annotated[int, "回看天数"] = 14
    ) -> str:
        """获取行业分析"""
        try:
            logger.info(f"开始获取 {industry} 行业分析")
            
            # 创建行业新闻采集任务
            tasks = [
                DataCollectionTask(
                    source_type=DataSourceType.YICAI,
                    target=industry,
                    data_type="news",
                    priority=1
                ),
                DataCollectionTask(
                    source_type=DataSourceType.CNS,
                    target=f"{industry}行业",
                    data_type="policy",
                    priority=1
                )
            ]
            
            for task in tasks:
                self.data_collector.add_collection_task(task)
            
            asyncio.run(self.data_collector.run_collection_pipeline())
            
            # 搜索相关数据
            search_results = self.storage_manager.search_data(
                keyword=industry,
                data_types=['news', 'announcement'],
                limit=30
            )
            
            news_data = search_results.get('news', [])
            ann_data = search_results.get('announcement', [])
            
            if not news_data and not ann_data:
                return f"未找到 {industry} 行业的相关分析数据"
            
            report = f"## {industry}行业分析报告（近{days_back}天）\n\n"
            
            if news_data:
                report += f"### 行业新闻动态 ({len(news_data)}条)\n\n"
                for i, news in enumerate(news_data[:10], 1):
                    report += f"**{i}. {news['title']}**\n"
                    report += f"来源: {news['source']} | 时间: {news['publish_time']}\n\n"
                report += "---\n\n"
            
            if ann_data:
                report += f"### 相关公告信息 ({len(ann_data)}条)\n\n"
                for i, ann in enumerate(ann_data[:5], 1):
                    report += f"**{i}. {ann['title']}**\n"
                    report += f"类型: {ann.get('type', '未知')} | 时间: {ann['publish_time']}\n\n"
                report += "---\n\n"
            
            # 行业关注度分析
            total_items = len(news_data) + len(ann_data)
            report += f"### 行业关注度评估\n"
            report += f"- 总信息量: {total_items}条\n"
            
            if total_items > 30:
                report += "- 关注度: 🔴 高热度行业\n"
            elif total_items > 15:
                report += "- 关注度: 🟡 中等热度行业\n"
            else:
                report += "- 关注度: 🟢 常规关注行业\n"
            
            return report
            
        except Exception as e:
            logger.error(f"行业分析失败: {str(e)}")
            return f"获取 {industry} 行业分析失败: {str(e)}"
    
    def search_stock_data(
        self,
        query: Annotated[str, "搜索查询，可以是股票代码、公司名称或关键词"],
        data_types: Annotated[str, "数据类型，用逗号分隔：news,announcement,interaction"] = "news,announcement,interaction"
    ) -> str:
        """搜索股票数据"""
        try:
            # 解析数据类型
            types_list = [t.strip() for t in data_types.split(',')]
            
            # 执行搜索
            results = self.storage_manager.search_data(
                keyword=query,
                data_types=types_list,
                limit=50
            )
            
            if not any(results.values()):
                return f"未找到关于 '{query}' 的相关数据"
            
            report = f"## '{query}' 搜索结果\n\n"
            
            for data_type, items in results.items():
                if not items:
                    continue
                
                type_name = {
                    'news': '新闻',
                    'announcement': '公告', 
                    'interaction': '互动问答'
                }.get(data_type, data_type)
                
                report += f"### {type_name} ({len(items)}条)\n\n"
                
                for i, item in enumerate(items[:10], 1):
                    if data_type == 'news':
                        report += f"**{i}. {item['title']}**\n"
                        report += f"来源: {item['source']} | 时间: {item['publish_time']} | 质量: {item['quality']}\n"
                    elif data_type == 'announcement':
                        report += f"**{i}. {item['title']}**\n"
                        report += f"类型: {item.get('type', '未知')} | 时间: {item['publish_time']} | 质量: {item['quality']}\n"
                    elif data_type == 'interaction':
                        report += f"**{i}. 问答**\n"
                        report += f"问题: {item['question']}\n"
                        report += f"时间: {item['question_time']} | 质量: {item['quality']}\n"
                    
                    if item.get('url'):
                        report += f"链接: {item['url']}\n"
                    report += "\n"
                
                report += "---\n\n"
            
            return report
            
        except Exception as e:
            logger.error(f"搜索数据失败: {str(e)}")
            return f"搜索 '{query}' 失败: {str(e)}"
    
    def get_data_quality_report(self) -> str:
        """获取数据质量报告"""  
        try:
            stats = self.storage_manager.get_data_statistics()
            
            report = "## A股数据库质量报告\n\n"
            
            # 数据总量统计
            report += "### 数据总量统计\n"
            report += f"- 新闻数据: {stats['news_count']:,}条\n"
            report += f"- 公告数据: {stats['announcement_count']:,}条\n"
            report += f"- 互动问答: {stats['interaction_count']:,}条\n"
            report += f"- 研究报告: {stats['research_count']:,}条\n"
            total = stats['news_count'] + stats['announcement_count'] + stats['interaction_count'] + stats['research_count']
            report += f"- **总数据量**: {total:,}条\n\n"
            
            # 质量分布统计
            report += "### 数据质量分布\n"
            quality_dist = stats['quality_distribution']
            
            for quality, counts in quality_dist.items():
                total_quality = counts['total']
                if total_quality > 0:
                    percentage = total_quality / total * 100
                    quality_name = {
                        'excellent': '优秀',
                        'good': '良好',
                        'average': '一般',
                        'poor': '较差',
                        'invalid': '无效'
                    }.get(quality, quality)
                    
                    report += f"**{quality_name}**: {total_quality:,}条 ({percentage:.1f}%)\n"
                    report += f"  - 新闻: {counts['news']:,}条\n"
                    report += f"  - 公告: {counts['announcement']:,}条\n"
                    report += f"  - 互动: {counts['interaction']:,}条\n\n"
            
            # 近期数据统计
            report += "### 近7天数据增长\n"
            recent = stats['recent_data']
            report += f"- 新增新闻: {recent['news_count']:,}条\n"
            report += f"- 新增公告: {recent['announcement_count']:,}条\n"
            report += f"- 新增互动: {recent['interaction_count']:,}条\n"
            
            recent_total = recent['news_count'] + recent['announcement_count'] + recent['interaction_count']
            if total > 0:
                growth_rate = recent_total / total * 100
                report += f"- 增长率: {growth_rate:.2f}%\n\n"
            
            # 数据质量建议
            excellent_rate = quality_dist.get('excellent', {}).get('total', 0) / total * 100 if total > 0 else 0
            good_rate = quality_dist.get('good', {}).get('total', 0) / total * 100 if total > 0 else 0
            
            report += "### 质量评估与建议\n"
            if excellent_rate + good_rate > 70:
                report += "✅ 数据质量优秀，高质量数据占比超过70%\n"
            elif excellent_rate + good_rate > 50:
                report += "⚠️ 数据质量良好，建议继续优化数据源\n"
            else:
                report += "❌ 数据质量需要改进，建议检查数据采集规则\n"
            
            report += f"\n数据库路径: {self.storage_manager.db_path}\n"
            report += f"报告生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            
            return report
            
        except Exception as e:
            logger.error(f"获取数据质量报告失败: {str(e)}")
            return f"获取数据质量报告失败: {str(e)}"
    
    def export_data_excel(self, output_path: str = None) -> str:
        """导出数据到Excel"""
        try:
            if not output_path:
                output_path = f"ashare_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            success = self.storage_manager.export_data_to_excel(output_path)
            
            if success:
                return f"数据导出成功: {output_path}"
            else:
                return "数据导出失败"
                
        except Exception as e:
            logger.error(f"数据导出失败: {str(e)}")
            return f"数据导出失败: {str(e)}"

def create_enhanced_ashare_data_agent(llm: BaseLanguageModel) -> EnhancedAShareDataAgent:
    """创建增强版A股数据智能体"""
    return EnhancedAShareDataAgent(llm)