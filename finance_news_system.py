"""
财经晨/晚间新闻投资分析系统
结合央视新闻、国内外事件，自动分析生成投资策略报告
"""
import requests
import json
import csv
import os
import re
import time
from datetime import datetime, timedelta
from collections import defaultdict

# ============== 配置 ==============
OUTPUT_DIR = r'D:\finance_reports'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
}

# ============== 新闻获取模块 ==============

class CCTVNewsFetcher:
    """央视新闻获取器"""

    def __init__(self):
        self.name = "央视新闻"

    def fetch_morning_news(self):
        """获取晨间新闻(朝闻天下等)"""
        # 模拟获取，实际需对接新闻API
        return []

    def fetch_evening_news(self):
        """获取晚间新闻(新闻联播等)"""
        return []


class EastMoneyNewsFetcher:
    """东方财富新闻爬虫"""

    def __init__(self):
        self.name = "东方财富"
        self.base_url = 'https://np-anotice-stock.eastmoney.com'

    def get_important_news(self, days=1):
        """获取重要新闻(近N天)"""
        news_list = []
        page = 1

        while len(news_list) < 100:
            try:
                url = 'https://np-anotice-stock.eastmoney.com/api/security/ann'
                params = {
                    'sr': -1,
                    'page': page,
                    'pageSize': 50,
                    'type': ['015001001', '015001002', '015001003'],
                    'code': '',
                    'org': '1',
                    'source': 'web'
                }
                resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
                data = resp.json()
                items = data.get('data', {}).get('list', [])

                if not items:
                    break

                news_list.extend(items)
                page += 1
                time.sleep(0.3)
            except Exception as e:
                print(f'获取失败: {e}')
                break

        return news_list

    def parse_news(self, item):
        return {
            'title': item.get('title', ''),
            'time': item.get('notice_date', ''),
            'source': '东方财富',
            'type': item.get('art_type', ''),
            'url': item.get('art_url', '')
        }


class CLSNewsFetcher:
    """财联社新闻爬虫"""

    def __init__(self):
        self.name = "财联社"
        self.api_url = 'https://www.cls.cn/api/sw'

    def get_telegraph(self, page=1):
        """获取财联社电报"""
        try:
            url = 'https://www.cls.cn/nodeapi/updateTelegraph'
            params = {
                'app': 'Cailianpress',
                'os': 'web',
                'sv': '8.4.1',
                'page': page,
                'rn': 20,
                'type': '1',  # 1-电报 2-快讯
                'hasFirstVipArticle': '0'
            }
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            return data.get('data', {}).get('roll_data', [])
        except Exception as e:
            print(f'财联社获取失败: {e}')
            return []


class SinaNewsFetcher:
    """新浪财经新闻"""

    def __init__(self):
        self.name = "新浪财经"

    def get_finance_headlines(self):
        """获取财经头条"""
        try:
            url = 'https://feed.mix.sina.com.cn/api/proxy/get'
            params = {
                'page': 1,
                'size': 30,
                'channel': 'finance',
                'id': 'finance'
            }
            resp = requests.get(url, params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            return data.get('result', {}).get('data', [])
        except Exception as e:
            print(f'新浪获取失败: {e}')
            return []

    def parse_news(self, item):
        return {
            'title': item.get('title', ''),
            'time': item.get('ctime', ''),
            'source': '新浪财经',
            'category': item.get('channelname', ''),
            'url': item.get('url', '')
        }


# ============== 事件分析模块 ==============

class EventClassifier:
    """事件分类器"""

    # 政策关键词
    POLICY_KEYWORDS = [
        '政策', '监管', '改革', '央行', '证监会', '银保监', '国务院',
        '财政部', '发改委', '商务部', '工信部', '出台', '发布', '实施',
        '通知', '意见', '方案', '规划', '纲要', '决定'
    ]

    # 行业关键词
    INDUSTRY_KEYWORDS = {
        '新能源': ['新能源', '锂电', '光伏', '风电', '储能', '电动车', '电池', '碳中和'],
        '半导体': ['半导体', '芯片', '集成电路', '光刻', '代工', '晶圆'],
        '医药': ['医药', '疫苗', '中药', '创新药', '医疗器械', '集采'],
        '消费': ['消费', '白酒', '食品', '家电', '汽车', '零售', '旅游'],
        '金融': ['银行', '保险', '券商', '信托', '基金', '理财'],
        '科技': ['科技', 'AI', '人工智能', '大数据', '云计算', '软件', '互联网'],
        '地产': ['地产', '房地产', '建筑', '建材', '物业'],
        '军工': ['军工', '国防', '航天', '航空', '船舶', '导弹']
    }

    # 市场情绪关键词
    SENTIMENT_KEYWORDS = {
        '利好': ['涨', '牛', '大涨', '突破', '创新高', '利好', '爆发', '涨停', '红', '反弹'],
        '利空': ['跌', '熊', '大跌', '破位', '新低', '利空', '暴雷', '跌停', '绿', '跳水']
    }

    def classify_event(self, title):
        """分类事件类型"""
        title = str(title)

        # 政策面
        if any(k in title for k in self.POLICY_KEYWORDS):
            return '政策'

        # 行业面
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(k in title for k in keywords):
                return industry

        return '综合'

    def analyze_sentiment(self, title):
        """分析情绪倾向"""
        title = str(title)

        pos_count = sum(1 for k in self.SENTIMENT_KEYWORDS['利好'] if k in title)
        neg_count = sum(1 for k in self.SENTIMENT_KEYWORDS['利空'] if k in title)

        if pos_count > neg_count:
            return '利好'
        elif neg_count > pos_count:
            return '利空'
        return '中性'

    def extract_stock_codes(self, text):
        """提取股票代码/名称"""
        codes = re.findall(r'(?:600|000|001|002|003|688|300)\d{4}', text)
        return list(set(codes))


class StrategyGenerator:
    """策略生成器"""

    # 策略信号定义
    SIGNALS = {
        '强烈买入': {'sentiment': '利好', 'policy_weight': 3, 'min_score': 8},
        '买入': {'sentiment': '利好', 'policy_weight': 2, 'min_score': 5},
        '观望': {'sentiment': '中性', 'policy_weight': 1, 'min_score': 0},
        '减持': {'sentiment': '利空', 'policy_weight': 2, 'min_score': 5},
        '强烈卖出': {'sentiment': '利空', 'policy_weight': 3, 'min_score': 8}
    }

    def calculate_score(self, item):
        """计算综合评分"""
        score = 0

        sentiment = item.get('sentiment', '中性')
        if sentiment == '利好':
            score += 3
        elif sentiment == '利空':
            score -= 3

        category = item.get('category', '综合')
        if category == '政策':
            score *= 1.5  # 政策加权

        return score

    def generate_signal(self, item):
        """生成交易信号"""
        score = self.calculate_score(item)

        if score >= 8:
            return '强烈买入', score
        elif score >= 5:
            return '买入', score
        elif score >= 0:
            return '观望', score
        elif score >= -5:
            return '减持', score
        else:
            return '强烈卖出', score

    def get_related_sectors(self, title):
        """获取相关板块"""
        sectors = []
        keywords_map = {
            '新能源': ['宁德时代', '比亚迪', '隆基绿能', '亿纬锂能'],
            '半导体': ['中芯国际', '韦尔股份', '北方华创', '长电科技'],
            '医药': ['恒瑞医药', '药明康德', '迈瑞医疗', '片仔癀'],
            '消费': ['贵州茅台', '五粮液', '美的集团', '海尔智家'],
            '金融': ['中国平安', '招商银行', '中信证券', '东方财富'],
            '科技': ['阿里', '腾讯', '百度', '字节跳动'],
        }

        for sector, stocks in keywords_map.items():
            if any(s in title for s in stocks):
                sectors.append(sector)

        return sectors if sectors else ['大盘']


# ============== 报告生成模块 ==============

class ReportGenerator:
    """报告生成器"""

    def __init__(self):
        self.classifier = EventClassifier()
        self.strategy_gen = StrategyGenerator()

    def generate_morning_report(self, news_items):
        """生成晨间报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        report = []
        report.append('# ' + '=' * 60)
        report.append('# 晨间投资参考')
        report.append(f'# 生成时间: {date} {datetime.now().strftime("%H:%M")}')
        report.append('# ' + '=' * 60)
        report.append('')

        # 今日要闻
        report.append('## 一、今日要闻速览')
        report.append('')
        for i, item in enumerate(news_items[:10], 1):
            sentiment_icon = '↑' if item.get('sentiment') == '利好' else ('↓' if item.get('sentiment') == '利空' else '→')
            report.append(f'{i}. [{sentiment_icon}] {item.get("title", "")}')
            report.append(f'   来源: {item.get("source", "")} | 时间: {item.get("time", "")}')
            report.append('')

        # 政策面分析
        policy_news = [n for n in news_items if self.classifier.classify_event(n.get('title', '')) == '政策']
        if policy_news:
            report.append('## 二、政策面解读')
            report.append('')
            for item in policy_news[:5]:
                report.append(f'- **{item.get("title", "")}**')
                report.append(f'  {item.get("source", "")} {item.get("time", "")}')
            report.append('')

        # 行业机会
        report.append('## 三、行业机会提示')
        report.append('')
        for category in ['新能源', '半导体', '医药', '消费', '科技']:
            cat_news = [n for n in news_items if self.classifier.classify_event(n.get('title', '')) == category]
            if cat_news:
                report.append(f'### {category}')
                for item in cat_news[:3]:
                    signal, score = self.strategy_gen.generate_signal(item)
                    report.append(f'- [{signal}] {item.get("title", "")}')
                report.append('')

        # 投资策略
        report.append('## 四、晨间投资策略')
        report.append('')
        bullish = [n for n in news_items if self.strategy_gen.generate_signal(n)[0] in ['强烈买入', '买入']]
        bearish = [n for n in news_items if self.strategy_gen.generate_signal(n)[0] in ['强烈卖出', '减持']]

        report.append(f'**多头信号**: {len(bullish)} 条')
        report.append(f'**空头信号**: {len(bearish)} 条')
        report.append('')

        if bullish:
            report.append('### 值得关注')
            for item in bullish[:5]:
                sectors = self.strategy_gen.get_related_sectors(item.get('title', ''))
                report.append(f'- {item.get("title", "")} [相关: {", ".join(sectors)}]')
            report.append('')

        if bearish:
            report.append('### 风险提示')
            for item in bearish[:5]:
                report.append(f'- ⚠️ {item.get("title", "")}')
            report.append('')

        # 风险提示
        report.append('## 五、综合风险提示')
        report.append('')
        report.append('1. 本报告仅供参考，不构成投资建议')
        report.append('2. 市场有风险，投资需谨慎')
        report.append('3. 建议仓位控制在50%-70%')
        report.append('')
        report.append('---')
        report.append(f'*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')

        return '\n'.join(report)

    def generate_evening_report(self, news_items, market_data=None):
        """生成晚间报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        report = []
        report.append('# ' + '=' * 60)
        report.append('# 晚间投资复盘')
        report.append(f'# 生成时间: {date} {datetime.now().strftime("%H:%M")}')
        report.append('# ' + '=' * 60)
        report.append('')

        # 今日复盘
        report.append('## 一、今日盘面回顾')
        report.append('')
        if market_data:
            for k, v in market_data.items():
                report.append(f'- {k}: {v}')
        else:
            report.append('今日市场整体震荡，板块分化明显')
        report.append('')

        # 重大事件回顾
        report.append('## 二、重大事件回顾')
        report.append('')
        for i, item in enumerate(news_items[:15], 1):
            sentiment = item.get('sentiment', '中性')
            icon = '↑' if sentiment == '利好' else ('↓' if sentiment == '利空' else '→')
            report.append(f'{i}. [{icon}] {item.get("title", "")}')
            report.append(f'   {item.get("source", "")} | {item.get("time", "")}')
            report.append('')

        # 政策解读
        policy_news = [n for n in news_items if self.classifier.classify_event(n.get('title', '')) == '政策']
        if policy_news:
            report.append('## 三、政策消息汇总')
            report.append('')
            for item in policy_news:
                report.append(f'- {item.get("title", "")}')
                report.append(f'  来源: {item.get("source", "")} {item.get("time", "")}')
            report.append('')

        # 明日展望
        report.append('## 四、明日市场展望')
        report.append('')

        positive_signals = [n for n in news_items if n.get('sentiment') == '利好']
        negative_signals = [n for n in news_items if n.get('sentiment') == '利空']

        report.append(f'**利好因素**: {len(positive_signals)} 条')
        for item in positive_signals[:5]:
            report.append(f'  + {item.get("title", "")}')

        report.append('')
        report.append(f'**利空因素**: {len(negative_signals)} 条')
        for item in negative_signals[:5]:
            report.append(f'  - {item.get("title", "")}')

        report.append('')
        report.append('### 操作建议')
        report.append('')

        # 生成策略
        buy_signals = [n for n in news_items if self.strategy_gen.generate_signal(n)[0] in ['强烈买入', '买入']]
        sell_signals = [n for n in news_items if self.strategy_gen.generate_signal(n)[0] in ['强烈卖出', '减持']]

        if buy_signals:
            report.append('**关注板块**:')
            for item in buy_signals[:5]:
                sectors = self.strategy_gen.get_related_sectors(item.get('title', ''))
                report.append(f'- {", ".join(sectors)}: {item.get("title", "")}')

        if sell_signals:
            report.append('')
            report.append('**规避板块**:')
            for item in sell_signals[:5]:
                report.append(f'- ⚠️ {item.get("title", "")}')

        report.append('')
        report.append('---')
        report.append('*本报告仅供投资参考，不构成投资建议*')
        report.append(f'*生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')

        return '\n'.join(report)

    def save_report(self, content, filename, report_type='morning'):
        """保存报告"""
        if report_type == 'morning':
            fullname = f'morning_report_{datetime.now().strftime("%Y%m%d")}.md'
        else:
            fullname = f'evening_report_{datetime.now().strftime("%Y%m%d")}.md'

        if filename:
            fullname = filename

        filepath = os.path.join(OUTPUT_DIR, fullname)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath


# ============== 主程序 ==============

class FinanceNewsSystem:
    """财经新闻投资分析系统"""

    def __init__(self):
        self.cctv = CCTVNewsFetcher()
        self.eastmoney = EastMoneyNewsFetcher()
        self.cls = CLSNewsFetcher()
        self.sina = SinaNewsFetcher()
        self.classifier = EventClassifier()
        self.strategy_gen = StrategyGenerator()
        self.report_gen = ReportGenerator()

    def fetch_all_news(self, days=1):
        """获取所有新闻源"""
        print('正在获取新闻...')
        all_news = []

        # 东方财富
        print('- 东方财富网...')
        try:
            em_news = self.eastmoney.get_important_news(days)
            for item in em_news:
                parsed = self.eastmoney.parse_news(item)
                parsed['category'] = self.classifier.classify_event(parsed['title'])
                parsed['sentiment'] = self.classifier.analyze_sentiment(parsed['title'])
                all_news.append(parsed)
        except Exception as e:
            print(f'  东方财富获取失败: {e}')

        # 财联社
        print('- 财联社...')
        try:
            cls_news = self.cls.get_telegraph()
            for item in cls_news:
                parsed = {
                    'title': item.get('roll_content', '')[:100],
                    'time': item.get('ctime', ''),
                    'source': '财联社',
                    'category': self.classifier.classify_event(item.get('roll_content', '')),
                    'sentiment': self.classifier.analyze_sentiment(item.get('roll_content', ''))
                }
                all_news.append(parsed)
        except Exception as e:
            print(f'  财联社获取失败: {e}')

        # 新浪财经
        print('- 新浪财经...')
        try:
            sina_news = self.sina.get_finance_headlines()
            for item in sina_news:
                parsed = self.sina.parse_news(item)
                parsed['category'] = self.classifier.classify_event(parsed['title'])
                parsed['sentiment'] = self.classifier.analyze_sentiment(parsed['title'])
                all_news.append(parsed)
        except Exception as e:
            print(f'  新浪财经获取失败: {e}')

        print(f'共获取 {len(all_news)} 条新闻')
        return all_news

    def run_morning(self):
        """运行晨间报告"""
        print('=' * 60)
        print('\t晨间投资参考生成')
        print('=' * 60)

        news = self.fetch_all_news(days=1)
        report = self.report_gen.generate_morning_report(news)

        filepath = self.report_gen.save_report(report, None, 'morning')
        print(f'\n晨间报告已生成: {filepath}')

        return report

    def run_evening(self):
        """运行晚间报告"""
        print('=' * 60)
        print('\t晚间投资复盘生成')
        print('=' * 60)

        news = self.fetch_all_news(days=1)
        report = self.report_gen.generate_evening_report(news)

        filepath = self.report_gen.save_report(report, None, 'evening')
        print(f'\n晚间报告已生成: {filepath}')

        return report


# ============== CLI ==============
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='财经新闻投资分析系统')
    parser.add_argument('--mode', choices=['morning', 'evening', 'both'], default='morning',
                        help='运行模式: morning(晨间)/evening(晚间)/both(全部)')
    parser.add_argument('--output', default='', help='输出文件路径')

    args = parser.parse_args()

    system = FinanceNewsSystem()

    if args.mode == 'morning':
        system.run_morning()
    elif args.mode == 'evening':
        system.run_evening()
    else:
        system.run_morning()
        print('\n')
        system.run_evening()