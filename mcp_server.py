#!/usr/bin/env python3
"""
UniMCPSim - Universal MCP Simulator Server
"""

import os
import sys
import json
import asyncio
import threading
import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import re

from fastmcp import FastMCP
from pydantic import BaseModel
from models import db_manager, ApplicationTemplate, Action, ActionParameter, Application
from ai_generator import ai_generator
from version import get_version
from logger_utils import mcp_logger

load_dotenv()

# 创建Flask应用
app = Flask(__name__)
CORS(app, origins="*", methods=["GET", "POST", "OPTIONS"],
     allow_headers=["Content-Type", "Accept", "Authorization", "mcp-session-id"])

# 会话管理
sessions = {}

# 创建FastMCP实例（用于MCP协议处理）
mcp = FastMCP(
    name="UniMCPSim",
    version=get_version(),
    instructions="Universal MCP Simulator - 通用MCP模拟器，可动态模拟各种产品的API接口"
)

# 线程本地存储
request_context = threading.local()

def set_current_context(token: str, app_path: str):
    """设置当前请求上下文"""
    request_context.token = token
    request_context.app_path = app_path

def get_current_context():
    """获取当前请求上下文"""
    return {
        'token': getattr(request_context, 'token', None),
        'app_path': getattr(request_context, 'app_path', None)
    }

class SimulatorEngine:
    """模拟器引擎"""

    def __init__(self):
        self.db = db_manager

    def process_request(self, category: str, product: str, action: str, params: Dict[str, Any], token: str) -> Dict[str, Any]:
        """处理模拟请求"""

        # 验证Token
        token_info = self.db.validate_token(token)
        if not token_info:
            return {"error": "Invalid token", "code": 401}

        # 获取应用
        app = self.db.get_application_by_path(category, product)
        if not app:
            return {"error": f"Application {category}/{product} not found", "code": 404}

        # 检查权限
        apps = self.db.get_token_applications(token)
        app_ids = [a.id for a in apps]
        if app.id not in app_ids:
            return {"error": "Access denied", "code": 403}

        # 解析模板
        template = app.template if app.template else {}
        actions = template.get('actions', [])

        # 查找动作
        action_def = None
        for act in actions:
            if act.get('name') == action:
                action_def = act
                break

        if not action_def:
            return {"error": f"Action {action} not found", "code": 404}

        # 验证参数
        required_params = [p for p in action_def.get('parameters', []) if p.get('required', False)]
        for param in required_params:
            if param['key'] not in params:
                return {"error": f"Missing required parameter: {param['key']}", "code": 400}

        # 生成响应（传递动作定义）
        response = ai_generator.generate_response(app.display_name, action, params, action_def)

        # 记录日志
        self.db.log_action(
            token_id=token_info['id'],
            app_id=app.id,
            action=action,
            params=params,
            response=response
        )

        return response


# 全局模拟器引擎
simulator = SimulatorEngine()


# 简化MCP工具注册 - 使用通用工具而不是动态生成
# 动态工具注册有复杂性，这里用静态通用工具


# 通用查询工具
@mcp.tool()
async def test_tool() -> str:
    """测试工具，返回简单信息"""
    return "UniMCPSim working!"




# 注释掉middleware，FastMCP的middleware语法可能不同
# 认证将通过其他方式处理


# MCP协议处理函数
def handle_mcp_request(data: dict, session_id: str = None, app_context: dict = None) -> dict:
    """处理MCP协议请求"""
    method = data.get('method')
    params = data.get('params', {})
    request_id = data.get('id')

    if method == 'initialize':
        # 创建新会话
        if not session_id:
            session_id = str(uuid.uuid4())

        sessions[session_id] = {
            'initialized': True,
            'client_info': params.get('clientInfo', {}),
            'created_at': datetime.now()
        }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "experimental": {},
                    "prompts": {"listChanged": True},
                    "resources": {"subscribe": False, "listChanged": True},
                    "tools": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "UniMCPSim",
                    "version": "1.0.0"
                },
                "instructions": "Universal MCP Simulator - 通用MCP模拟器，可动态模拟各种产品的API接口"
            }
        }

    elif method == 'tools/list':
        tools = []

        # 如果有应用上下文，生成该应用的专用工具
        if app_context and 'app' in app_context:
            app = app_context['app']
            token = app_context.get('token')

            # 获取应用的actions
            template = app.template if app.template else {}
            actions = template.get('actions', [])

            # 为每个action生成一个MCP工具
            for action in actions:
                action_name = action.get('name', '')
                action_display_name = action.get('display_name', action_name)
                action_description = action.get('description', '')
                action_parameters = action.get('parameters', [])

                # 构建输入schema
                input_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }

                for param in action_parameters:
                    param_key = param.get('key', '')
                    param_type = param.get('type', 'String').lower()
                    param_description = param.get('description', '')
                    param_required = param.get('required', False)
                    param_default = param.get('default')
                    param_options = param.get('options', [])

                    # 映射类型
                    schema_type = "string"
                    if param_type in ["integer", "int"]:
                        schema_type = "integer"
                    elif param_type in ["boolean", "bool"]:
                        schema_type = "boolean"
                    elif param_type == "array":
                        schema_type = "array"

                    prop_schema = {
                        "type": schema_type,
                        "description": param_description
                    }

                    if param_default is not None:
                        prop_schema["default"] = param_default

                    if param_options:
                        prop_schema["enum"] = param_options

                    if schema_type == "array":
                        prop_schema["items"] = {"type": "string"}

                    input_schema["properties"][param_key] = prop_schema

                    if param_required:
                        input_schema["required"].append(param_key)

                tools.append({
                    "name": action_name,
                    "description": f"{action_display_name} - {action_description}",
                    "inputSchema": input_schema
                })

        # 仅返回当前应用的专用工具

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "tools": tools
            }
        }

    elif method == 'tools/call':
        tool_name = params.get('name')
        arguments = params.get('arguments', {})

        if app_context and 'app' in app_context:
            # 处理应用特定的工具调用
            app = app_context['app']
            token = app_context.get('token')
            app_path = f"{app.category}/{app.name}"

            try:
                result = simulator.process_request(
                    app.category,
                    app.name,
                    tool_name,  # 工具名称就是action名称
                    arguments,
                    token
                )

                # 判断是否成功
                success = 'error' not in result or result.get('code', 200) < 400

                # 记录工具调用
                mcp_logger.log_tool_call(
                    tool_name=tool_name,
                    arguments=arguments,
                    result=result,
                    success=success,
                    error=result.get('error') if not success else None,
                    app_path=app_path
                )

                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "content": [{
                            "type": "text",
                            "text": json.dumps(result, ensure_ascii=False, indent=2)
                        }]
                    }
                }

            except Exception as e:
                error_msg = str(e)
                mcp_logger.log_tool_call(
                    tool_name=tool_name,
                    arguments=arguments,
                    success=False,
                    error=error_msg,
                    app_path=app_path
                )
                raise

    # 处理 ping 方法（心跳检测）
    elif method == 'ping':
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {}  # 返回空对象表示服务器存活
        }

    # 处理 notifications/initialized 方法（通知）
    elif method == 'notifications/initialized':
        # 这是一个通知，不需要返回结果
        # 但根据 JSON-RPC 规范，如果有 id 字段，需要返回响应
        if request_id is not None:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": {}
            }
        # 对于没有 id 的通知，不返回响应
        return None

    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "error": {
            "code": -32601,
            "message": "Method not found"
        }
    }


# Flask路由
@app.route('/<path:product_path>', methods=['GET', 'POST', 'OPTIONS'])
def handle_product_endpoint(product_path):
    """处理产品特定的端点"""
    if request.method == 'OPTIONS':
        return '', 200

    # 解析路径：/Category/Product
    path_parts = product_path.strip('/').split('/')
    if len(path_parts) != 2:
        mcp_logger.log_mcp_request(
            method=request.method,
            path=f"/{product_path}",
            token=request.args.get('token'),
            headers=dict(request.headers),
            success=False,
            error="Invalid path format. Expected: /Category/Product"
        )
        return jsonify({"error": "Invalid path format. Expected: /Category/Product"}), 400

    category, product = path_parts
    token = request.args.get('token')

    if not token:
        mcp_logger.log_auth_failure(
            reason="Token required",
            path=f"/{product_path}",
            ip=request.remote_addr
        )
        return jsonify({"error": "Token required"}), 401

    # 验证应用是否存在
    app_obj = db_manager.get_application_by_path(category, product)
    if not app_obj:
        mcp_logger.log_mcp_request(
            method=request.method,
            path=f"/{product_path}",
            token=token,
            headers=dict(request.headers),
            success=False,
            error=f"Application {category}/{product} not found"
        )
        return jsonify({"error": f"Application {category}/{product} not found"}), 404

    # 获取或创建会话ID
    session_id = request.headers.get('mcp-session-id')

    if request.method == 'GET':
        # GET请求返回应用信息
        apps = db_manager.get_token_applications(token)
        if app_obj not in apps:
            mcp_logger.log_auth_failure(
                reason="Access denied - token not authorized for this app",
                token=token,
                path=f"/{product_path}",
                ip=request.remote_addr
            )
            return jsonify({"error": "Access denied"}), 403

        template = app_obj.template if app_obj.template else {}
        actions = template.get('actions', [])

        response_data = {
            "category": app_obj.category,
            "name": app_obj.name,
            "display_name": app_obj.display_name,
            "description": app_obj.description,
            "actions": actions
        }

        mcp_logger.log_mcp_request(
            method=request.method,
            path=f"/{product_path}",
            token=token,
            headers=dict(request.headers),
            success=True,
            response=response_data
        )

        return jsonify(response_data)

    elif request.method == 'POST':
        # POST请求处理MCP协议
        if not request.is_json:
            mcp_logger.log_mcp_request(
                method=request.method,
                path=f"/{product_path}",
                token=token,
                headers=dict(request.headers),
                success=False,
                error="Content-Type must be application/json"
            )
            return jsonify({"error": "Content-Type must be application/json"}), 400

        data = request.get_json()
        mcp_method = data.get('method', 'unknown')

        # 创建应用上下文
        app_context = {
            'app': app_obj,
            'token': token
        }

        try:
            # 处理MCP请求
            response = handle_mcp_request(data, session_id, app_context)

            # 记录成功的MCP调用
            mcp_logger.log_mcp_request(
                method=f"POST:{mcp_method}",
                path=f"/{product_path}",
                params=data.get('params', {}),
                token=token,
                headers=dict(request.headers),
                success=True,
                response=response
            )

            # 设置响应头
            resp = Response(
                f"event: message\ndata: {json.dumps(response, ensure_ascii=False)}\n\n",
                content_type='text/event-stream'
            )

            # 如果是initialize请求，设置session ID
            if data.get('method') == 'initialize' and not session_id:
                new_session_id = list(sessions.keys())[-1] if sessions else str(uuid.uuid4())
                resp.headers['mcp-session-id'] = new_session_id

            return resp

        except Exception as e:
            error_msg = str(e)
            mcp_logger.log_mcp_request(
                method=f"POST:{mcp_method}",
                path=f"/{product_path}",
                params=data.get('params', {}),
                token=token,
                headers=dict(request.headers),
                success=False,
                error=error_msg
            )
            mcp_logger.error(f"MCP request processing error: {error_msg}", exc_info=True)
            return jsonify({"error": f"Internal server error: {error_msg}"}), 500




@app.route('/health', methods=['GET', 'HEAD', 'OPTIONS'])
def health_check():
    """健康检查端点"""
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # 检查数据库连接
        session = db_manager.get_session()
        session.query(Application).first()
        session.close()
        return jsonify({
            "status": "healthy",
            "service": "UniMCPSim",
            "version": get_version(),
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


def run_mcp_server():
    """运行MCP服务器"""
    # 获取端口配置
    port = int(os.getenv('MCP_SERVER_PORT', '9090'))
    print(f"Starting UniMCPSim MCP Server on port {port}...")

    # 初始化数据库
    db_manager.create_default_admin()

    print("Server endpoints:")
    print(f"- Product-specific: http://localhost:{port}/<Category>/<Product>?token=<token>")
    print(f"- Example: http://localhost:{port}/IM/WeChat?token=<token>")
    print("- CORS enabled for all origins")

    # 运行Flask服务器
    app.run(host='0.0.0.0', port=port, debug=False)


if __name__ == "__main__":
    run_mcp_server()