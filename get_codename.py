# -*- coding: utf-8 -*-
import pandas as pd
import requests
import json
import os
import time
from datetime import datetime
import logging
from stock_config import API_CONFIG, API_ENDPOINTS, MARKET_MAPPING, DATA_CONFIG, LOG_CONFIG

# 配置日志
os.makedirs('./logs', exist_ok=True)
logging.basicConfig(
    level=getattr(logging, LOG_CONFIG['level']),
    format=LOG_CONFIG['format'],
    handlers=[
        logging.FileHandler(LOG_CONFIG['file'], encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 数据文件路径
DATA_FILE = DATA_CONFIG['file_path']

# 加载静态数据
def load_static_data():
    """加载静态股票数据"""
    try:
        if os.path.exists(DATA_FILE):
            allstockinfo = pd.read_csv(
                DATA_FILE, 
                sep=DATA_CONFIG['separator'], 
                encoding=DATA_CONFIG['encoding']
            )
            # 确保代码和名称都是字符串类型
            allstockinfo['code'] = allstockinfo['code'].astype(str)
            allstockinfo['name'] = allstockinfo['name'].astype(str)
            return dict(zip(allstockinfo['code'].to_list(), allstockinfo['name'].to_list()))
        else:
            logger.warning(f"静态数据文件不存在: {DATA_FILE}")
            # 创建空的数据文件
            os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
            empty_df = pd.DataFrame(columns=DATA_CONFIG['columns'])
            empty_df.to_csv(DATA_FILE, sep=DATA_CONFIG['separator'], 
                          encoding=DATA_CONFIG['encoding'], index=False)
            return {}
    except Exception as e:
        logger.error(f"加载静态数据失败: {e}")
        return {}

# 初始化静态数据
codename = load_static_data()

def validate_stock_query(query):
    """验证股票查询输入"""
    if not query:
        raise ValueError("查询参数不能为空")
    
    query_str = str(query).strip()
    
    # 长度限制
    if len(query_str) > 50:
        raise ValueError("查询参数过长")
    
    # 字符验证 - 只允许字母、数字、中文、点号
    import re
    if not re.match(r'^[a-zA-Z0-9一-鿿.]+$', query_str):
        raise ValueError("包含非法字符")
    
    return query_str

def sanitize_log_data(data):
    """敏感信息脱敏"""
    data_str = str(data)
    if len(data_str) > 20:
        return data_str[:8] + "***" + data_str[-4:]
    return data_str

# 实时查询股票信息的API接口
class StockInfoFetcher:
    """股票信息实时查询器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.verify = True  # 启用SSL验证
        self.session.headers.update({
            'User-Agent': API_CONFIG['user_agent']
        })
        self.timeout = API_CONFIG['timeout']
        self.retry_count = API_CONFIG['retry_count']
        self.request_interval = API_CONFIG['request_interval']
    
    def _make_request(self, url, encoding='utf-8'):
        """统一的请求方法，包含重试机制"""
        for attempt in range(self.retry_count):
            try:
                time.sleep(self.request_interval)
                response = self.session.get(url, timeout=self.timeout)
                response.encoding = encoding
                
                if response.status_code == 200:
                    return response
                else:
                    logger.warning(f"请求失败，状态码: {response.status_code}, 尝试 {attempt + 1}/{self.retry_count}")
                    
            except Exception as e:
                logger.warning(f"请求异常: {e}, 尝试 {attempt + 1}/{self.retry_count}")
                if attempt < self.retry_count - 1:
                    time.sleep(1)  # 重试前等待
        return None
    
    def search_a_stock(self, query):
        """查询A股信息"""
        # 尝试新浪API
        try:
            from urllib.parse import quote
            url = API_ENDPOINTS['a_stock']['sina_suggest'].format(quote(str(query), safe=''))
            response = self._make_request(url, 'gbk')
            
            if response:
                content = response.text.strip()
                if content and content != 'var suggestvalue="";':
                    # 解析返回数据
                    data = content.split('"')[1]
                    if data:
                        items = data.split(';')
                        for item in items:
                            if item:
                                parts = item.split(',')
                                if len(parts) >= 6:
                                    code = parts[3]
                                    name = parts[4]
                                    market_type = parts[0]
                                    
                                    # 判断市场类型
                                    market = MARKET_MAPPING.get(market_type, 'CN')
                                    
                                    return {
                                        'code': code,
                                        'name': name,
                                        'market': market,
                                        'Industry': '未知'
                                    }
        except Exception as e:
            logger.debug(f"新浪API查询失败: {e}")
        
        # 尝试腾讯API作为备用
        try:
            url = API_ENDPOINTS['a_stock']['tencent_search'].format(quote(str(query), safe=''))
            response = self._make_request(url, 'gbk')
            
            if response:
                content = response.text.strip()
                if content and 'v_hint' in content:
                    # 解析腾讯API返回的数据
                    data = content.split('="')[1].split('";')[0]
                    if data:
                        items = data.split('^')
                        for item in items:
                            if item:
                                parts = item.split('~')
                                if len(parts) >= 3:
                                    code = parts[1]
                                    name = parts[2]
                                    
                                    return {
                                        'code': code,
                                        'name': name,
                                        'market': 'CN',
                                        'Industry': '未知'
                                    }
        except Exception as e:
            logger.debug(f"腾讯API查询失败: {e}")
        
        return None
    
    def search_hk_stock(self, query):
        """查询港股信息"""
        try:
            # 确保港股代码格式正确
            hk_code = query.zfill(5) if query.isdigit() else query
            
            # 使用腾讯财经API查询港股
            url = API_ENDPOINTS['hk_stock']['tencent'].format(quote(str(hk_code), safe=''))
            response = self._make_request(url, 'gbk')
            
            if response:
                content = response.text.strip()
                if content and 'v_s_hk' in content:
                    # 解析数据
                    data = content.split('="')[1].split('";')[0]
                    parts = data.split('~')
                    if len(parts) > 1 and parts[1]:
                        return {
                            'code': hk_code,
                            'name': parts[1],
                            'market': 'HK',
                            'Industry': '未知'
                        }
        except Exception as e:
            logger.error(f"港股查询失败: {e}")
        return None
    
    def search_us_stock(self, query):
        """查询美股信息"""
        try:
            # 使用Yahoo Finance API查询美股
            url = API_ENDPOINTS['us_stock']['yahoo'].format(quote(str(query), safe=''))
            response = self._make_request(url)
            
            if response:
                data = response.json()
                if 'quotes' in data and data['quotes']:
                    quote = data['quotes'][0]
                    return {
                        'code': quote.get('symbol', query).upper(),
                        'name': quote.get('longname', quote.get('shortname', '未知')),
                        'market': 'US',
                        'Industry': quote.get('sector', '未知')
                    }
        except Exception as e:
            logger.error(f"美股查询失败: {e}")
        return None
    
    def search_stock_info(self, query):
        """综合查询股票信息"""
        # 首先尝试A股查询
        result = self.search_a_stock(query)
        if result:
            return result
        
        # 如果是数字开头，可能是港股
        if query.isdigit() and len(query) <= 5:
            result = self.search_hk_stock(query.zfill(5))
            if result:
                return result
        
        # 最后尝试美股查询
        result = self.search_us_stock(query)
        if result:
            return result
        
        return None

# 全局查询器实例
fetcher = StockInfoFetcher()

def backup_data_file():
    """备份数据文件"""
    try:
        if os.path.exists(DATA_FILE):
            backup_dir = DATA_CONFIG['backup_path']
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = os.path.join(backup_dir, f'ALL_STOCK_LIST_{timestamp}.csv')
            
            import shutil
            shutil.copy2(DATA_FILE, backup_file)
            logger.info(f"数据文件已备份到: {backup_file}")
            return True
    except Exception as e:
        logger.error(f"备份数据文件失败: {e}")
    return False

def update_static_data(code, name, market='CN', industry='未知'):
    """更新静态数据文件"""
    try:
        # 读取现有数据
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(
                DATA_FILE, 
                sep=DATA_CONFIG['separator'], 
                encoding=DATA_CONFIG['encoding']
            )
        else:
            df = pd.DataFrame(columns=DATA_CONFIG['columns'])
        
        # 检查是否已存在
        if code not in df['code'].values:
            # 每100条新记录备份一次
            if len(df) % 100 == 0 and len(df) > 0:
                backup_data_file()
            
            # 添加新记录
            new_row = pd.DataFrame({
                'code': [code],
                'name': [name],
                'market': [market],
                'Industry': [industry]
            })
            df = pd.concat([df, new_row], ignore_index=True)
            
            # 保存到文件
            df.to_csv(
                DATA_FILE, 
                sep=DATA_CONFIG['separator'], 
                encoding=DATA_CONFIG['encoding'], 
                index=False
            )
            
            # 更新内存中的数据
            global codename
            codename[code] = name
            
            logger.info(f"已添加新股票: {code} - {name} ({market})")
            return True
        else:
            logger.debug(f"股票已存在: {code} - {name}")
            return False
    except Exception as e:
        logger.error(f"更新静态数据失败: {e}")
    return False

def get_codename(data, *kwords, enable_realtime=True):
    """
    获取股票代码或名称
    
    Args:
        data: 股票代码或名称
        *kwords: 可选参数，'name' 返回名称，'code' 返回代码
        enable_realtime: 是否启用实时查询，默认True
    
    Returns:
        股票代码或名称，如果找不到则返回None
    """
    if data is None:
        return None
    
    # 输入验证
    try:
        validated_data = validate_stock_query(data)
    except ValueError as e:
        logger.warning(f"输入验证失败: {e}")
        return None
    
    data = validated_data
    
    # 首先在静态数据中查找
    def search_in_static(query, return_type=None):
        for key, value in codename.items():
            if str(query) == str(key) or str(query) == str(value):
                if return_type == 'name':
                    return str(value)
                elif return_type == 'code':
                    return str(key)
                else:
                    return str(key)  # 默认返回代码
        return None
    
    # 在静态数据中查找
    if len(kwords) > 0:
        retname = kwords[0]
        result = search_in_static(data, retname)
        if result:
            return result
    else:
        result = search_in_static(data)
        if result:
            return result
    
    # 如果静态数据中找不到且启用实时查询，进行实时查询
    if enable_realtime:
        logger.info(f"静态数据中未找到 '{sanitize_log_data(data)}'，开始实时查询...")
        
        try:
            stock_info = fetcher.search_stock_info(str(data))
            if stock_info:
                # 更新静态数据
                update_static_data(
                    stock_info['code'],
                    stock_info['name'],
                    stock_info['market'],
                    stock_info['Industry']
                )
                
                # 返回请求的数据
                if len(kwords) > 0:
                    retname = kwords[0]
                    if retname == 'name':
                        return stock_info['name']
                    elif retname == 'code':
                        return stock_info['code']
                else:
                    return stock_info['code']
            else:
                logger.warning(f"实时查询也未找到股票信息: {sanitize_log_data(data)}")
                return None
                
        except Exception as e:
            logger.error(f"实时查询出错: {e}")
            return None
    else:
        logger.debug(f"实时查询已禁用，未找到股票信息: {data}")
        return None
def reload_static_data():
    """重新加载静态数据"""
    global codename
    codename = load_static_data()
    logger.info("静态数据已重新加载")

def get_stock_count():
    """获取当前股票数量"""
    return len(codename)

def search_stocks(keyword, limit=10):
    """
    模糊搜索股票
    
    Args:
        keyword: 搜索关键词
        limit: 返回结果数量限制
    
    Returns:
        匹配的股票列表
    """
    results = []
    keyword = str(keyword).lower()
    
    for code, name in codename.items():
        try:
            code_str = str(code).lower()
            name_str = str(name).lower()
            
            if (keyword in code_str or keyword in name_str):
                results.append({'code': str(code), 'name': str(name)})
                if len(results) >= limit:
                    break
        except Exception as e:
            logger.debug(f"搜索时跳过异常数据: {code}, {name}, 错误: {e}")
            continue
    
    return results

if __name__ == '__main__':
    # 测试现有股票
    print("=== 测试现有股票 ===")
    print(f"长电科技代码: {get_codename('长电科技', 'code')}")
    print(f"00981名称: {get_codename('00981', 'name')}")
    
    # 测试新股票（实时查询）
    print("\n=== 测试实时查询 ===")
    print(f"测试A股 - 比亚迪代码: {get_codename('比亚迪', 'code')}")
    print(f"测试港股 - 00700名称: {get_codename('00700', 'name')}")
    print(f"测试美股 - AAPL名称: {get_codename('AAPL', 'name')}")
    
    # 显示当前股票数量
    print(f"\n当前股票数量: {get_stock_count()}")
    
    # 测试模糊搜索
    print("\n=== 模糊搜索测试 ===")
    results = search_stocks('科技', 5)
    for result in results:
        print(f"{result['code']} - {result['name']}")
    
    print("\n优化完成！现在支持实时查询和自动更新静态文件。")

