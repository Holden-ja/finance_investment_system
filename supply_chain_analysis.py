"""
产业链投资分析系统 v2.0
=========================
分析龙头公司上下游产业链，筛选低价高价值股票
"""
import os
import sys
sys.stdout.reconfigure(encoding='utf-8')

# ==================== 产业链配置 ====================
FULL_INDUSTRY_CHAINS = {
    '新能源车': {
        '描述': '新能源汽车整个产业链',
        '上游': {
            '矿产开采': ['天齐锂业', '赣锋锂业', '华友钴业', '洛阳钼业', '北方稀土'],
            '电池材料': ['恩捷股份', '星源材质', '璞泰来', '当升科技', '容百科技'],
            '设备制造': ['先导智能', '杭可科技', '赢合科技', '利元亨']
        },
        '中游': {
            '电池制造': ['宁德时代', '比亚迪', '亿纬锂能', '国轩高科', '欣旺达'],
            '电机电控': ['汇川技术', '麦格米特', '英搏尔', '卧龙电驱']
        },
        '下游': {
            '整车制造': ['比亚迪', '理想汽车', '蔚来汽车', '小鹏汽车'],
            '充电桩': ['特锐德', '盛弘股份', '绿能慧充', '英可瑞']
        }
    },
    'AI': {
        '描述': '人工智能整个产业链',
        '上游': {
            '算力芯片': ['寒武纪', '景嘉微', '海光信息', '龙芯中科'],
            '服务器': ['中科曙光', '浪潮信息', '工业富联'],
            '数据中心': ['宝信软件', '光环新网', '数据港', '奥飞数据']
        },
        '中游': {
            '大模型': ['科大讯飞', '百度', '阿里云', '腾讯混元'],
            '算法平台': ['商汤科技', '旷视科技', '云从科技', '依图科技'],
            'AI应用': ['海康威视', '大华股份', '科大智能']
        },
        '下游': {
            '企业服务': ['用友网络', '金山办公', '致远互联'],
            '消费应用': ['小米集团', '字节跳动', '快手']
        }
    },
    '电力': {
        '描述': '电力行业产业链',
        '上游': {
            '煤炭': ['中国神华', '中煤能源', '陕西煤业'],
            '天然气': ['新奥股份', '深圳燃气']
        },
        '中游': {
            '水电': ['长江电力', '华能水电', '国投电力', '川投能源'],
            '火电': ['华电国际', '国电电力', '大唐发电', '华能国际'],
            '风电': ['三峡能源', '龙源电力', '金风科技', '明阳智能', '节能风电'],
            '光伏发电': ['太阳能', '林洋能源'],
            '特高压': ['特变电工', '平高电气', '许继电气', '思源电气'],
            '电网': ['国电南瑞', '涪陵电力']
        },
        '下游': {
            '工业用电': ['大工业用户'],
            '居民用电': ['居民用户']
        }
    },
    'AI硬件': {
        '描述': 'AI算力基础设施细分产业链（机箱→配件→元器件）',
        '芯片设计': {
            'AI芯片': ['寒武纪', '景嘉微', '海光信息', '平头哥'],
            'GPU': ['景嘉微', '芯动科技'],
            'CPU': ['龙芯中科', '兆芯', '飞腾'],
            'FPGA': ['紫光国微', '复旦微电']
        },
        '芯片制造': {
            '晶圆制造': ['中芯国际', '华虹半导体'],
            '封装测试': ['长电科技', '通富微电', '华天科技'],
            '光刻机配件': ['华特气体', '中微公司']
        },
        '服务器组件': {
            '机箱': ['工业富联', '华为'],
            '电源': ['华为电源', 'Eaton', '施耐德'],
            '散热': ['英维克', '艾默生', '华为散热'],
            '光纤': ['中天科技', '亨通光电', '烽火通信', '长飞光纤'],
            '连接器': ['中航光电', '航天电器']
        },
        '存储': {
            '内存': ['兆易创新', '澜起科技'],
            'SSD': ['长江存储', '三星代理'],
            '硬盘': ['长城汽车']
        },
        '网络设备': {
            '交换机': ['华为', '新华三', '锐捷网络'],
            '路由器': ['华为', '中兴通讯'],
            '光模块': ['中际旭创', '光迅科技', '新易盛', '剑桥科技']
        }
    },
    '白酒': {
        '描述': '白酒整个产业链',
        '上游': {
            '高粱种植': ['北大荒', '登海种业'],
            '包装材料': ['裕同科技', '合兴包装', '美盈森'],
            '基酒供应': ['老白干酒', '舍得酒业']
        },
        '中游': {
            '高端酒': ['贵州茅台', '五粮液', '泸州老窖'],
            '次高端': ['洋河股份', '山西汾酒', '古井贡酒'],
            '中端': ['口子窖', '今世缘', '迎驾贡酒']
        },
        '下游': {
            '经销商': ['华致酒行', '酒仙网'],
            '电商': ['京东酒类', '天猫酒类']
        }
    },
    '半导体': {
        '描述': '半导体整个产业链',
        '上游': {
            '硅片制造': ['沪硅产业', '中环股份', '立昂微'],
            '光刻胶': ['华懋科技', '彤程新材', '晶瑞电材'],
            '电子气体': ['华特气体', '金宏气体', '雅克科技'],
            '溅射靶材': ['江丰电子', '阿石创']
        },
        '中游': {
            '芯片设计': ['韦尔股份', '卓胜微', '圣邦股份', '兆易创新'],
            '晶圆制造': ['中芯国际', '华虹半导体', '华润微'],
            '封装测试': ['长电科技', '通富微电', '华天科技', '晶方科技']
        },
        '下游': {
            '消费电子': ['苹果产业链', '华为产业链'],
            '汽车电子': ['德赛西威', '华阳集团'],
            '工业控制': ['汇川技术', '信捷电气']
        }
    },
    '光伏': {
        '描述': '光伏整个产业链',
        '上游': {
            '多晶硅': ['通威股份', '大全能源', '保利协鑫', '新特能源'],
            '硅片': ['隆基绿能', 'TCL中环', '双良节能', '京运通']
        },
        '中游': {
            '电池片': ['通威股份', '爱旭股份', '润阳股份'],
            '组件': ['隆基绿能', '晶科能源', '天合光能', '晶澳科技', '东方日升'],
            '逆变器': ['阳光电源', '锦浪科技', '固德威', '德业股份', '上能电气']
        },
        '下游': {
            '光伏电站': ['国电投', '三峡集团', '华能'],
            'EPC': ['特变电工', '正泰电器']
        }
    },
    '医药': {
        '描述': '医药整个产业链',
        '上游': {
            '原料药': ['普洛药业', '九洲药业', '新和成', '浙江医药'],
            '中间体': ['雅本化学', '联化科技', '天宇股份'],
            '中药材': ['片仔癀', '云南白药', '同仁堂']
        },
        '中游': {
            '化学药': ['恒瑞医药', '复星医药', '华东医药', '石药集团'],
            '生物药': ['药明康德', '泰格医药', '康龙化成', '凯莱英'],
            '医疗器械': ['迈瑞医疗', '联影医疗', '乐普医疗', '微创医疗']
        },
        '下游': {
            '医院': ['爱尔眼科', '通策医疗'],
            '药店': ['益丰药房', '大参林', '老百姓', '一心堂'],
            '线上医疗': ['阿里健康', '京东健康']
        }
    },
    '券商': {
        '描述': '证券行业产业链',
        '上游': {
            '交易所': ['上海交易所', '深圳交易所'],
            '行情数据': ['东方财富', '同花顺', '大智慧']
        },
        '中游': {
            '经纪业务': ['中信证券', '国泰君安', '华泰证券', '银河证券'],
            '投行业务': ['中信建投', '中金公司', '海通证券'],
            '资管业务': ['广发证券', '招商证券', '兴业证券'],
            '自营业务': ['头部券商均有布局']
        },
        '下游': {
            '企业用户': ['上市公司'],
            '个人用户': ['散户', '机构']
        }
    },
    '银行': {
        '描述': '银行行业产业链',
        '上游': {
            '吸储': ['个人储蓄', '企业存款'],
            '同业拆借': ['银行间市场']
        },
        '中游': {
            '国有大行': ['工商银行', '建设银行', '农业银行', '中国银行', '交通银行'],
            '股份制': ['招商银行', '兴业银行', '平安银行', '民生银行', '浦发银行'],
            '城商行': ['宁波银行', '杭州银行', '南京银行', '苏州银行'],
            '农商行': ['渝农商行', '沪农商行', '苏农银行']
        },
        '下游': {
            '企业贷款': ['大中小微企业'],
            '个人贷款': ['房贷', '消费贷', '经营贷']
        }
    }
}

# 股票基础数据 (股价模拟，实际应从API获取)
STOCK_DATA = {
    # 新能源车上游
    '天齐锂业': {'price': 28.5, 'pe': 12, 'roe': 35, 'rev_growth': 80, 'industry': '新能源车上游-矿产'},
    '赣锋锂业': {'price': 25.8, 'pe': 15, 'roe': 28, 'rev_growth': 65, 'industry': '新能源车上游-矿产'},
    '华友钴业': {'price': 22.5, 'pe': 18, 'roe': 22, 'rev_growth': 50, 'industry': '新能源车上游-矿产'},
    '恩捷股份': {'price': 26.5, 'pe': 22, 'roe': 20, 'rev_growth': 45, 'industry': '新能源车上游-材料'},
    '星源材质': {'price': 12.8, 'pe': 25, 'roe': 15, 'rev_growth': 40, 'industry': '新能源车上游-材料'},
    '璞泰来': {'price': 18.5, 'pe': 20, 'roe': 18, 'rev_growth': 50, 'industry': '新能源车上游-材料'},
    '当升科技': {'price': 24.5, 'pe': 18, 'roe': 22, 'rev_growth': 55, 'industry': '新能源车上游-材料'},
    '容百科技': {'price': 19.5, 'pe': 22, 'roe': 18, 'rev_growth': 60, 'industry': '新能源车上游-材料'},
    '先导智能': {'price': 22.8, 'pe': 28, 'roe': 20, 'rev_growth': 50, 'industry': '新能源车上游-设备'},

    # 新能源车中游
    '宁德时代': {'price': 185.0, 'pe': 25, 'roe': 18, 'rev_growth': 85, 'industry': '新能源车中游-电池'},
    '亿纬锂能': {'price': 45.0, 'pe': 30, 'roe': 16, 'rev_growth': 70, 'industry': '新能源车中游-电池'},
    '国轩高科': {'price': 15.8, 'pe': 35, 'roe': 12, 'rev_growth': 60, 'industry': '新能源车中游-电池'},
    '欣旺达': {'price': 12.5, 'pe': 30, 'roe': 14, 'rev_growth': 55, 'industry': '新能源车中游-电池'},
    '汇川技术': {'price': 58.0, 'pe': 45, 'roe': 22, 'rev_growth': 40, 'industry': '新能源车中游-电机'},
    '麦格米特': {'price': 22.5, 'pe': 35, 'roe': 18, 'rev_growth': 35, 'industry': '新能源车中游-电机'},
    '英搏尔': {'price': 18.5, 'pe': 40, 'roe': 12, 'rev_growth': 50, 'industry': '新能源车中游-电机'},

    # 新能源车下游
    '特锐德': {'price': 15.8, 'pe': 45, 'roe': 10, 'rev_growth': 35, 'industry': '新能源车下游-充电桩'},
    '盛弘股份': {'price': 19.5, 'pe': 35, 'roe': 15, 'rev_growth': 45, 'industry': '新能源车下游-充电桩'},
    '绿能慧充': {'price': 8.5, 'pe': 50, 'roe': 8, 'rev_growth': 60, 'industry': '新能源车下游-充电桩'},
    '英可瑞': {'price': 12.5, 'pe': 55, 'roe': 6, 'rev_growth': 40, 'industry': '新能源车下游-充电桩'},

    # 白酒上游
    '北大荒': {'price': 14.5, 'pe': 18, 'roe': 12, 'rev_growth': 8, 'industry': '白酒上游-种植'},
    '裕同科技': {'price': 16.5, 'pe': 20, 'roe': 14, 'rev_growth': 15, 'industry': '白酒上游-包装'},

    # 白酒中游
    '贵州茅台': {'price': 1680.0, 'pe': 35, 'roe': 30, 'rev_growth': 18, 'industry': '白酒中游-高端'},
    '五粮液': {'price': 145.0, 'pe': 28, 'roe': 25, 'rev_growth': 15, 'industry': '白酒中游-高端'},
    '泸州老窖': {'price': 168.0, 'pe': 30, 'roe': 28, 'rev_growth': 20, 'industry': '白酒中游-高端'},
    '洋河股份': {'price': 125.0, 'pe': 25, 'roe': 22, 'rev_growth': 12, 'industry': '白酒中游-次高端'},
    '山西汾酒': {'price': 185.0, 'pe': 40, 'roe': 25, 'rev_growth': 25, 'industry': '白酒中游-次高端'},
    '古井贡酒': {'price': 198.0, 'pe': 38, 'roe': 24, 'rev_growth': 18, 'industry': '白酒中游-次高端'},
    '口子窖': {'price': 42.5, 'pe': 22, 'roe': 20, 'rev_growth': 15, 'industry': '白酒中游-中端'},
    '今世缘': {'price': 35.8, 'pe': 25, 'roe': 22, 'rev_growth': 18, 'industry': '白酒中游-中端'},

    # 半导体上游
    '沪硅产业': {'price': 18.5, 'pe': 60, 'roe': 5, 'rev_growth': 30, 'industry': '半导体上游-硅片'},
    '中环股份': {'price': 32.5, 'pe': 35, 'roe': 15, 'rev_growth': 40, 'industry': '半导体上游-硅片'},
    '立昂微': {'price': 28.5, 'pe': 45, 'roe': 12, 'rev_growth': 35, 'industry': '半导体上游-硅片'},
    '华懋科技': {'price': 22.5, 'pe': 50, 'roe': 10, 'rev_growth': 25, 'industry': '半导体上游-光刻胶'},
    '彤程新材': {'price': 25.8, 'pe': 48, 'roe': 12, 'rev_growth': 30, 'industry': '半导体上游-光刻胶'},
    '晶瑞电材': {'price': 15.8, 'pe': 55, 'roe': 8, 'rev_growth': 20, 'industry': '半导体上游-光刻胶'},
    '华特气体': {'price': 58.5, 'pe': 55, 'roe': 15, 'rev_growth': 35, 'industry': '半导体上游-气体'},
    '金宏气体': {'price': 22.5, 'pe': 50, 'roe': 12, 'rev_growth': 30, 'industry': '半导体上游-气体'},
    '雅克科技': {'price': 48.5, 'pe': 45, 'roe': 18, 'rev_growth': 40, 'industry': '半导体上游-气体'},
    '江丰电子': {'price': 65.0, 'pe': 80, 'roe': 12, 'rev_growth': 35, 'industry': '半导体上游-靶材'},
    '阿石创': {'price': 18.5, 'pe': 60, 'roe': 8, 'rev_growth': 25, 'industry': '半导体上游-靶材'},

    # 半导体中游
    '韦尔股份': {'price': 85.0, 'pe': 50, 'roe': 15, 'rev_growth': 25, 'industry': '半导体中游-设计'},
    '卓胜微': {'price': 95.0, 'pe': 60, 'roe': 20, 'rev_growth': 35, 'industry': '半导体中游-设计'},
    '圣邦股份': {'price': 125.0, 'pe': 70, 'roe': 22, 'rev_growth': 40, 'industry': '半导体中游-设计'},
    '兆易创新': {'price': 98.0, 'pe': 55, 'roe': 18, 'rev_growth': 30, 'industry': '半导体中游-设计'},
    '中芯国际': {'price': 42.5, 'pe': 55, 'roe': 8, 'rev_growth': 30, 'industry': '半导体中游-制造'},
    '华虹半导体': {'price': 28.5, 'pe': 45, 'roe': 10, 'rev_growth': 25, 'industry': '半导体中游-制造'},
    '华润微': {'price': 38.5, 'pe': 40, 'roe': 12, 'rev_growth': 28, 'industry': '半导体中游-制造'},
    '长电科技': {'price': 25.8, 'pe': 35, 'roe': 15, 'rev_growth': 35, 'industry': '半导体中游-封测'},
    '通富微电': {'price': 15.8, 'pe': 40, 'roe': 12, 'rev_growth': 30, 'industry': '半导体中游-封测'},
    '华天科技': {'price': 9.5, 'pe': 35, 'roe': 10, 'rev_growth': 28, 'industry': '半导体中游-封测'},
    '晶方科技': {'price': 18.5, 'pe': 45, 'roe': 12, 'rev_growth': 25, 'industry': '半导体中游-封测'},

    # 光伏上游
    '通威股份': {'price': 28.5, 'pe': 12, 'roe': 40, 'rev_growth': 60, 'industry': '光伏上游-硅料'},
    '大全能源': {'price': 22.5, 'pe': 15, 'roe': 35, 'rev_growth': 55, 'industry': '光伏上游-硅料'},
    '保利协鑫': {'price': 1.8, 'pe': 20, 'roe': 15, 'rev_growth': 40, 'industry': '光伏上游-硅料'},
    '新特能源': {'price': 12.5, 'pe': 18, 'roe': 25, 'rev_growth': 50, 'industry': '光伏上游-硅料'},
    '隆基绿能': {'price': 22.5, 'pe': 22, 'roe': 22, 'rev_growth': 55, 'industry': '光伏上游-硅片'},
    'TCL中环': {'price': 12.5, 'pe': 25, 'roe': 18, 'rev_growth': 45, 'industry': '光伏上游-硅片'},
    '双良节能': {'price': 8.5, 'pe': 30, 'roe': 12, 'rev_growth': 50, 'industry': '光伏上游-硅片'},
    '京运通': {'price': 6.5, 'pe': 35, 'roe': 10, 'rev_growth': 40, 'industry': '光伏上游-硅片'},

    # 光伏中游
    '爱旭股份': {'price': 28.5, 'pe': 30, 'roe': 18, 'rev_growth': 65, 'industry': '光伏中游-电池片'},
    '润阳股份': {'price': 15.8, 'pe': 35, 'roe': 15, 'rev_growth': 55, 'industry': '光伏中游-电池片'},
    '晶科能源': {'price': 8.5, 'pe': 25, 'roe': 15, 'rev_growth': 60, 'industry': '光伏中游-组件'},
    '天合光能': {'price': 25.8, 'pe': 28, 'roe': 18, 'rev_growth': 55, 'industry': '光伏中游-组件'},
    '晶澳科技': {'price': 22.5, 'pe': 22, 'roe': 20, 'rev_growth': 50, 'industry': '光伏中游-组件'},
    '东方日升': {'price': 12.5, 'pe': 30, 'roe': 15, 'rev_growth': 45, 'industry': '光伏中游-组件'},
    '阳光电源': {'price': 85.0, 'pe': 35, 'roe': 20, 'rev_growth': 50, 'industry': '光伏中游-逆变器'},
    '锦浪科技': {'price': 65.0, 'pe': 40, 'roe': 25, 'rev_growth': 60, 'industry': '光伏中游-逆变器'},
    '固德威': {'price': 85.0, 'pe': 45, 'roe': 22, 'rev_growth': 55, 'industry': '光伏中游-逆变器'},
    '德业股份': {'price': 72.0, 'pe': 38, 'roe': 24, 'rev_growth': 58, 'industry': '光伏中游-逆变器'},
    '上能电气': {'price': 28.5, 'pe': 50, 'roe': 15, 'rev_growth': 50, 'industry': '光伏中游-逆变器'},

    # 医药上游
    '普洛药业': {'price': 18.5, 'pe': 25, 'roe': 15, 'rev_growth': 20, 'industry': '医药上游-原料药'},
    '九洲药业': {'price': 22.5, 'pe': 30, 'roe': 18, 'rev_growth': 25, 'industry': '医药上游-原料药'},
    '新和成': {'price': 18.8, 'pe': 22, 'roe': 16, 'rev_growth': 15, 'industry': '医药上游-原料药'},
    '浙江医药': {'price': 12.5, 'pe': 20, 'roe': 14, 'rev_growth': 12, 'industry': '医药上游-原料药'},
    '雅本化学': {'price': 8.5, 'pe': 35, 'roe': 10, 'rev_growth': 18, 'industry': '医药上游-中间体'},
    '联化科技': {'price': 12.5, 'pe': 30, 'roe': 12, 'rev_growth': 15, 'industry': '医药上游-中间体'},
    '天宇股份': {'price': 22.5, 'pe': 28, 'roe': 18, 'rev_growth': 20, 'industry': '医药上游-中间体'},

    # 医药中游
    '恒瑞医药': {'price': 28.5, 'pe': 65, 'roe': 12, 'rev_growth': 8, 'industry': '医药中游-化药'},
    '复星医药': {'price': 25.8, 'pe': 30, 'roe': 14, 'rev_growth': 15, 'industry': '医药中游-化药'},
    '华东医药': {'price': 32.5, 'pe': 28, 'roe': 18, 'rev_growth': 12, 'industry': '医药中游-化药'},
    '石药集团': {'price': 6.5, 'pe': 22, 'roe': 15, 'rev_growth': 10, 'industry': '医药中游-化药'},
    '药明康德': {'price': 72.0, 'pe': 40, 'roe': 18, 'rev_growth': 35, 'industry': '医药中游-生物药'},
    '泰格医药': {'price': 65.0, 'pe': 45, 'roe': 16, 'rev_growth': 30, 'industry': '医药中游-生物药'},
    '康龙化成': {'price': 28.5, 'pe': 50, 'roe': 14, 'rev_growth': 35, 'industry': '医药中游-生物药'},
    '凯莱英': {'price': 95.0, 'pe': 42, 'roe': 18, 'rev_growth': 32, 'industry': '医药中游-生物药'},
    '迈瑞医疗': {'price': 285.0, 'pe': 45, 'roe': 25, 'rev_growth': 22, 'industry': '医药中游-器械'},
    '联影医疗': {'price': 125.0, 'pe': 60, 'roe': 18, 'rev_growth': 30, 'industry': '医药中游-器械'},
    '乐普医疗': {'price': 12.5, 'pe': 28, 'roe': 15, 'rev_growth': 18, 'industry': '医药中游-器械'},
    '微创医疗': {'price': 8.5, 'pe': 50, 'roe': -5, 'rev_growth': 20, 'industry': '医药中游-器械'},

    # 医药下游
    '爱尔眼科': {'price': 25.8, 'pe': 55, 'roe': 20, 'rev_growth': 25, 'industry': '医药下游-医院'},
    '通策医疗': {'price': 32.5, 'pe': 60, 'roe': 22, 'rev_growth': 20, 'industry': '医药下游-医院'},
    '益丰药房': {'price': 45.0, 'pe': 35, 'roe': 18, 'rev_growth': 25, 'industry': '医药下游-药店'},
    '大参林': {'price': 18.5, 'pe': 30, 'roe': 16, 'rev_growth': 22, 'industry': '医药下游-药店'},
    '老百姓': {'price': 22.5, 'pe': 32, 'roe': 17, 'rev_growth': 23, 'industry': '医药下游-药店'},
    '一心堂': {'price': 18.8, 'pe': 28, 'roe': 15, 'rev_growth': 20, 'industry': '医药下游-药店'},

    # 券商
    '东方财富': {'price': 18.5, 'pe': 50, 'roe': 16, 'rev_growth': 25, 'industry': '券商-数据'},
    '同花顺': {'price': 85.0, 'pe': 55, 'roe': 25, 'rev_growth': 30, 'industry': '券商-数据'},
    '中信证券': {'price': 22.5, 'pe': 20, 'roe': 10, 'rev_growth': 15, 'industry': '券商-经纪'},
    '国泰君安': {'price': 15.8, 'pe': 18, 'roe': 9, 'rev_growth': 12, 'industry': '券商-经纪'},
    '华泰证券': {'price': 14.5, 'pe': 16, 'roe': 10, 'rev_growth': 14, 'industry': '券商-经纪'},
    '中信建投': {'price': 25.8, 'pe': 22, 'roe': 12, 'rev_growth': 18, 'industry': '券商-投行'},
    '中金公司': {'price': 35.0, 'pe': 25, 'roe': 11, 'rev_growth': 15, 'industry': '券商-投行'},

    # 银行
    '招商银行': {'price': 32.5, 'pe': 8, 'roe': 16, 'rev_growth': 10, 'industry': '银行-股份制'},
    '宁波银行': {'price': 28.5, 'pe': 10, 'roe': 18, 'rev_growth': 15, 'industry': '银行-城商行'},
    '杭州银行': {'price': 12.5, 'pe': 8, 'roe': 15, 'rev_growth': 18, 'industry': '银行-城商行'},
    '南京银行': {'price': 9.5, 'pe': 7, 'roe': 14, 'rev_growth': 15, 'industry': '银行-城商行'},
    '渝农商行': {'price': 4.2, 'pe': 6, 'roe': 10, 'rev_growth': 8, 'industry': '银行-农商行'},

    # AI上游
    '寒武纪': {'price': 85.0, 'pe': 0, 'roe': -5, 'rev_growth': 50, 'industry': 'AI上游-芯片'},
    '景嘉微': {'price': 45.0, 'pe': 120, 'roe': 8, 'rev_growth': 30, 'industry': 'AI上游-芯片'},
    '海光信息': {'price': 38.5, 'pe': 80, 'roe': 10, 'rev_growth': 60, 'industry': 'AI上游-芯片'},
    '龙芯中科': {'price': 28.5, 'pe': 200, 'roe': 2, 'rev_growth': 20, 'industry': 'AI上游-芯片'},
    '中科曙光': {'price': 32.5, 'pe': 45, 'roe': 12, 'rev_growth': 35, 'industry': 'AI上游-服务器'},
    '浪潮信息': {'price': 28.5, 'pe': 35, 'roe': 15, 'rev_growth': 40, 'industry': 'AI上游-服务器'},
    '工业富联': {'price': 18.5, 'pe': 25, 'roe': 18, 'rev_growth': 45, 'industry': 'AI上游-服务器'},
    '宝信软件': {'price': 35.0, 'pe': 40, 'roe': 20, 'rev_growth': 25, 'industry': 'AI上游-数据中心'},
    '光环新网': {'price': 8.5, 'pe': 30, 'roe': 12, 'rev_growth': 20, 'industry': 'AI上游-数据中心'},
    '数据港': {'price': 18.5, 'pe': 45, 'roe': 10, 'rev_growth': 30, 'industry': 'AI上游-数据中心'},
    '奥飞数据': {'price': 12.5, 'pe': 50, 'roe': 8, 'rev_growth': 35, 'industry': 'AI上游-数据中心'},

    # AI中游
    '科大讯飞': {'price': 45.0, 'pe': 80, 'roe': 10, 'rev_growth': 30, 'industry': 'AI中游-大模型'},
    '海康威视': {'price': 28.5, 'pe': 30, 'roe': 22, 'rev_growth': 15, 'industry': 'AI中游-应用'},
    '大华股份': {'price': 18.5, 'pe': 25, 'roe': 18, 'rev_growth': 18, 'industry': 'AI中游-应用'},
    '商汤科技': {'price': 2.5, 'pe': 0, 'roe': -30, 'rev_growth': 40, 'industry': 'AI中游-算法'},
    '云从科技': {'price': 8.5, 'pe': 0, 'roe': -20, 'rev_growth': 50, 'industry': 'AI中游-算法'},

    # AI下游
    '用友网络': {'price': 18.5, 'pe': 60, 'roe': 8, 'rev_growth': 15, 'industry': 'AI下游-企业服务'},
    '金山办公': {'price': 285.0, 'pe': 120, 'roe': 25, 'rev_growth': 35, 'industry': 'AI下游-企业服务'},

    # AI硬件上游
    '中天科技': {'price': 18.5, 'pe': 18, 'roe': 15, 'rev_growth': 25, 'industry': 'AI硬件-光纤'},
    '亨通光电': {'price': 22.5, 'pe': 22, 'roe': 14, 'rev_growth': 20, 'industry': 'AI硬件-光纤'},
    '烽火通信': {'price': 25.8, 'pe': 30, 'roe': 12, 'rev_growth': 18, 'industry': 'AI硬件-光纤'},
    '长飞光纤': {'price': 28.5, 'pe': 35, 'roe': 15, 'rev_growth': 22, 'industry': 'AI硬件-光纤'},
    '中际旭创': {'price': 85.0, 'pe': 60, 'roe': 22, 'rev_growth': 60, 'industry': 'AI硬件-光模块'},
    '光迅科技': {'price': 32.5, 'pe': 45, 'roe': 15, 'rev_growth': 35, 'industry': 'AI硬件-光模块'},
    '新易盛': {'price': 45.0, 'pe': 55, 'roe': 20, 'rev_growth': 55, 'industry': 'AI硬件-光模块'},
    '剑桥科技': {'price': 28.5, 'pe': 40, 'roe': 18, 'rev_growth': 45, 'industry': 'AI硬件-光模块'},
    '中航光电': {'price': 42.5, 'pe': 35, 'roe': 20, 'rev_growth': 25, 'industry': 'AI硬件-连接器'},
    '航天电器': {'price': 35.0, 'pe': 40, 'roe': 18, 'rev_growth': 22, 'industry': 'AI硬件-连接器'},
    '英维克': {'price': 38.5, 'pe': 50, 'roe': 16, 'rev_growth': 40, 'industry': 'AI硬件-散热'},
    '兆易创新': {'price': 95.0, 'pe': 60, 'roe': 18, 'rev_growth': 30, 'industry': 'AI硬件-存储'},
    '澜起科技': {'price': 65.0, 'pe': 55, 'roe': 20, 'rev_growth': 40, 'industry': 'AI硬件-存储'},
    '紫光国微': {'price': 58.0, 'pe': 45, 'roe': 22, 'rev_growth': 35, 'industry': 'AI硬件-FPGA'},
    '复旦微电': {'price': 45.0, 'pe': 70, 'roe': 15, 'rev_growth': 30, 'industry': 'AI硬件-FPGA'},

    # AI应用
    '海康威视': {'price': 28.5, 'pe': 30, 'roe': 22, 'rev_growth': 15, 'industry': 'AI中游-应用'},
    '大华股份': {'price': 18.5, 'pe': 25, 'roe': 18, 'rev_growth': 18, 'industry': 'AI中游-应用'},
    '科大讯飞': {'price': 45.0, 'pe': 80, 'roe': 10, 'rev_growth': 30, 'industry': 'AI中游-大模型'},
    '商汤科技': {'price': 2.5, 'pe': 0, 'roe': -30, 'rev_growth': 40, 'industry': 'AI中游-算法'},
    '云从科技': {'price': 8.5, 'pe': 0, 'roe': -20, 'rev_growth': 50, 'industry': 'AI中游-算法'},

    # 电力
    '长江电力': {'price': 28.5, 'pe': 22, 'roe': 16, 'rev_growth': 10, 'industry': '电力-水电'},
    '华能水电': {'price': 8.5, 'pe': 18, 'roe': 14, 'rev_growth': 8, 'industry': '电力-水电'},
    '国投电力': {'price': 12.5, 'pe': 20, 'roe': 12, 'rev_growth': 10, 'industry': '电力-水电'},
    '川投能源': {'price': 15.8, 'pe': 18, 'roe': 14, 'rev_growth': 12, 'industry': '电力-水电'},
    '华电国际': {'price': 5.5, 'pe': 15, 'roe': 8, 'rev_growth': 5, 'industry': '电力-火电'},
    '国电电力': {'price': 4.5, 'pe': 12, 'roe': 10, 'rev_growth': 6, 'industry': '电力-火电'},
    '大唐发电': {'price': 3.8, 'pe': 18, 'roe': 6, 'rev_growth': 4, 'industry': '电力-火电'},
    '华能国际': {'price': 8.5, 'pe': 20, 'roe': 5, 'rev_growth': 3, 'industry': '电力-火电'},
    '三峡能源': {'price': 6.5, 'pe': 25, 'roe': 12, 'rev_growth': 25, 'industry': '电力-风电'},
    '龙源电力': {'price': 18.5, 'pe': 22, 'roe': 14, 'rev_growth': 20, 'industry': '电力-风电'},
    '金风科技': {'price': 8.5, 'pe': 28, 'roe': 10, 'rev_growth': 18, 'industry': '电力-风电'},
    '明阳智能': {'price': 12.5, 'pe': 25, 'roe': 12, 'rev_growth': 22, 'industry': '电力-风电'},
    '节能风电': {'price': 4.5, 'pe': 30, 'roe': 8, 'rev_growth': 20, 'industry': '电力-风电'},
    '太阳能': {'price': 8.5, 'pe': 25, 'roe': 10, 'rev_growth': 25, 'industry': '电力-光伏发电'},
    '林洋能源': {'price': 7.5, 'pe': 22, 'roe': 12, 'rev_growth': 18, 'industry': '电力-光伏发电'},
    '特变电工': {'price': 22.5, 'pe': 12, 'roe': 18, 'rev_growth': 30, 'industry': '电力-特高压'},
    '国电南瑞': {'price': 28.5, 'pe': 35, 'roe': 18, 'rev_growth': 20, 'industry': '电力-电网'},
    '许继电气': {'price': 18.5, 'pe': 30, 'roe': 15, 'rev_growth': 22, 'industry': '电力-电网'},
    '平高电气': {'price': 12.5, 'pe': 35, 'roe': 12, 'rev_growth': 25, 'industry': '电力-电网'},
    '思源电气': {'price': 25.8, 'pe': 32, 'roe': 16, 'rev_growth': 18, 'industry': '电力-电网'},
    '涪陵电力': {'price': 15.8, 'pe': 25, 'roe': 15, 'rev_growth': 20, 'industry': '电力-电网'},
}


def analyze_supply_chain():
    """分析产业链并筛选股票"""
    print('=' * 70)
    print('  产业链投资分析系统 v2.0')
    print('=' * 70)
    print()

    # 筛选0-30元股票
    print('【一】0-30元低价股票筛选')
    print('-' * 70)
    print()

    low_price_stocks = []
    for stock, data in STOCK_DATA.items():
        if data['price'] <= 30 and data['price'] > 0:
            low_price_stocks.append((stock, data))

    # 按价格排序
    low_price_stocks.sort(key=lambda x: x[1]['price'])

    print(f'共筛选出 {len(low_price_stocks)} 只0-30元股票:')
    print()
    print('| 股票 | 价格 | PE | ROE | 营收增长 | 行业 |')
    print('|------|------|----|----|---------|------|')
    for stock, data in low_price_stocks:
        print(f'| {stock} | {data["price"]:.1f} | {data["pe"]} | {data["roe"]}% | {data["rev_growth"]}% | {data["industry"]} |')

    print()

    # 按行业分类分析
    print('=' * 70)
    print('【二】产业链投资价值分析')
    print('=' * 70)
    print()

    for industry, chain in FULL_INDUSTRY_CHAINS.items():
        print(f'## {industry}: {chain["描述"]}')
        print()

        for stage, contents in chain.items():
            if stage == '描述':
                continue

            print(f'### {stage}')
            print()

            # 筛选该阶段的低价股
            stage_stocks = []
            for category, stocks in contents.items():
                for stock in stocks:
                    if stock in STOCK_DATA:
                        data = STOCK_DATA[stock]
                        if data['price'] <= 30:
                            stage_stocks.append((stock, data, category))

            if stage_stocks:
                print(f'| 股票 | 价格 | PE | ROE | 营收增长 | 细分 |')
                print('|------|------|----|----|---------|------|')
                for stock, data, category in stage_stocks:
                    print(f'| {stock} | {data["price"]:.1f} | {data["pe"]} | {data["roe"]}% | {data["rev_growth"]}% | {category} |')
            else:
                print('该阶段无符合条件的低价股')
            print()

    # 投资价值评估
    print('=' * 70)
    print('【三】投资价值综合评估')
    print('=' * 70)
    print()

    # 综合评分公式: 成长性(40%) + 盈利能力(30%) + 估值(30%)
    def calculate_score(data):
        growth_score = min(data['rev_growth'] / 100 * 100, 40)  # 成长性满分40
        profit_score = (data['roe'] / 30) * 30 if data['roe'] > 0 else 0  # 盈利能力满分30
        pe_score = max(0, (30 - data['pe']) / 30 * 30) if data['pe'] < 60 else 0  # 估值满分30

        # 负面扣分
        if data['roe'] < 0:
            profit_score = -10

        return growth_score + profit_score + pe_score

    # 分类评估
    categories = {
        '新能源车上游': [],
        '新能源车中游': [],
        '新能源车下游': [],
        'AI硬件': [],
        '电力': [],
        '半导体上游': [],
        '半导体中游': [],
        '光伏上游': [],
        '光伏中游': [],
        '医药上游': [],
        '医药中游': [],
        '医药下游': [],
        '白酒': [],
        '券商': [],
        '银行': []
    }

    for stock, data in STOCK_DATA.items():
        if data['price'] <= 30:
            score = calculate_score(data)
            # 处理行业分类键
            ind_category = data['industry'].split('-')[0]
            if ind_category in categories:
                categories[ind_category].append((stock, data, score))

    print('| 产业阶段 | 推荐股票 | 综合评分 | 投资逻辑 |')
    print('|----------|---------|---------|----------|')

    recommendations = []

    # 上游优先(资源为王)
    for cat in ['新能源车上游', '半导体上游', '光伏上游']:
        if categories.get(cat):
            top = sorted(categories[cat], key=lambda x: x[2], reverse=True)[:3]
            for stock, data, score in top:
                if score > 30:  # 只推荐评分>30的
                    logic = get_investment_logic(data)
                    print(f'| {cat} | {stock} | {score:.1f} | {logic} |')
                    recommendations.append((stock, data, score))

    print()

    # 中游筛选
    for cat in ['新能源车中游', '半导体中游', '光伏中游', '医药中游']:
        if categories.get(cat):
            top = sorted(categories[cat], key=lambda x: x[2], reverse=True)[:3]
            for stock, data, score in top:
                if score > 30:
                    logic = get_investment_logic(data)
                    print(f'| {cat} | {stock} | {score:.1f} | {logic} |')
                    recommendations.append((stock, data, score))

    print()

    # 下游筛选
    for cat in ['新能源车下游', '医药下游', '白酒中游']:
        if categories.get(cat):
            top = sorted(categories[cat], key=lambda x: x[2], reverse=True)[:2]
            for stock, data, score in top:
                if score > 25:
                    logic = get_investment_logic(data)
                    print(f'| {cat} | {stock} | {score:.1f} | {logic} |')
                    recommendations.append((stock, data, score))

    print()

    # 最终推荐
    print('=' * 70)
    print('【四】最终投资建议(0-30元)')
    print('=' * 70)
    print()

    # 按综合评分排序
    recommendations.sort(key=lambda x: x[2], reverse=True)
    top_recommendations = recommendations[:15]

    print('**短线机会(高成长低估值)**')
    print()
    short_term = [(s, d, sc) for s, d, sc in top_recommendations
                  if d['rev_growth'] > 40 and d['pe'] < 30 and sc > 35]
    for stock, data, score in short_term[:5]:
        print(f'- {stock}: 涨幅{data["rev_growth"]}%, PE={data["pe"]}, 评分{score:.1f}')

    print()
    print('**中线配置(稳健增长)**')
    print()
    mid_term = [(s, d, sc) for s, d, sc in top_recommendations
                if 20 < d['rev_growth'] <= 50 and d['roe'] > 15 and sc > 30]
    for stock, data, score in mid_term[:5]:
        print(f'- {stock}: ROE {data["roe"]}%, 估值合理, 评分{score:.1f}')

    print()
    print('**价值投资(低估值高分红)**')
    print()
    value_inv = [(s, d, sc) for s, d, sc in top_recommendations
                 if d['pe'] < 15 and d['roe'] > 12 and sc > 25]
    for stock, data, score in value_inv[:5]:
        print(f'- {stock}: PE={data["pe"]}, ROE={data["roe"]}%, 评分{score:.1f}')

    print()
    print('=' * 70)
    print('【五】重点关注股票池')
    print('=' * 70)
    print()

    print('| 股票 | 价格 | PE | ROE | 增长 | 行业 | 评分 | 建议 |')
    print('|------|------|----|----|------|------|-----|------|')
    for stock, data, score in top_recommendations[:15]:
        # 建议
        if score >= 40:
            action = '强烈推荐'
        elif score >= 35:
            action = '推荐买入'
        elif score >= 30:
            action = '关注'
        else:
            action = '观望'

        print(f'| {stock} | {data["price"]:.1f} | {data["pe"]} | {data["roe"]}% | {data["rev_growth"]}% | {data["industry"]} | {score:.1f} | {action} |')

    print()
    print('=' * 70)
    print('系统分析完成')
    print('=' * 70)


def get_investment_logic(data):
    """生成投资逻辑"""
    logic = []

    if data['rev_growth'] > 50:
        logic.append('高成长')
    elif data['rev_growth'] > 20:
        logic.append('稳健增长')

    if data['roe'] > 20:
        logic.append('强盈利')
    elif data['roe'] > 15:
        logic.append('良好盈利')

    if data['pe'] < 20:
        logic.append('低估')
    elif data['pe'] > 50:
        logic.append('高估')

    return ', '.join(logic) if logic else '一般'


if __name__ == '__main__':
    analyze_supply_chain()