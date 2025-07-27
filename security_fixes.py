#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
安全修复脚本
自动修复代码中的安全问题
"""

import re
import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """备份原文件"""
    backup_path = f"{filepath}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(filepath, backup_path)
    print(f"✅ 已备份: {filepath} -> {backup_path}")
    return backup_path

def fix_get_codename_security():
    """修复get_codename.py的安全问题"""
    filepath = "get_codename.py"
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. 添加输入验证函数
    input_validation = '''
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
    if not re.match(r'^[a-zA-Z0-9\u4e00-\u9fff.]+$', query_str):
        raise ValueError("包含非法字符")
    
    return query_str

def sanitize_log_data(data):
    """敏感信息脱敏"""
    data_str = str(data)
    if len(data_str) > 20:
        return data_str[:8] + "***" + data_str[-4:]
    return data_str

'''
    
    # 2. 在类定义前插入验证函数
    class_pattern = r'(# 实时查询股票信息的API接口\nclass StockInfoFetcher:)'
    content = re.sub(class_pattern, input_validation + r'\1', content)
    
    # 3. 修复URL构造安全问题
    url_fixes = [
        (
            r"url = API_ENDPOINTS\['a_stock'\]\['sina_suggest'\]\.format\(query\)",
            "from urllib.parse import quote\n            url = API_ENDPOINTS['a_stock']['sina_suggest'].format(quote(str(query), safe=''))"
        ),
        (
            r"url = API_ENDPOINTS\['a_stock'\]\['tencent_search'\]\.format\(query\)",
            "url = API_ENDPOINTS['a_stock']['tencent_search'].format(quote(str(query), safe=''))"
        ),
        (
            r"url = API_ENDPOINTS\['hk_stock'\]\['tencent'\]\.format\(hk_code\)",
            "url = API_ENDPOINTS['hk_stock']['tencent'].format(quote(str(hk_code), safe=''))"
        ),
        (
            r"url = API_ENDPOINTS\['us_stock'\]\['yahoo'\]\.format\(query\)",
            "url = API_ENDPOINTS['us_stock']['yahoo'].format(quote(str(query), safe=''))"
        )
    ]
    
    for pattern, replacement in url_fixes:
        content = re.sub(pattern, replacement, content)
    
    # 4. 添加SSL验证
    session_init = r"(self\.session = requests\.Session\(\))"
    ssl_config = r"\1\n        self.session.verify = True  # 启用SSL验证"
    content = re.sub(session_init, ssl_config, content)
    
    # 5. 修复get_codename函数的输入验证
    get_codename_pattern = r'(def get_codename\(data, \*kwords, enable_realtime=True\):.*?if data is None:\s+return None)'
    get_codename_replacement = r'''\1
    
    # 输入验证
    try:
        validated_data = validate_stock_query(data)
    except ValueError as e:
        logger.warning(f"输入验证失败: {e}")
        return None
    
    data = validated_data'''
    
    content = re.sub(get_codename_pattern, get_codename_replacement, content, flags=re.DOTALL)
    
    # 6. 修复日志中的敏感信息
    log_patterns = [
        (
            r"logger\.info\(f\"静态数据中未找到 '\{data\}'，开始实时查询\.\.\.\"\)",
            "logger.info(f\"静态数据中未找到 '{sanitize_log_data(data)}'，开始实时查询...\")"
        ),
        (
            r"logger\.warning\(f\"实时查询也未找到股票信息: \{data\}\"\)",
            "logger.warning(f\"实时查询也未找到股票信息: {sanitize_log_data(data)}\")"
        )
    ]
    
    for pattern, replacement in log_patterns:
        content = re.sub(pattern, replacement, content)
    
    # 保存修复后的文件
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复: {filepath}")
    return True

def fix_install_dependencies_security():
    """修复install_dependencies.py的安全问题"""
    filepath = "install_dependencies.py"
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修复subprocess shell注入
    shell_pattern = r'subprocess\.run\(command, shell=True,'
    shell_replacement = 'subprocess.run(command.split(), shell=False,'
    content = re.sub(shell_pattern, shell_replacement, content)
    
    # 修复pip命令构造
    pip_pattern = r'f"\{sys\.executable\} -m pip install -r \{requirements_file\}"'
    pip_replacement = f'[sys.executable, "-m", "pip", "install", "-r", requirements_file]'
    
    # 更新run_command函数
    run_command_fix = '''def run_command(command_list, description):
    """执行命令并处理错误"""
    print(f"\\n🔄 {description}...")
    try:
        if isinstance(command_list, str):
            command_list = command_list.split()
        
        result = subprocess.run(command_list, check=True, 
                              capture_output=True, text=True)
        print(f"✅ {description} 完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败:")
        print(f"错误信息: {e.stderr}")
        return False'''
    
    # 替换run_command函数
    content = re.sub(
        r'def run_command\(command, description\):.*?return False',
        run_command_fix,
        content,
        flags=re.DOTALL
    )
    
    # 修复install_requirements函数
    install_fix = '''def install_requirements(env_type="dev"):
    """安装依赖包"""
    if env_type == "prod":
        requirements_file = "requirements-prod.txt"
        description = "安装生产环境依赖"
    else:
        requirements_file = "requirements.txt"
        description = "安装开发环境依赖"
    
    if not Path(requirements_file).exists():
        print(f"❌ 找不到 {requirements_file} 文件")
        return False
    
    return run_command(
        [sys.executable, "-m", "pip", "install", "-r", requirements_file],
        description
    )'''
    
    content = re.sub(
        r'def install_requirements\(env_type="dev"\):.*?return run_command\([^)]+\)',
        install_fix,
        content,
        flags=re.DOTALL
    )
    
    # 修复upgrade_pip函数
    upgrade_fix = '''def upgrade_pip():
    """升级pip"""
    return run_command(
        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
        "升级pip"
    )'''
    
    content = re.sub(
        r'def upgrade_pip\(\):.*?return run_command\([^)]+\)',
        upgrade_fix,
        content,
        flags=re.DOTALL
    )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复: {filepath}")
    return True

def fix_stock_config_security():
    """修复stock_config.py的安全问题"""
    filepath = "stock_config.py"
    if not os.path.exists(filepath):
        print(f"❌ 文件不存在: {filepath}")
        return False
    
    backup_file(filepath)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 修改为HTTPS端点（如果可用）
    https_fixes = [
        (
            r"'sina_suggest': 'http://suggest3\.sinajs\.cn/suggest/type=11,12,13,14,15&key=\{\}'",
            "'sina_suggest': 'https://suggest3.sinajs.cn/suggest/type=11,12,13,14,15&key={}'"
        )
    ]
    
    for pattern, replacement in https_fixes:
        content = re.sub(pattern, replacement, content)
    
    # 添加安全配置
    security_config = '''
# 安全配置
SECURITY_CONFIG = {
    # 输入验证
    'max_query_length': 50,
    'allowed_chars_pattern': r'^[a-zA-Z0-9\\u4e00-\\u9fff.]+$',
    
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
'''
    
    content += security_config
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ 已修复: {filepath}")
    return True

def create_security_utils():
    """创建安全工具模块"""
    filepath = "security_utils.py"
    
    security_utils_content = '''#!/usr/bin/env python3
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
        if not re.match(r'^[a-zA-Z0-9\\u4e00-\\u9fff.]+$', query_str):
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
'''
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(security_utils_content)
    
    print(f"✅ 已创建安全工具模块: {filepath}")
    return True

def main():
    """主修复函数"""
    print("🔒 开始安全修复...")
    print("=" * 50)
    
    fixes = [
        ("修复get_codename.py安全问题", fix_get_codename_security),
        ("修复install_dependencies.py安全问题", fix_install_dependencies_security),
        ("修复stock_config.py安全问题", fix_stock_config_security),
        ("创建安全工具模块", create_security_utils)
    ]
    
    success_count = 0
    
    for description, fix_func in fixes:
        print(f"\\n🔄 {description}...")
        try:
            if fix_func():
                success_count += 1
                print(f"✅ {description} 完成")
            else:
                print(f"❌ {description} 失败")
        except Exception as e:
            print(f"❌ {description} 出错: {e}")
    
    print(f"\\n📊 修复结果: {success_count}/{len(fixes)} 成功")
    
    if success_count == len(fixes):
        print("\\n🎉 所有安全修复完成!")
        print("\\n📝 后续步骤:")
        print("1. 运行测试验证修复效果")
        print("2. 检查备份文件是否正确")
        print("3. 更新部署配置")
    else:
        print("\\n⚠️  部分修复失败，请检查错误信息")
    
    return success_count == len(fixes)

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)