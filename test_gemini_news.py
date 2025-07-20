#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Gemini工具调用和新闻获取功能
专门验证在使用Gemini时是否能正确调用工具获取新闻
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_gemini_function_calling():
    """测试Gemini的工具调用功能"""
    print("=" * 60)
    print("测试 Gemini 工具调用功能")
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
        print(f"新闻分析模型: {ai_client.get_news_model()}")
        print()
        
        # 定义测试工具
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
                                "description": "搜索查询词，用于查找相关新闻"
                            },
                            "stock_code": {
                                "type": "string", 
                                "description": "股票代码"
                            }
                        },
                        "required": ["query"]
                    }
                }
            }
        ]
        
        # 测试工具调用
        print("测试Gemini工具调用...")
        test_messages = [
            {"role": "user", "content": "请帮我搜索平安银行(000001)的最新新闻"}
        ]
        
        response = ai_client.chat_completion(
            messages=test_messages,
            model=ai_client.get_function_call_model(),
            tools=tools,
            tool_choice="auto",
            temperature=0.3,
            timeout=30
        )
        
        if hasattr(response, 'choices') and response.choices:
            message = response.choices[0].message
            if hasattr(message, 'tool_calls') and message.tool_calls:
                print("✓ Gemini工具调用成功")
                for tool_call in message.tool_calls:
                    print(f"工具名称: {tool_call.function.name}")
                    print(f"调用参数: {tool_call.function.arguments}")
                return True
            else:
                print("○ Gemini没有调用工具，直接回答:")
                print(f"回答: {message.content}")
                return False
        else:
            print("✗ Gemini工具调用测试失败")
            return False
            
    except Exception as e:
        print(f"✗ Gemini工具调用测试异常: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_stock_analyzer_news_with_gemini():
    """测试StockAnalyzer在使用Gemini时的新闻获取功能"""
    print("=" * 60)
    print("测试 StockAnalyzer 使用 Gemini 获取新闻")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import AIClientManager
        from stock_analyzer import StockAnalyzer
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        
        # 初始化StockAnalyzer
        analyzer = StockAnalyzer()
        
        print(f"StockAnalyzer AI提供商: {analyzer.API_PROVIDER}")
        print(f"AI客户端提供商: {analyzer.ai_client.api_provider}")
        print(f"工具调用模型: {analyzer.ai_client.get_function_call_model()}")
        print(f"新闻分析模型: {analyzer.ai_client.get_news_model()}")
        print()
        
        # 测试获取股票新闻
        print("测试获取股票新闻...")
        stock_code = "000001"  # 平安银行
        
        try:
            news_data = analyzer.get_stock_news(stock_code, market_type='A', limit=3)
            
            if news_data and isinstance(news_data, dict):
                print("✓ 成功获取股票新闻")
                
                # 检查新闻内容
                if 'news' in news_data and news_data['news']:
                    print(f"获取到 {len(news_data['news'])} 条新闻:")
                    for i, news in enumerate(news_data['news'][:2]):
                        print(f"  {i+1}. {news.get('title', '无标题')}")
                        print(f"     来源: {news.get('source', '未知')} | 日期: {news.get('date', '未知')}")
                
                if 'announcements' in news_data and news_data['announcements']:
                    print(f"获取到 {len(news_data['announcements'])} 条公告")
                
                if 'market_sentiment' in news_data:
                    print(f"市场情绪: {news_data['market_sentiment']}")
                    
                return True
            else:
                print("✗ 获取股票新闻失败或返回空数据")
                print(f"返回数据: {news_data}")
                return False
                
        except Exception as e:
            print(f"✗ 获取股票新闻异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ StockAnalyzer新闻测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_stock_qa_with_gemini():
    """测试StockQA在使用Gemini时的功能"""
    print("=" * 60)
    print("测试 StockQA 使用 Gemini 智能问答")
    print("=" * 60)
    
    # 临时设置为gemini_openai模式
    original_provider = os.getenv('API_PROVIDER', 'openai')
    os.environ['API_PROVIDER'] = 'gemini_openai'
    
    try:
        from ai_client import AIClientManager
        from stock_analyzer import StockAnalyzer
        from stock_qa import StockQA
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        
        # 初始化模块
        analyzer = StockAnalyzer()
        stock_qa = StockQA(analyzer)
        
        print(f"StockQA AI提供商: {stock_qa.API_PROVIDER}")
        print(f"AI客户端提供商: {stock_qa.ai_client.api_provider}")
        print()
        
        # 测试智能问答
        print("测试智能问答功能...")
        stock_code = "000001"  # 平安银行
        question = "请分析一下平安银行最近的表现和投资价值"
        
        try:
            result = stock_qa.answer_question(
                stock_code=stock_code,
                question=question,
                market_type='A'
            )
            
            if result and 'answer' in result and not result.get('error'):
                print("✓ 智能问答功能测试成功")
                print(f"问题: {result.get('question', question)}")
                print(f"回答: {result['answer'][:200]}...")
                print(f"是否使用搜索工具: {result.get('used_search_tool', False)}")
                return True
            else:
                print("✗ 智能问答功能测试失败")
                print(f"错误: {result.get('error', '未知错误')}")
                return False
                
        except Exception as e:
            print(f"✗ 智能问答功能测试异常: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
            
    except Exception as e:
        print(f"✗ StockQA测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_model_configuration():
    """测试模型配置是否正确"""
    print("=" * 60)
    print("测试 Gemini 模型配置")
    print("=" * 60)
    
    # 检查环境变量配置
    google_api_key = os.getenv('GOOGLE_API_KEY')
    google_model = os.getenv('GOOGLE_API_MODEL')
    google_function_call_model = os.getenv('GOOGLE_FUNCTION_CALL_MODEL')
    google_news_model = os.getenv('GOOGLE_NEWS_MODEL')
    
    print(f"GOOGLE_API_KEY: {'✓' if google_api_key else '✗'}")
    print(f"GOOGLE_API_MODEL: {google_model}")
    print(f"GOOGLE_FUNCTION_CALL_MODEL: {google_function_call_model}")
    print(f"GOOGLE_NEWS_MODEL: {google_news_model}")
    print()
    
    # 测试不同提供商的模型选择
    providers = ['openai', 'gemini_openai', 'gemini_native']
    original_provider = os.getenv('API_PROVIDER', 'openai')
    
    for provider in providers:
        print(f"测试提供商: {provider}")
        os.environ['API_PROVIDER'] = provider
        
        try:
            from ai_client import get_ai_client, AIClientManager
            
            # 重新加载客户端
            ai_manager = AIClientManager()
            ai_manager.reload_client()
            ai_client = get_ai_client()
            
            print(f"  默认模型: {ai_client._get_default_model()}")
            print(f"  工具调用模型: {ai_client.get_function_call_model()}")
            print(f"  新闻分析模型: {ai_client.get_news_model()}")
            
        except Exception as e:
            print(f"  配置测试失败: {str(e)}")
        
        print()
    
    # 恢复原始设置
    os.environ['API_PROVIDER'] = original_provider
    return True

def main():
    """主函数"""
    print("StockAnal_Sys Gemini 工具调用和新闻获取测试")
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
    
    # 测试1: 模型配置
    if test_model_configuration():
        success_count += 1
        print("✓ 模型配置测试通过\n")
    else:
        print("✗ 模型配置测试失败\n")
    
    # 测试2: Gemini工具调用
    if test_gemini_function_calling():
        success_count += 1
        print("✓ Gemini工具调用测试通过\n")
    else:
        print("✗ Gemini工具调用测试失败\n")
    
    # 测试3: StockAnalyzer新闻获取
    if test_stock_analyzer_news_with_gemini():
        success_count += 1
        print("✓ StockAnalyzer新闻获取测试通过\n")
    else:
        print("✗ StockAnalyzer新闻获取测试失败\n")
    
    # 测试4: StockQA智能问答
    if test_stock_qa_with_gemini():
        success_count += 1
        print("✓ StockQA智能问答测试通过\n")
    else:
        print("✗ StockQA智能问答测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"Gemini工具调用和新闻获取测试完成: {success_count}/{total_tests} 项测试通过")
    if success_count == total_tests:
        print("🎉 所有Gemini功能测试通过！")
        print("✓ Gemini可以正确调用工具获取新闻")
        print("✓ 模型配置正确，避免了与OpenAI配置的混淆")
    elif success_count > 0:
        print("⚠️  部分Gemini功能正常，请检查失败的测试项")
    else:
        print("❌ 所有Gemini功能测试失败，请检查配置和网络连接")
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)