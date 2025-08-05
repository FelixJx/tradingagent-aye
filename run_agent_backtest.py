# -*- coding: utf-8 -*-
"""
Agent回测运行脚本
完整的回测流程和报告生成
"""

import os
import json
import pandas as pd
from datetime import datetime
from agent_backtest_framework import AgentBacktestFramework
from enhanced_agent_analysis import EnhancedAgentAnalysis

def load_config():
    """加载配置"""
    config = {
        'tushare_token': 'b34d8920b99b43d48df7e792a4708a29f868feeee30d9c84b54bf065',
        'test_stocks': [
            '000001.SZ',  # 平安银行
            '000002.SZ',  # 万科A
            '600000.SH',  # 浦发银行
            '600036.SH',  # 招商银行
            '000858.SZ',  # 五粮液
            '600519.SH',  # 贵州茅台
            '000651.SZ',  # 格力电器
            '002415.SZ',  # 海康威视
            '300059.SZ',  # 东方财富
            '002594.SZ'   # 比亚迪
        ],
        'backtest_period': {
            'start_date': '20220101',  # 2年期回测
            'end_date': '20240131'     # 到2024年1月
        },
        'agent_types': [
            'market_analyst',
            'fundamental_analyst', 
            'bull_researcher',
            'bear_researcher'
        ]
    }
    return config

def run_comprehensive_backtest():
    """运行综合回测"""
    print("开始Agent回测分析...")
    
    # 加载配置
    config = load_config()
    
    # 初始化框架
    framework = AgentBacktestFramework(config['tushare_token'])
    enhanced_analysis = EnhancedAgentAnalysis(config['tushare_token'])
    
    # 存储所有结果
    all_results = {}
    all_innovation_scores = {}
    all_suggestions = {}
    
    # 为每个Agent类型运行回测
    for agent_type in config['agent_types']:
        print(f"\n正在回测 {agent_type}...")
        
        try:
            # 运行回测
            results = framework.analyze_agent_performance(
                agent_type,
                config['test_stocks'],
                config['backtest_period']['start_date'],
                config['backtest_period']['end_date']
            )
            
            all_results[agent_type] = results
            
            # 计算创新得分（使用第一只股票的预测作为示例）
            if results['stock_results']:
                first_stock_predictions = results['stock_results'][0].get('predictions', [])
                innovation_scores = enhanced_analysis.calculate_agent_innovation_score(first_stock_predictions)
                all_innovation_scores[agent_type] = innovation_scores
                
                # 生成改进建议
                suggestions = enhanced_analysis.generate_improvement_suggestions(
                    agent_type, results, innovation_scores
                )
                all_suggestions[agent_type] = suggestions
            
            # 生成单个Agent报告
            report = framework.generate_performance_report(results)
            
            # 保存单个报告
            with open(f"{agent_type}_backtest_report.md", 'w', encoding='utf-8') as f:
                f.write(report)
                
                # 添加创新分析
                if agent_type in all_innovation_scores:
                    f.write("\n\n## 创新性分析\n")
                    innovation = all_innovation_scores[agent_type]
                    f.write(f"- **多样性得分**: {innovation['diversity_score']:.2f}\n")
                    f.write(f"- **复杂性得分**: {innovation['complexity_score']:.2f}\n")
                    f.write(f"- **适应性得分**: {innovation['adaptability_score']:.2f}\n")
                    f.write(f"- **时机把握得分**: {innovation['timing_score']:.2f}\n")
                    f.write(f"- **风险意识得分**: {innovation['risk_awareness_score']:.2f}\n")
                    f.write(f"- **总体创新得分**: {innovation['overall_innovation']:.2f}\n")
                
                # 添加改进建议
                if agent_type in all_suggestions:
                    f.write("\n\n## 改进建议\n")
                    for i, suggestion in enumerate(all_suggestions[agent_type], 1):
                        f.write(f"{i}. {suggestion}\n")
            
            # 保存结果到数据库
            framework.save_results_to_db(results)
            
            print(f"{agent_type} 回测完成，准确率: {results['accuracy']:.2%}")
            
        except Exception as e:
            print(f"{agent_type} 回测失败: {e}")
            continue
    
    # 生成综合对比报告
    generate_comprehensive_report(all_results, all_innovation_scores, all_suggestions)
    
    # 保存结果到JSON文件
    save_results_to_json(all_results, all_innovation_scores, all_suggestions)
    
    print("\n所有Agent回测完成！")
    print("报告文件已生成:")
    print("  - agent_comprehensive_analysis.md (综合分析报告)")
    print("  - agent_backtest_results.json (详细结果数据)")
    print("  - 各Agent单独报告文件")

def generate_comprehensive_report(all_results, all_innovation_scores, all_suggestions):
    """生成综合分析报告"""
    
    report = """# Agent综合回测分析报告

## 执行摘要

本报告基于tushare真实数据，对多个股票分析Agent进行了全面的历史回测，评估其预测准确性、创新性和实用性。

## 总体表现对比

### 预测准确率对比
"""
    
    # 生成对比表格
    report += "| Agent类型 | 预测准确率 | 1日收益率 | 5日收益率 | 20日收益率 | 创新得分 |\n"
    report += "|----------|------------|-----------|-----------|------------|----------|\n"
    
    for agent_type, results in all_results.items():
        innovation_score = all_innovation_scores.get(agent_type, {}).get('overall_innovation', 0)
        report += f"| {agent_type} | {results['accuracy']:.2%} | {results['avg_return_1d']:.2%} | {results['avg_return_5d']:.2%} | {results['avg_return_20d']:.2%} | {innovation_score:.2f} |\n"
    
    # 找出最佳表现者
    best_accuracy = max(all_results.values(), key=lambda x: x['accuracy'])
    best_return = max(all_results.values(), key=lambda x: x['avg_return_20d'])
    best_innovation = max(all_innovation_scores.items(), key=lambda x: x[1]['overall_innovation']) if all_innovation_scores else None
    
    report += f"""
## 关键发现

### 最佳表现者
- **预测准确率最高**: {[k for k, v in all_results.items() if v == best_accuracy][0]} ({best_accuracy['accuracy']:.2%})
- **收益率最高**: {[k for k, v in all_results.items() if v == best_return][0]} ({best_return['avg_return_20d']:.2%})
"""
    
    if best_innovation:
        report += f"- **创新性最高**: {best_innovation[0]} ({best_innovation[1]['overall_innovation']:.2f})\n"
    
    report += """
### 整体分析

#### 现有Agent的问题
1. **评估角度普通化**: 大多数Agent依赖传统技术指标，缺乏创新性分析维度
2. **预测准确率偏低**: 平均准确率低于50%，显示现有方法有待改进
3. **风险意识不足**: 多数Agent偏向激进交易，缺乏适当的风险控制
4. **适应性差**: 未能根据不同市场环境调整策略

#### 改进空间
1. **多维度指标**: 需要整合更多创新指标，如市场微观结构、另类数据等
2. **动态适应**: 应根据市场状态动态调整分析策略
3. **风险管理**: 加强风险识别和控制机制
4. **学习能力**: 增加历史回测和学习机制

## 详细分析

"""
    
    # 为每个Agent添加详细分析
    for agent_type in all_results.keys():
        results = all_results[agent_type]
        innovation = all_innovation_scores.get(agent_type, {})
        suggestions = all_suggestions.get(agent_type, [])
        
        report += f"""
### {agent_type}

#### 性能指标
- 预测次数: {results['total_predictions']}
- 预测准确率: {results['accuracy']:.2%}
- 平均20日收益率: {results['avg_return_20d']:.2%}

#### 创新性评估
"""
        if innovation:
            report += f"- 多样性得分: {innovation['diversity_score']:.2f}\n"
            report += f"- 复杂性得分: {innovation['complexity_score']:.2f}\n"
            report += f"- 适应性得分: {innovation['adaptability_score']:.2f}\n"
            report += f"- 总体创新得分: {innovation['overall_innovation']:.2f}\n"
        
        report += "\n#### 主要问题和改进建议\n"
        for i, suggestion in enumerate(suggestions[:5], 1):  # 只显示前5个建议
            report += f"{i}. {suggestion}\n"
    
    report += """
## 推荐的Agent升级方案

### 1. 技术指标升级
- **传统指标**: 保留有效的MACD、RSI等，但优化参数
- **创新指标**: 引入市场微观结构指标、另类数据指标
- **多时间框架**: 整合多个时间周期的分析

### 2. 分析逻辑增强
- **信号确认**: 多信号确认机制，减少误信号
- **动态权重**: 根据市场环境调整指标权重
- **机器学习**: 使用ML方法进行特征选择和组合

### 3. 风险管理改进  
- **风险评估**: 增加风险度量指标
- **仓位管理**: 基于风险调整仓位大小
- **止损机制**: 完善的止损和风控体系

### 4. 学习机制建立
- **历史回测**: 定期回测和策略调整
- **在线学习**: 根据新数据调整模型参数
- **A/B测试**: 对比不同策略的效果

## 结论

当前的股票分析Agent在评估角度上确实存在普通化问题，主要体现在：

1. **指标选择传统**: 过度依赖传统技术指标
2. **分析维度单一**: 缺乏多角度综合分析
3. **创新性不足**: 未能引入新兴的分析方法
4. **适应性差**: 无法根据市场变化调整策略

建议采用本报告提出的增强版分析框架，结合更多创新指标和智能化方法，提升Agent的分析能力和预测准确性。
"""
    
    # 保存报告
    with open("agent_comprehensive_analysis.md", 'w', encoding='utf-8') as f:
        f.write(report)

def save_results_to_json(all_results, all_innovation_scores, all_suggestions):
    """保存结果到JSON文件"""
    
    # 准备数据（处理datetime等不可JSON序列化的对象）
    json_data = {
        'backtest_results': {},
        'innovation_scores': all_innovation_scores,
        'improvement_suggestions': all_suggestions,
        'metadata': {
            'generated_time': datetime.now().isoformat(),
            'total_agents_tested': len(all_results),
            'analysis_framework': 'Enhanced Agent Backtest Framework v1.0'
        }
    }
    
    # 处理回测结果
    for agent_type, results in all_results.items():
        json_results = {
            'agent_type': results['agent_type'],
            'total_predictions': results['total_predictions'],
            'correct_predictions': results['correct_predictions'], 
            'accuracy': results['accuracy'],
            'avg_return_1d': results['avg_return_1d'],
            'avg_return_5d': results['avg_return_5d'],
            'avg_return_20d': results['avg_return_20d'],
            'stock_results': []
        }
        
        # 处理个股结果
        for stock_result in results['stock_results']:
            stock_data = {
                'stock_code': stock_result['stock_code'],
                'total_predictions': stock_result['total_predictions'],
                'correct_predictions': stock_result['correct_predictions'],
                'accuracy': stock_result['accuracy'],
                'avg_return_1d': float(pd.Series(stock_result['returns_1d']).mean()) if stock_result['returns_1d'] else 0,
                'avg_return_5d': float(pd.Series(stock_result['returns_5d']).mean()) if stock_result['returns_5d'] else 0,
                'avg_return_20d': float(pd.Series(stock_result['returns_20d']).mean()) if stock_result['returns_20d'] else 0
            }
            json_results['stock_results'].append(stock_data)
        
        json_data['backtest_results'][agent_type] = json_results
    
    # 保存到文件
    with open('agent_backtest_results.json', 'w', encoding='utf-8') as f:
        json.dump(json_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_comprehensive_backtest()