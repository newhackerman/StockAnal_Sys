#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全工具模块
提供各种安全相关的工具函数
"""

import re
import os
import hashlib
import time
from functools import wraps
from urllib.parse import quote
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """安全验证器"""
    
    @staticmethod
    def validate_stock_query(query):
        """验证股票查询输入"""
        if not query:
            raise ValueError("查询参数不能为空")
        
        query_str = str(query).strip()
        
        # 长度限制
        if len(query_str) > 50:
            raise ValueError("查询参数过长")
        
        # 字符验证
        if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fff.]+$', query_str):
            raise ValueError("包含非法字符")
        
        return query_str
    
    @staticmethod
    def validate_file_path(filepath, base_dir="."):
        """验证文件路径，防止目录遍历"""
        abs_base = os.path.abspath(base_dir)
        abs_path = os.path.abspath(filepath)
        
        if not abs_path.startswith(abs_base):
            raise ValueError("路径遍历攻击检测")
        
        return abs_path
    
    @staticmethod
    def sanitize_url_param(param):
        """安全的URL参数编码"""
        return quote(str(param), safe='')

class SecurityLogger:
    """安全日志记录器"""
    
    @staticmethod
    def sanitize_data(data, max_length=20):
        """敏感信息脱敏"""
        data_str = str(data)
        if len(data_str) > max_length:
            return data_str[:8] + "***" + data_str[-4:]
        return data_str
    
    @staticmethod
    def hash_sensitive_data(data):
        """对敏感数据进行哈希处理"""
        return hashlib.sha256(str(data).encode()).hexdigest()[:8]

class RateLimiter:
    """简单的速率限制器"""
    
    def __init__(self, max_requests=100, window=3600):
        self.max_requests = max_requests
        self.window = window
        self.requests = {}
    
    def is_allowed(self, client_id):
        """检查是否允许请求"""
        now = time.time()
        
        # 清理过期记录
        self.requests = {
            k: v for k, v in self.requests.items() 
            if now - v['first_request'] < self.window
        }
        
        if client_id not in self.requests:
            self.requests[client_id] = {
                'count': 1,
                'first_request': now
            }
            return True
        
        if self.requests[client_id]['count'] >= self.max_requests:
            return False
        
        self.requests[client_id]['count'] += 1
        return True

def rate_limit(max_requests=100, window=3600):
    """速率限制装饰器"""
    limiter = RateLimiter(max_requests, window)
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 使用函数名作为客户端ID（简化版）
            client_id = func.__name__
            
            if not limiter.is_allowed(client_id):
                raise Exception("请求频率过高，请稍后重试")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

def secure_request_headers():
    """生成安全的请求头"""
    return {
        'User-Agent': 'StockAnalysis/1.0 (Security Enhanced)',
        'Accept': 'application/json,text/html',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'close'
    }
