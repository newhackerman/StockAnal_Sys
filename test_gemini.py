#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Gemini AI客户端专项测试脚本
专门测试Gemini API的各种调用方式
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ai_client import get_ai_client, AIClientManager

def test_gemini_openai_compatible():
    """测试Gemini OpenAI兼容接口"""
    print("=" * 60)
    print("测试 Gemini OpenAI 兼容接口")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        # 显示客户端信息
        client_info = ai_client.get_client_info()
        print(f"AI提供商: {client_info['provider']}")
        print(f"默认模型: {client_info['default_model']}")
        print(f"Gemini配置: {'✓' if client_info['gemini_configured'] else '✗'}")
        print()
        
        if not client_info['gemini_configured']:
            print("⚠️  Gemini未配置，请在.env文件中设置GOOGLE_API_KEY")
            return False
        
        # 测试连接
        print("测试Gemini OpenAI兼容接口连接...")
        connection_test = ai_client.test_connection()
        
        if connection_test['success']:
            print("✓ Gemini OpenAI兼容接口连接成功")
            print(f"模型: {connection_test['model']}")
            print(f"响应: {connection_test['response']}")
        else:
            print("✗ Gemini OpenAI兼容接口连接失败")
            print(f"错误: {connection_test['error']}")
            return False
            
        print()
        
        # 测试股票分析相关的聊天
        print("测试股票分析聊天功能...")
        test_messages = [
            {"role": "user", "content": "请简单分析一下当前A股市场的整体趋势，用100字以内回答。"}
        ]
        
        response = ai_client.chat_completion(
            messages=test_messages,
            temperature=0.7,
            max_tokens=200,
            timeout=30
        )
        
        if hasattr(response, 'choices') and response.choices:
            print("✓ 股票分析聊天功能测试成功")
            print(f"回答: {response.choices[0].message.content}")
        else:
            print("✗ 股票分析聊天功能测试失败")
            return False
            
        print()
        
        # 测试工具调用功能
        print("测试Gemini工具调用功能...")
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "analyze_stock",
                        "description": "分析股票的技术指标和基本面",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "stock_code": {
                                    "type": "string",
                                    "description": "股票代码，如000001"
                                },
                                "analysis_type": {
                                    "type": "string",
                                    "description": "分析类型：technical（技术分析）或fundamental（基本面分析）"
                                }
                            },
                            "required": ["stock_code", "analysis_type"]
                        }
                    }
                }
            ]
            
            tool_test_messages = [
                {"role": "user", "content": "请帮我分析一下平安银行(000001)的技术指标"}
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
                    print("✓ Gemini工具调用功能测试成功")
                    print(f"工具调用: {message.tool_calls[0].function.name}")
                    print(f"参数: {message.tool_calls[0].function.arguments}")
                else:
                    print("○ Gemini工具调用功能可用，但模型选择不使用工具")
                    print(f"直接回答: {message.content[:100]}...")
            else:
                print("○ Gemini工具调用功能测试跳过")
                
        except Exception as e:
            print(f"○ Gemini工具调用功能测试异常: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Gemini OpenAI兼容接口测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始提供商设置
        os.environ['API_PROVIDER'] = original_provider

def test_gemini_native():
    """测试Gemini原生接口"""
    print("=" * 60)
    print("测试 Gemini 原生接口")
    print("=" * 60)
    
    # 临时设置为gemini_native模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_native'
    
    try:
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        # 显示客户端信息
        client_info = ai_client.get_client_info()
        print(f"AI提供商: {client_info['provider']}")
        print(f"默认模型: {client_info['default_model']}")
        print(f"Gemini配置: {'✓' if client_info['gemini_configured'] else '✗'}")
        print()
        
        if not client_info['gemini_configured']:
            print("⚠️  Gemini未配置，请在.env文件中设置GOOGLE_API_KEY")
            return False
        
        # 测试连接
        print("测试Gemini原生接口连接...")
        connection_test = ai_client.test_connection()
        
        if connection_test['success']:
            print("✓ Gemini原生接口连接成功")
            print(f"模型: {connection_test['model']}")
            print(f"响应: {connection_test['response']}")
        else:
            print("✗ Gemini原生接口连接失败")
            print(f"错误: {connection_test['error']}")
            return False
            
        print()
        
        # 测试股票分析相关的聊天
        print("测试股票分析聊天功能...")
        test_messages = [
            {"role": "system", "content": "你是专业的股票分析师，请提供专业的投资建议。"},
            {"role": "user", "content": "请分析一下科技股在当前市场环境下的投资机会，用150字以内回答。"}
        ]
        
        response = ai_client.chat_completion(
            messages=test_messages,
            temperature=0.7,
            max_tokens=300,
            timeout=30
        )
        
        if hasattr(response, 'choices') and response.choices:
            print("✓ 股票分析聊天功能测试成功")
            print(f"回答: {response.choices[0].message.content}")
        else:
            print("✗ 股票分析聊天功能测试失败")
            return False
            
        print()
        
        # 测试多轮对话
        print("测试多轮对话功能...")
        try:
            conversation = [
                {"role": "user", "content": "什么是PE估值？"},
            ]
            
            first_response = ai_client.chat_completion(
                messages=conversation,
                temperature=0.5,
                max_tokens=200,
                timeout=30
            )
            
            if hasattr(first_response, 'choices') and first_response.choices:
                conversation.append({"role": "assistant", "content": first_response.choices[0].message.content})
                conversation.append({"role": "user", "content": "那么PE估值多少算合理？"})
                
                second_response = ai_client.chat_completion(
                    messages=conversation,
                    temperature=0.5,
                    max_tokens=200,
                    timeout=30
                )
                
                if hasattr(second_response, 'choices') and second_response.choices:
                    print("✓ 多轮对话功能测试成功")
                    print(f"第一轮回答: {first_response.choices[0].message.content[:50]}...")
                    print(f"第二轮回答: {second_response.choices[0].message.content[:50]}...")
                else:
                    print("✗ 多轮对话第二轮失败")
            else:
                print("✗ 多轮对话第一轮失败")
                
        except Exception as e:
            print(f"○ 多轮对话功能测试异常: {str(e)}")
            
        return True
        
    except Exception as e:
        print(f"✗ Gemini原生接口测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始提供商设置
        os.environ['API_PROVIDER'] = original_provider

def test_stock_analyzer_with_gemini():
    """测试StockAnalyzer与Gemini的集成"""
    print("=" * 60)
    print("测试 StockAnalyzer 与 Gemini 集成")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        
        # 导入并初始化StockAnalyzer
        from stock_analyzer import StockAnalyzer
        analyzer = StockAnalyzer()
        
        print(f"StockAnalyzer AI提供商: {analyzer.API_PROVIDER}")
        print(f"AI客户端提供商: {analyzer.ai_client.api_provider}")
        print()
        
        # 测试获取股票数据
        print("测试获取股票数据...")
        try:
            # 使用一个常见的股票代码进行测试
            stock_code = "000001"  # 平安银行
            df = analyzer.get_stock_data(stock_code, market_type='A')
            
            if df is not None and not df.empty:
                print(f"✓ 成功获取股票 {stock_code} 数据，共 {len(df)} 条记录")
                print(f"最新价格: {df.iloc[-1]['close']}")
                
                # 计算技术指标
                print("计算技术指标...")
                df = analyzer.calculate_indicators(df)
                print(f"✓ 技术指标计算完成")
                print(f"RSI: {df.iloc[-1]['RSI']:.2f}")
                print(f"MACD: {df.iloc[-1]['MACD']:.4f}")
                
                # 测试AI分析功能
                print("测试AI分析功能...")
                try:
                    ai_analysis = analyzer.get_ai_analysis(df, stock_code, market_type='A')
                    if ai_analysis and len(ai_analysis) > 50:
                        print("✓ AI分析功能测试成功")
                        print(f"分析结果预览: {ai_analysis[:200]}...")
                    else:
                        print("✗ AI分析功能测试失败或结果过短")
                        print(f"结果: {ai_analysis}")
                        
                except Exception as e:
                    print(f"✗ AI分析功能测试异常: {str(e)}")
                    
            else:
                print(f"✗ 无法获取股票 {stock_code} 数据")
                return False
                
        except Exception as e:
            print(f"✗ 股票数据获取异常: {str(e)}")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ StockAnalyzer与Gemini集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始提供商设置
        os.environ['API_PROVIDER'] = original_provider

def main():
    """主函数"""
    print("StockAnal_Sys Gemini AI 专项测试工具")
    print("版本: 1.0.0")
    print()
    
    # 检查Gemini配置
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("⚠️  警告: 未检测到GOOGLE_API_KEY配置")
        print("请在.env文件中配置GOOGLE_API_KEY以测试Gemini功能")
        print()
        return False
    else:
        print(f"✓ 检测到Gemini配置: GOOGLE_API_KEY")
        print()
    
    success_count = 0
    total_tests = 3
    
    # 测试1: Gemini OpenAI兼容接口
    if test_gemini_openai_compatible():
        success_count += 1
        print("✓ Gemini OpenAI兼容接口测试通过\n")
    else:
        print("✗ Gemini OpenAI兼容接口测试失败\n")
    
    # 测试2: Gemini原生接口
    if test_gemini_native():
        success_count += 1
        print("✓ Gemini原生接口测试通过\n")
    else:
        print("✗ Gemini原生接口测试失败\n")
    
    # 测试3: StockAnalyzer集成测试
    if test_stock_analyzer_with_gemini():
        success_count += 1
        print("✓ StockAnalyzer与Gemini集成测试通过\n")
    else:
        print("✗ StockAnalyzer与Gemini集成测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"Gemini测试完成: {success_count}/{total_tests} 项测试通过")
    if success_count == total_tests:
        print("🎉 所有Gemini功能测试通过！")
    elif success_count > 0:
        print("⚠️  部分Gemini功能正常，请检查失败的测试项")
    else:
        print("❌ 所有Gemini功能测试失败，请检查配置和网络连接")
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)