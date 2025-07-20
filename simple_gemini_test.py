#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简化的Gemini测试脚本
"""

import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def test_gemini_direct():
    """直接测试Gemini API"""
    print("直接测试Gemini API...")
    
    try:
        from google import genai
        from google.genai import types
        
        # 获取API密钥
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ 未找到GOOGLE_API_KEY")
            return False
            
        print(f"✓ API密钥已配置: {api_key[:10]}...")
        
        # 初始化客户端
        client = genai.Client(api_key=api_key)
        model = os.getenv('GOOGLE_API_MODEL', 'gemini-2.0-flash-exp')
        
        print(f"✓ 使用模型: {model}")
        
        # 构建请求
        contents = [
            types.Content(
                role="user",
                parts=[
                    types.Part.from_text(text="请简单回答：什么是股票？用50字以内回答。"),
                ],
            ),
        ]
        
        config = types.GenerateContentConfig(
            response_modalities=["text"],
            response_mime_type="text/plain",
            temperature=0.7
        )
        
        print("发送请求到Gemini...")
        
        # 发送请求
        response = client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )
        
        if hasattr(response, 'text') and response.text:
            print("✓ Gemini原生API测试成功")
            print(f"回答: {response.text}")
            return True
        else:
            print("❌ Gemini响应为空")
            print(f"响应对象: {response}")
            return False
            
    except ImportError as e:
        print(f"❌ 导入google-genai失败: {e}")
        print("请运行: pip install google-genai")
        return False
    except Exception as e:
        print(f"❌ Gemini API测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gemini_openai_compatible():
    """测试Gemini OpenAI兼容接口"""
    print("\n测试Gemini OpenAI兼容接口...")
    
    try:
        from openai import OpenAI
        
        # 获取API密钥
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            print("❌ 未找到GOOGLE_API_KEY")
            return False
            
        # 初始化OpenAI客户端，使用Gemini的OpenAI兼容端点
        client = OpenAI(
            api_key=api_key,
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        
        model = os.getenv('GOOGLE_API_MODEL', 'gemini-2.0-flash-exp')
        print(f"✓ 使用模型: {model}")
        
        # 发送请求
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "user", "content": "请简单解释什么是技术分析？用80字以内回答。"}
            ],
            temperature=0.7,
            max_tokens=200
        )
        
        if response.choices and response.choices[0].message.content:
            print("✓ Gemini OpenAI兼容接口测试成功")
            print(f"回答: {response.choices[0].message.content}")
            return True
        else:
            print("❌ Gemini OpenAI兼容接口响应为空")
            return False
            
    except ImportError as e:
        print(f"❌ 导入openai失败: {e}")
        return False
    except Exception as e:
        print(f"❌ Gemini OpenAI兼容接口测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_client_with_gemini():
    """测试我们的AI客户端与Gemini"""
    print("\n测试AI客户端与Gemini...")
    
    try:
        # 临时设置为gemini_openai
        original_provider = os.getenv('API_PROVIDER', 'openai')
        os.environ['API_PROVIDER'] = 'gemini_openai'
        
        from ai_client import get_ai_client, AIClientManager
        
        # 重新加载客户端
        ai_manager = AIClientManager()
        ai_manager.reload_client()
        ai_client = get_ai_client()
        
        print(f"✓ AI客户端提供商: {ai_client.api_provider}")
        
        # 测试聊天
        response = ai_client.chat_completion(
            messages=[
                {"role": "user", "content": "请简单说明什么是基本面分析？用100字以内回答。"}
            ],
            temperature=0.7,
            max_tokens=200,
            timeout=30
        )
        
        if hasattr(response, 'choices') and response.choices:
            print("✓ AI客户端与Gemini集成测试成功")
            print(f"回答: {response.choices[0].message.content}")
            return True
        else:
            print("❌ AI客户端与Gemini集成测试失败")
            return False
            
    except Exception as e:
        print(f"❌ AI客户端与Gemini测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # 恢复原始设置
        os.environ['API_PROVIDER'] = original_provider

def main():
    """主函数"""
    print("简化Gemini测试")
    print("=" * 50)
    
    # 检查配置
    google_api_key = os.getenv('GOOGLE_API_KEY')
    if not google_api_key:
        print("❌ 未配置GOOGLE_API_KEY")
        return False
        
    print(f"✓ GOOGLE_API_KEY: {google_api_key[:10]}...")
    print(f"✓ GOOGLE_API_MODEL: {os.getenv('GOOGLE_API_MODEL', 'gemini-2.0-flash-exp')}")
    print()
    
    success_count = 0
    total_tests = 3
    
    # 测试1: 直接Gemini API
    if test_gemini_direct():
        success_count += 1
    
    # 测试2: Gemini OpenAI兼容接口
    if test_gemini_openai_compatible():
        success_count += 1
    
    # 测试3: AI客户端集成
    if test_ai_client_with_gemini():
        success_count += 1
    
    print(f"\n测试结果: {success_count}/{total_tests} 项通过")
    
    if success_count == total_tests:
        print("🎉 所有Gemini测试通过！")
    elif success_count > 0:
        print("⚠️  部分Gemini功能正常")
    else:
        print("❌ 所有Gemini测试失败")
    
    return success_count > 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)