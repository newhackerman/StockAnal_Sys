# -*- coding: utf-8 -*-
"""
股票查询配置文件
"""

# API配置
API_CONFIG = {
    # 查询超时时间（秒）
    'timeout': 5,
    
    # 重试次数
    'retry_count': 3,
    
    # 请求间隔（秒）
    'request_interval': 0.5,
    
    # User-Agent
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# API端点配置
API_ENDPOINTS = {
    # A股查询API
    'a_stock': {
        'sina_suggest': 'https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15&key={}',
        'tencent_search': 'http://smartbox.gtimg.cn/s3/?q={}&t=gp'
    },
    
    # 港股查询API
    'hk_stock': {
        'tencent': 'http://qt.gtimg.cn/q=s_hk{}',
        'sina': 'http://hq.sinajs.cn/list=hk{}'
    },
    
    # 美股查询API
    'us_stock': {
        'yahoo': 'https://query1.finance.yahoo.com/v1/finance/search?q={}&quotesCount=1&newsCount=0',
        'alpha_vantage': 'https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={}&apikey={}'
    }
}

# 市场代码映射
MARKET_MAPPING = {
    '11': 'CN',  # 深圳A股
    '12': 'CN',  # 上海A股
    '13': 'CN',  # 创业板
    '14': 'CN',  # 科创板
    '15': 'CN',  # 北交所
    '31': 'HK',  # 港股
    '32': 'HK',  # 港股
    'US': 'US'   # 美股
}

# 数据文件配置
DATA_CONFIG = {
    'file_path': './data/ALL_STOCK_LIST.csv',
    'backup_path': './data/backup/',
    'encoding': 'utf8',
    'separator': ',',
    'columns': ['code', 'name', 'market', 'Industry']
}

# 日志配置
LOG_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': './logs/stock_query.log'
}
# 安全配置
SECURITY_CONFIG = {
    # 输入验证
    'max_query_length': 50,
    'allowed_chars_pattern': r'^[a-zA-Z0-9\u4e00-\u9fff.]+$',
    
    # 网络安全
    'ssl_verify': True,
    'max_redirects': 3,
    'max_response_size': 1024 * 1024,  # 1MB
    
    # 速率限制
    'rate_limit_requests': 100,
    'rate_limit_window': 3600,  # 1小时
    
    # 文件安全
    'max_file_size': 100 * 1024 * 1024,  # 100MB
    'allowed_file_extensions': {'.csv', '.log', '.json'},
    
    # 日志安全
    'log_sensitive_data': False,
    'log_max_length': 200
}
