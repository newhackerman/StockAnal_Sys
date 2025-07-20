#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专门测试Gemini工具调用功能
诊断为什么Gemini没有调用TAVILY工具获取新闻
"""

import os
import sys
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_tool_calling_direct():
    """直接测试Gemini的工具调用能力"""
    print("=" * 60)
    print("直接测试Gemini工具调用能力")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import get_ai_client, AIClientManager
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        print(f"AI提供商: {ai_client.api_provider}")
        print(f"工具调用模型: {ai_client.get_function_call_model()}")
        print()
        
        # 定义简单的测试工具
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_weather",
                    "description": "获取指定城市的天气信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city": {
                                "type": "string",
                                "description": "城市名称"
                            }
                        },
                        "required": ["city"]
                    }
                }
            }
        ]
        
        # 测试1: 明确要求使用工具的问题
        print("测试1: 明确要求使用工具")
        test_messages = [
            {"role": "user", "content": "请使用get_weather工具查询北京的天气"}
        ]
        
        response = ai_client.chat_completion(
            messages=test_messages,
            model=ai_client.get_function_call_model(),
            tools=tools,
            tool_choice="auto",
            temperature=0.3
        )
        
        if hasattr(response, 'choices') and response.choices:
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print("✓ Gemini成功调用工具")
                for tool_call in message.tool_calls:
                    print(f"  工具: {tool_call.function.name}")
                    print(f"  参数: {tool_call.function.arguments}")
            else:
                print("✗ Gemini没有调用工具")
                print(f"  直接回答: {message.content}")
        
        print()
        
        # 测试2: 隐含需要工具的问题
        print("测试2: 隐含需要工具的问题")
        test_messages2 = [
            {"role": "user", "content": "北京今天天气怎么样？"}
        ]
        
        response2 = ai_client.chat_completion(
            messages=test_messages2,
            model=ai_client.get_function_call_model(),
            tools=tools,
            tool_choice="auto",
            temperature=0.3
        )
        
        if hasattr(response2, 'choices') and response2.choices:
            message2 = response2.choices[0].message
            if hasattr(message2, 'tool_calls') and message2.tool_calls:
                print("✓ Gemini成功调用工具")
                for tool_call in message2.tool_calls:
                    print(f"  工具: {tool_call.function.name}")
                    print(f"  参数: {tool_call.function.arguments}")
            else:
                print("✗ Gemini没有调用工具")
                print(f"  直接回答: {message2.content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 直接测试Gemini工具调用失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_stock_news_tool_calling():
    """测试股票新闻工具调用"""
    print("=" * 60)
    print("测试股票新闻工具调用")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import get_ai_client, AIClientManager
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        # 定义股票新闻搜索工具
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_stock_news",
                    "description": "搜索股票相关的最新新闻、公告和行业动态信息，以获取实时市场信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询词，用于查找相关新闻"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # 测试不同类型的股票问题
        test_cases = [
            "请搜索平安银行的最新新闻",
            "帮我查一下中芯国际最近有什么消息",
            "我想了解腾讯控股的最新动态",
            "平安银行最近表现如何？有什么新闻吗？",
            "请分析一下平安银行的投资价值，需要最新信息"
        ]
        
        for i, question in enumerate(test_cases, 1):
            print(f"测试{i}: {question}")
            
            test_messages = [
                {"role": "user", "content": question}
            ]
            
            response = ai_client.chat_completion(
                messages=test_messages,
                model=ai_client.get_function_call_model(),
                tools=tools,
                tool_choice="auto",
                temperature=0.3
            )
            
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print("  ✓ Gemini调用了工具")
                    for tool_call in message.tool_calls:
                        print(f"    工具: {tool_call.function.name}")
                        print(f"    参数: {tool_call.function.arguments}")
                else:
                    print("  ✗ Gemini没有调用工具")
                    print(f"    直接回答: {message.content[:80]}...")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 股票新闻工具调用测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_different_tool_choice_strategies():
    """测试不同的工具选择策略"""
    print("=" * 60)
    print("测试不同的工具选择策略")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import get_ai_client, AIClientManager
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        # 定义工具
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_stock_news",
                    "description": "搜索股票相关的最新新闻、公告和行业动态信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询词"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        question = "请搜索平安银行的最新新闻"
        test_messages = [{"role": "user", "content": question}]
        
        # 测试不同的tool_choice设置
        tool_choices = ["auto", "required"]
        
        for tool_choice in tool_choices:
            print(f"测试tool_choice='{tool_choice}':")
            
            try:
                if tool_choice == "required":
                    # 对于required，需要指定具体的工具
                    response = ai_client.chat_completion(
                        messages=test_messages,
                        model=ai_client.get_function_call_model(),
                        tools=tools,
                        tool_choice={"type": "function", "function": {"name": "search_stock_news"}},
                        temperature=0.3
                    )
                else:
                    response = ai_client.chat_completion(
                        messages=test_messages,
                        model=ai_client.get_function_call_model(),
                        tools=tools,
                        tool_choice=tool_choice,
                        temperature=0.3
                    )
                
                if hasattr(response, 'choices') and response.choices:
                    message = response.choices[0].message
                    if hasattr(message, 'tool_calls') and message.tool_calls:
                        print(f"  ✓ 成功调用工具")
                        for tool_call in message.tool_calls:
                            print(f"    工具: {tool_call.function.name}")
                            print(f"    参数: {tool_call.function.arguments}")
                    else:
                        print(f"  ✗ 没有调用工具")
                        print(f"    回答: {message.content[:80]}...")
                        
            except Exception as e:
                print(f"  ✗ 调用失败: {str(e)}")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 工具选择策略测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_prompt_engineering():
    """测试不同的提示词工程方法"""
    print("=" * 60)
    print("测试提示词工程方法")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import get_ai_client, AIClientManager
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        # 定义工具
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "search_stock_news",
                    "description": "搜索股票相关的最新新闻、公告和行业动态信息，获取实时市场信息",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "搜索查询词，用于查找相关新闻"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # 测试不同的提示词
        prompts = [
            # 1. 直接命令式
            "搜索平安银行最新新闻",
            
            # 2. 明确要求使用工具
            "请使用search_stock_news工具搜索平安银行的最新新闻",
            
            # 3. 强调需要实时信息
            "我需要平安银行的最新实时新闻信息，请帮我搜索",
            
            # 4. 系统提示+用户问题
            "你必须使用可用的工具来获取最新信息。用户问题：平安银行最近有什么新闻？"
        ]
        
        for i, prompt in enumerate(prompts, 1):
            print(f"测试提示词{i}: {prompt}")
            
            # 对于第4个测试，使用系统消息
            if i == 4:
                test_messages = [
                    {"role": "system", "content": "你是一个专业的股票分析助手。当用户询问股票相关信息时，你必须使用search_stock_news工具获取最新的实时信息，不要基于过时的知识回答。"},
                    {"role": "user", "content": "平安银行最近有什么新闻？"}
                ]
            else:
                test_messages = [{"role": "user", "content": prompt}]
            
            response = ai_client.chat_completion(
                messages=test_messages,
                model=ai_client.get_function_call_model(),
                tools=tools,
                tool_choice="auto",
                temperature=0.1  # 降低温度，让模型更倾向于使用工具
            )
            
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print("  ✓ 成功调用工具")
                    for tool_call in message.tool_calls:
                        print(f"    工具: {tool_call.function.name}")
                        print(f"    参数: {tool_call.function.arguments}")
                else:
                    print("  ✗ 没有调用工具")
                    print(f"    回答: {message.content[:100]}...")
            
            print()
        
        return True
        
    except Exception as e:
        print(f"✗ 提示词工程测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def main():
    """主函数"""
    print("StockAnal_Sys Gemini 工具调用诊断测试")
    print("版本: 1.0.0")
    print()
    
    # 检查配置
    google_api_key = os.getenv('GOOGLE_API_KEY')
    tavily_api_key = os.getenv('TAVILY_API_KEY')
    
    if not google_api_key:
        print("❌ 未配置GOOGLE_API_KEY")
        return False
        
    print(f"✓ GOOGLE_API_KEY: {google_api_key[:10]}...")
    print(f"✓ TAVILY_API_KEY: {'已配置' if tavily_api_key else '未配置'}")
    print()
    
    success_count = 0
    total_tests = 4
    
    # 测试1: 直接测试Gemini工具调用能力
    if test_gemini_tool_calling_direct():
        success_count += 1
        print("✓ Gemini基础工具调用测试通过\n")
    else:
        print("✗ Gemini基础工具调用测试失败\n")
    
    # 测试2: 股票新闻工具调用
    if test_stock_news_tool_calling():
        success_count += 1
        print("✓ 股票新闻工具调用测试通过\n")
    else:
        print("✗ 股票新闻工具调用测试失败\n")
    
    # 测试3: 不同工具选择策略
    if test_different_tool_choice_strategies():
        success_count += 1
        print("✓ 工具选择策略测试通过\n")
    else:
        print("✗ 工具选择策略测试失败\n")
    
    # 测试4: 提示词工程
    if test_prompt_engineering():
        success_count += 1
        print("✓ 提示词工程测试通过\n")
    else:
        print("✗ 提示词工程测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"Gemini工具调用诊断完成: {success_count}/{total_tests} 项测试通过")
    
    if success_count < total_tests:
        print("\n🔍 诊断建议:")
        print("1. 检查Gemini模型是否支持Function Calling")
        print("2. 尝试调整提示词，明确要求使用工具")
        print("3. 检查tool_choice参数设置")
        print("4. 考虑使用系统消息引导模型行为")
        print("5. 降低temperature参数，让模型更确定性地选择工具")
    else:
        print("🎉 所有测试通过！Gemini工具调用功能正常")
    
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)