"""
财经投资决策系统 v3.0 - 投资大师评审版
============================================
将新闻分析、行业研究、财务评估结果交由投资大师团队评审，
综合巴菲特、芒格等投资大师的观点，生成最终投资建议。
"""
import os
import sys

# 配置
OUTPUT_DIR = r'D:\finance_reports'

# ==================== 步骤1: 运行新闻分析系统 ====================
print('=' * 70)
print('  步骤1: 运行财经新闻分析系统')
print('=' * 70)
print()

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入新闻分析模块
from investment_advisor import (
    NewsFetcher, Analyzer, StockPicker, ReportGenerator,
    INDUSTRY_CHAINS, FINANCIAL_DATA, MOCK_NEWS
)

def run_news_analysis():
    """运行新闻分析并返回选股结果"""
    print('[1/4] 获取新闻数据...')
    fetcher = NewsFetcher()
    news = fetcher.fetch_all()
    print(f'    获取到 {len(news)} 条新闻')
    print()

    print('[2/4] 分析行业与选股...')
    picker = StockPicker()
    picker.process(news)
    stock_picks = picker.rank(15)
    print(f'    精选出 {len(stock_picks)} 只股票')
    print()

    return news, stock_picks

# ==================== 步骤2: 调用投资大师团队评审 ====================
print('=' * 70)
print('  步骤2: 投资大师团队评审')
print('=' * 70)
print()

# 准备要评审的股票列表
news, stock_picks = run_news_analysis()

if stock_picks:
    top_stocks = [s['stock'] for s in stock_picks[:8]]
    print('待评审股票:', ', '.join(top_stocks))
    print()

    # 调用Agno投资大师团队
    try:
        # 切换到agno项目目录
        agno_dir = os.path.join(os.path.dirname(__file__), 'agno_ai_investment')
        if os.path.exists(agno_dir):
            os.chdir(agno_dir)
            sys.path.insert(0, os.path.join(agno_dir, 'src'))

            from apps.investment_team import InvestmentMasterTeam

            # 检查API Key
            if not os.getenv("ALIYUN_API_KEY"):
                print('⚠️ 未设置 ALIYUN_API_KEY，跳过投资大师评审')
                print('💡 请在 agno_ai_investment 目录配置 .env 文件')
            else:
                print('正在启动投资大师团队...')
                print()

                team_manager = InvestmentMasterTeam()
                investment_team = team_manager.create_investment_team()

                # 构建评审任务
                stock_list = '\n'.join([f'{i+1}. {s}' for i, s in enumerate(top_stocks)])

                task = f"""
## 股票池
来自财经新闻分析系统的精选股票池:
{stock_list}

## 系统评分参考
| 股票 | 综合评分 | 估值 | PE | ROE | 营收增长 |
|------|---------|------|----|----|---------|
""" + '\n'.join([f"| {s['stock']} | {s['score']:.0f} | {s['valuation']} | {s['financial']['pe']} | {s['financial']['roe']}% | {s['financial']['rev_growth']}% |" for s in stock_picks[:8]])

                task += f"""

## 评审任务
请扮演巴菲特和芒格，对上述股票池进行投资价值评估：

1. **行业分析**: 从行业景气度、竞争格局、成长空间角度分析
2. **基本面评估**: 评估各股票的财务健康度、盈利能力、估值合理性
3. **风险评估**: 识别主要风险因素
4. **投资建议**: 对每只股票给出明确的投资建议(强烈买入/买入/持有/卖出/强烈卖出)
5. **综合推荐**: 结合当前市场环境，给出最终投资组合建议和仓位配置

请两位大师充分讨论后，给出最终评审结论。
"""

                print('=' * 70)
                print('  投资大师评审中...')
                print('=' * 70)
                print()

                # 执行评审
                investment_team.print_response(
                    task,
                    stream=True,
                    stream_intermediate_steps=True,
                    show_full_reasoning=True,
                )

                # 保存评审结果
                print()
                print('评审完成!')
        else:
            print(f'⚠️ agno_ai_investment 目录未找到: {agno_dir}')

    except ImportError as e:
        print(f'⚠️ 无法导入Agno模块: {e}')
        print('请确保已安装agno及依赖: pip install agno')
    except Exception as e:
        print(f'⚠️ 投资大师评审出错: {e}')
        import traceback
        traceback.print_exc()

else:
    print('⚠️ 未选出股票，跳过评审')

# ==================== 步骤3: 生成最终报告 ====================
print()
print('=' * 70)
print('  步骤3: 生成最终投资决策报告')
print('=' * 70)
print()

# 生成综合报告
generator = ReportGenerator()
report = generator.generate(news, stock_picks)

# 保存报告
filepath = generator.save(report)

# 输出摘要
print()
print('=' * 70)
print('  最终投资建议摘要')
print('=' * 70)
print()

for i, s in enumerate(stock_picks[:10], 1):
    fin = s['financial']
    print(f"{i:2d}. {s['stock']:<10} 评分:{s['score']:>5.1f} "
          f"估值:{s['valuation']:<4} PE:{fin['pe']:>4} "
          f"ROE:{fin['roe']:>3}% 行业:{s['industries'][0]}")

print()
print(f'📊 详细报告: {filepath}')
print()
print('=' * 70)
print('  系统运行完成')
print('=' * 70)