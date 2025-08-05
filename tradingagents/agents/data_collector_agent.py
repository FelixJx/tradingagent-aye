# -*- coding: utf-8 -*-
"""
A股数据采集智能体
强大的、不达目的不罢休的数据采集系统
支持多数据源：巨潮信息网、新浪财经、东方财富网、中国证券网、深交所互动易、第一财经、韭研公社
"""

import os
import time
import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
import traceback
from pathlib import Path

import requests
import pandas as pd
from bs4 import BeautifulSoup
import json
import sqlite3
from dataclasses import dataclass
from enum import Enum

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
from langchain.schema import AgentAction, AgentFinish
from langchain.callbacks.manager import CallbackManagerForAgentRun
from langchain_core.language_models import BaseLanguageModel

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataSourceType(Enum):
    """数据源类型枚举"""
    JUCHAO = "juchao"  # 巨潮信息网
    SINA = "sina"      # 新浪财经
    EASTMONEY = "eastmoney"  # 东方财富网
    CNS = "cns"        # 中国证券网
    SZSE_INTERACT = "szse_interact"  # 深交所互动易
    YICAI = "yicai"    # 第一财经
    JIUYAN = "jiuyan"  # 韭研公社

@dataclass
class DataCollectionTask:
    """数据采集任务"""
    source_type: DataSourceType
    target: str  # 目标股票代码或关键词
    data_type: str  # 数据类型：news, announcement, financial, etc.
    priority: int = 1  # 优先级 1-5，1最高
    max_retries: int = 5
    timeout: int = 30
    created_at: datetime = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

@dataclass
class DataCollectionResult:
    """数据采集结果"""
    task: DataCollectionTask
    success: bool
    data: Optional[List[Dict]] = None
    error_msg: Optional[str] = None
    retry_count: int = 0
    collected_at: datetime = None
    
    def __post_init__(self):
        if self.collected_at is None:
            self.collected_at = datetime.now()

class DataSourceCrawler:
    """数据源爬虫基类"""
    
    def __init__(self, source_type: DataSourceType):
        self.source_type = source_type
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取数据的抽象方法"""
        raise NotImplementedError

class JuchaoInfoCrawler(DataSourceCrawler):
    """巨潮信息网爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.JUCHAO)
        self.base_url = "http://www.cninfo.com.cn"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取巨潮信息网数据"""
        try:
            if task.data_type == "announcement":
                return self._crawl_announcements(task)
            elif task.data_type == "financial":
                return self._crawl_financial_data(task)
            else:
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg=f"不支持的数据类型: {task.data_type}"
                )
        except Exception as e:
            logger.error(f"巨潮信息网爬取失败: {str(e)}")
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_announcements(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取公告数据"""
        try:
            # 巨潮信息网公告查询API
            api_url = f"{self.base_url}/new/hisAnnouncement"
            
            params = {
                'stock': task.target,
                'searchkey': '',
                'category': '',
                'trade': '',
                'column': 'szse',
                'columnTitle': '历史公告查询',
                'pageNum': 1,
                'pageSize': 30,
                'tabName': 'fulltext',
                'sortName': '',
                'sortType': '',
                'limit': '',
                'showTitle': '',
                'seDate': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d') + '~' + datetime.now().strftime('%Y-%m-%d')
            }
            
            response = self.session.post(api_url, data=params, timeout=task.timeout)
            response.raise_for_status()
            
            data = response.json()
            announcements = []
            
            if 'announcements' in data:
                for item in data['announcements']:
                    announcements.append({
                        'title': item.get('announcementTitle', ''),
                        'time': item.get('announcementTime', ''),
                        'type': item.get('announcementType', ''),
                        'url': f"{self.base_url}/{item.get('adjunctUrl', '')}" if item.get('adjunctUrl') else '',
                        'stock_code': task.target,
                        'source': '巨潮信息网'
                    })
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=announcements
            )
            
        except Exception as e:
            logger.error(f"爬取巨潮公告失败: {str(e)}")
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def _crawl_financial_data(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取财务数据"""
        # 实现财务数据爬取逻辑
        try:
            # 这里可以调用巨潮的财务数据API
            financial_data = []
            # ... 具体实现
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=financial_data
            )
        except Exception as e:
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )

class SZSEInteractiveCrawler(DataSourceCrawler):
    """深交所互动易爬虫"""
    
    def __init__(self):
        super().__init__(DataSourceType.SZSE_INTERACT)
        self.base_url = "http://irm.cninfo.com.cn"
        
    def crawl(self, task: DataCollectionTask) -> DataCollectionResult:
        """爬取深交所互动易数据"""
        try:
            # 互动易查询API
            api_url = f"{self.base_url}/szse/query/cninfoQuery.do"
            
            params = {
                'keyWord': task.target,
                'condition.stockCode': task.target if task.target.isdigit() else '',
                'condition.searchScope': '1',
                'condition.replyTime.start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                'condition.replyTime.end': datetime.now().strftime('%Y-%m-%d'),
                'pageNo': 1,
                'pageSize': 50
            }
            
            response = self.session.post(api_url, data=params, timeout=task.timeout)
            response.raise_for_status()
            
            data = response.json()
            interactions = []
            
            if 'records' in data:
                for item in data['records']:
                    interactions.append({
                        'question': item.get('question', ''),
                        'answer': item.get('answer', ''),
                        'question_time': item.get('questionTime', ''),
                        'answer_time': item.get('answerTime', ''),
                        'company_name': item.get('company', ''),
                        'stock_code': task.target,
                        'source': '深交所互动易'
                    })
            
            return DataCollectionResult(
                task=task,
                success=True,
                data=interactions
            )
            
        except Exception as e:
            logger.error(f"深交所互动易爬取失败: {str(e)}")
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )

class GitHubCrawlerDetector:
    """GitHub爬虫工具检测器"""
    
    def __init__(self):
        self.github_api_base = "https://api.github.com"
        self.detected_crawlers = {}
        
    def search_crawlers(self, keywords: List[str]) -> List[Dict]:
        """搜索GitHub上的爬虫工具"""
        crawlers = []
        
        for keyword in keywords:
            try:
                search_url = f"{self.github_api_base}/search/repositories"
                params = {
                    'q': f'{keyword} crawler spider 爬虫 language:Python',
                    'sort': 'stars',
                    'order': 'desc',
                    'per_page': 10
                }
                
                response = requests.get(search_url, params=params, timeout=30)
                response.raise_for_status()
                
                data = response.json()
                
                for item in data.get('items', []):
                    crawler_info = {
                        'name': item['name'],
                        'full_name': item['full_name'],
                        'description': item['description'],
                        'url': item['html_url'],
                        'clone_url': item['clone_url'],
                        'stars': item['stargazers_count'],
                        'keyword': keyword,
                        'last_updated': item['updated_at']
                    }
                    crawlers.append(crawler_info)
                    
                time.sleep(1)  # 避免API限制
                
            except Exception as e:
                logger.error(f"搜索GitHub爬虫失败 {keyword}: {str(e)}")
                continue
        
        return crawlers
    
    def clone_and_setup_crawler(self, crawler_info: Dict, target_dir: str) -> bool:
        """克隆并设置爬虫工具"""
        try:
            import subprocess
            
            clone_dir = Path(target_dir) / crawler_info['name']
            
            if clone_dir.exists():
                logger.info(f"爬虫 {crawler_info['name']} 已存在")
                return True
            
            # 克隆仓库
            result = subprocess.run([
                'git', 'clone', crawler_info['clone_url'], str(clone_dir)
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"克隆失败: {result.stderr}")
                return False
            
            # 尝试安装依赖
            requirements_file = clone_dir / 'requirements.txt'
            if requirements_file.exists():
                subprocess.run([
                    'pip', 'install', '-r', str(requirements_file)
                ], capture_output=True, timeout=300)
            
            logger.info(f"成功设置爬虫: {crawler_info['name']}")
            return True
            
        except Exception as e:
            logger.error(f"设置爬虫失败 {crawler_info['name']}: {str(e)}")
            return False

class DataCollectorAgent:
    """不达目的不罢休的数据采集智能体"""
    
    def __init__(self, llm: BaseLanguageModel, db_path: str = "ashare_data.db"):
        self.llm = llm
        self.db_path = db_path
        self.crawlers = self._init_crawlers()
        self.github_detector = GitHubCrawlerDetector()
        self.task_queue = []
        self.failed_tasks = []
        self.max_concurrent_tasks = 5
        self.setup_database()
        
        # 预搜索GitHub爬虫工具
        self._preload_github_crawlers()
        
    def _init_crawlers(self) -> Dict[DataSourceType, DataSourceCrawler]:
        """初始化爬虫"""
        return {
            DataSourceType.JUCHAO: JuchaoInfoCrawler(),
            DataSourceType.SZSE_INTERACT: SZSEInteractiveCrawler(),
            # 其他爬虫将在下一步实现
        }
    
    def _preload_github_crawlers(self):
        """预加载GitHub爬虫工具"""
        keywords = [
            "巨潮信息网", "cninfo", "新浪财经", "sina finance",
            "东方财富", "eastmoney", "中国证券网", "cs.com.cn",
            "第一财经", "yicai", "韭研公社", "jiuyan"
        ]
        
        logger.info("正在搜索GitHub爬虫工具...")
        self.available_crawlers = self.github_detector.search_crawlers(keywords)
        logger.info(f"发现 {len(self.available_crawlers)} 个潜在爬虫工具")
    
    def setup_database(self):
        """设置数据库"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 创建数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collected_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                data_type TEXT NOT NULL,
                target TEXT NOT NULL,
                title TEXT,
                content TEXT,
                url TEXT,
                publish_time TEXT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS collection_tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_type TEXT NOT NULL,
                data_type TEXT NOT NULL,
                target TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                retry_count INTEGER DEFAULT 0,
                error_msg TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def add_collection_task(self, task: DataCollectionTask):
        """添加采集任务"""
        self.task_queue.append(task)
        
        # 保存到数据库
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO collection_tasks (source_type, data_type, target)
            VALUES (?, ?, ?)
        ''', (task.source_type.value, task.data_type, task.target))
        conn.commit()
        conn.close()
        
        logger.info(f"添加采集任务: {task.source_type.value} - {task.target}")
    
    def collect_data_with_retry(self, task: DataCollectionTask) -> DataCollectionResult:
        """带重试机制的数据采集"""
        retry_count = 0
        last_error = None
        
        while retry_count <= task.max_retries:
            try:
                logger.info(f"尝试采集数据 (第{retry_count + 1}次): {task.source_type.value} - {task.target}")
                
                # 首先尝试使用内置爬虫
                if task.source_type in self.crawlers:
                    result = self.crawlers[task.source_type].crawl(task)
                    if result.success:
                        return result
                    last_error = result.error_msg
                
                # 如果内置爬虫失败，尝试使用GitHub爬虫
                github_result = self._try_github_crawlers(task)
                if github_result and github_result.success:
                    return github_result
                
                # 如果都失败了，使用LLM智能分析和重试
                llm_result = self._llm_guided_retry(task, last_error)
                if llm_result.success:
                    return llm_result
                
                retry_count += 1
                if retry_count <= task.max_retries:
                    # 指数退避
                    sleep_time = min(300, 2 ** retry_count + random.uniform(0, 1))
                    logger.info(f"等待 {sleep_time:.1f} 秒后重试...")
                    time.sleep(sleep_time)
                
            except Exception as e:
                last_error = str(e)
                logger.error(f"采集过程中出错: {last_error}")
                retry_count += 1
        
        # 所有重试都失败了
        logger.error(f"采集任务最终失败: {task.source_type.value} - {task.target}")
        return DataCollectionResult(
            task=task,
            success=False,
            error_msg=last_error,
            retry_count=retry_count
        )
    
    def _try_github_crawlers(self, task: DataCollectionTask) -> Optional[DataCollectionResult]:
        """尝试使用GitHub爬虫"""
        relevant_crawlers = [
            c for c in self.available_crawlers 
            if task.source_type.value in c['description'].lower() or 
               task.source_type.value in c['name'].lower()
        ]
        
        for crawler_info in relevant_crawlers[:3]:  # 最多尝试3个
            try:
                logger.info(f"尝试使用GitHub爬虫: {crawler_info['name']}")
                
                # 动态加载和执行爬虫
                success = self._execute_github_crawler(crawler_info, task)
                if success:
                    return DataCollectionResult(
                        task=task,
                        success=True,
                        data=[{'source': 'github_crawler', 'crawler': crawler_info['name']}]
                    )
                    
            except Exception as e:
                logger.error(f"GitHub爬虫执行失败 {crawler_info['name']}: {str(e)}")
                continue
        
        return None
    
    def _execute_github_crawler(self, crawler_info: Dict, task: DataCollectionTask) -> bool:
        """执行GitHub爬虫"""
        # 这里实现动态执行GitHub爬虫的逻辑
        # 由于复杂性，这里返回False，在实际实现中需要更详细的逻辑
        return False
    
    def _llm_guided_retry(self, task: DataCollectionTask, error_msg: str) -> DataCollectionResult:
        """LLM指导的智能重试"""
        try:
            prompt = f"""
            作为数据采集专家，我遇到了以下采集任务失败的情况：
            
            任务详情：
            - 数据源：{task.source_type.value}
            - 目标：{task.target}
            - 数据类型：{task.data_type}
            - 错误信息：{error_msg}
            
            请分析失败原因并提供解决方案：
            1. 可能的失败原因
            2. 替代的数据获取方法
            3. 参数调整建议
            4. 是否需要更换数据源
            
            请用JSON格式回复，包含：
            {{
                "analysis": "失败原因分析",
                "alternative_method": "替代方法",
                "parameter_adjustment": "参数调整建议",
                "should_switch_source": true/false,
                "alternative_source": "如果需要切换，建议的数据源"
            }}
            """
            
            # 调用LLM分析
            response = self.llm.invoke(prompt)
            
            try:
                analysis = json.loads(response.content)
                logger.info(f"LLM分析结果: {analysis['analysis']}")
                
                # 根据LLM建议执行相应操作
                if analysis.get('should_switch_source'):
                    # 切换数据源重试
                    pass
                
                # 这里可以根据LLM的建议调整策略
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg="LLM分析完成，但未找到有效解决方案"
                )
                
            except json.JSONDecodeError:
                logger.error("LLM返回格式不正确")
                return DataCollectionResult(
                    task=task,
                    success=False,
                    error_msg="LLM分析失败"
                )
                
        except Exception as e:
            logger.error(f"LLM指导重试失败: {str(e)}")
            return DataCollectionResult(
                task=task,
                success=False,
                error_msg=str(e)
            )
    
    def save_data(self, result: DataCollectionResult):
        """保存采集到的数据"""
        if not result.success or not result.data:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for item in result.data:
            cursor.execute('''
                INSERT INTO collected_data 
                (source_type, data_type, target, title, content, url, publish_time, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                result.task.source_type.value,
                result.task.data_type,
                result.task.target,
                item.get('title', ''),
                item.get('content', ''),
                item.get('url', ''),
                item.get('publish_time', ''),
                json.dumps(item, ensure_ascii=False)
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"保存了 {len(result.data)} 条数据")
    
    async def run_collection_pipeline(self):
        """运行数据采集管道"""
        logger.info("启动数据采集管道...")
        
        while self.task_queue or self.failed_tasks:
            # 处理正常任务队列
            current_tasks = []
            for _ in range(min(self.max_concurrent_tasks, len(self.task_queue))):
                if self.task_queue:
                    current_tasks.append(self.task_queue.pop(0))
            
            # 并发处理任务
            if current_tasks:
                tasks = [
                    asyncio.create_task(self._async_collect_data(task))
                    for task in current_tasks
                ]
                
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                for result in results:
                    if isinstance(result, DataCollectionResult):
                        if result.success:
                            self.save_data(result)
                        else:
                            if result.retry_count < result.task.max_retries:
                                logger.info(f"任务失败，加入重试队列: {result.task.target}")
                                self.failed_tasks.append(result.task)
            
            # 处理失败任务重试
            if self.failed_tasks:
                retry_task = self.failed_tasks.pop(0)
                retry_result = await self._async_collect_data(retry_task)
                if retry_result.success:
                    self.save_data(retry_result)
                elif retry_result.retry_count < retry_result.task.max_retries:
                    self.failed_tasks.append(retry_result.task)
            
            await asyncio.sleep(1)  # 短暂休息
        
        logger.info("数据采集管道完成")
    
    async def _async_collect_data(self, task: DataCollectionTask) -> DataCollectionResult:
        """异步数据采集"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.collect_data_with_retry, task)

def create_data_collector_agent(llm: BaseLanguageModel) -> DataCollectorAgent:
    """创建数据采集智能体"""
    return DataCollectorAgent(llm)