"""
行业投资分析系统 v2.0
基于产业链分析、财务报表、新闻舆情的智能选股系统
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
}

# ============== 行业分类与产业链 ==============

INDUSTRY_CHAINS = {
    '新能源车': {
        '上游': ['锂矿', '钴矿', '镍矿', '石墨', '电解液', '隔膜', '正极材料', '负极材料'],
        '中游': ['电池芯', '电池组', 'BMS', '热管理'],
        '下游': ['整车', '充电桩', '换电站', '储能'],
        '关键公司': {
            '上游': ['赣锋锂业', '天齐锂业', '华友钴业', '恩捷股份', '星源材质'],
            '中游': ['宁德时代', '比亚迪', '亿纬锂能', '国轩高科', '欣旺达'],
            '下游': ['特斯拉', '蔚来', '小鹏', '理想', '比亚迪']
        }
    },
    '半导体': {
        '上游': ['硅片', '光刻胶', '电子气体', '溅射靶材', 'CMP材料'],
        '中游': ['芯片设计', '晶圆制造', '封装测试', 'IP授权'],
        '下游': ['消费电子', '汽车电子', '工业控制', '物联网'],
        '关键公司': {
            '上游': ['沪硅产业', '中环股份', '雅克科技', '华特气体'],
            '中游': ['中芯国际', '华虹半导体', '长电科技', '通富微电', '华天科技'],
            '下游': ['华为', '苹果', '英伟达', 'AMD']
        }
    },
    '光伏': {
        '上游': ['多晶硅', '硅片', '银浆'],
        '中游': ['电池片', '组件', '逆变器', '支架'],
        '下游': ['光伏电站', '分布式', '储能'],
        '关键公司': {
            '上游': ['通威股份', '大全能源', '保利协鑫', '隆基绿能'],
            '中游': ['隆基绿能', '晶科能源', '天合光能', '晶澳科技', '阳光电源'],
            '下游': ['国电投', '三峡集团', '华能']
        }
    },
    '医药': {
        '上游': ['原料药', '中间体', '中药材'],
        '中游': ['化学药', '生物药', '中药', '医疗器械'],
        '下游': ['医院', '药店', '线上医疗'],
        '关键公司': {
            '上游': ['普洛药业', '九州药业', '新和成'],
            '中游': ['恒瑞医药', '药明康德', '迈瑞医疗', '片仔癀', '云南白药'],
            '下游': ['益丰药房', '大参林', '阿里健康']
        }
    },
    '消费电子': {
        '上游': ['芯片', '显示屏', '存储器', '摄像头', '电池'],
        '中游': ['手机', 'PC', '平板', '耳机', '手表'],
        '下游': ['运营商', '电商', '零售'],
        '关键公司': {
            '上游': ['京东方', 'TCL科技', '韦尔股份', '舜宇光学'],
            '中游': ['苹果', '三星', '华为', '小米', 'OPPO'],
            '下游': ['中国移动', '京东', '苏宁']
        }
    },
    '白酒': {
        '上游': ['高粱', '小麦', '包装', '基酒'],
        '中游': ['高端酒', '次高端', '中端', '低端'],
        '下游': ['经销商', '酒店', '电商', '超市'],
        '关键公司': {
            '上游': ['金种子', '舍得酒业'],
            '中游': ['贵州茅台', '五粮液', '泸州老窖', '洋河股份', '山西汾酒', '古井贡酒'],
            '下游': ['华致酒行', '酒仙网']
        }
    },
    '银行': {
        '上游': ['吸储', '同业拆借'],
        '中游': ['对公业务', '零售业务', '同业业务', '投行业务'],
        '下游': ['企业', '个人', '政府'],
        '关键公司': {
            '上游': [],
            '中游': ['工商银行', '建设银行', '农业银行', '中国银行', '招商银行', '兴业银行', '平安银行'],
            '下游': []
        }
    },
    '券商': {
        '上游': ['客户', '资金'],
        '中游': ['经纪业务', '投行业务', '资管业务', '自营业务', '两融业务'],
        '下游': ['企业', '个人', '机构'],
        '关键公司': {
            '上游': [],
            '中游': ['中信证券', '中信建投', '华泰证券', '国泰君安', '海通证券', '广发证券', '东方财富'],
            '下游': []
        }
    }
}

# ============== 新闻获取 ==============

class NewsFetcher:
    """新闻获取器"""

    def __init__(self):
        self.sources = {
            '东方财富': 'https://np-anotice-stock.eastmoney.com/api/security/ann',
            '财联社': 'https://www.cls.cn/nodeapi/updateTelegraph',
            '新浪': 'https://feed.mix.sina.com.cn/api/proxy/get'
        }

    def fetch_eastmoney(self, page=1, page_size=50):
        """获取东方财富新闻"""
        try:
            params = {
                'sr': -1, 'page': page, 'pageSize': page_size,
                'type': ['015001001', '015001002', '015001003'],
                'org': '1', 'source': 'web'
            }
            resp = requests.get(self.sources['东方财富'], params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            return data.get('data', {}).get('list', [])
        except Exception as e:
            print(f'东方财富获取失败: {e}')
            return []

    def fetch_cls_telegraph(self, page=1):
        """获取财联社电报"""
        try:
            params = {
                'app': 'Cailianpress', 'os': 'web', 'sv': '8.4.1',
                'page': page, 'rn': 20, 'type': '1', 'hasFirstVipArticle': '0'
            }
            resp = requests.get(self.sources['财联社'], params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            return data.get('data', {}).get('roll_data', [])
        except Exception as e:
            print(f'财联社获取失败: {e}')
            return []

    def fetch_sina_finance(self):
        """获取新浪财经"""
        try:
            params = {'page': 1, 'size': 30, 'channel': 'finance', 'id': 'finance'}
            resp = requests.get(self.sources['新浪'], params=params, headers=HEADERS, timeout=10)
            data = resp.json()
            return data.get('result', {}).get('data', [])
        except Exception as e:
            print(f'新浪获取失败: {e}')
            return []

    def fetch_all(self):
        """获取所有新闻"""
        all_news = []

        print('获取东方财富新闻...')
        for page in range(1, 4):
            items = self.fetch_eastmoney(page)
            for item in items:
                all_news.append({
                    'title': item.get('title', ''),
                    'time': item.get('notice_date', ''),
                    'source': '东方财富',
                    'type': '财经'
                })
            time.sleep(0.3)

        print('获取财联社电报...')
        for page in range(1, 4):
            items = self.fetch_cls_telegraph(page)
            for item in items:
                all_news.append({
                    'title': item.get('roll_content', '')[:100],
                    'time': item.get('ctime', ''),
                    'source': '财联社',
                    'type': '电报'
                })
            time.sleep(0.3)

        print('获取新浪财经...')
        items = self.fetch_sina_finance()
        for item in items:
            all_news.append({
                'title': item.get('title', ''),
                'time': item.get('ctime', ''),
                'source': '新浪财经',
                'type': item.get('channelname', '财经')
            })

        return all_news


# ============== 分析引擎 ==============

class IndustryAnalyzer:
    """行业分析器"""

    # 行业关键词映射
    INDUSTRY_KEYWORDS = {
        '新能源车': ['新能源', '电动车', '电动汽车', '锂电池', '动力电池', '充电桩', '锂', '电池'],
        '半导体': ['半导体', '芯片', '集成电路', '晶圆', '代工', '光刻', '封装', 'IDM'],
        '光伏': ['光伏', '太阳能', '硅片', '组件', '逆变器', '多晶硅', '单晶硅'],
        '医药': ['医药', '制药', '生物药', '中药', '医疗器械', '疫苗', '创新药', '集采'],
        '消费电子': ['消费电子', '手机', '面板', '显示屏', '摄像头', '存储器', '苹果', '华为'],
        '白酒': ['白酒', '茅台', '五粮液', '泸州老窖', '洋河', '汾酒', '酒'],
        '银行': ['银行', '信贷', '存款', '降准', 'LPR', '息差'],
        '券商': ['券商', '证券', '经纪', '投行', '两融', '资管', '自营']
    }

    def classify_industry(self, title):
        """识别新闻关联行业"""
        title = str(title)
        matched = []

        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            if any(k in title for k in keywords):
                matched.append(industry)

        return matched if matched else ['综合']

    def analyze_news_sentiment(self, title):
        """分析新闻情绪"""
        title = str(title)

        positive = ['涨', '牛', '大涨', '突破', '创新高', '利好', '爆发', '涨停', '红', '反弹',
                    '扩张', '增长', '景气', '看好', '增持', '买入', '业绩', '超预期']
        negative = ['跌', '熊', '大跌', '破位', '新低', '利空', '暴雷', '跌停', '绿', '跳水',
                    '萎缩', '下滑', '亏损', '减持', '卖出', '风险', '警示', '问题']

        pos_score = sum(1 for w in positive if w in title)
        neg_score = sum(1 for w in negative if w in title)

        if pos_score > neg_score:
            return '利好'
        elif neg_score > pos_score:
            return '利空'
        return '中性'


class FinancialAnalyzer:
    """财务分析器"""

    def __init__(self):
        self.mock_data = self._load_mock_financial_data()

    def _load_mock_financial_data(self):
        """模拟财务数据(实际应从东方财富/同花顺API获取)"""
        return {
            '宁德时代': {'pe': 25, 'pb': 5, 'roe': 18, 'revenue_growth': 85, 'profit_growth': 75, 'score': 85},
            '比亚迪': {'pe': 45, 'pb': 6, 'roe': 15, 'revenue_growth': 65, 'profit_growth': 55, 'score': 78},
            '隆基绿能': {'pe': 20, 'pb': 4, 'roe': 22, 'revenue_growth': 55, 'profit_growth': 45, 'score': 80},
            '贵州茅台': {'pe': 35, 'pb': 12, 'roe': 30, 'revenue_growth': 18, 'profit_growth': 20, 'score': 88},
            '五粮液': {'pe': 28, 'pb': 7, 'roe': 25, 'revenue_growth': 15, 'profit_growth': 18, 'score': 82},
            '恒瑞医药': {'pe': 60, 'pb': 8, 'roe': 20, 'revenue_growth': 10, 'profit_growth': 5, 'score': 65},
            '药明康德': {'pe': 40, 'pb': 6, 'roe': 18, 'revenue_growth': 35, 'profit_growth': 30, 'score': 75},
            '中芯国际': {'pe': 50, 'pb': 3, 'roe': 8, 'revenue_growth': 30, 'profit_growth': 15, 'score': 60},
            '东方财富': {'pe': 55, 'pb': 5, 'roe': 16, 'revenue_growth': 25, 'profit_growth': 20, 'score': 72},
            '招商银行': {'pe': 8, 'pb': 1.2, 'roe': 16, 'revenue_growth': 10, 'profit_growth': 12, 'score': 80},
            '中国平安': {'pe': 10, 'pb': 1.5, 'roe': 14, 'revenue_growth': 5, 'profit_growth': 3, 'score': 68}
        }

    def get_financial_score(self, stock_name):
        """获取财务评分"""
        return self.mock_data.get(stock_name, {'score': 50})

    def analyze_valuation(self, stock_name):
        """估值分析"""
        data = self.get_financial_score(stock_name)
        pe = data.get('pe', 50)

        if pe < 15:
            return '低估'
        elif pe < 30:
            return '合理'
        elif pe < 50:
            return '偏高'
        return '高估'


class StockPicker:
    """智能选股器"""

    def __init__(self):
        self.industry_analyzer = IndustryAnalyzer()
        self.financial_analyzer = FinancialAnalyzer()

    def calculate_comprehensive_score(self, news_sentiment, industry_match, financial_score):
        """综合评分"""
        score = 0

        # 情绪权重 30%
        if news_sentiment == '利好':
            score += 30
        elif news_sentiment == '利空':
            score -= 20

        # 行业匹配权重 30%
        if industry_match:
            score += 30

        # 财务评分权重 40%
        score += financial_score * 0.4

        return min(100, max(0, score))

    def pick_stocks(self, news_list, top_n=10):
        """精选股票"""
        stock_scores = defaultdict(lambda: {'news_score': 0, 'news_count': 0, 'industries': set(), 'news_details': []})

        # 按行业归类新闻
        for news in news_list:
            sentiment = self.industry_analyzer.analyze_news_sentiment(news.get('title', ''))
            industries = self.industry_analyzer.classify_industry(news.get('title', ''))

            for industry in industries:
                for stock in INDUSTRY_CHAINS.get(industry, {}).get('关键公司', {}).get('中游', []):
                    if sentiment == '利好':
                        stock_scores[stock]['news_score'] += 10
                    elif sentiment == '利空':
                        stock_scores[stock]['news_score'] -= 5

                    stock_scores[stock]['news_count'] += 1
                    stock_scores[stock]['industries'].add(industry)
                    stock_scores[stock]['news_details'].append({
                        'title': news.get('title', ''),
                        'sentiment': sentiment,
                        'industry': industry
                    })

        # 计算综合评分
        results = []
        for stock, data in stock_scores.items():
            fin_data = self.financial_analyzer.get_financial_score(stock)
            fin_score = fin_data.get('score', 50)

            total_score = self.calculate_comprehensive_score(
                '利好' if data['news_score'] > 0 else ('利空' if data['news_score'] < 0 else '中性'),
                len(data['industries']) > 0,
                fin_score
            )

            results.append({
                'stock': stock,
                'total_score': total_score,
                'news_score': data['news_score'],
                'news_count': data['news_count'],
                'industries': list(data['industries']),
                'news_details': data['news_details'][:3],
                'financial': fin_data,
                'valuation': self.financial_analyzer.analyze_valuation(stock)
            })

        # 排序
        results.sort(key=lambda x: x['total_score'], reverse=True)
        return results[:top_n]


# ============== 报告生成 ==============

class ReportGenerator:
    """报告生成器"""

    def generate_industry_report(self, news_list, stock_picks):
        """生成行业分析报告"""
        date = datetime.now().strftime('%Y-%m-%d')
        report = []

        report.append('# ' + '=' * 70)
        report.append('# 行业投资分析报告')
        report.append(f'# 生成时间: {date} {datetime.now().strftime("%H:%M")}')
        report.append('# ' + '=' * 70)
        report.append('')

        # 一、宏观与政策面
        report.append('## 一、宏观与政策面分析')
        report.append('')
        policy_news = [n for n in news_list if any(k in str(n.get('title', ''))
                    for k in ['政策', '央行', '证监会', '国务院', '财政部', '发改委'])]
        if policy_news:
            report.append('### 政策动态')
            for item in policy_news[:8]:
                report.append(f'- {item.get("title", "")}')
                report.append(f'  来源: {item.get("source", "")} | 时间: {item.get("time", "")}')
            report.append('')
        else:
            report.append('今日无重大政策发布，市场平稳运行。')
            report.append('')

        # 二、行业动态
        report.append('## 二、各行业动态追踪')
        report.append('')

        industries = ['新能源车', '半导体', '光伏', '医药', '消费电子', '白酒', '银行', '券商']

        for industry in industries:
            chain = INDUSTRY_CHAINS.get(industry, {})
            report.append(f'### {industry}')
            report.append('')
            report.append(f'**产业链结构**: 上游({", ".join(chain.get("上游", [])[:5])}) → '
                         f'中游({", ".join(chain.get("中游", [])[:5])}) → '
                         f'下游({", ".join(chain.get("下游", [])[:3])})')
            report.append('')

            # 上中下游代表性公司
            report.append('**代表性公司**:')
            all_companies = []
            for stage in ['上游', '中游', '下游']:
                companies = chain.get('关键公司', {}).get(stage, [])
                all_companies.extend(companies)

            if all_companies:
                report.append(', '.join(all_companies[:8]))
            report.append('')

            # 今日相关新闻
            industry_news = [n for n in news_list
                           if any(k in str(n.get('title', ''))
                                 for k in IndustryAnalyzer.INDUSTRY_KEYWORDS.get(industry, []))]

            if industry_news:
                report.append('**今日新闻**:')
                for item in industry_news[:5]:
                    sentiment = IndustryAnalyzer().analyze_news_sentiment(item.get('title', ''))
                    icon = '↑' if sentiment == '利好' else ('↓' if sentiment == '利空' else '→')
                    report.append(f'- [{icon}] {item.get("title", "")}')
                report.append('')
            report.append('')

        # 三、财务分析
        report.append('## 三、重点公司财务分析')
        report.append('')
        report.append('| 股票 | 行业 | 估值 | PE | PB | ROE | 营收增长 | 利润增长 | 综合评分 |')
        report.append('|------|------|------|----|----|----|---------|---------|---------|')

        for stock in stock_picks[:10]:
            fin = stock.get('financial', {})
            industries_str = ', '.join(stock.get('industries', [])[:2])
            report.append(f"| {stock['stock']} | {industries_str} | {stock['valuation']} | "
                         f"{fin.get('pe', '-')} | {fin.get('pb', '-')} | {fin.get('roe', '-')}% | "
                         f"{fin.get('revenue_growth', '-')}% | {fin.get('profit_growth', '-')}% | "
                         f"**{stock['total_score']:.0f}** |")

        report.append('')

        # 四、智能选股
        report.append('## 四、智能选股推荐')
        report.append('')

        for i, stock in enumerate(stock_picks[:10], 1):
            fin = stock.get('financial', {})
            report.append(f'### {i}. {stock["stock"]}')
            report.append('')
            report.append(f'- **综合评分**: {stock["total_score"]:.0f}/100')
            report.append(f'- **估值**: {stock["valuation"]}')
            report.append(f'- **行业**: {", ".join(stock.get("industries", []))}')
            report.append(f'- **PE**: {fin.get("pe", "-")} | **PB**: {fin.get("pb", "-")} | **ROE**: {fin.get("roe", "-")}%')
            report.append(f'- **营收增长**: {fin.get("revenue_growth", "-")}% | **利润增长**: {fin.get("profit_growth", "-")}%')
            report.append('')
            report.append('**相关新闻**:')
            for news in stock.get('news_details', []):
                icon = '↑' if news['sentiment'] == '利好' else ('↓' if news['sentiment'] == '利空' else '→')
                report.append(f'- [{icon}] {news["title"]}')
            report.append('')

        # 五、投资策略
        report.append('## 五、投资策略建议')
        report.append('')

        top_buy = stock_picks[:3]
        if top_buy:
            report.append('### 重点关注')
            for stock in top_buy:
                report.append(f'- **{stock["stock"]}** ({stock["valuation"]})')
                report.append(f'  理由: 行业景气度高，财务数据优良，近期利好频发')
            report.append('')

        report.append('### 仓位建议')
        report.append('')
        report.append('| 市场环境 | 仓位建议 | 操作策略 |')
        report.append('|----------|----------|----------|')
        report.append('| 强势 | 70%-80% | 积极布局，持有为主 |')
        report.append('| 中性 | 50%-60% | 精选个股，高抛低吸 |')
        report.append('| 弱势 | 30%-40% | 防守为主，控制风险 |')
        report.append('')

        # 六、风险提示
        report.append('## 六、风险提示')
        report.append('')
        report.append('1. 本报告仅供参考，不构成投资建议')
        report.append('2. 市场有风险，投资需谨慎')
        report.append('3. 建议分散投资，单一行业仓位不超过30%')
        report.append('4. 注意控制杠杆，警惕系统性风险')
        report.append('')
        report.append('---')
        report.append(f'*报告生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')
        report.append(f'*数据来源: 东方财富、财联社、新浪财经*')

        return '\n'.join(report)

    def save_report(self, content, filename='industry_report.md'):
        """保存报告"""
        filepath = os.path.join(OUTPUT_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'报告已保存: {filepath}')
        return filepath


# ============== 主程序 ==============

class IndustryAnalysisSystem:
    """行业投资分析系统"""

    def __init__(self):
        self.news_fetcher = NewsFetcher()
        self.industry_analyzer = IndustryAnalyzer()
        self.stock_picker = StockPicker()
        self.report_gen = ReportGenerator()

    def run(self):
        """运行系统"""
        print('=' * 60)
        print('\t行业投资分析系统 v2.0')
        print('=' * 60)
        print()

        # 获取新闻
        print('正在获取新闻...')
        news = self.news_fetcher.fetch_all()
        print(f'共获取 {len(news)} 条新闻')
        print()

        # 选股
        print('正在分析行业与选股...')
        stock_picks = self.stock_picker.pick_stocks(news)
        print(f'精选出 {len(stock_picks)} 只股票')
        print()

        # 生成报告
        print('正在生成报告...')
        report = self.report_gen.generate_industry_report(news, stock_picks)
        filepath = self.report_gen.save_report(report)
        print()

        # 打印推荐
        print('=' * 60)
        print('\t精选股票TOP10')
        print('=' * 60)
        print()

        for i, stock in enumerate(stock_picks[:10], 1):
            fin = stock.get('financial', {})
            print(f'{i:2d}. {stock["stock"]:<10} 评分: {stock["total_score"]:>5.0f}  '
                  f'估值: {stock["valuation"]:<4} PE: {fin.get("pe", "-"):>4} '
                  f'ROE: {fin.get("roe", "-"):>3}% '
                  f'行业: {", ".join(stock.get("industries", [])[:2])}')

        print()
        print(f'详细报告: {filepath}')

        return report


# ============== CLI ==============
if __name__ == '__main__':
    system = IndustryAnalysisSystem()
    system.run()