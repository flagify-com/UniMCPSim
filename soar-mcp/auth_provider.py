#!/usr/bin/env python3
"""
自定义AuthProvider - 基于FastMCP的认证提供者
集成现有的数据库token验证系统
"""

from typing import Optional, List
from starlette.requests import Request
from starlette.middleware import Middleware
from starlette.routing import BaseRoute, Route
from starlette.responses import JSONResponse

from fastmcp.server.auth import AuthProvider, AccessToken
from models import db_manager
from logger_config import logger


class SOARAuthProvider(AuthProvider):
    """
    SOAR自定义认证提供者
    基于URL参数中的token进行认证
    """

    def __init__(self, required_scopes: List[str] = None):
        """
        初始化认证提供者

        Args:
            required_scopes: 必需的作用域列表（暂时不使用，保留扩展性）
        """
        self.required_scopes = required_scopes or []
        logger.info("🔐 SOARAuthProvider初始化完成")

    async def authenticate(self, request: Request) -> Optional[AccessToken]:
        """
        认证请求并返回访问令牌

        Args:
            request: Starlette请求对象

        Returns:
            AccessToken对象（如果认证成功）或None（如果失败）
        """
        try:
            # 从URL参数获取token
            token_value = request.query_params.get('token')

            if not token_value:
                logger.debug("❌ 请求中缺少token参数")
                return None

            logger.debug(f"🔍 验证token: {token_value[:8]}...{token_value[-4:]}")

            # 使用现有的数据库验证逻辑
            token_info = db_manager.get_token_by_value(token_value)

            if not token_info:
                logger.warning(f"❌ 无效的token: {token_value[:8]}...")
                return None

            # 验证token是否有效（包括更新最后使用时间）
            is_valid = db_manager.verify_token(token_value)

            if not is_valid:
                logger.warning(f"❌ Token验证失败: {token_value[:8]}...")
                return None

            logger.debug(f"✅ Token验证成功: 用户={token_info['name']}")

            # 将用户信息存储到线程本地存储（简化版本，直接存储）
            try:
                # 由于这里不能直接导入simple_mcp_server（会产生循环导入），
                # 我们将在protected_mcp_endpoint中处理用户信息存储
                pass
            except Exception as e:
                logger.debug(f"存储用户信息到线程本地存储失败: {e}")

            # 创建AccessToken对象
            access_token = AccessToken(
                token=token_value,
                scopes=self.required_scopes,  # 使用配置的作用域
                expires_at=None,  # 我们的token没有过期时间限制
                user_id=str(token_info['id']),
                username=token_info['name']
            )

            return access_token

        except Exception as e:
            logger.error(f"❌ 认证过程出错: {e}")
            return None

    def get_middleware(self) -> List[Middleware]:
        """
        返回认证中间件列表

        Returns:
            中间件列表
        """
        # 使用FastMCP内置的认证中间件
        # 这个中间件会自动调用我们的authenticate方法
        return []

    def get_routes(self, mcp_path: str, mcp_endpoint) -> List[BaseRoute]:
        """
        返回认证相关的路由

        Args:
            mcp_path: MCP端点路径
            mcp_endpoint: MCP端点处理器

        Returns:
            路由列表
        """
        routes = []

        # 创建受保护的MCP端点
        async def protected_mcp_endpoint(request: Request):
            """受保护的MCP端点"""
            # 先进行认证
            access_token = await self.authenticate(request)

            if not access_token:
                return JSONResponse(
                    status_code=401,
                    content={
                        "error": "unauthorized",
                        "message": "Invalid or missing token. Please add ?token=your_token to the URL."
                    }
                )

            # 在请求中存储认证信息，供后续使用
            request.state.access_token = access_token
            request.state.user_id = access_token.user_id
            request.state.username = access_token.username

            # 将用户信息存储到线程本地存储中，供审计日志使用
            try:
                # 从token获取完整的token_info
                token_info = db_manager.get_token_by_value(access_token.token)
                # 由于循环导入问题，我们需要动态导入
                import simple_mcp_server
                simple_mcp_server.set_current_user_info(access_token.token, token_info)
                logger.debug(f"✅ 用户信息已存储到线程本地存储: {access_token.username}")
            except Exception as e:
                logger.debug(f"存储用户信息到线程本地存储失败: {e}")

            logger.debug(f"✅ 用户 {access_token.username} 通过认证，访问MCP端点")

            # 调用原始的MCP端点
            if callable(mcp_endpoint):
                return await mcp_endpoint(request)
            else:
                # 对于ASGI应用
                return await mcp_endpoint(request.scope, request.receive, request._send)

        # 添加受保护的MCP路由
        routes.append(
            Route(
                mcp_path,
                endpoint=protected_mcp_endpoint,
                methods=["GET", "POST"]
            )
        )

        # 添加健康检查端点
        async def health_check(request: Request):
            """健康检查端点"""
            return JSONResponse({
                "status": "healthy",
                "auth_provider": "SOARAuthProvider",
                "timestamp": db_manager.get_current_timestamp()
            })

        routes.append(
            Route("/health", endpoint=health_check, methods=["GET"])
        )

        return routes

    def _get_resource_url(self, path: str) -> str:
        """
        获取资源URL

        Args:
            path: 资源路径

        Returns:
            完整的资源URL
        """
        # 这个方法用于OAuth相关功能，我们暂时不需要
        return f"http://localhost{path}"


# 创建全局认证提供者实例
soar_auth_provider = SOARAuthProvider()