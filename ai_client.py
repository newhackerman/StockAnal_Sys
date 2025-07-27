# -*- coding: utf-8 -*-
"""
智能分析系统（股票） - 通用AI客户端
开发者：Kiro AI Assistant
版本：v1.0.0
许可证：MIT License

通用AI客户端，支持多种AI服务提供商，包括OpenAI、Gemini等
"""

import os
import json
import logging
import threading
import queue
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dotenv import load_dotenv

# 导入不同的AI客户端
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None

# 加载环境变量
load_dotenv()

class AIClient:
    """
    通用AI客户端，支持多种AI服务提供商
    """
    
    def __init__(self):
        """初始化AI客户端"""
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.api_provider = os.getenv('API_PROVIDER', 'openai').lower()
        self.timeout = int(os.getenv('AI_TIMEOUT', '180'))
        
        # OpenAI配置
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_api_url = os.getenv('OPENAI_API_URL', 'https://api.openai.com/v1')
        self.openai_model = os.getenv('OPENAI_API_MODEL', 'gpt-4o')
        
        # Gemini配置
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.google_api_url = os.getenv('GOOGLE_API_URL', 'https://generativelanguage.googleapis.com/v1beta')
        self.google_model = os.getenv('GOOGLE_API_MODEL', 'gemini-2.0-flash-exp')
        
        # 功能模型配置
        self.function_call_model = os.getenv('FUNCTION_CALL_MODEL', self.openai_model)
        self.news_model = os.getenv('NEWS_MODEL', self.openai_model)
        
        # Gemini专用模型配置 - 使用更明确的配置名称
        self.google_function_call_model = os.getenv('GOOGLE_FUNCTION_CALL_MODEL', self.google_model)
        self.google_news_model = os.getenv('GOOGLE_NEWS_MODEL', self.google_model)
        
        # 初始化客户端
        self.client = None
        self.gemini_client = None
        self._initialize_clients()
        
    def _initialize_clients(self):
        """初始化AI客户端"""
        try:
            # 初始化OpenAI客户端（用于OpenAI兼容的API）
            if self.openai_api_key:
                if self.api_provider == 'gemini_openai':
                    # 使用Gemini的OpenAI兼容接口
                    self.client = OpenAI(
                        api_key=self.google_api_key,
                        base_url=f"{self.google_api_url}/openai/"
                    )
                else:
                    # 标准OpenAI客户端
                    self.client = OpenAI(
                        api_key=self.openai_api_key,
                        base_url=self.openai_api_url
                    )
                    
            # 初始化原生Gemini客户端
            if self.google_api_key and genai:
                self.gemini_client = genai.Client(api_key=self.google_api_key)
                
            self.logger.info(f"AI客户端初始化完成，提供商: {self.api_provider}")
            
        except Exception as e:
            self.logger.error(f"初始化AI客户端失败: {str(e)}")
            
    def chat_completion(self, 
                       messages: List[Dict[str, str]], 
                       model: Optional[str] = None,
                       temperature: float = 0.7,
                       max_tokens: Optional[int] = None,
                       tools: Optional[List[Dict]] = None,
                       tool_choice: str = "auto",
                       stream: bool = False,
                       timeout: Optional[int] = None) -> Dict[str, Any]:
        """
        通用聊天完成接口
        
        参数:
            messages: 对话消息列表
            model: 使用的模型名称
            temperature: 温度参数
            max_tokens: 最大token数
            tools: 工具列表（用于function calling）
            tool_choice: 工具选择策略
            stream: 是否流式输出
            timeout: 超时时间
            
        返回:
            AI响应结果
        """
        if timeout is None:
            timeout = self.timeout
            
        if model is None:
            model = self._get_default_model()
            
        try:
            if self.api_provider == 'gemini_native':
                return self._gemini_native_completion(
                    messages, model, temperature, max_tokens, timeout
                )
            else:
                return self._openai_compatible_completion(
                    messages, model, temperature, max_tokens, tools, 
                    tool_choice, stream, timeout
                )
                
        except Exception as e:
            self.logger.error(f"AI聊天完成失败: {str(e)}")
            raise
            
    def _openai_compatible_completion(self, 
                                    messages: List[Dict[str, str]], 
                                    model: str,
                                    temperature: float,
                                    max_tokens: Optional[int],
                                    tools: Optional[List[Dict]],
                                    tool_choice: str,
                                    stream: bool,
                                    timeout: int) -> Dict[str, Any]:
        """OpenAI兼容的聊天完成"""
        if not self.client:
            raise ValueError("OpenAI客户端未初始化")
            
        # 构建请求参数
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
            "timeout": timeout
        }
        
        if max_tokens:
            params["max_tokens"] = max_tokens
            
        if tools:
            params["tools"] = tools
            params["tool_choice"] = tool_choice
            
        # 使用线程和队列实现超时控制
        result_queue = queue.Queue()
        
        def call_api():
            try:
                response = self.client.chat.completions.create(**params)
                result_queue.put(response)
            except Exception as e:
                result_queue.put(e)
                
        # 启动API调用线程
        api_thread = threading.Thread(target=call_api)
        api_thread.daemon = True
        api_thread.start()
        
        # 等待结果
        try:
            result = result_queue.get(timeout=timeout + 30)
            if isinstance(result, Exception):
                raise result
            return result
        except queue.Empty:
            raise TimeoutError(f"AI请求超时 ({timeout}秒)")
            
    def _gemini_native_completion(self, 
                                messages: List[Dict[str, str]], 
                                model: str,
                                temperature: float,
                                max_tokens: Optional[int],
                                timeout: int) -> Dict[str, Any]:
        """原生Gemini API聊天完成"""
        if not self.gemini_client:
            raise ValueError("Gemini客户端未初始化")
            
        # 转换消息格式为Gemini格式
        contents = self._convert_messages_to_gemini(messages)
        
        # 构建生成配置
        config = types.GenerateContentConfig(
            response_modalities=["text"],
            response_mime_type="text/plain",
            temperature=temperature
        )
        
        if max_tokens:
            config.max_output_tokens = max_tokens
            
        # 使用线程和队列实现超时控制
        result_queue = queue.Queue()
        
        def call_api():
            try:
                response = self.gemini_client.models.generate_content(
                    model=model,
                    contents=contents,
                    config=config
                )
                result_queue.put(response)
            except Exception as e:
                result_queue.put(e)
                
        # 启动API调用线程
        api_thread = threading.Thread(target=call_api)
        api_thread.daemon = True
        api_thread.start()
        
        # 等待结果
        try:
            result = result_queue.get(timeout=timeout + 30)
            if isinstance(result, Exception):
                raise result
                
            # 转换为OpenAI兼容格式
            return self._convert_gemini_response(result)
            
        except queue.Empty:
            raise TimeoutError(f"AI请求超时 ({timeout}秒)")
            
    def _convert_messages_to_gemini(self, messages: List[Dict[str, str]]) -> List[types.Content]:
        """将OpenAI格式的消息转换为Gemini格式"""
        contents = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            # Gemini的角色映射
            if role == "system":
                # 系统消息作为用户消息的前缀
                gemini_role = "user"
                content = f"[系统指令] {content}"
            elif role == "assistant":
                gemini_role = "model"
            else:
                gemini_role = "user"
                
            contents.append(types.Content(
                role=gemini_role,
                parts=[types.Part.from_text(text=content)]
            ))
            
        return contents
        
    def _convert_gemini_response(self, response) -> Dict[str, Any]:
        """将Gemini响应转换为OpenAI兼容格式"""
        try:
            # 提取文本内容
            text_content = ""
            if hasattr(response, 'text'):
                text_content = response.text
            elif hasattr(response, 'candidates') and response.candidates:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and candidate.content:
                    if hasattr(candidate.content, 'parts') and candidate.content.parts:
                        text_content = candidate.content.parts[0].text
                        
            # 构建OpenAI兼容的响应格式
            return type('Response', (), {
                'choices': [type('Choice', (), {
                    'message': type('Message', (), {
                        'content': text_content,
                        'role': 'assistant'
                    })()
                })()]
            })()
            
        except Exception as e:
            self.logger.error(f"转换Gemini响应失败: {str(e)}")
            raise
            
    def _get_default_model(self) -> str:
        """获取默认模型"""
        if self.api_provider == 'gemini_native':
            return self.google_model
        elif self.api_provider == 'gemini_openai':
            return self.google_model
        else:
            return self.openai_model
            
    def get_function_call_model(self) -> str:
        """获取工具调用专用模型"""
        if self.api_provider in ['gemini_native', 'gemini_openai']:
            return self.google_function_call_model
        else:
            return self.function_call_model
            
    def get_news_model(self) -> str:
        """获取新闻分析专用模型"""
        if self.api_provider in ['gemini_native', 'gemini_openai']:
            return self.google_news_model
        else:
            return self.news_model
            
    def get_available_models(self) -> List[str]:
        """获取可用的模型列表"""
        models = []
        
        if self.api_provider == 'openai' and self.openai_api_key:
            models.extend([
                'gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo'
            ])
            
        if self.google_api_key:
            models.extend([
                'gemini-2.0-flash-exp', 'gemini-1.5-pro', 'gemini-1.5-flash'
            ])
            
        return models
        
    def test_connection(self) -> Dict[str, Any]:
        """测试AI连接"""
        try:
            test_messages = [
                {"role": "user", "content": "Hello, please respond with 'Connection test successful'"}
            ]
            
            response = self.chat_completion(
                messages=test_messages,
                temperature=0.1,
                max_tokens=50,
                timeout=30
            )
            
            return {
                "success": True,
                "provider": self.api_provider,
                "model": self._get_default_model(),
                "response": response.choices[0].message.content
            }
            
        except Exception as e:
            return {
                "success": False,
                "provider": self.api_provider,
                "error": str(e)
            }
            
    def get_client_info(self) -> Dict[str, Any]:
        """获取客户端信息"""
        return {
            "provider": self.api_provider,
            "default_model": self._get_default_model(),
            "available_models": self.get_available_models(),
            "openai_configured": bool(self.openai_api_key),
            "gemini_configured": bool(self.google_api_key),
            "timeout": self.timeout
        }


class AIClientManager:
    """AI客户端管理器，提供单例模式的AI客户端"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if not self._initialized:
            self.client = AIClient()
            self._initialized = True
            
    def get_client(self) -> AIClient:
        """获取AI客户端实例"""
        return self.client
        
    def reload_client(self):
        """重新加载AI客户端（用于配置更新后）"""
        self.client = AIClient()


# 全局AI客户端管理器实例
ai_manager = AIClientManager()

def get_ai_client() -> AIClient:
    """获取全局AI客户端实例"""
    return ai_manager.get_client()