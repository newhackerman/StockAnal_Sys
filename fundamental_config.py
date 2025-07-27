#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本面分析配置文件
用户可以根据需要调整数据源优先级和API配置
"""

# 数据源配置
DATA_SOURCES = {
    'A': ['akshare', 'eastmoney', 'sina'],  # A股数据源优先级
    'HK': ['yfinance', 'akshare', 'yahoo'],  # 港股数据源优先级
    'US': ['yfinance', 'yahoo', 'alpha_vantage']  # 美股数据源优先级
}

# API配置
API_CONFIG = {
    'eastmoney_base': 'http://push2.eastmoney.com/api/qt/stock/get',
    'sina_base': 'http://hq.sinajs.cn/list=',
    'yahoo_base': 'https://query1.finance.yahoo.com/v8/finance/chart/',
    'alpha_vantage_key': None,  # 请在这里填入您的Alpha Vantage API密钥
    'finnhub_key': None,  # 请在这里填入您的Finnhub API密钥
    'quandl_key': None  # 请在这里填入您的Quandl API密钥
}

# 缓存配置
CACHE_CONFIG = {
    'financial_indicators': 600,  # 财务指标缓存时间（秒）
    'growth_data': 900,          # 成长数据缓存时间（秒）
    'hk_data': 300,              # 港股数据缓存时间（秒）
    'us_data': 600               # 美股数据缓存时间（秒）
}

# 请求配置
REQUEST_CONFIG = {
    'timeout': 10,               # 请求超时时间（秒）
    'max_retries': 3,           # 最大重试次数
    'retry_delay': 2,           # 重试延迟（秒）
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# 数据质量配置
QUALITY_CONFIG = {
    'min_indicators_for_high_quality': 5,  # 高质量数据的最小指标数量
    'min_indicators_for_medium_quality': 3,  # 中等质量数据的最小指标数量
    'enable_data_validation': True,  # 是否启用数据验证
    'max_pe_ratio': 1000,  # PE比率的最大合理值
    'max_pb_ratio': 100,   # PB比率的最大合理值
    'min_roe': -100,       # ROE的最小合理值
    'max_roe': 100         # ROE的最大合理值
}

# 评分配置
SCORING_CONFIG = {
    'valuation_weight': 0.3,    # 估值评分权重
    'financial_weight': 0.4,    # 财务健康评分权重
    'growth_weight': 0.3,       # 成长性评分权重
    'enable_market_adjustment': True,  # 是否启用市场调整
    'hk_score_adjustment': 0.8,  # 港股评分调整系数
    'us_score_adjustment': 1.0   # 美股评分调整系数
}

# 日志配置
LOGGING_CONFIG = {
    'enable_debug': True,        # 是否启用调试日志
    'log_api_calls': True,       # 是否记录API调用
    'log_cache_hits': False,     # 是否记录缓存命中
    'log_data_quality': True     # 是否记录数据质量信息
}

def get_config():
    """获取完整配置"""
    return {
        'data_sources': DATA_SOURCES,
        'api_config': API_CONFIG,
        'cache_config': CACHE_CONFIG,
        'request_config': REQUEST_CONFIG,
        'quality_config': QUALITY_CONFIG,
        'scoring_config': SCORING_CONFIG,
        'logging_config': LOGGING_CONFIG
    }

def update_api_key(service, key):
    """更新API密钥"""
    if service in API_CONFIG:
        API_CONFIG[service] = key
        print(f"已更新 {service} API密钥")
    else:
        print(f"未知服务: {service}")

def set_data_source_priority(market, sources):
    """设置数据源优先级"""
    if market in DATA_SOURCES:
        DATA_SOURCES[market] = sources
        print(f"已更新 {market} 市场数据源优先级: {sources}")
    else:
        print(f"未知市场: {market}")

# 使用示例
if __name__ == "__main__":
    print("基本面分析配置")
    print("=" * 40)
    
    config = get_config()
    
    print("当前数据源配置:")
    for market, sources in config['data_sources'].items():
        print(f"  {market}: {sources}")
    
    print("\nAPI配置状态:")
    for service, key in config['api_config'].items():
        if 'key' in service:
            status = "已配置" if key else "未配置"
            print(f"  {service}: {status}")
    
    print("\n配置修改示例:")
    print("# 更新Alpha Vantage API密钥")
    print("update_api_key('alpha_vantage_key', 'YOUR_API_KEY')")
    
    print("\n# 调整A股数据源优先级")
    print("set_data_source_priority('A', ['eastmoney', 'akshare', 'sina'])")
    
    print("\n# 禁用某个数据源")
    print("set_data_source_priority('US', ['yfinance', 'yahoo'])")  # 移除alpha_vantage