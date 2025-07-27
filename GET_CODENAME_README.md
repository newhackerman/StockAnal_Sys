# get_codename.py 优化说明

## 功能概述

优化后的 `get_codename.py` 支持：
- 静态数据查询（原有功能）
- 实时股票信息查询（新增）
- 自动更新静态数据文件（新增）
- 支持A股、港股、美股查询（新增）
- 模糊搜索功能（新增）
- 完善的错误处理和日志记录（新增）

## 主要改进

### 1. 实时查询功能
当静态数据中找不到股票信息时，系统会自动：
- 查询A股信息（使用新浪财经API）
- 查询港股信息（使用腾讯财经API）
- 查询美股信息（使用Yahoo Finance API）
- 将查询结果自动添加到静态数据文件

### 2. 多市场支持
- **A股**: 支持股票代码和中文名称查询
- **港股**: 支持5位数字代码查询（如00700）
- **美股**: 支持股票代码查询（如AAPL、TSLA）

### 3. 配置化管理
- `stock_config.py`: 集中管理API配置、端点、超时设置等
- 支持自定义超时时间、重试次数、请求间隔
- 可配置的日志级别和输出格式

### 4. 数据备份机制
- 每100条新记录自动备份数据文件
- 备份文件带时间戳，存储在 `./data/backup/` 目录

## 使用方法

### 基本用法（与原版兼容）

```python
from get_codename import get_codename

# 获取股票代码（默认行为）
code = get_codename('长电科技')  # 返回股票代码

# 指定返回类型
code = get_codename('长电科技', 'code')  # 返回代码
name = get_codename('000001', 'name')   # 返回名称
```

### 新增功能

```python
from get_codename import get_codename, search_stocks, get_stock_count

# 实时查询（如果静态数据中没有，会自动查询并更新）
tesla_name = get_codename('TSLA', 'name')      # 美股查询
tencent_code = get_codename('腾讯控股', 'code')  # 港股查询
byd_code = get_codename('比亚迪', 'code')       # A股查询

# 模糊搜索
results = search_stocks('科技', limit=10)
for result in results:
    print(f"{result['code']} - {result['name']}")

# 获取当前股票数量
count = get_stock_count()
print(f"当前股票数量: {count}")
```

## 配置说明

### API配置 (stock_config.py)

```python
API_CONFIG = {
    'timeout': 5,           # 请求超时时间（秒）
    'retry_count': 3,       # 重试次数
    'request_interval': 0.5, # 请求间隔（秒）
    'user_agent': '...'     # User-Agent字符串
}
```

### 数据文件配置

```python
DATA_CONFIG = {
    'file_path': './data/ALL_STOCK_LIST.csv',
    'backup_path': './data/backup/',
    'encoding': 'utf8',
    'separator': ',',
    'columns': ['code', 'name', 'market', 'Industry']
}
```

## 测试

运行测试脚本验证功能：

```bash
python test_get_codename.py
```

测试内容包括：
- 现有股票查询测试
- 实时查询功能测试
- 模糊搜索测试
- 错误处理测试

## 日志

系统会在 `./logs/stock_query.log` 中记录：
- 查询请求和结果
- 新股票添加记录
- 错误和警告信息
- 性能统计

## 文件结构

```
├── get_codename.py          # 主功能文件
├── stock_config.py          # 配置文件
├── test_get_codename.py     # 测试脚本
├── data/
│   ├── ALL_STOCK_LIST.csv   # 静态股票数据
│   └── backup/              # 数据备份目录
└── logs/
    └── stock_query.log      # 日志文件
```

## 性能优化

1. **缓存机制**: 静态数据优先查询，减少API调用
2. **重试机制**: 网络请求失败时自动重试
3. **请求限制**: 控制请求频率，避免被API限制
4. **异常处理**: 完善的错误处理，确保系统稳定性

## 注意事项

1. **网络依赖**: 实时查询功能需要网络连接
2. **API限制**: 各API服务商可能有调用频率限制
3. **数据准确性**: 实时查询的数据准确性依赖于第三方API
4. **备份重要性**: 建议定期备份 `ALL_STOCK_LIST.csv` 文件

## 故障排除

### 常见问题

1. **查询失败**: 检查网络连接和API可用性
2. **编码问题**: 确保文件编码设置正确
3. **权限问题**: 确保有写入数据文件的权限

### 调试方法

1. 查看日志文件 `./logs/stock_query.log`
2. 调整日志级别为 `DEBUG` 获取详细信息
3. 使用测试脚本验证各项功能

## 扩展性

系统设计支持：
- 添加新的API数据源
- 扩展支持更多市场
- 自定义数据字段
- 集成到更大的系统中