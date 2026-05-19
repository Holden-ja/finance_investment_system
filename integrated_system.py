"""
财经投资决策分析系统 v3.0 - 集成TradingAgents版
================================================
以我们的系统为主，将选股结果通过TradingAgents的多Agent辩论机制做最终评审

融合两个系统的优势：
- 我们的系统：新闻抓取 → 产业链分析 → 智能选股 → 低价股筛选
- TradingAgents：7位分析师辩论 → Bull/Bear多空辩论 → 最终Buy/Hold/Sell信号
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==================== 配置 ====================
OUTPUT_DIR = r'D:\finance_reports'
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# ==================== 产业链全景图 ====================
INDUSTRY_CHAINS = {
    '新能源车': {
        'desc': '新能源汽车完整产业链',
        '全链图': '''
新能源汽车产业链
├── 上游：矿产资源
│   ├── 锂矿：天齐锂业、赣锋锂业
│   ├── 钴矿：华友钴业、洛阳钼业
│   └── 稀土：北方稀土
├── 中游：电池与材料
│   ├── 正极材料：当升科技、容百科技
│   ├── 负极材料：璞泰来、贝特瑞
│   ├── 隔膜：恩捷股份、星源材质
│   ├── 电解液：天赐材料、新宙邦
│   └── 电池制造：宁德时代、比亚迪、国轩高科
├── 下游：整车与配套
│   ├── 整车：比亚迪、理想汽车、蔚来汽车
│   └── 充电桩：特锐德、盛弘股份、绿能慧充
''',
        '投资逻辑': '上游资源为王，中游电池龙头集中，下游充电桩待爆发'
    },
    'AI算力': {
        'desc': 'AI算力基础设施产业链（从砂子到数据中心）',
        '全链图': '''
AI算力产业链
├── 资源层：沙粒→硅矿
│   └── 硅矿：合盛硅业、东岳硅材、新安股份
├── 材料层：金属→多晶硅→硅片
│   ├── 多晶硅：通威股份、大全能源、保利协鑫
│   └── 硅片：隆基绿能、TCL中环、双良节能
├── 芯片层：晶圆→设计→制造→封装
│   ├── 芯片设计：寒武纪、海光信息、景嘉微
│   ├── 晶圆制造：中芯国际、华虹半导体
│   └── 封装测试：长电科技、通富微电、华天科技
├── 组件层：服务器配件
│   ├── 光纤：中天科技、亨通光电、烽火通信、长飞光纤
│   ├── 光模块：中际旭创、光迅科技、新易盛、剑桥科技
│   ├── 连接器：中航光电、航天电器
│   ├── 散热：英维克、艾默生
│   └── 存储：兆易创新、澜起科技
├── 整机层：服务器→数据中心
│   ├── AI服务器：中科曙光、浪潮信息、工业富联
│   └── 数据中心：宝信软件、光环新网、数据港、奥飞数据
├── 电力层：算力耗电大户
│   └── 电力：长江电力、三峡能源、华能水电、特变电工
''',
        '投资逻辑': '资源端低估，芯片端国产替代，电力是长期受益'
    },
    '电力能源': {
        'desc': '电力能源完整产业链',
        '全链图': '''
电力能源产业链
├── 上游：能源开采
│   ├── 煤炭：中国神华、中煤能源、陕西煤业
│   └── 天然气：新奥股份、深圳燃气
├── 中游：发电与输电
│   ├── 水电：长江电力、华能水电、国投电力、川投能源
│   ├── 火电：华电国际、国电电力、大唐发电、华能国际
│   ├── 风电：三峡能源、龙源电力、金风科技、明阳智能、节能风电
│   ├── 光伏发电：太阳能、林洋能源
│   ├── 特高压：特变电工、平高电气、许继电气、思源电气
│   └── 智能电网：国电南瑞、涪陵电力
└── 下游：用电
    ├── 工业用电：大工业用户、数据中心
    └── 居民用电：居民用户
''',
        '投资逻辑': '水电稳定高分红，风电光伏高增长，电网设备低估'
    },
    '半导体': {
        'desc': '半导体完整产业链',
        '全链图': '''
半导体产业链
├── 上游：材料与设备
│   ├── 硅片：沪硅产业、中环股份、立昂微
│   ├── 光刻胶：华懋科技、彤程新材、晶瑞电材
│   ├── 电子气体：华特气体、金宏气体、雅克科技
│   └── 溅射靶材：江丰电子、阿石创
├── 中游：制造与封测
│   ├── 晶圆制造：中芯国际、华虹半导体、华润微
│   └── 封装测试：长电科技、通富微电、华天科技、晶方科技
├── 下游：设计与应用
│   ├── 芯片设计：韦尔股份、卓胜微、圣邦股份、兆易创新
│   ├── 消费电子：苹果产业链、华为产业链
│   ├── 汽车电子：德赛西威、华阳集团
│   └── 工业控制：汇川技术、信捷电气
''',
        '投资逻辑': '国产替代加速，上游材料设备估值修复，封测率先复苏'
    },
    '光伏': {
        'desc': '光伏完整产业链',
        '全链图': '''
光伏产业链
├── 上游：原材料
│   ├── 多晶硅：通威股份、大全能源、保利协鑫、新特能源
│   └── 硅片：隆基绿能、TCL中环、双良节能、京运通
├── 中游：电池与组件
│   ├── 电池片：通威股份、爱旭股份、润阳股份
│   ├── 组件：隆基绿能、晶科能源、天合光能、晶澳科技、东方日升
│   └── 逆变器：阳光电源、锦浪科技、固德威、德业股份、上能电气
└── 下游：光伏应用
    ├── 光伏电站：国电投、三峡集团、华能
    └── EPC：特变电工、正泰电器
''',
        '投资逻辑': '上游硅料利润丰厚，中游组件竞争激烈，下游电站稳定'
    },
    '医药': {
        'desc': '医药完整产业链',
        '全链图': '''
医药产业链
├── 上游：原料与材料
│   ├── 原料药：普洛药业、九洲药业、新和成、浙江医药
│   ├── 中间体：雅本化学、联化科技、天宇股份
│   └── 中药材：片仔癀、云南白药、同仁堂
├── 中游：制药与器械
│   ├── 化学药：恒瑞医药、复星医药、华东医药、石药集团
│   ├── 生物药：药明康德、泰格医药、康龙化成、凯莱英
│   └── 医疗器械：迈瑞医疗、联影医疗、乐普医疗、微创医疗
└── 下游：医疗服务与零售
    ├── 医院：爱尔眼科、通策医疗
    ├── 药店：益丰药房、大参林、老百姓、一心堂
    └── 线上医疗：阿里健康、京东健康
''',
        '投资逻辑': '创新药和CXO高增长，医疗器械国产替代，连锁药店整合'
    },
    '白酒': {
        'desc': '白酒完整产业链',
        '全链图': '''
白酒产业链
├── 上游：原材料与包装
│   ├── 高粱种植：北大荒、登海种业
│   ├── 包装材料：裕同科技、合兴包装、美盈森
│   └── 基酒供应：老白干酒、舍得酒业
├── 中游：酒企
│   ├── 高端酒：贵州茅台、五粮液、泸州老窖
│   ├── 次高端：洋河股份、山西汾酒、古井贡酒
│   └── 中端酒：口子窖、今世缘、迎驾贡酒
└── 下游：销售渠道
    ├── 经销商：华致酒行、酒仙网
    └── 电商：京东酒类、天猫酒类
''',
        '投资逻辑': '高端酒护城河深，次高端增长快，渠道创新'
    },
    '银行': {
        'desc': '银行完整产业链',
        '全链图': '''
银行产业链
├── 上游：资金来源
│   ├── 个人储蓄：居民存款
│   ├── 企业存款：企业对公存款
│   └── 同业拆借：银行间市场
├── 中游：银行业务
│   ├── 国有大行：工商银行、建设银行、农业银行、中国银行、交通银行
│   ├── 股份制银行：招商银行、兴业银行、平安银行、民生银行、浦发银行
│   ├── 城商行：宁波银行、杭州银行、南京银行、苏州银行
│   └── 农商行：渝农商行、沪农商行、苏农银行
└── 下游：服务对象
    ├── 企业贷款：大中小微企业
    └── 个人贷款：房贷、消费贷、经营贷
''',
        '投资逻辑': '城商行增长快，国股行估值低，农商行风险大'
    },
    '券商': {
        'desc': '券商完整产业链',
        '全链图': '''
券商产业链
├── 上游：基础设施
│   ├── 交易所：上海交易所、深圳交易所
│   └── 行情数据：东方财富、同花顺、大智慧
├── 中游：券商业务
│   ├── 经纪业务：中信证券、国泰君安、华泰证券、银河证券
│   ├── 投行业务：中信建投、中金公司、海通证券
│   ├── 资管业务：广发证券、招商证券、兴业证券
│   ├── 自营业务：头部券商均有布局
│   └── 两融业务：融资融券
└── 下游：客户
    ├── 企业用户：上市公司
    └── 个人用户：散户、机构
''',
        '投资逻辑': '市场回暖经纪业务反弹，注册制利好投行，财富管理转型'
    }
}

# ==================== 股票数据库 ====================
STOCK_DB = {
    # 新能源车上游
    '天齐锂业': {'price': 28.5, 'pe': 12, 'roe': 35, 'rev_growth': 80, 'industry': '新能源车-上游'},
    '赣锋锂业': {'price': 25.8, 'pe': 15, 'roe': 28, 'rev_growth': 65, 'industry': '新能源车-上游'},
    '华友钴业': {'price': 22.5, 'pe': 18, 'roe': 22, 'rev_growth': 50, 'industry': '新能源车-上游'},
    '恩捷股份': {'price': 26.5, 'pe': 22, 'roe': 20, 'rev_growth': 45, 'industry': '新能源车-上游'},
    '星源材质': {'price': 12.8, 'pe': 25, 'roe': 15, 'rev_growth': 40, 'industry': '新能源车-上游'},
    '璞泰来': {'price': 18.5, 'pe': 20, 'roe': 18, 'rev_growth': 50, 'industry': '新能源车-上游'},
    '当升科技': {'price': 24.5, 'pe': 18, 'roe': 22, 'rev_growth': 55, 'industry': '新能源车-上游'},
    '容百科技': {'price': 19.5, 'pe': 22, 'roe': 18, 'rev_growth': 60, 'industry': '新能源车-上游'},

    # 新能源车中游
    '宁德时代': {'price': 185.0, 'pe': 25, 'roe': 18, 'rev_growth': 85, 'industry': '新能源车-中游'},
    '比亚迪': {'price': 280.0, 'pe': 35, 'roe': 15, 'rev_growth': 65, 'industry': '新能源车-中游'},
    '亿纬锂能': {'price': 45.0, 'pe': 30, 'roe': 16, 'rev_growth': 70, 'industry': '新能源车-中游'},
    '国轩高科': {'price': 15.8, 'pe': 35, 'roe': 12, 'rev_growth': 60, 'industry': '新能源车-中游'},
    '欣旺达': {'price': 12.5, 'pe': 30, 'roe': 14, 'rev_growth': 55, 'industry': '新能源车-中游'},
    '汇川技术': {'price': 58.0, 'pe': 45, 'roe': 22, 'rev_growth': 40, 'industry': '新能源车-中游'},
    '麦格米特': {'price': 22.5, 'pe': 35, 'roe': 18, 'rev_growth': 35, 'industry': '新能源车-中游'},
    '英搏尔': {'price': 18.5, 'pe': 40, 'roe': 12, 'rev_growth': 50, 'industry': '新能源车-中游'},

    # 新能源车下游
    '特锐德': {'price': 15.8, 'pe': 45, 'roe': 10, 'rev_growth': 35, 'industry': '新能源车-下游'},
    '盛弘股份': {'price': 19.5, 'pe': 35, 'roe': 15, 'rev_growth': 45, 'industry': '新能源车-下游'},
    '绿能慧充': {'price': 8.5, 'pe': 50, 'roe': 8, 'rev_growth': 60, 'industry': '新能源车-下游'},
    '英可瑞': {'price': 12.5, 'pe': 55, 'roe': 6, 'rev_growth': 40, 'industry': '新能源车-下游'},

    # AI算力
    '合盛硅业': {'price': 28.5, 'pe': 15, 'roe': 20, 'rev_growth': 30, 'industry': 'AI算力-上游'},
    '通威股份': {'price': 28.5, 'pe': 12, 'roe': 40, 'rev_growth': 60, 'industry': 'AI算力-上游'},
    '大全能源': {'price': 22.5, 'pe': 15, 'roe': 35, 'rev_growth': 55, 'industry': 'AI算力-上游'},
    '隆基绿能': {'price': 22.5, 'pe': 22, 'roe': 22, 'rev_growth': 55, 'industry': 'AI算力-上游'},
    'TCL中环': {'price': 12.5, 'pe': 25, 'roe': 18, 'rev_growth': 45, 'industry': 'AI算力-上游'},
    '双良节能': {'price': 8.5, 'pe': 30, 'roe': 12, 'rev_growth': 50, 'industry': 'AI算力-上游'},
    '中芯国际': {'price': 42.5, 'pe': 55, 'roe': 8, 'rev_growth': 30, 'industry': 'AI算力-中游'},
    '长电科技': {'price': 25.8, 'pe': 35, 'roe': 15, 'rev_growth': 35, 'industry': 'AI算力-中游'},
    '通富微电': {'price': 15.8, 'pe': 40, 'roe': 12, 'rev_growth': 30, 'industry': 'AI算力-中游'},
    '华天科技': {'price': 9.5, 'pe': 35, 'roe': 10, 'rev_growth': 28, 'industry': 'AI算力-中游'},
    '中际旭创': {'price': 85.0, 'pe': 60, 'roe': 22, 'rev_growth': 60, 'industry': 'AI算力-中游'},
    '光迅科技': {'price': 32.5, 'pe': 45, 'roe': 15, 'rev_growth': 35, 'industry': 'AI算力-中游'},
    '新易盛': {'price': 45.0, 'pe': 55, 'roe': 20, 'rev_growth': 55, 'industry': 'AI算力-中游'},
    '剑桥科技': {'price': 28.5, 'pe': 40, 'roe': 18, 'rev_growth': 45, 'industry': 'AI算力-中游'},
    '中天科技': {'price': 18.5, 'pe': 18, 'roe': 15, 'rev_growth': 25, 'industry': 'AI算力-中游'},
    '亨通光电': {'price': 22.5, 'pe': 22, 'roe': 14, 'rev_growth': 20, 'industry': 'AI算力-中游'},
    '烽火通信': {'price': 25.8, 'pe': 30, 'roe': 12, 'rev_growth': 18, 'industry': 'AI算力-中游'},
    '长飞光纤': {'price': 28.5, 'pe': 35, 'roe': 15, 'rev_growth': 22, 'industry': 'AI算力-中游'},
    '中航光电': {'price': 42.5, 'pe': 35, 'roe': 20, 'rev_growth': 25, 'industry': 'AI算力-中游'},
    '英维克': {'price': 38.5, 'pe': 50, 'roe': 16, 'rev_growth': 40, 'industry': 'AI算力-中游'},
    '兆易创新': {'price': 95.0, 'pe': 60, 'roe': 18, 'rev_growth': 30, 'industry': 'AI算力-中游'},
    '澜起科技': {'price': 65.0, 'pe': 55, 'roe': 20, 'rev_growth': 40, 'industry': 'AI算力-中游'},
    '寒武纪': {'price': 85.0, 'pe': 0, 'roe': -5, 'rev_growth': 50, 'industry': 'AI算力-中游'},
    '海光信息': {'price': 38.5, 'pe': 80, 'roe': 10, 'rev_growth': 60, 'industry': 'AI算力-中游'},
    '中科曙光': {'price': 32.5, 'pe': 45, 'roe': 12, 'rev_growth': 35, 'industry': 'AI算力-下游'},
    '浪潮信息': {'price': 28.5, 'pe': 35, 'roe': 15, 'rev_growth': 40, 'industry': 'AI算力-下游'},
    '工业富联': {'price': 18.5, 'pe': 25, 'roe': 18, 'rev_growth': 45, 'industry': 'AI算力-下游'},
    '宝信软件': {'price': 35.0, 'pe': 40, 'roe': 20, 'rev_growth': 25, 'industry': 'AI算力-下游'},
    '光环新网': {'price': 8.5, 'pe': 30, 'roe': 12, 'rev_growth': 20, 'industry': 'AI算力-下游'},
    '数据港': {'price': 18.5, 'pe': 45, 'roe': 10, 'rev_growth': 30, 'industry': 'AI算力-下游'},
    '奥飞数据': {'price': 12.5, 'pe': 50, 'roe': 8, 'rev_growth': 35, 'industry': 'AI算力-下游'},

    # 电力能源
    '长江电力': {'price': 28.5, 'pe': 22, 'roe': 16, 'rev_growth': 10, 'industry': '电力-水电'},
    '华能水电': {'price': 8.5, 'pe': 18, 'roe': 14, 'rev_growth': 8, 'industry': '电力-水电'},
    '国投电力': {'price': 12.5, 'pe': 20, 'roe': 12, 'rev_growth': 10, 'industry': '电力-水电'},
    '三峡能源': {'price': 6.5, 'pe': 25, 'roe': 12, 'rev_growth': 25, 'industry': '电力-风电'},
    '龙源电力': {'price': 18.5, 'pe': 22, 'roe': 14, 'rev_growth': 20, 'industry': '电力-风电'},
    '金风科技': {'price': 8.5, 'pe': 28, 'roe': 10, 'rev_growth': 18, 'industry': '电力-风电'},
    '明阳智能': {'price': 12.5, 'pe': 25, 'roe': 12, 'rev_growth': 22, 'industry': '电力-风电'},
    '特变电工': {'price': 22.5, 'pe': 12, 'roe': 18, 'rev_growth': 30, 'industry': '电力-特高压'},
    '国电南瑞': {'price': 28.5, 'pe': 35, 'roe': 18, 'rev_growth': 20, 'industry': '电力-电网'},
    '许继电气': {'price': 18.5, 'pe': 30, 'roe': 15, 'rev_growth': 22, 'industry': '电力-电网'},
    '平高电气': {'price': 12.5, 'pe': 35, 'roe': 12, 'rev_growth': 25, 'industry': '电力-电网'},
    '思源电气': {'price': 25.8, 'pe': 32, 'roe': 16, 'rev_growth': 18, 'industry': '电力-电网'},

    # 光伏
    '新特能源': {'price': 12.5, 'pe': 18, 'roe': 25, 'rev_growth': 50, 'industry': '光伏-上游'},
    '晶科能源': {'price': 8.5, 'pe': 25, 'roe': 15, 'rev_growth': 60, 'industry': '光伏-中游'},
    '天合光能': {'price': 25.8, 'pe': 28, 'roe': 18, 'rev_growth': 55, 'industry': '光伏-中游'},
    '晶澳科技': {'price': 22.5, 'pe': 22, 'roe': 20, 'rev_growth': 50, 'industry': '光伏-中游'},
    '东方日升': {'price': 12.5, 'pe': 30, 'roe': 15, 'rev_growth': 45, 'industry': '光伏-中游'},
    '阳光电源': {'price': 85.0, 'pe': 35, 'roe': 20, 'rev_growth': 50, 'industry': '光伏-中游'},
    '锦浪科技': {'price': 65.0, 'pe': 40, 'roe': 25, 'rev_growth': 60, 'industry': '光伏-中游'},
    '上能电气': {'price': 28.5, 'pe': 50, 'roe': 15, 'rev_growth': 50, 'industry': '光伏-中游'},
    '爱旭股份': {'price': 28.5, 'pe': 30, 'roe': 18, 'rev_growth': 65, 'industry': '光伏-中游'},
    '润阳股份': {'price': 15.8, 'pe': 35, 'roe': 15, 'rev_growth': 55, 'industry': '光伏-中游'},

    # 医药
    '普洛药业': {'price': 18.5, 'pe': 25, 'roe': 15, 'rev_growth': 20, 'industry': '医药-上游'},
    '九洲药业': {'price': 22.5, 'pe': 30, 'roe': 18, 'rev_growth': 25, 'industry': '医药-上游'},
    '新和成': {'price': 18.8, 'pe': 22, 'roe': 16, 'rev_growth': 15, 'industry': '医药-上游'},
    '恒瑞医药': {'price': 28.5, 'pe': 65, 'roe': 12, 'rev_growth': 8, 'industry': '医药-中游'},
    '复星医药': {'price': 25.8, 'pe': 30, 'roe': 14, 'rev_growth': 15, 'industry': '医药-中游'},
    '石药集团': {'price': 6.5, 'pe': 22, 'roe': 15, 'rev_growth': 10, 'industry': '医药-中游'},
    '药明康德': {'price': 72.0, 'pe': 40, 'roe': 18, 'rev_growth': 35, 'industry': '医药-中游'},
    '康龙化成': {'price': 28.5, 'pe': 50, 'roe': 14, 'rev_growth': 35, 'industry': '医药-中游'},
    '迈瑞医疗': {'price': 285.0, 'pe': 45, 'roe': 25, 'rev_growth': 22, 'industry': '医药-中游'},
    '乐普医疗': {'price': 12.5, 'pe': 28, 'roe': 15, 'rev_growth': 18, 'industry': '医药-中游'},
    '爱尔眼科': {'price': 25.8, 'pe': 55, 'roe': 20, 'rev_growth': 25, 'industry': '医药-下游'},
    '益丰药房': {'price': 45.0, 'pe': 35, 'roe': 18, 'rev_growth': 25, 'industry': '医药-下游'},
    '大参林': {'price': 18.5, 'pe': 30, 'roe': 16, 'rev_growth': 22, 'industry': '医药-下游'},
    '老百姓': {'price': 22.5, 'pe': 32, 'roe': 17, 'rev_growth': 23, 'industry': '医药-下游'},

    # 半导体
    '沪硅产业': {'price': 18.5, 'pe': 60, 'roe': 5, 'rev_growth': 30, 'industry': '半导体-上游'},
    '立昂微': {'price': 28.5, 'pe': 45, 'roe': 12, 'rev_growth': 35, 'industry': '半导体-上游'},
    '华懋科技': {'price': 22.5, 'pe': 50, 'roe': 10, 'rev_growth': 25, 'industry': '半导体-上游'},
    '彤程新材': {'price': 25.8, 'pe': 48, 'roe': 12, 'rev_growth': 30, 'industry': '半导体-上游'},
    '晶瑞电材': {'price': 15.8, 'pe': 55, 'roe': 8, 'rev_growth': 20, 'industry': '半导体-上游'},
    '华特气体': {'price': 58.5, 'pe': 55, 'roe': 15, 'rev_growth': 35, 'industry': '半导体-上游'},
    '华虹半导体': {'price': 28.5, 'pe': 45, 'roe': 10, 'rev_growth': 25, 'industry': '半导体-中游'},
    '晶方科技': {'price': 18.5, 'pe': 45, 'roe': 12, 'rev_growth': 25, 'industry': '半导体-中游'},
    '韦尔股份': {'price': 85.0, 'pe': 50, 'roe': 15, 'rev_growth': 25, 'industry': '半导体-下游'},
    '兆易创新': {'price': 98.0, 'pe': 55, 'roe': 18, 'rev_growth': 30, 'industry': '半导体-下游'},
    '圣邦股份': {'price': 125.0, 'pe': 70, 'roe': 22, 'rev_growth': 40, 'industry': '半导体-下游'},

    # 银行
    '招商银行': {'price': 32.5, 'pe': 8, 'roe': 16, 'rev_growth': 10, 'industry': '银行'},
    '宁波银行': {'price': 28.5, 'pe': 10, 'roe': 18, 'rev_growth': 15, 'industry': '银行'},
    '杭州银行': {'price': 12.5, 'pe': 8, 'roe': 15, 'rev_growth': 18, 'industry': '银行'},
    '南京银行': {'price': 9.5, 'pe': 7, 'roe': 14, 'rev_growth': 15, 'industry': '银行'},
    '渝农商行': {'price': 4.2, 'pe': 6, 'roe': 10, 'rev_growth': 8, 'industry': '银行'},

    # 券商
    '东方财富': {'price': 18.5, 'pe': 50, 'roe': 16, 'rev_growth': 25, 'industry': '券商'},
    '同花顺': {'price': 85.0, 'pe': 55, 'roe': 25, 'rev_growth': 30, 'industry': '券商'},
    '中信证券': {'price': 22.5, 'pe': 20, 'roe': 10, 'rev_growth': 15, 'industry': '券商'},
    '国泰君安': {'price': 15.8, 'pe': 18, 'roe': 9, 'rev_growth': 12, 'industry': '券商'},
    '华泰证券': {'price': 14.5, 'pe': 16, 'roe': 10, 'rev_growth': 14, 'industry': '券商'},
    '中信建投': {'price': 25.8, 'pe': 22, 'roe': 12, 'rev_growth': 18, 'industry': '券商'},
}


# ==================== 分析工具 ====================

def calculate_score(data):
    """计算综合评分"""
    growth = min(data['rev_growth'] / 100 * 40, 40)
    profit = (data['roe'] / 30) * 30 if data['roe'] > 0 else 0
    pe = max(0, (30 - data['pe']) / 30 * 30) if 0 < data['pe'] < 60 else 0
    return growth + profit + pe


def generate_trading_agents_prompt(stocks):
    """生成传给TradingAgents的Prompt"""
    stock_list = '\n'.join([f'{i+1}. {s}: 价格={d["price"]}元, PE={d["pe"]}, ROE={d["roe"]}%, 增长={d["rev_growth"]}%, {d["industry"]}'
                            for i, (s, d) in enumerate(stocks)])

    prompt = f"""
## 候选股票池（来自财经投资决策分析系统初步筛选）

{stock_list}

## 系统初步评分
{'-' * 60}
"""

    for stock, data in stocks:
        score = calculate_score(data)
        prompt += f"| {stock} | {score:.1f} | PE={data['pe']} | ROE={data['roe']}% | 增长={data['rev_growth']}% |\n"

    prompt += f"""
{'-' * 60}

## 评审任务
请作为7位A股分析师，对上述候选股票进行**多空辩论评审**：

1. **市场分析师**：从技术面、资金面、趋势角度分析
2. **舆情分析师**：从市场情绪、资金流向角度分析
3. **新闻分析师**：从消息面、突发事件角度分析
4. **基本面分析师**：从财务数据、估值角度分析
5. **政策分析师**：从政策导向、行业扶持角度分析（A 股特化）
6. **游资追踪分析师**：从龙虎榜、游资动向角度分析（A 股特化）
7. **解禁监控分析师**：从解禁压力、减持风险角度分析（A 股特化）

### 辩论流程
1. 7位分析师各自给出初步判断
2. Bull vs Bear 多空辩论（N 轮）
3. 三方风险辩论（激进/保守/中立）
4. 研究经理综合研判
5. 交易员制定方案（含 A 股特有约束：T+1、涨跌停）
6. 投资组合经理最终决策

### 输出要求
- 对每只股票给出：**Buy / Hold / Sell** 信号
- 给出目标仓位（0-100%）
- 说明投资逻辑和风险因素
- 考虑 A 股特有规则（T+1、涨跌停限制）
"""
    return prompt


def print_chain_diagrams():
    """打印产业链全景图"""
    print('=' * 80)
    print('  产业链全景图')
    print('=' * 80)
    print()

    for industry, data in INDUSTRY_CHAINS.items():
        print(f'【{industry}】{data["desc"]}')
        print('-' * 60)
        print(data['全链图'])
        print(f'投资逻辑: {data["投资逻辑"]}')
        print()


def analyze_stocks():
    """分析股票并生成排名"""
    print('=' * 80)
    print('  行业股票分析 (0-30元)')
    print('=' * 80)
    print()

    results = []
    for stock, data in STOCK_DB.items():
        if 0 < data['price'] <= 30:
            score = calculate_score(data)
            results.append((stock, data, score))

    results.sort(key=lambda x: x[2], reverse=True)

    industries = ['新能源车', 'AI算力', '电力', '光伏', '医药', '半导体', '银行', '券商']

    for ind in industries:
        print(f'\n### {ind}')
        print('|' + '-'*20 + '|' + '-'*8 + '|' + '-'*6 + '|' + '-'*6 + '|' + '-'*8 + '|' + '-'*10 + '|' + '-'*6 + '|')
        print('| 股票 | 价格 | PE | ROE | 增长 | 行业 | 评分 |')
        print('|' + '-'*20 + '|' + '-'*8 + '|' + '-'*6 + '|' + '-'*6 + '|' + '-'*8 + '|' + '-'*10 + '|' + '-'*6 + '|')

        ind_stocks = [(s, d, sc) for s, d, sc in results if ind in d['industry']]
        for stock, data, score in ind_stocks[:10]:
            print(f'| {stock} | {data["price"]:.1f} | {data["pe"]} | {data["roe"]}% | {data["rev_growth"]}% | {data["industry"]} | {score:.1f} |')

    return results


def generate_final_report(results):
    """生成最终投资报告"""
    print('=' * 80)
    print('  最终投资建议报告')
    print('=' * 80)
    print()

    print('**一、强烈推荐（评分>70）**')
    print()
    top = [(s, d, sc) for s, d, sc in results if sc > 70]
    for stock, data, score in top[:8]:
        pe_note = '高估' if data['pe'] > 50 else ('低估' if data['pe'] < 20 else '合理')
        print(f'- **{stock}** ({pe_note}): PE={data["pe"]}, ROE={data["roe"]}%, 增长={data["rev_growth"]}%, 评分={score:.1f}')

    print()
    print('**二、推荐关注（评分50-70）**')
    print()
    mid = [(s, d, sc) for s, d, sc in results if 50 <= sc <= 70]
    for stock, data, score in mid[:10]:
        print(f'- {stock}: PE={data["pe"]}, ROE={data["roe"]}%, 增长={data["rev_growth"]}%, 评分={score:.1f}')

    print()
    print('**三、低估值价值股（PE<20且ROE>15%）**')
    print()
    value = [(s, d, sc) for s, d, sc in results if data['pe'] < 20 and data['roe'] > 15]
    for stock, data, score in value[:8]:
        print(f'- {stock}: PE={data["pe"]}, ROE={data["roe"]}%, 评分={score:.1f}')

    print()
    print('**四、产业配置建议**')
    print()
    print('| 产业 | 配置逻辑 | 推荐标的 |')
    print('|------|---------|---------|')
    print('| 新能源车上游 | 锂价反弹，矿产为王 | 天齐锂业、赣锋锂业 |')
    print('| AI算力 | 算力爆发，电力先行 | 中天科技、亨通光电、特变电工 |')
    print('| 电力 | 稳定高分红，新能源转型 | 长江电力、三峡能源 |')
    print('| 光伏 | 周期底部，龙头份额提升 | 通威股份、晶科能源 |')
    print('| 医药 | 估值历史低位，创新出海 | 康龙化成、乐普医疗 |')
    print('| 半导体 | 国产替代，设备先行 | 长电科技、华天科技 |')
    print('| 银行 | 低估值高分红，防御性强 | 招商银行、南京银行 |')
    print('| 券商 | 市场回暖，弹性最大 | 东方财富、中信证券 |')

    return top[:10]


def save_tradingagents_prompt(stocks, filepath=None):
    """保存TradingAgents评审Prompt"""
    if filepath is None:
        filepath = os.path.join(OUTPUT_DIR, 'tradingagents_prompt.md')

    prompt = generate_trading_agents_prompt(stocks)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(prompt)

    print(f'TradingAgents评审Prompt已保存: {filepath}')
    return filepath


# ==================== 主程序 ====================

def main():
    """主程序"""
    print()
    print('=' * 80)
    print('  财经投资决策分析系统 v3.0 - 集成TradingAgents版')
    print('  Finance Investment Decision System with Multi-Agent Debate')
    print('=' * 80)
    print()

    # 1. 打印产业链全景图
    print_chain_diagrams()

    # 2. 股票分析
    results = analyze_stocks()

    # 3. 生成最终报告
    top_stocks = generate_final_report(results)

    # 4. 生成TradingAgents评审Prompt
    print()
    print('=' * 80)
    print('  生成TradingAgents评审Prompt')
    print('=' * 80)
    print()

    # 取评分最高的前10只股票传给TradingAgents
    top_10 = [(s, d) for s, d, sc in results[:10]]
    prompt_file = save_tradingagents_prompt(top_10)

    print()
    print('=' * 80)
    print('  使用说明')
    print('=' * 80)
    print()
    print('1. 我们的系统完成：新闻→产业链→选股→低价股筛选')
    print('2. 将筛选结果传给TradingAgents进行最终多空辩论评审')
    print()
    print(f'评审Prompt文件: {prompt_file}')
    print()
    print('使用TradingAgents评审方法:')
    print('  cd C:/Users/1/TradingAgents-astock')
    print('  python main.py --stock <股票代码>')
    print()
    print('或者将Prompt内容复制到TradingAgents的Web界面进行评审')
    print()
    print('=' * 80)
    print('  分析完成')
    print('=' * 80)


if __name__ == '__main__':
    main()