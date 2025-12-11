#!/usr/bin/env python3
"""
Playground 服务 - 处理对话和工具调用
"""

import json
import time
from typing import Dict, Any, Optional, List
from openai import OpenAI
from models import DatabaseManager
from mcp_client import MCPClient, MCPClientError, parse_mcp_config, test_mcp_connection
from logger_utils import mcp_logger


# 默认系统提示词
DEFAULT_SYSTEM_PROMPT = """# 角色
你是一个 MCP 工具调用助手。你可以使用 MCP 工具来帮助用户完成任务。

# 工具使用指南
1. 当用户请求需要使用工具时，选择合适的工具并调用
2. 在调用工具前，简要说明你将要执行的操作
3. 工具调用完成后，清晰地解释返回的结果
4. 如果工具调用失败，分析原因并尝试其他方法

# 注意事项
- 始终确保参数正确和完整
- 对于敏感操作（如封禁IP、删除数据），先确认用户意图
- 如果不确定应该使用哪个工具，可以询问用户
- 返回结果时，用简洁易懂的语言解释技术数据"""


class PlaygroundSession:
    """Playground 会话"""

    def __init__(self, session_id: str):
        self.session_id = session_id
        self.mcp_clients: Dict[str, MCPClient] = {}  # name -> MCPClient
        self.tools: List[Dict[str, Any]] = []
        self.tool_map: Dict[str, str] = {}  # tool_name -> server_name
        self.conversation_history: List[Dict[str, Any]] = []
        self.system_prompt = DEFAULT_SYSTEM_PROMPT
        self.created_at = time.time()

    def clear(self):
        """清除会话数据"""
        self.mcp_clients.clear()
        self.tools.clear()
        self.tool_map.clear()
        self.conversation_history.clear()


class PlaygroundService:
    """Playground 服务"""

    def __init__(self):
        self.db_manager = DatabaseManager()
        self.sessions: Dict[str, PlaygroundSession] = {}
        self._load_llm_config()

    def _load_llm_config(self):
        """加载 LLM 配置"""
        db_config = self.db_manager.get_llm_config()

        if db_config and db_config.api_key:
            self.api_key = db_config.api_key
            self.api_base = db_config.api_base_url or 'https://api.openai.com/v1'
            self.model = db_config.model_name or 'gpt-4o-mini'
            self.enable_stream = db_config.enable_stream
        else:
            import os
            from dotenv import load_dotenv
            load_dotenv()
            self.api_key = os.getenv('OPENAI_API_KEY')
            self.api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
            self.model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            self.enable_stream = os.getenv('OPENAI_STREAM', 'false').lower() == 'true'

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key, base_url=self.api_base)
            self.enabled = True
        else:
            self.client = None
            self.enabled = False

    def reload_config(self):
        """重新加载配置"""
        self._load_llm_config()

    def get_session(self, session_id: str) -> PlaygroundSession:
        """获取或创建会话"""
        if session_id not in self.sessions:
            self.sessions[session_id] = PlaygroundSession(session_id)
        return self.sessions[session_id]

    def clear_session(self, session_id: str):
        """清除会话"""
        if session_id in self.sessions:
            self.sessions[session_id].clear()

    def test_mcp_servers(self, session_id: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        测试 MCP Server 连接

        Args:
            session_id: 会话 ID
            config: MCP 配置

        Returns:
            测试结果
        """
        session = self.get_session(session_id)

        # 清除之前的连接
        session.mcp_clients.clear()
        session.tools.clear()
        session.tool_map.clear()

        # 解析配置
        servers = parse_mcp_config(config)
        if not servers:
            return {
                "success": False,
                "error": "未找到有效的 MCP Server 配置"
            }

        results = []
        all_tools = []

        for server in servers:
            server_name = server["name"]
            server_url = server["url"]

            try:
                client = MCPClient(server_url)
                init_result = client.initialize()
                tools = client.list_tools()

                # 保存客户端
                session.mcp_clients[server_name] = client

                # 为每个工具添加服务器标识
                for tool in tools:
                    tool_name = tool.get("name", "")
                    session.tool_map[tool_name] = server_name
                    all_tools.append(tool)

                results.append({
                    "server": server_name,
                    "display_name": server["display_name"],
                    "success": True,
                    "server_info": init_result.get("serverInfo", {}),
                    "tools": tools,
                    "tool_count": len(tools)
                })

            except MCPClientError as e:
                results.append({
                    "server": server_name,
                    "display_name": server["display_name"],
                    "success": False,
                    "error": str(e)
                })
            except Exception as e:
                mcp_logger.error(f"测试 MCP Server {server_name} 失败: {e}", exc_info=True)
                results.append({
                    "server": server_name,
                    "display_name": server["display_name"],
                    "success": False,
                    "error": f"连接失败: {str(e)}"
                })

        session.tools = all_tools

        # 统计成功和失败数量
        success_count = sum(1 for r in results if r["success"])
        total_count = len(results)

        return {
            "success": success_count > 0,
            "results": results,
            "summary": {
                "total": total_count,
                "success": success_count,
                "failed": total_count - success_count,
                "total_tools": len(all_tools)
            }
        }

    def _convert_tools_to_openai_format(self, tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        将 MCP 工具转换为 OpenAI 函数调用格式

        Args:
            tools: MCP 工具列表

        Returns:
            OpenAI 格式的工具列表
        """
        openai_tools = []

        for tool in tools:
            name = tool.get("name", "")
            description = tool.get("description", "")
            input_schema = tool.get("inputSchema", {})

            # 确保 schema 是有效的
            if not input_schema:
                input_schema = {"type": "object", "properties": {}}

            openai_tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": description,
                    "parameters": input_schema
                }
            })

        return openai_tools

    def chat(self, session_id: str, message: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """
        处理对话消息

        Args:
            session_id: 会话 ID
            message: 用户消息
            system_prompt: 系统提示词（可选）

        Returns:
            对话结果
        """
        if not self.enabled:
            return {
                "success": False,
                "error": "LLM 未配置，请先在「大模型配置」页面配置 API Key"
            }

        session = self.get_session(session_id)

        if system_prompt:
            session.system_prompt = system_prompt

        # 添加用户消息到历史
        session.conversation_history.append({
            "role": "user",
            "content": message
        })

        # 准备消息列表
        messages = [{"role": "system", "content": session.system_prompt}]
        messages.extend(session.conversation_history)

        # 转换工具为 OpenAI 格式
        tools = self._convert_tools_to_openai_format(session.tools) if session.tools else None

        # 记录对话过程
        events = []
        max_iterations = 10  # 防止无限循环

        try:
            for iteration in range(max_iterations):
                # 调用 LLM
                if tools:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        tools=tools,
                        tool_choice="auto"
                    )
                else:
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages
                    )

                assistant_message = response.choices[0].message

                # 检查是否有工具调用
                if assistant_message.tool_calls:
                    # 添加助手消息到历史
                    tool_calls_data = []
                    for tc in assistant_message.tool_calls:
                        tool_calls_data.append({
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        })

                    messages.append({
                        "role": "assistant",
                        "content": assistant_message.content,
                        "tool_calls": tool_calls_data
                    })

                    # 处理每个工具调用
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.function.name
                        try:
                            arguments = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            arguments = {}

                        # 记录工具调用事件
                        events.append({
                            "type": "tool_call",
                            "tool_name": tool_name,
                            "arguments": arguments
                        })

                        # 执行工具调用
                        tool_result = self._execute_tool(session, tool_name, arguments)

                        # 记录工具结果事件
                        events.append({
                            "type": "tool_result",
                            "tool_name": tool_name,
                            "result": tool_result
                        })

                        # 添加工具结果到消息
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result, ensure_ascii=False)
                        })

                else:
                    # 没有工具调用，返回最终响应
                    final_response = assistant_message.content or ""

                    # 添加助手消息到历史
                    session.conversation_history.append({
                        "role": "assistant",
                        "content": final_response
                    })

                    return {
                        "success": True,
                        "response": final_response,
                        "events": events
                    }

            # 达到最大迭代次数
            return {
                "success": False,
                "error": "达到最大工具调用次数，请简化您的请求",
                "events": events
            }

        except Exception as e:
            mcp_logger.error(f"Playground 对话失败: {e}", exc_info=True)
            return {
                "success": False,
                "error": f"对话失败: {str(e)}",
                "events": events
            }

    def _execute_tool(self, session: PlaygroundSession, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行工具调用

        Args:
            session: 会话
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具执行结果
        """
        # 查找工具所属的服务器
        server_name = session.tool_map.get(tool_name)
        if not server_name:
            return {"error": f"未找到工具: {tool_name}"}

        client = session.mcp_clients.get(server_name)
        if not client:
            return {"error": f"MCP Server 未连接: {server_name}"}

        try:
            result = client.call_tool(tool_name, arguments)
            return result
        except MCPClientError as e:
            return {"error": str(e)}
        except Exception as e:
            mcp_logger.error(f"工具调用失败: {tool_name}, {e}", exc_info=True)
            return {"error": f"调用失败: {str(e)}"}

    def get_conversation_history(self, session_id: str) -> List[Dict[str, Any]]:
        """获取对话历史"""
        session = self.get_session(session_id)
        return session.conversation_history

    def get_tools(self, session_id: str) -> List[Dict[str, Any]]:
        """获取当前会话的工具列表"""
        session = self.get_session(session_id)
        return session.tools

    def get_default_system_prompt(self) -> str:
        """获取默认系统提示词"""
        return DEFAULT_SYSTEM_PROMPT


# 全局 Playground 服务实例
playground_service = PlaygroundService()
