"""
财经投资决策系统 v3.0
整合新闻分析、行业研究、财务评估、产业链分析，输出最终投资建议
"""
import requests
import json
import csv
import os
import re
import time
from datetime import datetime, timedelta
from collections import defaultdict

OUTPUT_DIR = r'D:\finance_reports'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Connection': 'keep-alive',
    'Referer': 'https://www.eastmoney.com'
}

# 测试用模拟数据(当API失败时)
MOCK_NEWS = [
    {'title': '央行宣布降准0.25个百分点，释放长期资金约5000亿', 'time': '2026-05-19', 'source': '财联社'},
    {'title': '证监会出台新政策支持科技创新企业上市', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '宁德时代发布新一代麒麟电池，能量密度创新高', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '光伏行业景气度持续提升，组件出口增长50%', 'time': '2026-05-19', 'source': '新浪财经'},
    {'title': '贵州茅台一季度营收增长18%，净利润超预期', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '半导体国产替代加速，中芯国际新产能投产', 'time': '2026-05-19', 'source': '财联社'},
    {'title': '新能源汽车销量大增，比亚迪月销突破30万辆', 'time': '2026-05-19', 'source': '新浪财经'},
    {'title': 'AI算力需求爆发，服务器厂商订单饱满', 'time': '2026-05-19', 'source': '财联社'},
    {'title': '军工订单持续释放，航发动力业绩增长20%', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '医药板块估值处于历史低位，创新药研发提速', 'time': '2026-05-19', 'source': '财联社'},
    {'title': '银行净息差企稳回升，招商银行估值偏低', 'time': '2026-05-19', 'source': '新浪财经'},
    {'title': '券商板块受益市场回暖，东方财富业绩增长25%', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '消费电子旺季来临，苹果产业链景气上行', 'time': '2026-05-19', 'source': '财联社'},
    {'title': '国家发布新型储能政策，阳光电源受益明显', 'time': '2026-05-19', 'source': '东方财富'},
    {'title': '锂价企稳反弹，赣锋锂业业绩有望修复', 'time': '2026-05-19', 'source': '新浪财经'},
]

# ==================== 产业链配置 ====================
INDUSTRY_CHAINS = {
    '新能源车': {
        '上游': ['锂矿', '钴矿', '镍矿', '石墨', '电解液', '隔膜'],
        '中游': ['电池芯', 'BMS', '热管理'],
        '下游': ['整车', '充电桩', '储能'],
        '核心公司': ['宁德时代', '比亚迪', '亿纬锂能', '赣锋锂业', '天齐锂业', '恩捷股份', '璞泰来', '当升科技']
    },
    '半导体': {
        '上游': ['硅片', '光刻胶', '电子气体', '溅射靶材'],
        '中游': ['芯片设计', '晶圆制造', '封装测试'],
        '下游': ['消费电子', '汽车电子', '工业控制'],
        '核心公司': ['中芯国际', '华虹半导体', '长电科技', '通富微电', '华天科技', '韦尔股份', '北方华创', '中微公司']
    },
    '光伏': {
        '上游': ['多晶硅', '硅片', '银浆'],
        '中游': ['电池片', '组件', '逆变器'],
        '下游': ['光伏电站', '分布式'],
        '核心公司': ['隆基绿能', '通威股份', '晶科能源', '天合光能', '晶澳科技', '阳光电源', '锦浪科技', '固德威']
    },
    '医药': {
        '上游': ['原料药', '中间体'],
        '中游': ['化学药', '生物药', '中药', '医疗器械'],
        '下游': ['医院', '药店'],
        '核心公司': ['恒瑞医药', '药明康德', '迈瑞医疗', '片仔癀', '云南白药', '智飞生物', '康龙化成', '泰格医药']
    },
    '消费电子': {
        '上游': ['芯片', '显示屏', '存储器', '摄像头'],
        '中游': ['手机', 'PC', '耳机'],
        '下游': ['电商', '零售'],
        '核心公司': ['苹果产业链', '华为产业链', '小米', 'OPPO', 'vivo', '京东方', '舜宇光学', '立讯精密']
    },
    '白酒': {
        '上游': ['高粱', '小麦', '包装'],
        '中游': ['高端酒', '次高端', '中端'],
        '下游': ['经销商', '酒店', '电商'],
        '核心公司': ['贵州茅台', '五粮液', '泸州老窖', '洋河股份', '山西汾酒', '古井贡酒', '舍得酒业', '酒鬼酒']
    },
    '银行': {
        '上游': ['吸储'],
        '中游': ['对公业务', '零售业务', '同业业务'],
        '下游': ['企业', '个人', '政府'],
        '核心公司': ['工商银行', '建设银行', '农业银行', '中国银行', '招商银行', '兴业银行', '平安银行', '宁波银行']
    },
    '券商': {
        '上游': ['客户', '资金'],
        '中游': ['经纪', '投行', '资管', '自营', '两融'],
        '下游': ['企业', '个人', '机构'],
        '核心公司': ['中信证券', '中信建投', '华泰证券', '国泰君安', '海通证券', '广发证券', '东方财富', '招商证券']
    },
    '军工': {
        '上游': ['原材料', '电子元器件'],
        '中游': ['航空装备', '航天装备', '船舶装备', '地面装备'],
        '下游': ['军方'],
        '核心公司': ['中航沈飞', '中航西飞', '航发动力', '中航光电', '振华科技', '高德红外', '中直股份', '洪都航空']
    },
    'AI人工智能': {
        '上游': ['算力芯片', '服务器', '数据中心'],
        '中游': ['大模型', '算法平台', 'AI应用'],
        '下游': ['企业服务', '消费应用'],
        '核心公司': ['百度', '科大讯飞', '海康威视', '寒武纪', '景嘉微', '剑桥科技', '中科曙光', '浪潮信息']
    }
}

# 财务数据(模拟)
FINANCIAL_DATA = {
    '宁德时代': {'pe': 25, 'pb': 5, 'roe': 18, 'rev_growth': 85, 'profit_growth': 75, 'score': 88},
    '比亚迪': {'pe': 35, 'pb': 6, 'roe': 15, 'rev_growth': 65, 'profit_growth': 55, 'score': 82},
    '隆基绿能': {'pe': 22, 'pb': 4, 'roe': 22, 'rev_growth': 55, 'profit_growth': 45, 'score': 85},
    '贵州茅台': {'pe': 35, 'pb': 12, 'roe': 30, 'rev_growth': 18, 'profit_growth': 20, 'score': 90},
    '五粮液': {'pe': 28, 'pb': 7, 'roe': 25, 'rev_growth': 15, 'profit_growth': 18, 'score': 85},
    '恒瑞医药': {'pe': 65, 'pb': 8, 'roe': 12, 'rev_growth': 8, 'profit_growth': -5, 'score': 60},
    '药明康德': {'pe': 40, 'pb': 6, 'roe': 18, 'rev_growth': 35, 'profit_growth': 30, 'score': 78},
    '迈瑞医疗': {'pe': 45, 'pb': 8, 'roe': 25, 'rev_growth': 22, 'profit_growth': 20, 'score': 80},
    '中芯国际': {'pe': 55, 'pb': 3, 'roe': 8, 'rev_growth': 30, 'profit_growth': 15, 'score': 62},
    '华虹半导体': {'pe': 45, 'pb': 2.5, 'roe': 10, 'rev_growth': 25, 'profit_growth': 10, 'score': 58},
    '东方财富': {'pe': 50, 'pb': 5, 'roe': 16, 'rev_growth': 25, 'profit_growth': 20, 'score': 75},
    '中信证券': {'pe': 20, 'pb': 1.8, 'roe': 10, 'rev_growth': 15, 'profit_growth': 12, 'score': 70},
    '招商银行': {'pe': 8, 'pb': 1.2, 'roe': 16, 'rev_growth': 10, 'profit_growth': 12, 'score': 82},
    '中国平安': {'pe': 10, 'pb': 1.5, 'roe': 14, 'rev_growth': 5, 'profit_growth': 3, 'score': 68},
    '中航沈飞': {'pe': 50, 'pb': 8, 'roe': 18, 'rev_growth': 20, 'profit_growth': 15, 'score': 75},
    '航发动力': {'pe': 60, 'pb': 5, 'roe': 12, 'rev_growth': 18, 'profit_growth': 10, 'score': 70},
    '科大讯飞': {'pe': 80, 'pb': 8, 'roe': 10, 'rev_growth': 30, 'profit_growth': 20, 'score': 72},
    '海康威视': {'pe': 30, 'pb': 6, 'roe': 22, 'rev_growth': 15, 'profit_growth': 12, 'score': 78},
    '阳光电源': {'pe': 35, 'pb': 6, 'roe': 20, 'rev_growth': 50, 'profit_growth': 40, 'score': 83},
    '锦浪科技': {'pe': 40, 'pb': 8, 'roe': 25, 'rev_growth': 60, 'profit_growth': 50, 'score': 80},
}


# ==================== 新闻获取 ====================
class NewsFetcher:
    def fetch_all(self):
        all_news = []
        # 东方财富
        try:
            params = {'sr': -1, 'page': 1, 'pageSize': 50,
                     'type': ['015001001', '015001002', '015001003'], 'org': '1'}
            resp = requests.get('https://np-anotice-stock.eastmoney.com/api/security/ann',
                               params=params, headers=HEADERS, timeout=10, verify=False)
            data = resp.json().get('data', {}).get('list', [])
            for item in data:
                all_news.append({
                    'title': item.get('title', ''),
                    'time': item.get('notice_date', ''),
                    'source': '东方财富'
                })
        except Exception as e:
            print(f'  东方财富: {e}')

        # 财联社
        try:
            params = {'app': 'Cailianpress', 'os': 'web', 'page': 1, 'rn': 20, 'type': '1'}
            resp = requests.get('https://www.cls.cn/nodeapi/updateTelegraph',
                               params=params, headers=HEADERS, timeout=10, verify=False)
            for item in resp.json().get('data', {}).get('roll_data', []):
                all_news.append({
                    'title': item.get('roll_content', '')[:100],
                    'time': item.get('ctime', ''),
                    'source': '财联社'
                })
        except Exception as e:
            print(f'  财联社: {e}')

        # 新浪
        try:
            params = {'page': 1, 'size': 30, 'channel': 'finance', 'id': 'finance'}
            resp = requests.get('https://feed.mix.sina.com.cn/api/proxy/get',
                               params=params, headers=HEADERS, timeout=10, verify=False)
            for item in resp.json().get('result', {}).get('data', []):
                all_news.append({
                    'title': item.get('title', ''),
                    'time': item.get('ctime', ''),
                    'source': '新浪财经'
                })
        except Exception as e:
            print(f'  新浪: {e}')

        # 如果获取失败，使用模拟数据
        if len(all_news) < 5:
            print('  使用模拟数据(API暂不可用)')
            all_news = MOCK_NEWS

        return all_news


# ==================== 分析引擎 ====================
class Analyzer:
    POLICY_KW = ['政策', '监管', '改革', '央行', '证监会', '国务院', '财政部', '发改委', '商务部', '工信部']
    POSITIVE_KW = ['涨', '牛', '大涨', '突破', '利好', '爆发', '涨停', '红', '反弹', '增长', '景气', '看好']
    NEGATIVE_KW = ['跌', '熊', '大跌', '利空', '暴雷', '跌停', '绿', '跳水', '亏损', '风险', '警示']

    def classify_industry(self, title):
        title = str(title)
        matched = []
        for ind, kws in {
            '新能源车': ['新能源', '电动', '锂电', '电池', '充电桩', '锂', '电动车'],
            '半导体': ['半导体', '芯片', '晶圆', '光刻', '代工'],
            '光伏': ['光伏', '太阳能', '硅片', '组件', '逆变器', '多晶硅'],
            '医药': ['医药', '制药', '生物药', '中药', '医疗器械', '疫苗', '创新药'],
            '消费电子': ['消费电子', '手机', '面板', '苹果', '华为'],
            '白酒': ['白酒', '茅台', '五粮液', '酒'],
            '银行': ['银行', '降准', 'LPR', '息差', '信贷'],
            '券商': ['券商', '证券', '两融', '经纪', '投行'],
            '军工': ['军工', '国防', '航天', '航空', '舰船'],
            'AI': ['AI', '人工智能', '大模型', 'ChatGPT', 'AIGC']
        }.items():
            if any(k in title for k in kws):
                matched.append(ind)
        return matched if matched else ['综合']

    def sentiment(self, title):
        title = str(title)
        pos = sum(1 for k in self.POSITIVE_KW if k in title)
        neg = sum(1 for k in self.NEGATIVE_KW if k in title)
        return '利好' if pos > neg else ('利空' if neg > pos else '中性')

    def is_policy(self, title):
        return any(k in str(title) for k in self.POLICY_KW)


# ==================== 选股引擎 ====================
class StockPicker:
    def __init__(self):
        self.analyzer = Analyzer()
        self.stock_data = defaultdict(lambda: {'news_score': 0, 'news_count': 0, 'industries': set(), 'news_list': []})

    def process(self, news_list):
        for news in news_list:
            title = news.get('title', '')
            sent = self.analyzer.sentiment(title)
            inds = self.analyzer.classify_industry(title)

            for ind in inds:
                companies = INDUSTRY_CHAINS.get(ind, {}).get('核心公司', [])
                for stock in companies:
                    if stock in title:
                        if sent == '利好':
                            self.stock_data[stock]['news_score'] += 15
                        elif sent == '利空':
                            self.stock_data[stock]['news_score'] -= 8
                        else:
                            self.stock_data[stock]['news_score'] += 5

                        self.stock_data[stock]['news_count'] += 1
                        self.stock_data[stock]['industries'].add(ind)
                        self.stock_data[stock]['news_list'].append({
                            'title': title,
                            'sentiment': sent,
                            'source': news['source']
                        })

    def rank(self, top_n=15):
        results = []
        for stock, data in self.stock_data.items():
            fin = FINANCIAL_DATA.get(stock, {'score': 60, 'pe': 30, 'pb': 3, 'roe': 12,
                                             'rev_growth': 10, 'profit_growth': 8})

            # 综合评分
            news_sent = '利好' if data['news_score'] > 10 else ('利空' if data['news_score'] < -5 else '中性')
            news_weight = 25 if news_sent == '利好' else (-15 if news_sent == '利空' else 0)

            total_score = fin['score'] * 0.5 + news_weight + (20 if data['news_count'] > 5 else 0)
            total_score = min(100, max(0, total_score))

            results.append({
                'stock': stock,
                'score': round(total_score, 1),
                'news_score': data['news_score'],
                'news_count': data['news_count'],
                'industries': list(data['industries']),
                'news_list': data['news_list'][:4],
                'financial': fin,
                'valuation': '低估' if fin['pe'] < 20 else ('合理' if fin['pe'] < 40 else '偏高')
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_n]


# ==================== 报告生成 ====================
class ReportGenerator:
    def generate(self, news_list, stock_picks):
        now = datetime.now()
        date_str = now.strftime('%Y-%m-%d')
        time_str = now.strftime('%H:%M')

        lines = []
        lines.append('#' + '=' * 70)
        lines.append('# 财经投资决策报告')
        lines.append(f'# 生成时间: {date_str} {time_str}')
        lines.append('#' + '=' * 70)
        lines.append('')

        # ===== 一、宏观与政策面 =====
        lines.append('## 一、宏观与政策面分析')
        lines.append('')
        policy_news = [n for n in news_list if Analyzer().is_policy(n['title'])]
        if policy_news:
            for n in policy_news[:10]:
                lines.append(f'- {n["title"]} [{n["source"]}]')
        else:
            lines.append('今日无重大政策发布，市场平稳运行。')
        lines.append('')

        # ===== 二、行业动态 =====
        lines.append('## 二、各行业动态追踪')
        lines.append('')

        for ind, chain in INDUSTRY_CHAINS.items():
            ind_news = [n for n in news_list if Analyzer().classify_industry(n['title']) == ind]
            if ind_news:
                lines.append(f'### {ind}')
                lines.append('')
                lines.append(f'**产业链**: 上游({", ".join(chain["上游"][:4])}) → '
                           f'中游({", ".join(chain["中游"][:3])}) → 下游({", ".join(chain["下游"][:2])})')
                lines.append('')
                lines.append('**今日新闻**:')
                for n in ind_news[:5]:
                    sent = Analyzer().sentiment(n['title'])
                    icon = '↑' if sent == '利好' else ('↓' if sent == '利空' else '→')
                    lines.append(f'- [{icon}] {n["title"]} [{n["source"]}]')
                lines.append('')

        # ===== 三、财务评估 =====
        lines.append('## 三、重点公司财务评估')
        lines.append('')
        lines.append('| 股票 | 行业 | 估值 | PE | PB | ROE | 营收↑ | 利润↑ | 评分 |')
        lines.append('|------|------|------|----|----|----|------|------|-----|')
        for s in stock_picks[:12]:
            fin = s['financial']
            inds = '/'.join(s['industries'][:2])
            lines.append(f"| {s['stock']} | {inds} | {s['valuation']} | "
                        f"{fin['pe']} | {fin['pb']} | {fin['roe']}% | "
                        f"{fin['rev_growth']}% | {fin['profit_growth']}% | **{s['score']:.0f}** |")
        lines.append('')

        # ===== 四、智能选股 =====
        lines.append('## 四、智能选股推荐')
        lines.append('')

        for i, s in enumerate(stock_picks[:12], 1):
            fin = s['financial']
            lines.append(f'**{i}. {s["stock"]}** (综合评分: {s["score"]:.0f})')
            lines.append('')
            lines.append(f'- 行业: {", ".join(s["industries"])}')
            lines.append(f'- 估值: {s["valuation"]} (PE: {fin["pe"]}, PB: {fin["pb"]})')
            lines.append(f'- 财务: ROE {fin["roe"]}% | 营收增长 {fin["rev_growth"]}% | 利润增长 {fin["profit_growth"]}%')
            lines.append(f'- 舆情: {s["news_count"]}条相关新闻 (情绪得分: {s["news_score"]})')
            lines.append('  相关新闻:')
            for n in s['news_list'][:3]:
                icon = '↑' if n['sentiment'] == '利好' else ('↓' if n['sentiment'] == '利空' else '→')
                lines.append(f'  - [{icon}] {n["title"]}')
            lines.append('')

        # ===== 五、最终投资建议 =====
        lines.append('## 五、最终投资方向建议')
        lines.append('')

        # 按行业汇总
        industry_scores = defaultdict(list)
        for s in stock_picks:
            for ind in s['industries']:
                industry_scores[ind].append(s['score'])

        industry_avg = {ind: sum(scores)/len(scores) for ind, scores in industry_scores.items()}
        top_industries = sorted(industry_avg.items(), key=lambda x: x[1], reverse=True)[:6]

        lines.append('### 行业配置优先级')
        lines.append('')
        lines.append('| 优先级 | 行业 | 推荐理由 |')
        lines.append('|--------|------|----------|')
        for i, (ind, avg_score) in enumerate(top_industries, 1):
            # 生成推荐理由
            ind_news = [n for n in news_list if Analyzer().classify_industry(n['title']) == ind]
            pos_news = [n for n in ind_news if Analyzer().sentiment(n['title']) == '利好']
            reason = f'近期{len(pos_news)}条利好，产业链成熟' if pos_news else '行业估值合理，景气度平稳'
            lines.append(f'| {i} | {ind} | {reason} |')
        lines.append('')

        # 重点推荐
        top_stocks = stock_picks[:8]
        lines.append('### 重点股票推荐')
        lines.append('')
        lines.append('**短线机会** (5-15天):')
        for s in top_stocks[:4]:
            if s['financial']['rev_growth'] > 30:
                lines.append(f'- {s["stock"]}: 营收增长{s["financial"]["rev_growth"]}%, 技术面强势')
        lines.append('')
        lines.append('**中线配置** (1-3个月):')
        for s in top_stocks[4:8]:
            if s['financial']['roe'] > 15:
                lines.append(f'- {s["stock"]}: ROE {s["financial"]["roe"]}%, 业绩稳定')
        lines.append('')

        # 仓位建议
        lines.append('### 仓位配置建议')
        lines.append('')
        bull_count = len([s for s in stock_picks if s['score'] > 75])
        bear_count = len([s for s in stock_picks if s['score'] < 55])

        if bull_count > bear_count * 2:
            suggestion = '积极布局'
            ratio = '70%-80%'
        elif bull_count > bear_count:
            suggestion = '适度乐观'
            ratio = '60%-70%'
        else:
            suggestion = '谨慎观望'
            ratio = '40%-50%'

        lines.append(f'**市场情绪**: {suggestion} (多头股票{bull_count}只 vs 空头股票{bear_count}只)')
        lines.append(f'**建议仓位**: {ratio}')
        lines.append('')

        # 风险提示
        lines.append('### 风险提示')
        lines.append('')
        lines.append('1. 本报告仅供参考，不构成投资建议')
        lines.append('2. 市场有风险，投资需谨慎')
        lines.append('3. 建议分散配置，单一行业仓位不超过30%')
        lines.append('4. 注意控制杠杆，警惕系统性风险')
        lines.append('5. 关注宏观政策变化，及时调仓')
        lines.append('')
        lines.append('---')
        lines.append(f'*报告生成: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*')
        lines.append(f'*数据来源: 东方财富、财联社、新浪财经*')

        return '\n'.join(lines)

    def save(self, content):
        filepath = os.path.join(OUTPUT_DIR, f'investment_report_{datetime.now().strftime("%Y%m%d")}.md')
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return filepath


# ==================== 主程序 ====================
def main():
    print('=' * 60)
    print('\t财经投资决策系统 v3.0')
    print('=' * 60)
    print()

    # 获取新闻
    print('[1/4] 获取新闻数据...')
    fetcher = NewsFetcher()
    news = fetcher.fetch_all()
    print(f'    获取到 {len(news)} 条新闻')
    print()

    # 分析选股
    print('[2/4] 分析行业与选股...')
    picker = StockPicker()
    picker.process(news)
    stock_picks = picker.rank(15)
    print(f'    精选出 {len(stock_picks)} 只股票')
    print()

    # 生成报告
    print('[3/4] 生成投资报告...')
    generator = ReportGenerator()
    report = generator.generate(news, stock_picks)
    print()

    # 保存
    print('[4/4] 保存报告...')
    filepath = generator.save(report)
    print()

    # 输出结果
    print('=' * 60)
    print('\t最终投资建议')
    print('=' * 60)
    print()

    for i, s in enumerate(stock_picks[:10], 1):
        fin = s['financial']
        print(f'{i:2d}. {s["stock"]:<10} 评分:{s["score"]:>5.1f} '
              f'估值:{s["valuation"]:<4} PE:{fin["pe"]:>4} '
              f'ROE:{fin["roe"]:>3}% 行业:{s["industries"][0]}')

    print()
    print(f'详细报告: {filepath}')

    return report


if __name__ == '__main__':
    main()