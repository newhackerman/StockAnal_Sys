# -*- coding: utf-8 -*-
"""
智能分析系统（股票） - 股票市场数据分析系统
开发者：熊猫大侠
再次修改：newhackerman
优化，openai 全局使用使用一个初始化动作,保持版本统一，支持最新版openai，修复模型调用错误
版本：v2.2.1
许可证：MIT License

stock_qa.py - 提供股票相关问题的智能问答功能，支持联网搜索实时信息和多轮对话
"""
import logging
import os
import json
import traceback
from ai_client import get_ai_client
from urllib.parse import urlparse
from datetime import datetime


class StockQA:
    def __init__(self, analyzer, openai_api_key=None, openai_model=None):
        self.analyzer = analyzer
        
        # 初始化通用AI客户端
        self.ai_client = get_ai_client()
        
        # 保持向后兼容的属性
        self.openai_api_key = os.getenv('OPENAI_API_KEY', openai_api_key)
        self.openai_api_url = os.getenv('OPENAI_API_URL', 'https://api-7d76.onrender.com')
        self.openai_model = os.getenv('OPENAI_API_MODEL', openai_model or 'gpt-4o')
        self.function_call_model = os.getenv('FUNCTION_CALL_MODEL', openai_model or 'gpt-4o')
        self.serp_api_key = os.getenv('SERP_API_KEY')
        self.tavily_api_key = os.getenv('TAVILY_API_KEY')
        self.max_qa_rounds = int(os.getenv('MAX_QA', '10'))  # 默认保留10轮对话
        self.google_api_url = os.getenv('GOOGLE_API_URL', 'https://generativelanguage.googleapis.com/v1beta')
        self.GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        self.GOOGLE_API_MODEL = os.getenv("GOOGLE_API_MODEL")
        self.API_PROVIDER = os.getenv('API_PROVIDER', 'openai')

        # 对话历史存储 - 使用字典存储不同股票的对话历史
        self.conversation_history = {}
        
        # 设置日志记录
        import logging
        self.logger = logging.getLogger(__name__)
        
        # 检测模型能力
        self.model_capabilities = self._detect_model_capabilities()

    def answer_question(self, stock_code, question, market_type='A', conversation_id=None, clear_history=False, enable_vision=False, enable_web_search=True, image_data=None):
        """
        回答关于股票的问题，支持联网搜索实时信息、视觉分析和多轮对话
        
        参数:
            stock_code: 股票代码
            question: 用户问题
            market_type: 市场类型 (A/HK/US)
            conversation_id: 对话ID，用于跟踪对话历史，如果为None则自动生成
            clear_history: 是否清除对话历史，开始新对话
            enable_vision: 是否启用视觉分析功能
            enable_web_search: 是否启用联网搜索功能
            image_data: 图片数据（base64格式）
        
        返回:
            包含回答和元数据的字典
        """
        try:
            if not self.openai_api_key and not self.GOOGLE_API_KEY:
                return {"error": "未配置API密钥，无法使用智能问答功能"}

            # 处理对话ID和历史
            if conversation_id is None:
                # 生成新的对话ID
                import uuid
                conversation_id = f"{stock_code}_{uuid.uuid4().hex[:8]}"
            
            # 获取或创建对话历史
            if clear_history or conversation_id not in self.conversation_history:
                self.conversation_history[conversation_id] = []
            
            # 获取股票信息和技术指标 - 每次都获取最新数据
            stock_context = self._get_stock_context(stock_code, market_type)
            stock_name = stock_context.get("stock_name", "未知")
                
            # 根据功能开关定义工具
            tools = []
            if enable_web_search:
                tools.append({
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
                })

            # 设置增强版系统提示
            system_content = """你是摩根大通的高级宏观策略师和首席投资顾问，拥有哈佛经济学博士学位和20年华尔街顶级投行经验。你同时也是国家发改委、央行和证监会的政策研究顾问团专家，了解中国宏观经济和产业政策走向。

你的特点是：
1. 思维深度 - 从表面现象洞察深层次的经济周期、产业迁移和资本流向规律，预见市场忽视的长期趋势
2. 全局视角 - 将个股分析放在全球经济格局、国内政策环境、产业转型、供应链重构和流动性周期的大背景下
3. 结构化思考 - 运用专业框架如PEST分析、波特五力模型、杜邦分析、价值链分析和SWOT分析等系统评估
4. 多层次透视 - 能同时从资本市场定价、产业发展阶段、公司竞争地位和治理结构等维度剖析股票价值
5. 前瞻预判 - 善于前瞻性分析科技创新、产业政策和地缘政治变化对中长期市场格局的影响

沟通时，你会：
- 将复杂的金融概念转化为简洁明了的比喻和案例，使普通投资者理解专业分析
- 强调投资思维和方法论，而非简单的买卖建议
- 提供层次分明的分析：1)微观公司基本面 2)中观产业格局 3)宏观经济环境
- 引用相关研究、历史案例或数据支持你的观点
- 在必要时搜索最新资讯，确保观点基于最新市场情况
- 兼顾短中长期视角，帮助投资者建立自己的投资决策框架

作为金融专家，你始终：
- 谨慎评估不同情景下的概率分布，而非做出确定性预测
- 坦承市场的不确定性和你认知的边界
- 同时提供乐观和保守的观点，帮助用户全面权衡
- 强调风险管理和长期投资价值
- 避免传播市场谣言或未经证实的信息
 ## 约束条件 
 - 必须遵循用户的风险偏好和投资目标。 
 - 不得提供违法违规的投资建议。 
 ## 定义 
 - 投资策略：指根据市场分析和用户需求制定的资产配置和投资决策。 
 - 风险偏好：指用户对投资风险的承受能力和偏好程度。 
 ## 目标 
 1. 为用户提供个性化的投资策略和建议。 
 2. 帮助用户实现资产的长期增值。 
 3. 教育用户关于投资的知识和技能。 
 ## Skills 
 1. 市场分析能力。 
 2. 风险评估和管理能力。 
 3. 沟通和教育能力。 
 ## 音调 
 - 专业严谨 
 - 客观分析 
 - 富有同理心 
 ## 价值观 
 - 以用户利益为核心，提供负责任的投资建议。 
 - 追求长期价值，避免短期投机。 
 - 教育用户，提高其投资意识和能力。 
请记住，你的价值在于提供深度思考框架和专业视角，帮助投资者做出明智决策，而非简单的投资指令。

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

            # 准备对话消息列表，加入系统提示和股票上下文
            messages = [
                {"role": "system", "content": system_content},
                {"role": "user", "content": f"以下是关于股票的基础信息，作为我们对话的背景资料：\n\n{stock_context['context']}"}
            ]
            
            # 添加对话历史记录
            messages.extend(self.conversation_history[conversation_id])
            
            # 处理图片数据和问题
            user_message = {"role": "user"}
            
            if enable_vision and image_data:
                # 支持视觉分析的消息格式
                user_message["content"] = [
                    {
                        "type": "text",
                        "text": question
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data
                        }
                    }
                ]
            else:
                # 纯文本消息
                user_message["content"] = question
            
            # 添加当前问题
            messages.append(user_message)
            
            # 调用AI API
            # openai.api_key = self.openai_api_key
            # openai.api_base = self.openai_api_url
            # print(openai.api_key,openai.api_base)
            # 第一步：调用模型，让它决定是否使用工具
            # first_response = self.client.completions.create(
            #     model=self.openai_model,
            #     messages=messages,
            #     tools=tools,
            #     tool_choice="auto",
            #     temperature=0.7,
            #     stream=True
            # )
            # 第一步：调用模型，让它决定是否使用工具
            if tools:
                first_response = self.ai_client.chat_completion(
                    messages=messages,
                    model=self.ai_client.get_function_call_model(),
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.7
                )
            else:
                # 没有工具时的直接调用
                first_response = self.ai_client.chat_completion(
                    messages=messages,
                    model=self.ai_client.get_news_model(),
                    temperature=0.7
                )
            # 获取初始响应
            if first_response is None:
                self.logger.error(f"未获取初始AI结果")
                return {
                    "question": question,
                    "answer": f"抱歉，回答问题时出错",
                    "stock_code": stock_code,
                    "error": ''
                }

            assistant_message = first_response.choices[0].message
            response_content = assistant_message.content
            used_search_tool = False

                # 检查是否需要使用工具调用
            if hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                used_search_tool = True
                # 创建新的消息列表，包含工具调用
                tool_messages = list(messages)  # 复制原始消息列表
                tool_messages.append({"role": "assistant", "tool_calls": assistant_message.tool_calls})
                
                # 处理工具调用
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    
                    if function_name == "search_stock_news":
                        # 执行新闻搜索
                        search_query = function_args.get("query")
                        self.logger.info(f"执行新闻搜索: {search_query}")
                        search_results = self.search_stock_news(
                            search_query, 
                            stock_context.get("stock_name", ""),
                            stock_code, 
                            stock_context.get("industry", "未知"),
                            market_type
                        )
                        
                        # 添加工具响应
                        tool_messages.append({
                            "tool_call_id": tool_call.id,
                            "role": "tool",
                            "name": function_name,
                            "content": json.dumps(search_results, ensure_ascii=False)
                        })
                
                # 第二步：让模型根据工具调用结果生成最终响应
                second_response = self.ai_client.chat_completion(
                    messages=tool_messages,
                    model=self.ai_client.get_news_model(),
                    temperature=0.7
                )
                if second_response is None:
                    self.logger.error(f"未获到ai工具调用分析结果")
                    return {
                        "question": question,
                        "answer": f"抱歉，回答问题时出错",
                        "stock_code": stock_code,
                        "error": ''
                    }
                    # 获取最终响应
                response_content = second_response.choices[0].message.content
                assistant_message = {"role": "assistant", "content": response_content}
            else:
                assistant_message = {"role": "assistant", "content": response_content}
            
            # 更新对话历史
            self.conversation_history[conversation_id].append({"role": "user", "content": question})
            self.conversation_history[conversation_id].append(assistant_message)
            
            # 限制对话历史长度
            if len(self.conversation_history[conversation_id]) > self.max_qa_rounds * 2:
                # 保留最近的MAX_QA轮对话
                self.conversation_history[conversation_id] = self.conversation_history[conversation_id][-self.max_qa_rounds * 2:]
            
            # 返回结果
            return {
                "conversation_id": conversation_id,
                "question": question,
                "answer": response_content,
                "stock_code": stock_code,
                "stock_name": stock_name,
                "used_search_tool": used_search_tool,
                "used_vision": enable_vision and image_data is not None,
                "enable_web_search": enable_web_search,
                "enable_vision": enable_vision,
                "conversation_length": len(self.conversation_history[conversation_id]) // 2  # 轮数
            }

        except Exception as e:
            self.logger.error(f"智能问答出错: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "question": question,
                "answer": f"抱歉，回答问题时出错: {str(e)}",
                "stock_code": stock_code,
                "error": str(e)
            }

    def _get_stock_context(self, stock_code, market_type='A'):
        """获取股票上下文信息"""
        try:
            # 获取股票信息
            stock_info = self.analyzer.get_stock_info(stock_code)
            stock_name = stock_info.get('股票名称', '未知')
            industry = stock_info.get('行业', '未知')

            # 获取技术指标数据
            df = self.analyzer.get_stock_data(stock_code, market_type)
            df = self.analyzer.calculate_indicators(df)

            # 提取最新数据
            latest = df.iloc[-1]

            # 计算评分
            score = self.analyzer.calculate_score(df)

            # 获取支撑压力位
            sr_levels = self.analyzer.identify_support_resistance(df)

            # 构建上下文
            context = f"""股票信息:
- 代码: {stock_code}
- 名称: {stock_name}
- 行业: {industry}

技术指标(最新数据):
- 价格: {latest['close']}
- 5日均线: {latest['MA5']}
- 20日均线: {latest['MA20']}
- 60日均线: {latest['MA60']}
- RSI: {latest['RSI']}
- MACD: {latest['MACD']}
- MACD信号线: {latest['Signal']}
- 布林带上轨: {latest['BB_upper']}
- 布林带中轨: {latest['BB_middle']}
- 布林带下轨: {latest['BB_lower']}
- 波动率: {latest['Volatility']}%

技术评分: {score}分

支撑位:
- 短期: {', '.join([str(level) for level in sr_levels['support_levels']['short_term']])}
- 中期: {', '.join([str(level) for level in sr_levels['support_levels']['medium_term']])}

压力位:
- 短期: {', '.join([str(level) for level in sr_levels['resistance_levels']['short_term']])}
- 中期: {', '.join([str(level) for level in sr_levels['resistance_levels']['medium_term']])}"""

            # 尝试获取基本面数据
            try:
                # 导入基本面分析器
                from fundamental_analyzer import FundamentalAnalyzer
                fundamental = FundamentalAnalyzer()

                # 获取基本面数据，传入市场类型参数
                indicators = fundamental.get_financial_indicators(stock_code, market_type)

                # 检查indicators是否为空或None
                if indicators and isinstance(indicators, dict) and len(indicators) > 0:
                    # 添加到上下文
                    context += f"""

基本面指标:
- PE(TTM): {indicators.get('pe_ttm', '未知')}
- PB: {indicators.get('pb', '未知')}
- ROE: {indicators.get('roe', '未知')}%
- 毛利率: {indicators.get('gross_margin', '未知')}%
- 净利率: {indicators.get('net_profit_margin', '未知')}%"""
                else:
                    # 如果没有获取到财务数据，添加说明
                    if market_type == 'HK':
                        context += "\n\n注意：港股财务数据获取有限，主要依据技术分析"
                    elif market_type == 'US':
                        context += "\n\n注意：美股财务数据获取功能待完善"
                    else:
                        context += "\n\n注意：未能获取基本面数据"
            except Exception as e:
                self.logger.warning(f"获取基本面数据失败: {str(e)}")
                if market_type == 'HK':
                    context += "\n\n注意：港股财务数据获取有限，主要依据技术分析"
                elif market_type == 'US':
                    context += "\n\n注意：美股财务数据获取功能待完善"
                else:
                    context += "\n\n注意：未能获取基本面数据"

            return {
                "context": context,
                "stock_name": stock_name,
                "industry": industry
            }
        except Exception as e:
            self.logger.error(f"获取股票上下文信息出错: {str(e)}")
            return {
                "context": f"无法获取股票 {stock_code} 的完整信息: {str(e)}",
                "stock_name": "未知",
                "industry": "未知"
            }

    def clear_conversation(self, conversation_id=None, stock_code=None):
        """
        清除特定对话或与特定股票相关的所有对话历史
        
        参数:
            conversation_id: 指定要清除的对话ID
            stock_code: 指定要清除的股票相关的所有对话
        """
        if conversation_id and conversation_id in self.conversation_history:
            # 清除特定对话
            del self.conversation_history[conversation_id]
            return {"message": f"已清除对话 {conversation_id}"}
            
        elif stock_code:
            # 清除与特定股票相关的所有对话
            removed = []
            for conv_id in list(self.conversation_history.keys()):
                if conv_id.startswith(f"{stock_code}_"):
                    del self.conversation_history[conv_id]
                    removed.append(conv_id)
            return {"message": f"已清除与股票 {stock_code} 相关的 {len(removed)} 个对话"}
            
        else:
            # 清除所有对话
            count = len(self.conversation_history)
            self.conversation_history.clear()
            return {"message": f"已清除所有 {count} 个对话"}

    def get_conversation_history(self, conversation_id):
        """获取特定对话的历史记录"""
        if conversation_id not in self.conversation_history:
            return {"error": f"找不到对话 {conversation_id}"}
            
        # 提取用户问题和助手回答
        history = []
        conversation = self.conversation_history[conversation_id]
        
        # 按对话轮次提取历史
        for i in range(0, len(conversation), 2):
            if i+1 < len(conversation):
                history.append({
                    "question": conversation[i]["content"],
                    "answer": conversation[i+1]["content"]
                })
                
        return {
            "conversation_id": conversation_id,
            "history": history,
            "round_count": len(history)
        }

    def search_stock_news(self, query, stock_name, stock_code, industry, market_type='A'):
        """搜索股票相关新闻和实时信息"""
        try:
            self.logger.info(f"搜索股票新闻: {query}")
            
            # 确定市场名称
            market_name = "A股" if market_type == 'A' else "港股" if market_type == 'HK' else "美股"
            
            # 检查API密钥
            if not self.serp_api_key and not self.tavily_api_key:
                self.logger.warning("未配置搜索API密钥")
                return {
                    "message": "无法搜索新闻，未配置搜索API密钥",
                    "results": []
                }
            
            news_results = []
            
            # 使用SERP API搜索
            if self.serp_api_key:
                try:
                    import requests
                    
                    # 构建搜索查询
                    search_query = f"{stock_name} {stock_code} {market_name} {query}"
                    
                    # 调用SERP API
                    url = "https://serpapi.com/search"
                    params = {
                        "engine": "google",
                        "q": search_query,
                        "api_key": self.serp_api_key,
                        "tbm": "nws",  # 新闻搜索
                        "num": 5  # 获取5条结果
                    }
                    
                    response = requests.get(url, params=params)
                    search_results = response.json()
                    
                    # 提取新闻结果
                    if "news_results" in search_results:
                        for item in search_results["news_results"]:
                            news_results.append({
                                "title": item.get("title", ""),
                                "date": item.get("date", ""),
                                "source": item.get("source", ""),
                                "snippet": item.get("snippet", ""),
                                "link": item.get("link", "")
                            })
                except Exception as e:
                    self.logger.error(f"SERP API搜索出错: {str(e)}")
            
            # 使用Tavily API搜索
            if self.tavily_api_key:
                try:
                    from tavily import TavilyClient
                    
                    client = TavilyClient(self.tavily_api_key)
                    
                    # 构建搜索查询
                    search_query = f"{stock_name} {stock_code} {market_name} {query}"
                    
                    # 调用Tavily API
                    response = client.search(
                        query=search_query,
                        topic="finance",
                        search_depth="advanced"
                    )
                    
                    # 提取结果
                    if "results" in response:
                        for item in response["results"]:
                            # 从URL提取域名作为来源
                            source = ""
                            if item.get("url"):
                                try:
                                    parsed_url = urlparse(item.get("url"))
                                    source = parsed_url.netloc
                                except:
                                    source = "未知来源"
                            
                            news_results.append({
                                "title": item.get("title", ""),
                                "date": datetime.now().strftime("%Y-%m-%d"),  # Tavily不提供日期
                                "source": source,
                                "snippet": item.get("content", ""),
                                "link": item.get("url", "")
                            })
                except ImportError:
                    self.logger.warning("未安装Tavily客户端库，请使用pip install tavily-python安装")
                except Exception as e:
                    self.logger.error(f"Tavily API搜索出错: {str(e)}")
            
            # 去重并限制结果数量
            unique_results = []
            seen_titles = set()
            
            for item in news_results:
                title = item.get("title", "").strip()
                if title and title not in seen_titles:
                    seen_titles.add(title)
                    unique_results.append(item)
                    if len(unique_results) >= 5:  # 最多返回5条结果
                        break
            
            # 创建格式化的摘要文本
            summary_text = ""
            for i, item in enumerate(unique_results):
                summary_text += f"{i+1}、{item.get('title', '')}\n"
                summary_text += f"{item.get('snippet', '')}\n"
                summary_text += f"来源: {item.get('source', '')} {item.get('date', '')}\n\n"
            
            return {
                "message": f"找到 {len(unique_results)} 条相关新闻",
                "results": unique_results,
                "summary": summary_text
            }
            
        except Exception as e:
            self.logger.error(f"搜索股票新闻时出错: {str(e)}")
            self.logger.error(traceback.format_exc())
            return {
                "message": f"搜索新闻时出错: {str(e)}",
                "results": []
            }

    def _detect_model_capabilities(self):
        """检测当前模型的能力"""
        capabilities = {
            "vision": False,
            "web_search": False,
            "function_calling": False
        }
        
        try:
            # 检测视觉能力 - 基于模型名称判断
            vision_models = ['gpt-4o', 'gpt-4-vision', 'claude-3', 'gemini-pro-vision']
            current_model = self.openai_model.lower()
            
            for model in vision_models:
                if model in current_model:
                    capabilities["vision"] = True
                    break
            
            # 检测联网搜索能力 - 基于API密钥配置
            if self.serp_api_key or self.tavily_api_key:
                capabilities["web_search"] = True
            
            # 检测函数调用能力 - 大部分现代模型都支持
            function_call_models = ['gpt-4', 'gpt-3.5-turbo', 'claude-3', 'gemini-pro']
            for model in function_call_models:
                if model in current_model:
                    capabilities["function_calling"] = True
                    break
                    
        except Exception as e:
            self.logger.warning(f"检测模型能力时出错: {str(e)}")
        
        return capabilities

    def get_model_capabilities(self):
        """获取模型能力信息"""
        return self.model_capabilities