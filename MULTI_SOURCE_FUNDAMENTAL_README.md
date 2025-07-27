# 多数据源基本面分析系统

## 概述

这是一个支持A股、港股、美股的多数据源基本面分析系统。通过整合多个数据源，提供稳定可靠的财务数据获取和分析服务。

## 特性

### 🌐 多数据源支持
- **A股**: akshare、东方财富、新浪财经
- **港股**: yfinance、akshare、Yahoo Finance
- **美股**: yfinance、Yahoo Finance、Alpha Vantage

### 📊 完整的财务分析
- **估值指标**: PE、PB、PS等
- **盈利能力**: ROE、毛利率、净利润率等
- **财务健康**: 资产负债率、流动比率等
- **成长性**: 营收增长率、利润增长率等

### 🔄 智能容错机制
- 自动数据源切换
- 重试机制和指数退避
- 缓存优化
- 优雅降级

### ⚙️ 灵活配置
- 数据源优先级可调
- API密钥配置
- 缓存策略自定义
- 评分权重调整

## 安装

### 1. 安装依赖包

```bash
python install_dependencies.py
```

或手动安装：

```bash
pip install yfinance>=0.2.18 requests>=2.25.0 pandas>=1.3.0 numpy>=1.21.0 akshare>=1.11.0
```

### 2. 可选依赖（用于额外数据源）

```bash
pip install alpha-vantage finnhub-python quandl
```

## 快速开始

### 基本使用

```python
from fundamental_analyzer import FundamentalAnalyzer

# 创建分析器实例
analyzer = FundamentalAnalyzer()

# A股分析
a_score = analyzer.calculate_fundamental_score('600519')  # 茅台
print(f"A股评分: {a_score['total']}")

# 港股分析
hk_score = analyzer.calculate_fundamental_score('00700')  # 腾讯
print(f"港股评分: {hk_score['total']}")

# 美股分析
us_score = analyzer.calculate_fundamental_score('AAPL')  # 苹果
print(f"美股评分: {us_score['total']}")
```

### 获取详细财务指标

```python
# 获取财务指标
indicators = analyzer.get_financial_indicators('600519', 'A')
print(f"PE(TTM): {indicators.get('pe_ttm')}")
print(f"PB: {indicators.get('pb')}")
print(f"ROE: {indicators.get('roe')}%")

# 获取成长数据
growth = analyzer.get_growth_data('600519', 'A')
print(f"营收3年增长: {growth.get('revenue_growth_3y')}%")
print(f"利润3年增长: {growth.get('profit_growth_3y')}%")
```

## 配置

### 1. 基本配置

编辑 `fundamental_config.py` 文件：

```python
# 调整数据源优先级
DATA_SOURCES = {
    'A': ['eastmoney', 'akshare', 'sina'],  # 优先使用东方财富
    'HK': ['yfinance', 'yahoo', 'akshare'],  # 优先使用yfinance
    'US': ['yfinance', 'alpha_vantage', 'yahoo']  # 优先使用yfinance
}

# 配置API密钥
API_CONFIG = {
    'alpha_vantage_key': 'YOUR_ALPHA_VANTAGE_KEY',
    'finnhub_key': 'YOUR_FINNHUB_KEY'
}
```

### 2. 高级配置

```python
# 缓存配置
CACHE_CONFIG = {
    'financial_indicators': 600,  # 10分钟
    'growth_data': 900,          # 15分钟
    'hk_data': 300,              # 5分钟
    'us_data': 600               # 10分钟
}

# 评分权重配置
SCORING_CONFIG = {
    'valuation_weight': 0.3,    # 估值权重30%
    'financial_weight': 0.4,    # 财务健康权重40%
    'growth_weight': 0.3,       # 成长性权重30%
}
```

## 数据源说明

### A股数据源

1. **akshare** (默认优先)
   - 优点: 数据全面，更新及时
   - 缺点: 网络依赖性强

2. **东方财富**
   - 优点: 稳定性好，响应快
   - 缺点: 指标相对有限

3. **新浪财经**
   - 优点: 备用可靠
   - 缺点: 财务指标较少

### 港股数据源

1. **yfinance** (推荐)
   - 优点: 数据质量高，指标全面
   - 缺点: 需要良好的国际网络

2. **akshare**
   - 优点: 国内访问稳定
   - 缺点: 港股数据有限

3. **Yahoo Finance**
   - 优点: 备用选择
   - 缺点: API限制较多

### 美股数据源

1. **yfinance** (推荐)
   - 优点: 免费，数据全面
   - 缺点: 有请求频率限制

2. **Alpha Vantage**
   - 优点: 专业金融数据
   - 缺点: 需要API密钥

3. **Yahoo Finance**
   - 优点: 备用可靠
   - 缺点: 功能有限

## API密钥获取

### Alpha Vantage
1. 访问 https://www.alphavantage.co/support/#api-key
2. 免费注册获取API密钥
3. 在配置文件中设置 `alpha_vantage_key`

### Finnhub
1. 访问 https://finnhub.io/
2. 注册获取免费API密钥
3. 在配置文件中设置 `finnhub_key`

## 测试

### 运行完整测试

```bash
python test_multi_source_fundamental.py
```

### 测试特定功能

```python
# 测试数据源可用性
from test_multi_source_fundamental import test_data_sources
test_data_sources()

# 测试综合分析
from test_multi_source_fundamental import test_comprehensive_analysis
test_comprehensive_analysis()

# 测试性能和缓存
from test_multi_source_fundamental import test_performance
test_performance()
```

## 故障排除

### 常见问题

1. **网络连接问题**
   ```
   解决方案: 检查网络连接，考虑使用代理
   ```

2. **API密钥无效**
   ```
   解决方案: 检查API密钥是否正确配置
   ```

3. **数据获取失败**
   ```
   解决方案: 系统会自动切换到备用数据源
   ```

4. **yfinance安装问题**
   ```bash
   pip install --upgrade yfinance
   ```

### 调试模式

启用调试日志：

```python
# 在配置文件中设置
LOGGING_CONFIG = {
    'enable_debug': True,
    'log_api_calls': True,
    'log_cache_hits': True
}
```

## 性能优化

### 缓存策略
- 财务指标: 10分钟缓存
- 成长数据: 15分钟缓存
- 港股数据: 5分钟缓存（网络不稳定）

### 请求优化
- 自动重试机制
- 指数退避延迟
- 并发请求控制

### 数据质量控制
- 自动数据验证
- 异常值过滤
- 数据完整性检查

## 扩展开发

### 添加新数据源

1. 在 `fundamental_analyzer.py` 中添加新的获取方法
2. 更新配置文件中的数据源列表
3. 实现相应的数据解析逻辑

### 自定义评分算法

1. 修改 `calculate_fundamental_score` 方法
2. 调整评分权重配置
3. 添加新的评分维度

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目。

## 更新日志

### v2.2.0
- 实现多数据源支持
- 添加港股和美股完整支持
- 优化缓存和错误处理机制
- 添加配置文件支持

### v2.1.0
- 基础功能实现
- A股数据支持
- 基本评分算法