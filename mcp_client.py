#!/usr/bin/env python3
"""
MCP 客户端 - 用于调用外部 MCP Server
"""

import json
import httpx
from typing import Dict, Any, Optional, List
from logger_utils import mcp_logger


class MCPClient:
    """MCP 客户端，用于调用外部 MCP Server"""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """
        初始化 MCP 客户端

        Args:
            base_url: MCP Server 的基础 URL，如 http://127.0.0.1:9090/IM/WeChat?token=xxx
            timeout: 请求超时时间（秒）
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session_id: Optional[str] = None
        self.initialized = False

    def _make_request(self, method: str, params: Optional[Dict] = None, request_id: int = 1) -> Dict[str, Any]:
        """
        发送 MCP 请求

        Args:
            method: MCP 方法名
            params: 请求参数
            request_id: 请求 ID

        Returns:
            MCP 响应结果
        """
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "id": request_id
        }
        if params:
            payload["params"] = params

        headers = {
            "Content-Type": "application/json",
            "Accept": "text/event-stream"
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.base_url,
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()

                # 获取 session ID
                if "mcp-session-id" in response.headers:
                    self.session_id = response.headers["mcp-session-id"]

                # 解析 SSE 格式响应
                content = response.text
                return self._parse_sse_response(content)

        except httpx.TimeoutException:
            raise MCPClientError(f"请求超时（{self.timeout}秒）")
        except httpx.HTTPStatusError as e:
            raise MCPClientError(f"HTTP 错误: {e.response.status_code} - {e.response.text}")
        except httpx.RequestError as e:
            raise MCPClientError(f"请求错误: {str(e)}")

    def _parse_sse_response(self, content: str) -> Dict[str, Any]:
        """
        解析 SSE 格式的响应

        Args:
            content: 原始响应内容

        Returns:
            解析后的 JSON 对象
        """
        # SSE 格式: "event: message\ndata: {...}\n\n"
        lines = content.strip().split('\n')
        for line in lines:
            if line.startswith('data:'):
                json_str = line[5:].strip()
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    raise MCPClientError(f"JSON 解析错误: {str(e)}")

        # 如果没有 SSE 格式，尝试直接解析
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            raise MCPClientError(f"无法解析响应: {content[:200]}")

    def initialize(self) -> Dict[str, Any]:
        """
        初始化 MCP 会话

        Returns:
            初始化响应
        """
        params = {
            "protocolVersion": "2025-06-18",
            "capabilities": {
                "roots": {"listChanged": True},
                "sampling": {}
            },
            "clientInfo": {
                "name": "UniMCPSim-Playground",
                "version": "1.0.0"
            }
        }

        response = self._make_request("initialize", params)

        if "error" in response:
            raise MCPClientError(f"初始化失败: {response['error']}")

        self.initialized = True
        mcp_logger.info(f"MCP 会话初始化成功: {self.base_url}")
        return response.get("result", {})

    def list_tools(self) -> List[Dict[str, Any]]:
        """
        获取 MCP Server 的工具列表

        Returns:
            工具列表
        """
        if not self.initialized:
            self.initialize()

        response = self._make_request("tools/list")

        if "error" in response:
            raise MCPClientError(f"获取工具列表失败: {response['error']}")

        result = response.get("result", {})
        tools = result.get("tools", [])
        mcp_logger.info(f"获取到 {len(tools)} 个工具")
        return tools

    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        调用 MCP 工具

        Args:
            tool_name: 工具名称
            arguments: 工具参数

        Returns:
            工具调用结果
        """
        if not self.initialized:
            self.initialize()

        params = {
            "name": tool_name,
            "arguments": arguments
        }

        response = self._make_request("tools/call", params)

        if "error" in response:
            raise MCPClientError(f"工具调用失败: {response['error']}")

        result = response.get("result", {})

        # 解析返回的内容
        content = result.get("content", [])
        if content and isinstance(content, list):
            # 通常返回 [{"type": "text", "text": "..."}]
            for item in content:
                if item.get("type") == "text":
                    text = item.get("text", "")
                    try:
                        return json.loads(text)
                    except json.JSONDecodeError:
                        return {"result": text}

        return result


class MCPClientError(Exception):
    """MCP 客户端错误"""
    pass


def parse_mcp_config(config: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    解析 MCP 配置，提取服务器信息

    Args:
        config: MCP 配置 JSON

    Returns:
        服务器列表 [{"name": "xxx", "url": "xxx", "description": "xxx"}, ...]
    """
    servers = []
    mcp_servers = config.get("mcpServers", {})

    for name, server_config in mcp_servers.items():
        if not server_config.get("isActive", True):
            continue

        url = server_config.get("baseUrl") or server_config.get("url")
        if not url:
            continue

        servers.append({
            "name": name,
            "display_name": server_config.get("name", name),
            "url": url,
            "description": server_config.get("description", ""),
            "type": server_config.get("type", "streamableHttp")
        })

    return servers


def test_mcp_connection(url: str) -> Dict[str, Any]:
    """
    测试 MCP Server 连接

    Args:
        url: MCP Server URL

    Returns:
        测试结果，包含工具列表
    """
    try:
        client = MCPClient(url)
        init_result = client.initialize()
        tools = client.list_tools()

        return {
            "success": True,
            "server_info": init_result.get("serverInfo", {}),
            "capabilities": init_result.get("capabilities", {}),
            "tools": tools,
            "tool_count": len(tools)
        }

    except MCPClientError as e:
        return {
            "success": False,
            "error": str(e)
        }
    except Exception as e:
        mcp_logger.error(f"MCP 连接测试失败: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"连接失败: {str(e)}"
        }
