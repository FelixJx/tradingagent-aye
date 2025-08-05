#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A股新闻获取和分析脚本（简化版）
"""

from datetime import datetime, timedelta

def get_previous_trading_day(current_date_str):
    """
    获取上一个交易日（简单实现，假设周一到周五为交易日）
    """
    current_date = datetime.strptime(current_date_str, '%Y-%m-%d')
    
    # 如果是周一，上一个交易日是上周五
    if current_date.weekday() == 0:  # 周一
        previous_trading_day = current_date - timedelta(days=3)
    # 如果是周日，上一个交易日是上周五
    elif current_date.weekday() == 6:  # 周日
        previous_trading_day = current_date - timedelta(days=2)
    # 其他情况，上一个交易日是前一天
    else:
        previous_trading_day = current_date - timedelta(days=1)
    
    return previous_trading_day.strftime('%Y-%m-%d')

def get_sample_ashare_news():
    """
    获取A股新闻示例数据（模拟数据，因为实际API可能需要配置）
    """
    sample_news = [
        {
            'title': 'A股三大指数集体收涨 创业板指涨超1%',
            'content': '7月4日，A股三大指数集体收涨，上证指数涨0.8%，深证成指涨1.2%，创业板指涨1.3%。两市成交额超8000亿元。',
            'source': '财经网',
            'time': '2025-07-04 15:30:00'
        },
        {
            'title': '央行宣布降准0.25个百分点 释放流动性约5000亿元',
            'content': '中国人民银行决定于7月5日下调金融机构存款准备金率0.25个百分点，此次降准将释放长期资金约5000亿元。',
            'source': '新华财经',
            'time': '2025-07-04 18:00:00'
        },
        {
            'title': '科技股表现强劲 人工智能概念股领涨',
            'content': '科技板块今日表现亮眼，人工智能、芯片、新能源等概念股纷纷上涨，多只个股涨停。',
            'source': '证券时报',
            'time': '2025-07-04 16:45:00'
        },
        {
            'title': '外资持续流入A股市场 北向资金净买入超50亿',
            'content': '7月4日，北向资金全天净买入52.3亿元，连续5个交易日净流入，显示外资对A股市场信心增强。',
            'source': '中国证券报',
            'time': '2025-07-04 17:20:00'
        },
        {
            'title': '新能源汽车产业政策利好频出 相关个股大涨',
            'content': '工信部发布新能源汽车产业发展新政策，支持技术创新和产业升级，新能源汽车板块应声上涨。',
            'source': '经济参考报',
            'time': '2025-07-04 14:15:00'
        }
    ]
    return sample_news

def analyze_news_sentiment(news_list):
    """
    分析新闻情绪
    """
    positive_words = ['上涨', '涨', '利好', '增长', '突破', '创新高', '流入', '强劲', '亮眼']
    negative_words = ['下跌', '跌', '利空', '下降', '回调', '创新低', '流出', '疲软', '下滑']
    
    positive_count = 0
    negative_count = 0
    
    for news in news_list:
        text = news['title'] + ' ' + news['content']
        for word in positive_words:
            positive_count += text.count(word)
        for word in negative_words:
            negative_count += text.count(word)
    
    return positive_count, negative_count

def extract_keywords(news_list):
    """
    提取关键词
    """
    keywords = ['A股', '上证指数', '深证成指', '创业板', '科创板', '央行', '降准', 
                '科技股', '新能源', '外资', '北向资金', '政策', '涨停', '成交量']
    
    keyword_count = {}
    
    for news in news_list:
        text = news['title'] + ' ' + news['content']
        for keyword in keywords:
            count = text.count(keyword)
            if count > 0:
                if keyword in keyword_count:
                    keyword_count[keyword] += count
                else:
                    keyword_count[keyword] = count
    
    return keyword_count

def main():
    # 当前日期
    current_date = '2025-07-05'
    
    # 获取上一个交易日
    previous_trading_day = get_previous_trading_day(current_date)
    
    print("当前日期: {}".format(current_date))
    print("上一个交易日: {}".format(previous_trading_day))
    print("\n" + "="*60)
    print("A股市场新闻分析报告 - {}".format(previous_trading_day))
    print("="*60 + "\n")
    
    try:
        # 获取新闻数据（这里使用示例数据）
        news_list = get_sample_ashare_news()
        
        print("【主要新闻】\n")
        for i, news in enumerate(news_list, 1):
            print("{}. {}".format(i, news['title']))
            print("   来源: {} | 时间: {}".format(news['source'], news['time']))
            print("   内容: {}\n".format(news['content']))
        
        # 关键词分析
        keyword_count = extract_keywords(news_list)
        if keyword_count:
            print("\n" + "-"*40)
            print("【关键词统计】")
            print("-"*40)
            sorted_keywords = sorted(keyword_count.items(), key=lambda x: x[1], reverse=True)
            for keyword, count in sorted_keywords:
                print("- {}: {}次".format(keyword, count))
        
        # 情绪分析
        positive_count, negative_count = analyze_news_sentiment(news_list)
        
        print("\n" + "-"*40)
        print("【市场情绪分析】")
        print("-"*40)
        print("- 积极词汇出现: {}次".format(positive_count))
        print("- 消极词汇出现: {}次".format(negative_count))
        
        if positive_count > negative_count:
            sentiment = "偏积极 📈"
            sentiment_desc = "市场情绪较为乐观，多数新闻偏向正面"
        elif negative_count > positive_count:
            sentiment = "偏消极 📉"
            sentiment_desc = "市场情绪较为谨慎，存在一定担忧"
        else:
            sentiment = "中性 ➡️"
            sentiment_desc = "市场情绪相对平衡，观望情绪较浓"
        
        print("- 整体情绪倾向: {}".format(sentiment))
        print("- 情绪描述: {}".format(sentiment_desc))
        
        # 投资建议
        print("\n" + "-"*40)
        print("【投资参考建议】")
        print("-"*40)
        
        if positive_count > negative_count * 1.5:
            advice = "积极关注，可适当增加仓位"
        elif negative_count > positive_count * 1.5:
            advice = "谨慎观望，控制风险"
        else:
            advice = "保持现有仓位，密切关注市场变化"
        
        print("- 操作建议: {}".format(advice))
        print("- 风险提示: 以上分析仅供参考，投资需谨慎")
        
        print("\n" + "="*60)
        print("报告生成时间: {}".format(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        print("="*60)
        
    except Exception as e:
        print("获取新闻时发生错误: {}".format(str(e)))
        print("\n注意: 当前使用的是示例数据进行演示")
        print("实际使用时需要配置真实的新闻数据源")

if __name__ == "__main__":
    main()