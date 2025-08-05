#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
果麦文化数据采集脚本
使用增强数据采集系统收集果麦文化的所有相关资讯
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from pathlib import Path

# 添加项目路径
sys.path.append(str(Path(__file__).parent))

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guomai_collection.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_llm():
    """设置语言模型"""
    try:
        # 尝试使用千问模型
        dashscope_key = os.getenv("DASHSCOPE_API_KEY")
        if dashscope_key:
            from langchain_community.chat_models import ChatTongyi
            logger.info("使用阿里云千问模型")
            return ChatTongyi(
                dashscope_api_key=dashscope_key,
                model_name="qwen-turbo",
                temperature=0.7
            )
    except Exception as e:
        logger.warning(f"千问模型初始化失败: {str(e)}")
    
    try:
        # 尝试使用OpenAI
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            from langchain_openai import ChatOpenAI
            logger.info("使用OpenAI模型")
            return ChatOpenAI(
                api_key=openai_key,
                model="gpt-4o-mini",
                temperature=0.7
            )
    except Exception as e:
        logger.warning(f"OpenAI模型初始化失败: {str(e)}")
    
    try:
        # 尝试使用本地Ollama
        from langchain_community.llms import Ollama
        logger.info("使用本地Ollama模型")
        return Ollama(model="qwen2:7b")
    except Exception as e:
        logger.warning(f"Ollama模型初始化失败: {str(e)}")
    
    # 如果都失败了，创建一个简化的模拟LLM
    class MockLLM:
        def invoke(self, prompt):
            class MockResponse:
                content = '{"analysis": "数据采集分析", "alternative_method": "使用备用方法", "parameter_adjustment": "调整参数", "should_switch_source": false}'
            return MockResponse()
    
    logger.warning("使用模拟LLM")
    return MockLLM()

def collect_guomai_comprehensive_data():
    """全面收集果麦文化数据"""
    stock_code = "301052"
    company_name = "果麦文化"
    
    print("🚀 开始收集果麦文化全面数据")
    print("="*60)
    
    # 初始化LLM和数据采集agent
    llm = setup_llm()
    
    try:
        from tradingagents.agents.enhanced_ashare_data_agent import create_enhanced_ashare_data_agent
        data_agent = create_enhanced_ashare_data_agent(llm)
        logger.info("增强数据采集agent初始化成功")
    except Exception as e:
        logger.error(f"数据采集agent初始化失败: {str(e)}")
        return
    
    # 收集任务列表
    collection_tasks = [
        ("综合新闻数据", lambda: data_agent.get_comprehensive_stock_news(stock_code, days_back=30)),
        ("公告数据", lambda: data_agent.get_stock_announcements(stock_code, days_back=90)),
        ("互动问答", lambda: data_agent.get_interactive_qa(stock_code, days_back=60)),
        ("行业分析", lambda: data_agent.get_industry_analysis("文化传媒", days_back=30)),
        ("市场情绪分析", lambda: data_agent.get_market_sentiment_analysis("果麦文化", days_back=14)),
        ("综合搜索", lambda: data_agent.search_stock_data("果麦文化", data_types="news,announcement,interaction"))
    ]
    
    results = {}
    
    for task_name, task_func in collection_tasks:
        print(f"\n📊 正在执行: {task_name}")
        print("-" * 40)
        
        try:
            result = task_func()
            results[task_name] = result
            
            # 显示结果摘要
            if len(result) > 500:
                print(f"✅ {task_name} 完成，数据长度: {len(result)}字符")
                print("前500字符预览:")
                print(result[:500] + "...\n")
            else:
                print(f"✅ {task_name} 完成:")
                print(result[:300] + "...\n" if len(result) > 300 else result + "\n")
                
        except Exception as e:
            error_msg = f"❌ {task_name} 失败: {str(e)}"
            print(error_msg)
            results[task_name] = error_msg
            logger.error(error_msg)
    
    # 生成数据质量报告
    print("\n📈 生成数据质量报告")
    print("-" * 40)
    try:
        quality_report = data_agent.get_data_quality_report()
        results["数据质量报告"] = quality_report
        print("✅ 数据质量报告生成完成")
        print(quality_report[:300] + "...\n" if len(quality_report) > 300 else quality_report + "\n")
    except Exception as e:
        error_msg = f"❌ 数据质量报告生成失败: {str(e)}"
        print(error_msg)
        results["数据质量报告"] = error_msg
    
    # 导出数据
    print("\n📤 导出数据到Excel")
    print("-" * 40)
    try:
        export_file = f"果麦文化_数据采集_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        export_result = data_agent.export_data_excel(export_file)
        results["数据导出"] = export_result
        print(f"✅ {export_result}")
    except Exception as e:
        error_msg = f"❌ 数据导出失败: {str(e)}"
        print(error_msg)
        results["数据导出"] = error_msg
    
    # 保存结果到文件
    output_file = f"果麦文化_采集结果_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"果麦文化({stock_code})数据采集结果\n")
            f.write(f"采集时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            for task_name, result in results.items():
                f.write(f"【{task_name}】\n")
                f.write("-" * 40 + "\n")
                f.write(str(result) + "\n\n")
        
        print(f"\n✅ 采集结果已保存到: {output_file}")
        
    except Exception as e:
        print(f"❌ 保存结果文件失败: {str(e)}")
    
    # 显示采集总结
    print("\n📋 采集总结")
    print("="*60)
    successful_tasks = sum(1 for result in results.values() if not str(result).startswith("❌"))
    total_tasks = len(results)
    
    print(f"• 总任务数: {total_tasks}")
    print(f"• 成功任务: {successful_tasks}")
    print(f"• 失败任务: {total_tasks - successful_tasks}")
    print(f"• 成功率: {successful_tasks/total_tasks*100:.1f}%")
    
    if successful_tasks > 0:
        print(f"• 数据已存储到数据库: ashare_comprehensive_data.db")
        print(f"• 结果文件: {output_file}")
    
    return results

def main():
    """主函数"""
    print("🥬 果麦文化数据采集系统")
    print("="*60)
    print("股票代码: 301052")
    print("公司名称: 果麦文化")
    print("采集范围: 新闻、公告、互动问答、行业分析等")
    print("")
    
    # 检查环境
    print("🔧 检查环境配置...")
    
    env_status = []
    if os.getenv("DASHSCOPE_API_KEY"):
        env_status.append("✅ 阿里云千问API")
    if os.getenv("OPENAI_API_KEY"):
        env_status.append("✅ OpenAI API")
    if os.getenv("TUSHARE_TOKEN"):
        env_status.append("✅ Tushare Token")
    
    if env_status:
        print("环境配置:")
        for status in env_status:
            print(f"  {status}")
    else:
        print("⚠️ 未检测到API配置，将使用基础模式")
    
    print("")
    
    # 自动开始采集
    print("⏳ 自动开始采集果麦文化数据...")
    
    # 开始采集
    try:
        results = collect_guomai_comprehensive_data()
        
        print("\n🎉 果麦文化数据采集完成！")
        print("数据已存储到数据库，可通过以下方式查看：")
        print("1. 查看生成的Excel文件")
        print("2. 查看结果文本文件") 
        print("3. 直接查询数据库")
        
    except KeyboardInterrupt:
        print("\n⏹️ 采集被用户中断")
    except Exception as e:
        print(f"\n❌ 采集过程中出现错误: {str(e)}")
        logger.error(f"采集错误: {str(e)}", exc_info=True)

if __name__ == "__main__":
    main()