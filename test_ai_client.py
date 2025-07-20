#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI客户端测试脚本
用于测试通用AI客户端的功能和连接性
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_client import get_ai_client

def test_ai_client():
    """测试AI客户端功能"""
    print("=" * 60)
    print("AI客户端测试")
    print("=" * 60)
    
    try:
        # 获取AI客户端
        ai_client = get_ai_client()
        
        # 显示客户端信息
        client_info = ai_client.get_client_info()
        print(f"AI提供商: {client_info['provider']}")
        print(f"默认模型: {client_info['default_model']}")
        print(f"OpenAI配置: {'✓' if client_info['openai_configured'] else '✗'}")
        print(f"Gemini配置: {'✓' if client_info['gemini_configured'] else '✗'}")
        print(f"超时设置: {client_info['timeout']}秒")
        print(f"可用模型: {', '.join(client_info['available_models'])}")
        print()
        
        # 测试连接
        print("测试AI连接...")
        connection_test = ai_client.test_connection()
        
        if connection_test['success']:
            print("✓ 连接测试成功")
            print(f"提供商: {connection_test['provider']}")
            print(f"模型: {connection_test['model']}")
            print(f"响应: {connection_test['response']}")
        else:
            print("✗ 连接测试失败")
            print(f"错误: {connection_test['error']}")
            return False
            
        print()
        
        # 测试基本聊天功能
        print("测试基本聊天功能...")
        test_messages = [
            {"role": "user", "content": "请简单介绍一下股票投资的基本概念，用50字以内回答。"}
        ]
        
        response = ai_client.chat_completion(
            messages=test_messages,
            temperature=0.7,
            max_tokens=100,
            timeout=30
        )
        
        if hasattr(response, 'choices') and response.choices:
            print("✓ 聊天功能测试成功")
            print(f"回答: {response.choices[0].message.content}")
        else:
            print("✗ 聊天功能测试失败")
            return False
            
        print()
        
        # 测试工具调用功能（如果支持）
        print("测试工具调用功能...")
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_stock_price",
                        "description": "获取股票价格",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "symbol": {
                                    "type": "string",
                                    "description": "股票代码"
                                }
                            },
                            "required": ["symbol"]
                        }
                    }
                }
            ]
            
            tool_test_messages = [
                {"role": "user", "content": "请帮我查询苹果公司(AAPL)的股票价格"}
            ]
            
            tool_response = ai_client.chat_completion(
                messages=tool_test_messages,
                tools=tools,
                tool_choice="auto",
                temperature=0.3,
                timeout=30
            )
            
            if hasattr(tool_response, 'choices') and tool_response.choices:
                message = tool_response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print("✓ 工具调用功能测试成功")
                    print(f"工具调用: {message.tool_calls[0].function.name}")
                    print(f"参数: {message.tool_calls[0].function.arguments}")
                else:
                    print("○ 工具调用功能可用，但模型选择不使用工具")
            else:
                print("○ 工具调用功能测试跳过")
                
        except Exception as e:
            print(f"○ 工具调用功能测试跳过: {str(e)}")
            
        print()
        print("=" * 60)
        print("✓ 所有测试完成，AI客户端工作正常")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_different_providers():
    """测试不同的AI提供商"""
    print("\n" + "=" * 60)
    print("测试不同AI提供商")
    print("=" * 60)
    
    providers = ['openai', 'gemini_openai', 'gemini_native']
    original_provider = os.getenv('API_PROVIDER', 'openai')
    
    for provider in providers:
        print(f"\n测试提供商: {provider}")
        print("-" * 40)
        
        # 临时设置提供商
        os.environ['API_PROVIDER'] = provider
        
        try:
            # 重新加载客户端
            from ai_client import ai_manager
            ai_manager.reload_client()
            
            # 获取新客户端
            ai_client = get_ai_client()
            
            # 测试连接
            connection_test = ai_client.test_connection()
            
            if connection_test['success']:
                print(f"✓ {provider} 连接成功")
                print(f"模型: {connection_test['model']}")
            else:
                print(f"✗ {provider} 连接失败: {connection_test['error']}")
                
        except Exception as e:
            print(f"✗ {provider} 测试异常: {str(e)}")
            
    # 恢复原始提供商设置
    os.environ['API_PROVIDER'] = original_provider

def main():
    """主函数"""
    print("StockAnal_Sys AI客户端测试工具")
    print("版本: 1.0.0")
    print()
    
    # 检查环境变量
    required_vars = ['OPENAI_API_KEY', 'GOOGLE_API_KEY']
    configured_vars = []
    
    for var in required_vars:
        if os.getenv(var):
            configured_vars.append(var)
            
    if not configured_vars:
        print("⚠️  警告: 未检测到任何AI API密钥配置")
        print("请在.env文件中配置以下变量之一:")
        for var in required_vars:
            print(f"  - {var}")
        print()
        return False
    else:
        print(f"✓ 检测到配置: {', '.join(configured_vars)}")
        print()
    
    # 运行基本测试
    success = test_ai_client()
    
    if success:
        # 运行提供商测试
        test_different_providers()
        
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)