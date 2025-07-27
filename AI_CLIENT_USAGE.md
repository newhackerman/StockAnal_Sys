# 通用AI客户端使用指南

## 概述

新的通用AI客户端(`ai_client.py`)支持多种AI服务提供商，包括OpenAI、Gemini等，提供统一的接口和更好的扩展性。

## 支持的AI提供商

### 1. OpenAI
- 标准OpenAI API
- 支持GPT-4、GPT-3.5等模型
- 支持Function Calling

### 2. Gemini (OpenAI兼容接口)
- 使用Gemini的OpenAI兼容API
- 支持Gemini 2.0、1.5等模型
- 支持Function Calling

### 3. Gemini (原生接口)
- 使用Google原生Gemini API
- 更好的性能和功能支持
- 自动格式转换

## 配置说明

### 环境变量配置

在`.env`文件中配置以下变量：

```bash
# AI 提供商配置
# 可选值: openai, gemini_openai, gemini_native
API_PROVIDER=openai

# OpenAI API 配置
OPENAI_API_KEY=your_openai_api_key
OPENAI_API_URL=https://api.openai.com/v1
OPENAI_API_MODEL=gpt-4o

# Gemini API 配置
GOOGLE_API_KEY=your_google_api_key
GOOGLE_API_URL=https://generativelanguage.googleapis.com/v1beta
GOOGLE_API_MODEL=gemini-2.0-flash-exp

# 功能模型配置
NEWS_MODEL=gpt-4o
FUNCTION_CALL_MODEL=gpt-4o

# 超时设置
AI_TIMEOUT=180
```

### API_PROVIDER 选项说明

- `openai`: 使用标准OpenAI API
- `gemini_openai`: 使用Gemini的OpenAI兼容接口
- `gemini_native`: 使用Google原生Gemini API

## 使用方法

### 基本使用

```python
from ai_client import get_ai_client

# 获取AI客户端实例
ai_client = get_ai_client()

# 基本聊天
response = ai_client.chat_completion(
    messages=[
        {"role": "user", "content": "你好，请介绍一下股票投资"}
    ],
    temperature=0.7,
    max_tokens=1000
)

print(response.choices[0].message.content)
```

### 高级功能

```python
# 使用工具调用 (Function Calling)
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_stock_price",
            "description": "获取股票价格",
            "parameters": {
                "type": "object",
                "properties": {
                    "symbol": {"type": "string", "description": "股票代码"}
                },
                "required": ["symbol"]
            }
        }
    }
]

response = ai_client.chat_completion(
    messages=[{"role": "user", "content": "查询苹果公司股价"}],
    tools=tools,
    tool_choice="auto"
)

# 检查是否有工具调用
if hasattr(response.choices[0].message, 'tool_calls'):
    for tool_call in response.choices[0].message.tool_calls:
        print(f"工具: {tool_call.function.name}")
        print(f"参数: {tool_call.function.arguments}")
```

### 客户端信息和测试

```python
# 获取客户端信息
info = ai_client.get_client_info()
print(f"提供商: {info['provider']}")
print(f"默认模型: {info['default_model']}")
print(f"可用模型: {info['available_models']}")

# 测试连接
test_result = ai_client.test_connection()
if test_result['success']:
    print("连接成功")
else:
    print(f"连接失败: {test_result['error']}")
```

## 在现有代码中的集成

### StockAnalyzer 中的使用

```python
class StockAnalyzer:
    def __init__(self):
        # 使用新的通用AI客户端
        self.ai_client = get_ai_client()
        
    def get_ai_analysis(self, df, stock_code):
        # 使用统一的接口
        response = self.ai_client.chat_completion(
            messages=[{"role": "user", "content": prompt}],
            temperature=0.8,
            max_tokens=4000
        )
        return response.choices[0].message.content
```

### ScenarioPredictor 中的使用

```python
class ScenarioPredictor:
    def __init__(self, analyzer):
        self.analyzer = analyzer
        self.ai_client = get_ai_client()
        
    def _generate_ai_analysis(self, prompt):
        response = self.ai_client.chat_completion(
            messages=[
                {"role": "system", "content": "你是专业的股票分析师"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
```

## 测试和验证

运行测试脚本验证配置：

```bash
python test_ai_client.py
```

测试脚本会：
1. 检查配置是否正确
2. 测试AI连接
3. 验证基本聊天功能
4. 测试工具调用功能
5. 测试不同提供商

## 优势

### 1. 统一接口
- 所有AI提供商使用相同的接口
- 简化代码维护
- 易于切换提供商

### 2. 更好的错误处理
- 统一的超时控制
- 详细的错误信息
- 自动重试机制

### 3. 扩展性
- 易于添加新的AI提供商
- 支持自定义配置
- 模块化设计

### 4. 向后兼容
- 保持原有API接口
- 渐进式迁移
- 最小化代码变更

## 故障排除

### 常见问题

1. **连接超时**
   - 检查网络连接
   - 调整 `AI_TIMEOUT` 设置
   - 验证API密钥和URL

2. **模型不支持**
   - 检查模型名称是否正确
   - 确认API密钥权限
   - 查看提供商文档

3. **工具调用失败**
   - 确认提供商支持Function Calling
   - 检查工具定义格式
   - 验证模型兼容性

### 调试技巧

1. 启用详细日志：
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

2. 使用测试脚本：
```bash
python test_ai_client.py
```

3. 检查客户端信息：
```python
ai_client = get_ai_client()
print(ai_client.get_client_info())
```

## 最佳实践

1. **配置管理**
   - 使用环境变量管理敏感信息
   - 为不同环境设置不同配置
   - 定期轮换API密钥

2. **性能优化**
   - 合理设置超时时间
   - 使用适当的温度参数
   - 限制最大token数

3. **错误处理**
   - 实现重试机制
   - 提供降级方案
   - 记录详细错误信息

4. **成本控制**
   - 监控API使用量
   - 选择合适的模型
   - 优化提示词长度

## 更新日志

### v1.0.0
- 初始版本
- 支持OpenAI和Gemini
- 统一接口设计
- 完整的测试套件