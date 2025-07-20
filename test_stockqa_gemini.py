#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试优化后的StockQA在使用Gemini时的工具调用功能
验证是否能正确调用TAVILY获取新闻
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_stockqa_with_gemini():
    """测试StockQA在使用Gemini时的工具调用"""
    print("=" * 60)
    print("测试StockQA使用Gemini的工具调用功能")
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
        print(f"工具调用模型: {stock_qa.ai_client.get_function_call_model()}")
        print(f"新闻分析模型: {stock_qa.ai_client.get_news_model()}")
        print(f"TAVILY API配置: {'✓' if stock_qa.tavily_api_key else '✗'}")
        print()
        
        # 测试不同类型的问题，看是否会触发工具调用
        test_cases = [
            {
                "stock_code": "000001",
                "question": "平安银行最近有什么新闻？",
                "expected_tool_call": True,
                "description": "明确询问最新新闻"
            },
            {
                "stock_code": "000001", 
                "question": "请分析一下平安银行的投资价值",
                "expected_tool_call": True,
                "description": "投资价值分析（需要最新信息）"
            },
            {
                "stock_code": "000001",
                "question": "平安银行目前的表现如何？",
                "expected_tool_call": True,
                "description": "询问目前表现"
            },
            {
                "stock_code": "00700",
                "question": "腾讯控股最近的动态怎么样？",
                "expected_tool_call": True,
                "description": "港股最新动态"
            },
            {
                "stock_code": "000001",
                "question": "什么是PE估值？",
                "expected_tool_call": False,
                "description": "纯概念问题（不需要最新信息）"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"测试{i}: {test_case['description']}")
            print(f"股票: {test_case['stock_code']}")
            print(f"问题: {test_case['question']}")
            print(f"预期工具调用: {'是' if test_case['expected_tool_call'] else '否'}")
            
            try:
                # 确定市场类型
                market_type = 'HK' if test_case['stock_code'].startswith('00') else 'A'
                
                # 调用StockQA
                result = stock_qa.answer_question(
                    stock_code=test_case['stock_code'],
                    question=test_case['question'],
                    market_type=market_type
                )
                
                if result and not result.get('error'):
                    used_tool = result.get('used_search_tool', False)
                    print(f"实际工具调用: {'是' if used_tool else '否'}")
                    
                    # 检查是否符合预期
                    if used_tool == test_case['expected_tool_call']:
                        print("✓ 工具调用行为符合预期")
                        success_count += 1
                        
                        if used_tool:
                            print("✓ 成功调用TAVILY搜索工具")
                            # 显示回答的前100个字符
                            answer_preview = result['answer'][:150] + "..." if len(result['answer']) > 150 else result['answer']
                            print(f"回答预览: {answer_preview}")
                        else:
                            print("✓ 正确地没有调用工具（不需要最新信息）")
                    else:
                        print("✗ 工具调用行为不符合预期")
                        if test_case['expected_tool_call']:
                            print("  应该调用工具但没有调用")
                        else:
                            print("  不应该调用工具但调用了")
                else:
                    print(f"✗ 问答失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"✗ 测试异常: {str(e)}")
                import traceback
                traceback.print_exc()
            
            print("-" * 40)
            print()
        
        print(f"测试结果: {success_count}/{len(test_cases)} 项符合预期")
        return success_count == len(test_cases)
        
    except Exception as e:
        print(f"✗ StockQA Gemini测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def test_tavily_search_directly():
    """直接测试TAVILY搜索功能"""
    print("=" * 60)
    print("直接测试TAVILY搜索功能")
    print("=" * 60)
    
    try:
        from stock_analyzer import StockAnalyzer
        from stock_qa import StockQA
        
        # 初始化
        analyzer = StockAnalyzer()
        stock_qa = StockQA(analyzer)
        
        if not stock_qa.tavily_api_key:
            print("✗ 未配置TAVILY_API_KEY，跳过直接搜索测试")
            return True
            
        print(f"✓ TAVILY API密钥已配置: {stock_qa.tavily_api_key[:10]}...")
        
        # 直接调用搜索方法
        print("测试直接调用search_stock_news方法...")
        
        search_result = stock_qa.search_stock_news(
            query="平安银行",
            stock_name="平安银行", 
            stock_code="000001",
            industry="金融业",
            market_type="A"
        )
        
        if search_result:
            print("✓ TAVILY搜索调用成功")
            print(f"消息: {search_result.get('message', '')}")
            print(f"结果数量: {len(search_result.get('results', []))}")
            
            # 显示前2条结果
            results = search_result.get('results', [])
            for i, result in enumerate(results[:2]):
                print(f"  {i+1}. {result.get('title', '无标题')}")
                print(f"     来源: {result.get('source', '未知')}")
                print(f"     摘要: {result.get('snippet', '无摘要')[:80]}...")
            
            return True
        else:
            print("✗ TAVILY搜索返回空结果")
            return False
            
    except Exception as e:
        print(f"✗ TAVILY搜索测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_system_prompt_effectiveness():
    """测试系统提示词的有效性"""
    print("=" * 60)
    print("测试系统提示词的有效性")
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
        
        # 使用优化后的系统提示词
        system_content = """你是专业的股票分析师。

## 重要工具使用规则：
- 当用户询问任何股票的最新情况、近期表现、新闻动态、市场消息时，你必须首先使用search_stock_news工具获取最新信息
- 不要基于过时的训练数据回答关于股票近期表现的问题
- 即使你认为可能没有相关新闻，也要先搜索确认
- 搜索后再结合技术分析和基本面数据提供综合分析

使用search_stock_news工具的触发条件包括但不限于：
- "最新"、"近期"、"最近"、"现在"、"目前"等时间词汇
- "新闻"、"消息"、"动态"、"表现"、"情况"等信息词汇
- 询问股票投资价值和分析时需要最新市场信息支撑
"""
        
        # 测试不同的问题
        test_questions = [
            "平安银行最近有什么新闻？",
            "请分析平安银行的投资价值",
            "平安银行目前表现如何？"
        ]
        
        success_count = 0
        
        for i, question in enumerate(test_questions, 1):
            print(f"测试{i}: {question}")
            
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": question}
            ]
            
            response = ai_client.chat_completion(
                messages=messages,
                model=ai_client.get_function_call_model(),
                tools=tools,
                tool_choice="auto",
                temperature=0.3
            )
            
            if hasattr(response, 'choices') and response.choices:
                message = response.choices[0].message
                if hasattr(message, 'tool_calls') and message.tool_calls:
                    print("  ✓ 成功触发工具调用")
                    for tool_call in message.tool_calls:
                        print(f"    工具: {tool_call.function.name}")
                        print(f"    参数: {tool_call.function.arguments}")
                    success_count += 1
                else:
                    print("  ✗ 没有触发工具调用")
                    print(f"    回答: {message.content[:100]}...")
            
            print()
        
        print(f"系统提示词有效性: {success_count}/{len(test_questions)} 项成功触发工具调用")
        return success_count >= len(test_questions) * 0.8  # 80%成功率即可
        
    except Exception as e:
        print(f"✗ 系统提示词测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def main():
    """主函数"""
    print("StockQA Gemini 工具调用功能测试")
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
    total_tests = 3
    
    # 测试1: StockQA工具调用
    if test_stockqa_with_gemini():
        success_count += 1
        print("✓ StockQA工具调用测试通过\n")
    else:
        print("✗ StockQA工具调用测试失败\n")
    
    # 测试2: 直接TAVILY搜索
    if test_tavily_search_directly():
        success_count += 1
        print("✓ TAVILY搜索测试通过\n")
    else:
        print("✗ TAVILY搜索测试失败\n")
    
    # 测试3: 系统提示词有效性
    if test_system_prompt_effectiveness():
        success_count += 1
        print("✓ 系统提示词测试通过\n")
    else:
        print("✗ 系统提示词测试失败\n")
    
    # 总结
    print("=" * 60)
    print(f"StockQA Gemini工具调用测试完成: {success_count}/{total_tests} 项测试通过")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！")
        print("✓ Gemini能够正确调用TAVILY工具获取新闻")
        print("✓ 系统提示词有效引导模型行为")
        print("✓ StockQA在使用Gemini时功能完全正常")
    elif success_count > 0:
        print("⚠️  部分功能正常，请检查失败的测试项")
        if not tavily_api_key:
            print("💡 建议配置TAVILY_API_KEY以获得更好的新闻搜索体验")
    else:
        print("❌ 所有测试失败，请检查配置和实现")
    
    print("=" * 60)
    
    return success_count == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)