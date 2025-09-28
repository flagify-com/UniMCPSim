#!/usr/bin/env python3
"""
SOAR MCP服务器 - 使用FastMCP简化版本
超简洁的API，符合官方推荐的最佳实践
"""

import json
import os
import asyncio
import requests
import urllib3
import threading
import time
from datetime import datetime, timedelta
from typing import Optional, Union
from flask import Flask, jsonify, request, send_file
from threading import Thread

# 禁用SSL证书警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from fastmcp import FastMCP
from dotenv import load_dotenv
from version import __version__
from models import DatabaseManager, db_manager
from sync_service import PlaybookSyncService, AppsSyncService
from logger_config import logger
from auth_utils import jwt_required
from auth_provider import soar_auth_provider

# 加载环境变量
load_dotenv()

# 创建FastMCP应用 - 超简单！
mcp = FastMCP(
    name="SOAR MCP Server",
    version=__version__,
    instructions="SOAR (Security Orchestration, Automation and Response) 平台集成服务器，提供安全编排、自动化和响应功能。"
)

# 执行活动存储（用于跟踪剧本执行状态）
EXECUTIONS = {}

# ===== 线程本地存储 - 用于存储当前请求的用户信息 =====
request_context = threading.local()

def set_current_user_info(token: str, token_info: dict):
    """设置当前请求的用户信息到线程本地存储"""
    request_context.token = token
    request_context.token_info = token_info
    request_context.user_id = token_info.get('id') if token_info else None
    request_context.username = token_info.get('name') if token_info else None

def get_current_user_info() -> dict:
    """从线程本地存储获取当前请求的用户信息"""
    return {
        'token': getattr(request_context, 'token', None),
        'token_info': getattr(request_context, 'token_info', None),
        'user_id': getattr(request_context, 'user_id', None),
        'username': getattr(request_context, 'username', None)
    }

def clear_current_user_info():
    """清理当前请求的用户信息"""
    for attr in ['token', 'token_info', 'user_id', 'username']:
        if hasattr(request_context, attr):
            delattr(request_context, attr)

# ===== Token验证功能 =====

def get_token_from_context() -> Optional[str]:
    """
    从线程本地存储中获取token
    如果没有，则尝试从Flask上下文获取（兼容性）
    """
    try:
        # 首先从线程本地存储获取（主要认证方式）
        user_info = get_current_user_info()
        if user_info['token']:
            logger.debug(f"✅ 从线程本地存储获取token成功: {user_info['token'][:8]}...{user_info['token'][-4:]}")
            return user_info['token']

        # 回退到Flask上下文（兼容性支持，主要用于管理后台）
        try:
            from flask import has_request_context, request as flask_request

            if has_request_context():
                # 调试信息：打印请求详情
                logger.debug(f"🔍 Flask请求信息: URL={flask_request.url}, Path={flask_request.path}, Args={dict(flask_request.args)}")

                # 从URL参数获取token
                token = flask_request.args.get('token')
                if token:
                    logger.debug(f"✅ Flask获取token成功: {token[:8]}...{token[-4:]}")
                    return token.strip()
                else:
                    logger.debug("ℹ️ Flask URL参数中未找到token（正常，MCP请求通过FastMCP认证）")

            else:
                logger.debug("ℹ️ 没有Flask请求上下文（正常，MCP请求通过FastMCP处理）")
        except Exception as e:
            logger.debug(f"⚠️ Flask上下文访问失败: {e}")

        # 对于MCP请求，认证已在SOARAuthProvider中完成，这里找不到token是正常的
        logger.debug("ℹ️ 审计系统未找到token（MCP请求认证已在FastMCP层完成）")
        return None

    except Exception as e:
        logger.warning(f"获取token失败: {e}")
        return None


def log_audit_from_context(action: str = "unknown", resource: str = None, parameters: dict = None, result: str = "success") -> None:
    """
    从线程本地存储获取用户信息并记录审计日志
    AuthProvider已经完成认证并存储了用户信息，这里直接使用
    """
    try:
        # 从线程本地存储获取用户信息（推荐方式）
        user_info = get_current_user_info()
        token_info = user_info['token_info']

        # 如果线程本地存储中没有，则回退到传统方式
        if not token_info:
            try:
                # 从上下文获取token
                token = get_token_from_context()
                if token:
                    token_info = db_manager.get_token_by_value(token)
                    logger.debug(f"回退到传统方式获取token信息: {token[:8]}...{token[-4:]}")
            except Exception as e:
                logger.debug(f"获取token上下文失败: {e}")

        # 记录审计日志 - 使用现有的接口
        db_manager.log_audit_event(
            action=action,
            resource=resource,
            parameters=parameters,
            result=result,
            token_info=token_info  # 使用现有的token_info参数
        )

        user_name = token_info.get('name', 'unknown') if token_info else 'unknown'
        logger.debug(f"审计日志记录成功: {action} -> {result}")
        logger.debug(f"✅ 审计日志已记录: {action} - 用户={user_name}")

    except Exception as e:
        logger.error(f"记录审计日志异常: {e}")


def verify_mcp_token(action: str = "unknown", resource: str = None, parameters: dict = None) -> bool:
    """
    兼容性函数：保持与现有代码的兼容性
    现在只记录审计日志，认证由AuthProvider处理
    """
    log_audit_from_context(action, resource, parameters)
    return True  # AuthProvider已经完成认证，这里总是返回True



# ===== ID转换工具函数 =====

def parse_playbook_id(playbook_id) -> int:
    """
    解析剧本ID，支持两种输入格式
    - LONG整数：直接返回
    - 字符串格式的整数："123456"
    
    Args:
        playbook_id: 剧本ID，支持int或str格式
    
    Returns:
        int: 解析后的整数ID
    
    Raises:
        ValueError: 无法解析ID格式时抛出
    """
    if isinstance(playbook_id, int):
        return playbook_id
    elif isinstance(playbook_id, str):
        return int(playbook_id)  # 直接转换字符串数字
    else:
        raise ValueError(f"不支持的剧本ID格式: {type(playbook_id)} - {playbook_id}")

# 创建Flask应用用于后台管理
admin_app = Flask(__name__)

# ===== 后台管理API端点 =====

@admin_app.route('/login')
def login_page():
    """登录页面"""
    try:
        return send_file('login.html')
    except FileNotFoundError:
        return jsonify({"error": "登录页面未找到"}), 404

@admin_app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.get_json()
        if not data or 'adminPassword' not in data:
            return jsonify({"success": False, "error": "请提供管理员密码"}), 400

        admin_password = data['adminPassword'].strip()
        if not admin_password:
            return jsonify({"success": False, "error": "管理员密码不能为空"}), 400

        auth_manager = admin_app.auth_manager
        jwt_token = auth_manager.login_with_password(admin_password)

        if jwt_token:
            return jsonify({
                "success": True,
                "jwt": jwt_token,
                "message": "登录成功"
            })
        else:
            return jsonify({"success": False, "error": "密码无效，请检查后重试"}), 401

    except Exception as e:
        logger.error(f"管理员登录失败: {e}")
        return jsonify({"success": False, "error": "登录过程中发生错误"}), 500

@admin_app.route('/api/admin/verify', methods=['GET'])
def verify_token():
    """验证JWT Token"""
    try:
        from auth_utils import jwt_required
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({"valid": False}), 401

        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
        except IndexError:
            return jsonify({"valid": False}), 401

        auth_manager = admin_app.auth_manager
        payload = auth_manager.verify_jwt(token)

        if payload:
            return jsonify({"valid": True, "user": payload})
        else:
            return jsonify({"valid": False}), 401

    except Exception as e:
        logger.error(f"Token验证失败: {e}")
        return jsonify({"valid": False}), 401

def require_auth():
    """认证装饰器 - 检查JWT或重定向到登录页"""
    auth_header = request.headers.get('Authorization')

    # 如果是API请求，需要Authorization header
    if request.path.startswith('/api/admin/'):
        if not auth_header:
            return jsonify({'error': '需要认证token'}), 401

        try:
            token = auth_header.split(' ')[1]  # Bearer <token>
            auth_manager = admin_app.auth_manager
            payload = auth_manager.verify_jwt(token)
            if not payload:
                return jsonify({'error': 'token无效或已过期'}), 401
        except (IndexError, AttributeError):
            return jsonify({'error': 'Authorization header格式错误'}), 401

    # 如果是页面请求，检查是否需要重定向到登录
    else:
        # 简单检查 - 在实际应用中，你可能需要更复杂的会话管理
        pass

    return None

@admin_app.route('/admin')
def admin_page():
    """管理后台首页"""
    # 页面访问暂时不强制验证JWT，因为前端会通过localStorage检查
    try:
        return send_file('admin.html')
    except FileNotFoundError:
        return jsonify({"error": "管理页面未找到"}), 404

@admin_app.route('/static/<path:filename>')
def serve_static(filename):
    """提供静态文件服务"""
    try:
        return send_file(f'static/{filename}')
    except FileNotFoundError:
        return jsonify({"error": "文件未找到"}), 404

@admin_app.route('/api/admin/playbooks')
@jwt_required
def get_admin_playbooks():
    """获取所有剧本（用于管理界面）"""
    try:
        playbooks = db_manager.get_playbooks_admin()
        return jsonify({
            "success": True,
            "data": playbooks,
            "total": len(playbooks)
        })
    except Exception as e:
        logger.error(f"获取管理剧本列表失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_app.route('/api/admin/playbooks/<string:playbook_id>')
@jwt_required
def get_playbook_detail(playbook_id):
    """获取单个剧本详情"""
    try:
        # 移除id_前缀并转换为长整型进行数据库查询
        if playbook_id.startswith('id_'):
            playbook_id_int = int(playbook_id[3:])  # 移除'id_'前缀
        else:
            playbook_id_int = int(playbook_id)  # 兼容旧格式
        playbook = db_manager.get_playbook_by_id(playbook_id_int)
        if playbook:
            return jsonify({
                "success": True,
                "data": playbook
            })
        else:
            return jsonify({
                "success": False,
                "error": "剧本未找到"
            }), 404
    except Exception as e:
        logger.error(f"获取剧本详情失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@admin_app.route('/api/admin/playbooks/<string:playbook_id>/toggle', methods=['POST'])
@jwt_required
def toggle_playbook(playbook_id):
    """切换剧本启用状态"""
    try:
        # 移除id_前缀并转换为长整型进行数据库操作
        if playbook_id.startswith('id_'):
            playbook_id_int = int(playbook_id[3:])  # 移除'id_'前缀
        else:
            playbook_id_int = int(playbook_id)  # 兼容旧格式
        data = request.get_json()
        enabled = data.get('enabled', True)
        
        success = db_manager.update_playbook_status(playbook_id_int, enabled)
        
        if success:
            return jsonify({
                "success": True,
                "message": f"剧本 {playbook_id} 已{'启用' if enabled else '禁用'}"
            })
        else:
            return jsonify({
                "success": False,
                "error": f"未找到剧本 {playbook_id}"
            }), 404
            
    except Exception as e:
        logger.error(f"切换剧本状态失败: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# 系统配置API端点
@admin_app.route('/api/admin/config', methods=['GET'])
@jwt_required
def get_system_config():
    """获取系统配置"""
    try:
        from config_manager import config_manager
        config = config_manager.get_soar_config()
        
        # 隐藏敏感信息的部分内容
        config_dict = config.model_dump()
        if config_dict.get('soar_api_token'):
            token = config_dict['soar_api_token']
            if len(token) > 10:
                config_dict['soar_api_token'] = token[:6] + '*' * (len(token) - 10) + token[-4:]
        
        return jsonify({
            "success": True,
            "data": config_dict
        })
    except Exception as e:
        logger.error(f"获取系统配置失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/config', methods=['POST'])
@jwt_required
def update_system_config():
    """更新系统配置"""
    try:
        from config_manager import config_manager
        from models import SystemConfigData

        data = request.get_json()

        # 获取更新前的配置，用于比较变化
        old_config = config_manager.get_soar_config()

        # 如果Token字段不存在（部分更新），使用现有Token
        if 'soar_api_token' not in data:
            data['soar_api_token'] = old_config.soar_api_token

        # 验证数据
        try:
            config_data = SystemConfigData(**data)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"配置数据格式错误: {e}"
            }), 400

        # 检查是否有影响同步的关键配置发生变化
        sync_affecting_changes = False
        sync_affecting_fields = []

        # API地址变化
        if old_config.soar_api_url != config_data.soar_api_url:
            sync_affecting_changes = True
            sync_affecting_fields.append("API地址")

        # API Token变化（只有当新Token不是掩码时才比较）
        if 'soar_api_token' in data and not data['soar_api_token'].startswith('***'):
            if old_config.soar_api_token != config_data.soar_api_token:
                sync_affecting_changes = True
                sync_affecting_fields.append("API Token")

        # 标签变化
        if set(old_config.soar_labels or []) != set(config_data.soar_labels or []):
            sync_affecting_changes = True
            sync_affecting_fields.append("标签配置")

        # 超时时间变化
        if old_config.soar_timeout != config_data.soar_timeout:
            sync_affecting_changes = True
            sync_affecting_fields.append("超时设置")

        # 更新配置
        success = config_manager.update_soar_config(config_data)

        if success:
            # 如果有影响同步的配置变化，触发立即同步
            if sync_affecting_changes:
                logger.info(f"检测到影响同步的配置变化: {', '.join(sync_affecting_fields)}")

                # 触发立即同步（在后台线程中执行，避免阻塞API响应）
                import threading
                import asyncio

                def trigger_immediate_sync():
                    """在后台线程中触发立即同步"""
                    try:
                        # 检查配置是否完整（防止配置不完整时触发同步）
                        if not config_manager.is_first_run():
                            logger.sync_start(f"配置变化触发立即同步 ({', '.join(sync_affecting_fields)})...")

                            # 创建新的事件循环来执行同步
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            try:
                                # 执行同步
                                playbook_sync_service = PlaybookSyncService(db_manager)
                                result = loop.run_until_complete(playbook_sync_service.full_sync())

                                if "error" in result:
                                    logger.sync_warning(f"配置变化触发的同步失败: {result['error']}")
                                else:
                                    logger.sync_success("配置变化触发的同步完成!")
                                    logger.info(f"同步统计: {result.get('sync_result', {})}")

                            except Exception as e:
                                logger.sync_error(f"配置变化触发的同步异常: {e}")
                            finally:
                                loop.close()
                        else:
                            logger.info("配置仍不完整，跳过立即同步")

                    except Exception as e:
                        logger.error(f"触发立即同步失败: {e}")

                # 在后台线程中启动同步
                sync_thread = threading.Thread(target=trigger_immediate_sync, daemon=True)
                sync_thread.start()

                return jsonify({
                    "success": True,
                    "message": "系统配置已更新，正在触发数据同步..."
                })
            else:
                return jsonify({
                    "success": True,
                    "message": "系统配置已更新"
                })
        else:
            return jsonify({
                "success": False,
                "error": "配置更新失败"
            }), 500

    except Exception as e:
        logger.error(f"更新系统配置失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/config/validate', methods=['POST'])
@jwt_required
def validate_system_config():
    """验证系统配置"""
    try:
        from config_manager import config_manager
        
        # 如果请求中有配置数据，先临时更新再验证
        if request.is_json:
            data = request.get_json()
            if data:
                from models import SystemConfigData
                try:
                    config_data = SystemConfigData(**data)
                    # 临时更新配置用于验证（不保存到数据库）
                    config_manager._config_cache.update({
                        'soar_api_url': config_data.soar_api_url,
                        'soar_api_token': config_data.soar_api_token,
                        'soar_timeout': config_data.soar_timeout,
                        'soar_labels': config_data.soar_labels
                    })
                except Exception as e:
                    return jsonify({
                        "success": False,
                        "error": f"配置数据格式错误: {e}"
                    }), 400
        
        validation_result = config_manager.validate_config()
        
        return jsonify({
            "success": True,
            "data": validation_result
        })
        
    except Exception as e:
        logger.error(f"验证系统配置失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/config/test', methods=['POST'])
@jwt_required
def test_connection():
    """测试API连接"""
    try:
        from config_manager import config_manager
        
        # 如果请求中有配置数据，先临时更新再测试
        if request.is_json:
            data = request.get_json()
            if data:
                from models import SystemConfigData
                try:
                    config_data = SystemConfigData(**data)
                    # 临时更新配置用于测试（不保存到数据库）
                    config_manager._config_cache.update({
                        'soar_api_url': config_data.soar_api_url,
                        'soar_api_token': config_data.soar_api_token,
                        'soar_timeout': config_data.soar_timeout,
                        'soar_labels': config_data.soar_labels
                    })
                except Exception as e:
                    return jsonify({
                        "success": False,
                        "error": f"配置数据格式错误: {e}"
                    }), 400
        
        test_result = config_manager.test_connection()
        
        return jsonify({
            "success": True,
            "data": test_result
        })
        
    except Exception as e:
        logger.error(f"测试连接失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500

@admin_app.route('/api/admin/tokens', methods=['GET'])
@jwt_required
def get_tokens():
    """获取所有Token列表"""
    try:
        tokens = db_manager.get_user_tokens()
        return jsonify({
            "success": True,
            "data": tokens
        })
    except Exception as e:
        logger.error(f"获取Token列表失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/tokens', methods=['POST'])
@jwt_required
def create_token():
    """创建新Token"""
    try:
        data = request.get_json()
        if not data or 'name' not in data:
            return jsonify({"success": False, "error": "请提供Token名称"}), 400

        name = data['name'].strip()
        expires_in_days = data.get('expires_in_days')

        if not name:
            return jsonify({"success": False, "error": "Token名称不能为空"}), 400

        token = db_manager.create_user_token(name, expires_in_days)

        if token:
            return jsonify({
                "success": True,
                "token": token,
                "message": "Token创建成功"
            })
        else:
            return jsonify({"success": False, "error": "Token创建失败"}), 500

    except Exception as e:
        logger.error(f"创建Token失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/tokens/<int:token_id>', methods=['DELETE'])
@jwt_required
def delete_token(token_id):
    """删除Token"""
    try:
        success = db_manager.delete_user_token(token_id)

        if success:
            return jsonify({
                "success": True,
                "message": "Token删除成功"
            })
        else:
            return jsonify({"success": False, "error": "Token删除失败或不存在"}), 404

    except Exception as e:
        logger.error(f"删除Token失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/tokens/<int:token_id>/toggle', methods=['POST'])
@jwt_required
def toggle_token_status(token_id):
    """切换Token启用状态"""
    try:
        data = request.get_json()
        if not data or 'is_active' not in data:
            return jsonify({"success": False, "error": "请提供is_active参数"}), 400

        is_active = data['is_active']
        success = db_manager.update_token_status(token_id, is_active)

        if success:
            return jsonify({
                "success": True,
                "message": f"Token已{'启用' if is_active else '禁用'}"
            })
        else:
            return jsonify({"success": False, "error": "Token状态更新失败或不存在"}), 404

    except Exception as e:
        logger.error(f"更新Token状态失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


@admin_app.route('/api/admin/stats', methods=['GET'])
@jwt_required
def get_system_stats():
    """获取系统统计信息"""
    try:
        # 获取剧本统计
        playbooks_stats = db_manager.get_playbooks_stats()

        # 获取应用统计
        apps_stats = db_manager.get_apps_stats()
        
        # 组合统计信息
        stats = {
            **playbooks_stats,
            **apps_stats,
            "last_sync_time": db_manager.get_last_sync_time()
        }
        
        return jsonify({
            "success": True,
            "stats": stats
        })
        
    except Exception as e:
        logger.error(f"获取系统统计失败: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


def start_admin_server(port):
    """启动管理后台服务器"""
    admin_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# ===== 工具定义 - 超简洁的装饰器语法 =====

















# ===== 新增：剧本管理和执行工具 =====

@mcp.tool
def list_playbooks_quick(category: Optional[str] = None, limit: int = 100) -> str:
    """
    获取简洁的剧本列表 - 只包含基本信息(ID, name, displayName)
    适用于LLM快速理解剧本选项

    重要说明：返回的剧本ID为LONG类型（64位整数），在某些场景下可能超出JavaScript安全整数范围。

    Args:
        category: 按分类筛选剧本（可选）
        limit: 限制返回数量，默认100

    Returns:
        包含剧本列表的JSON字符串，每个剧本包含：
        - id: LONG类型剧本ID（用于API调用）
        - name: 剧本内部名称
        - displayName: 剧本显示名称
    """
    # Token验证
    if not verify_mcp_token(
        action="list_playbooks_quick",
        resource="soar://playbooks",
        parameters={"category": category, "limit": limit}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        playbooks = db_manager.get_playbooks(category=category, limit=limit)
        
        result = {
            "total": len(playbooks),
            "playbooks": [
                {
                    "id": p.id,
                    "name": p.name,
                    "displayName": p.display_name
                } for p in playbooks
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"获取剧本列表失败: {str(e)}"
        }, ensure_ascii=False, indent=2)


@mcp.tool
def query_playbook_execution_params(playbook_id: Union[int, str]) -> str:
    """
    查询剧本执行参数 - 根据剧本ID获取执行所需的参数定义

    重要说明：剧本ID为LONG类型（64位整数），支持整数和字符串格式输入。

    Args:
        playbook_id: 剧本ID，支持以下格式：
            - LONG整数：11210381659280175
            - 字符串整数："11210381659280175"

    Returns:
        包含剧本参数定义的JSON字符串，包含：
        - playbookId: LONG类型剧本ID
        - playbookName: 剧本内部名称
        - playbookDisplayName: 剧本显示名称
        - requiredParams: 必需参数列表
    """
    # Token验证
    if not verify_mcp_token(
        action="query_playbook_execution_params",
        resource=f"soar://playbooks/{playbook_id}",
        parameters={"playbook_id": playbook_id}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        # 解析并转换剧本ID为标准整数格式
        playbook_id_int = parse_playbook_id(playbook_id)
        playbook = db_manager.get_playbook(playbook_id_int)
        
        if not playbook:
            return json.dumps({
                "error": f"未找到剧本 ID: {playbook_id}"
            }, ensure_ascii=False, indent=2)
        
        result = {
            "playbookId": playbook.id,
            "playbookName": playbook.name,
            "playbookDisplayName": playbook.display_name,
            "requiredParams": [
                {
                    "paramName": param.cef_column,
                    "paramDesc": param.cef_desc,
                    "paramType": param.value_type,
                    "required": True  # 所有CEF参数都是必需的
                } for param in playbook.playbook_params
            ]
        }
        
        return json.dumps(result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": f"查询剧本参数失败: {str(e)}"
        }, ensure_ascii=False, indent=2)

@mcp.tool
def execute_playbook(playbook_id: Union[int, str], parameters: Optional[dict] = None, event_id: int = 0) -> str:
    """
    执行SOAR剧本

    Args:
        playbook_id: 剧本ID，支持整数或字符串格式
        parameters: 执行参数字典（可选），格式 {"参数名": "参数值"}
        event_id: 事件ID（默认0）

    Returns:
        返回包含activity_id的JSON，用此ID查询状态和结果
        示例: {"success": true, "activity_id": "c1ca56df-9d64-4dbb-be0f-44ffdda62384"}
    """
    # Token验证
    if not verify_mcp_token(
        action="execute_playbook",
        resource=f"soar://playbooks/{playbook_id}/execute",
        parameters={"playbook_id": playbook_id, "parameters": parameters, "event_id": event_id}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    if parameters is None:
        parameters = {}

    try:
        # 解析并转换剧本ID为标准整数格式
        playbook_id_int = parse_playbook_id(playbook_id)
        # 验证剧本是否存在
        playbook = db_manager.get_playbook(playbook_id_int)
        if not playbook:
            return json.dumps({
                "error": f"未找到剧本 ID: {playbook_id}"
            }, ensure_ascii=False, indent=2)
        
        # 转换参数格式为API所需的格式
        api_params = []
        if parameters:
            for key, value in parameters.items():
                api_params.append({
                    "key": key,
                    "value": str(value)
                })
        
        # 构造API请求数据格式（参考提供的curl示例）
        api_request = {
            "eventId": event_id,
            "executorInstanceId": playbook_id,
            "executorInstanceType": "PLAYBOOK",
            "params": api_params
        }
        
        # 调用真实的SOAR API执行剧本，使用配置管理器的配置
        from config_manager import config_manager
        base_url = config_manager.get_api_url()
        api_token = config_manager.get_api_token()
        api_url = f"{base_url.rstrip('/')}/api/event/execution"
        
        headers = {
            'hg-token': api_token,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"调用SOAR API执行剧本 ID: {playbook_id}, 事件ID: {event_id}, 参数: {parameters}")
        
        # 发送POST请求到SOAR API，使用配置管理器的超时和SSL设置
        timeout = config_manager.get_timeout()
        ssl_verify = config_manager.get_ssl_verify()
        response = requests.post(api_url, headers=headers, json=api_request, timeout=timeout, verify=ssl_verify)
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")
        
        api_result = response.json()
        
        if api_result.get('code') != 200:
            raise Exception(f"API返回错误: {api_result}")
        
        # 获取活动ID
        activity_id = api_result.get('result')
        if not activity_id:
            raise Exception("API未返回活动ID")
        
        logger.info(f"剧本执行启动成功，活动ID: {activity_id}")
        
        # 构造返回结果 - 简化结构，关键信息前置，与参数命名保持一致
        execution_result = {
            "success": True,
            "activity_id": activity_id  # 与MCP工具参数命名保持一致
        }
        
        # 存储执行记录（可选，用于历史查询）
        EXECUTIONS[activity_id] = execution_result
        
        return json.dumps(execution_result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"执行剧本失败: {str(e)}",
            "playbookId": playbook_id,
            "eventId": event_id,
            "parameters": parameters,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool
def query_playbook_execution_status_by_activity_id(activity_id: str) -> str:
    """
    查询剧本执行状态

    Args:
        activity_id: 活动ID，从execute_playbook返回的activity_id字段获取
                    示例: "c1ca56df-9d64-4dbb-be0f-44ffdda62384"

    Returns:
        返回执行状态，当status为SUCCESS时可查询结果
    """
    # 参数验证 - 确保activity_id不为空
    if not activity_id or activity_id.strip() == "":
        return json.dumps({
            "success": False,
            "error": "❌ activity_id 参数不能为空！",
            "help": "请从 execute_playbook 返回结果的 activity_id 字段中获取有效的活动ID",
            "example": "正确的activity_id应该类似: 'c1ca56df-9d64-4dbb-be0f-44ffdda62384'"
        }, ensure_ascii=False, indent=2)

    # Token验证
    if not verify_mcp_token(
        action="query_playbook_execution_status_by_activity_id",
        resource=f"soar://executions/{activity_id}/status",
        parameters={"activity_id": activity_id}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        # 调用真实的SOAR API查询执行状态，使用配置管理器的配置
        from config_manager import config_manager
        base_url = config_manager.get_api_url()
        api_token = config_manager.get_api_token()
        api_url = f"{base_url.rstrip('/')}/odp/core/v1/api/activity/{activity_id}"
        
        headers = {
            'hg-token': api_token,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"查询剧本执行状态，活动ID: {activity_id}")
        
        # 发送GET请求到SOAR API，使用配置管理器的超时和SSL设置
        timeout = config_manager.get_timeout()
        ssl_verify = config_manager.get_ssl_verify()
        response = requests.get(api_url, headers=headers, timeout=timeout, verify=ssl_verify)
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")
        
        api_result = response.json()
        
        if api_result.get('code') != 200:
            raise Exception(f"API返回错误: {api_result}")
        
        result_data = api_result.get('result', {})
        execution_status = result_data.get('executeStatus', 'UNKNOWN')
        
        logger.info(f"活动 {activity_id} 执行状态: {execution_status}")
        
        # 构造返回结果 - 关键信息前置
        status_result = {
            "success": True,
            "activityId": activity_id,
            "status": execution_status,
            "message": f"📊 执行状态: {execution_status}\n" + (
                f"✅ 执行已完成！请使用活动ID {activity_id} 调用 query_playbook_execution_result_by_activity_id 查询详细结果"
                if execution_status == "SUCCESS"
                else f"⏳ 执行进行中，请稍后使用活动ID {activity_id} 再次调用 query_playbook_execution_status_by_activity_id 查询"
            ),
            "queryTime": datetime.now().isoformat(),
            # 详细信息放在details中
            "details": {
                "executeStatus": execution_status,
                "eventId": result_data.get('eventId'),
                "executorInstanceId": result_data.get('executorInstanceId'),
                "executorInstanceName": result_data.get('executorInstanceName'),
                "executorInstanceType": result_data.get('executorInstanceType'),
                "createTime": result_data.get('createTime'),
                "updateTime": result_data.get('updateTime'),
                "postStatus": result_data.get('postStatus'),
                "apiResponse": api_result
            }
        }
        
        return json.dumps(status_result, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"查询执行状态失败: {str(e)}",
            "activityId": activity_id,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

@mcp.tool
def query_playbook_execution_result_by_activity_id(activity_id: str) -> str:
    """
    查询剧本执行详细结果

    Args:
        activity_id: 活动ID，从execute_playbook返回的activity_id字段获取
                    示例: "c1ca56df-9d64-4dbb-be0f-44ffdda62384"

    Returns:
        返回详细执行结果，建议先确认status为SUCCESS后调用
    """
    # 参数验证 - 确保activity_id不为空
    if not activity_id or activity_id.strip() == "":
        return json.dumps({
            "success": False,
            "error": "❌ activity_id 参数不能为空！",
            "help": "请从 execute_playbook 返回结果的 activity_id 字段中获取有效的活动ID",
            "example": "正确的activity_id应该类似: 'c1ca56df-9d64-4dbb-be0f-44ffdda62384'"
        }, ensure_ascii=False, indent=2)

    # Token验证
    if not verify_mcp_token(
        action="query_playbook_execution_result_by_activity_id",
        resource=f"soar://executions/{activity_id}/result",
        parameters={"activity_id": activity_id}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        # 调用真实的SOAR API查询执行结果，使用配置管理器的配置
        from config_manager import config_manager
        base_url = config_manager.get_api_url()
        api_token = config_manager.get_api_token()
        api_url = f"{base_url.rstrip('/')}/odp/core/v1/api/event/activity?activityId={activity_id}"
        
        headers = {
            'hg-token': api_token,
            'Content-Type': 'application/json'
        }
        
        logger.info(f"查询剧本执行结果，活动ID: {activity_id}")
        
        # 发送GET请求到SOAR API，使用配置管理器的超时和SSL设置
        timeout = config_manager.get_timeout()
        ssl_verify = config_manager.get_ssl_verify()
        response = requests.get(api_url, headers=headers, timeout=timeout, verify=ssl_verify)
        
        if response.status_code != 200:
            raise Exception(f"API调用失败: {response.status_code}, {response.text}")
        
        api_result = response.json()
        
        if api_result.get('code') != 200:
            raise Exception(f"API返回错误: {api_result}")
        
        logger.info(f"成功获取活动 {activity_id} 的执行结果")

        # 构造返回结果 - 关键信息前置
        result_info = {
            "success": True,
            "activityId": activity_id,
            "message": f"✅ 成功获取剧本执行结果！\n📋 活动ID: {activity_id}\n📊 执行结果数据已包含在 executionResult 字段中",
            "queryTime": datetime.now().isoformat(),
            "executionResult": api_result  # 包含完整的执行结果数据
        }
        
        return json.dumps(result_info, ensure_ascii=False, indent=2)
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": f"查询执行结果失败: {str(e)}",
            "activityId": activity_id,
            "timestamp": datetime.now().isoformat()
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)

# ===== 资源定义 - 超简洁的装饰器语法 =====

@mcp.resource("soar://applications")
def get_applications_resource() -> str:
    """获取SOAR应用资源"""
    # Token验证
    if not verify_mcp_token(
        action="get_applications_resource",
        resource="soar://applications",
        parameters={}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        apps = db_manager.get_apps(limit=10)
        return json.dumps([{
            "id": app.id,
            "name": app.name,
            "description": app.description,
            "version": app.version,
            "category": app.category
        } for app in apps], ensure_ascii=False, indent=2)
    except:
        return json.dumps({"message": "应用资源暂不可用"}, ensure_ascii=False, indent=2)

@mcp.resource("soar://playbooks")
def get_playbooks_resource() -> str:
    """获取SOAR剧本资源"""
    # Token验证
    if not verify_mcp_token(
        action="get_playbooks_resource",
        resource="soar://playbooks",
        parameters={}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    try:
        playbooks = db_manager.get_playbooks(limit=10)
        return json.dumps([{
            "id": p.id,
            "name": p.name,
            "displayName": p.display_name,
            "category": p.playbook_category
        } for p in playbooks], ensure_ascii=False, indent=2)
    except:
        return json.dumps({"message": "剧本资源暂不可用"}, ensure_ascii=False, indent=2)

@mcp.resource("soar://executions")
def get_executions_resource() -> str:
    """获取执行活动资源"""
    # Token验证
    if not verify_mcp_token(
        action="get_executions_resource",
        resource="soar://executions",
        parameters={}
    ):
        return json.dumps({
            "error": "访问被拒绝：无效的token或缺少token参数。请在MCP客户端URL中添加?token=your_token"
        }, ensure_ascii=False, indent=2)

    return json.dumps(list(EXECUTIONS.values()), ensure_ascii=False, indent=2)

# ===== 启动服务器 - 就这么简单！ =====

async def startup_sync():
    """服务器启动时执行初始同步"""
    try:
        # 检查是否跳过同步（用于测试）
        skip_sync = os.getenv("SKIP_SYNC", "false").lower() == "true"
        if skip_sync:
            logger.sync_warning("跳过启动同步 (SKIP_SYNC=true)")
            return

        # 检查是否为首次运行
        from config_manager import config_manager
        if config_manager.is_first_run():
            # 首次运行：跳过同步，提示用户配置
            missing_configs = config_manager.get_missing_required_configs()
            logger.info("=" * 60)
            logger.info("🔔 检测到首次运行，跳过数据同步")
            logger.info(f"📝 缺少必需配置: {', '.join(missing_configs)}")
            logger.info("🎛️  请访问管理后台完成SOAR服务配置:")
            logger.info(f"   👉 http://127.0.0.1:{int(os.getenv('ADMIN_PORT', str(int(os.getenv('SSE_PORT', '12345')) + 1)))}/admin")
            logger.info("✅ 配置完成后，系统将自动启用数据同步功能")
            logger.info("=" * 60)
            return

        logger.sync_start("执行启动同步...")

        # 同步剧本
        logger.sync_start("同步剧本数据...")
        playbook_sync_service = PlaybookSyncService(db_manager)
        playbook_result = await playbook_sync_service.full_sync()

        if "error" in playbook_result:
            logger.sync_warning(f"剧本同步失败: {playbook_result['error']}")
        else:
            logger.sync_success("剧本同步完成!")
            logger.info(f"剧本同步统计: {playbook_result.get('sync_result', {})}")

        # 暂停应用同步（仅保留剧本同步）
        # TODO: 将来可能需要重新启用应用同步
        logger.sync_warning("应用同步已暂停，当前版本仅同步剧本数据")

        # 原应用同步逻辑（已暂停）
        # skip_apps_sync = os.getenv("SKIP_APPS_SYNC", "false").lower() == "true"
        # if not skip_apps_sync:
        #     # 同步应用
        #     logger.sync_start("同步应用数据...")
        #     apps_sync_service = AppsSyncService(db_manager)
        #     apps_result = await apps_sync_service.full_sync()
        #
        #     if "error" in apps_result:
        #         logger.sync_warning(f"应用同步失败: {apps_result['error']}")
        #     else:
        #         logger.sync_success("应用同步完成!")
        #         logger.info(f"应用同步统计: {apps_result.get('sync_result', {})}")
        # else:
        #     logger.sync_warning("跳过应用同步 (SKIP_APPS_SYNC=true)")

        logger.sync_success("剧本数据同步完成!")

    except Exception as e:
        logger.sync_error(f"启动同步异常: {e}")


class PeriodicSyncService:
    """定时同步服务"""

    def __init__(self):
        self.sync_thread = None
        self.stop_event = None
        self.config_manager = None

    def start_periodic_sync(self):
        """启动定时同步服务"""
        try:
            from config_manager import config_manager
            self.config_manager = config_manager

            # 创建停止事件
            self.stop_event = threading.Event()

            # 启动同步线程
            self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.sync_thread.start()

            logger.info("定时同步服务已启动")

        except Exception as e:
            logger.error(f"启动定时同步服务失败: {e}")

    def _sync_worker(self):
        """同步工作线程"""
        # 设置为当前时间，避免启动时立即执行同步（因为启动同步刚执行过）
        last_sync_time = time.time()
        current_interval = None
        is_first_run = True  # 标记是否首次运行

        while not self.stop_event.is_set():
            try:
                # 获取当前同步间隔配置
                sync_interval = self.config_manager.get('sync_interval', 14400)  # 默认4小时

                # 检查配置是否发生变化
                if current_interval != sync_interval:
                    current_interval = sync_interval
                    logger.info(f"同步周期已更新为 {sync_interval} 秒 ({sync_interval//3600}小时)")
                    # 如果配置变化且不是首次启动，立即执行一次同步
                    if not is_first_run:  # 不是首次启动
                        logger.sync_start("配置变化，立即执行同步...")
                        asyncio.run(self._perform_sync())
                        last_sync_time = time.time()
                        logger.info(f"下次同步将在 {sync_interval} 秒后执行")
                        continue  # 跳过后面的时间检查，避免重复同步

                # 标记首次运行结束
                if is_first_run:
                    is_first_run = False

                # 检查是否需要执行同步
                current_time = time.time()
                if current_time - last_sync_time >= sync_interval:
                    # 执行同步
                    logger.sync_start("执行定时同步...")
                    asyncio.run(self._perform_sync())
                    last_sync_time = current_time
                    logger.info(f"下次同步将在 {sync_interval} 秒后执行")

                # 每分钟检查一次配置和同步时间，避免长时间阻塞
                self.stop_event.wait(timeout=60)

            except Exception as e:
                logger.sync_error(f"定时同步异常: {e}")
                # 发生异常时等待较短时间后重试
                self.stop_event.wait(timeout=60)

    async def _perform_sync(self):
        """执行同步操作"""
        try:
            # 检查配置是否完整
            if self.config_manager.is_first_run():
                missing_configs = self.config_manager.get_missing_required_configs()
                logger.sync_warning(f"定时同步暂停：缺少必需配置 {', '.join(missing_configs)}")
                logger.info("请访问管理后台完成SOAR服务配置后，同步将自动恢复")
                return

            # 同步剧本
            logger.sync_start("定时同步剧本数据...")
            playbook_sync_service = PlaybookSyncService(db_manager)
            playbook_result = await playbook_sync_service.full_sync()

            if "error" in playbook_result:
                logger.sync_warning(f"剧本同步失败: {playbook_result['error']}")
            else:
                logger.sync_success("剧本定时同步完成!")
                logger.info(f"剧本同步统计: {playbook_result.get('sync_result', {})}")

            # 暂停应用同步（仅保留剧本同步）
            # TODO: 将来可能需要重新启用应用同步
            logger.sync_warning("应用同步已暂停，当前版本仅同步剧本数据")

            # 原应用同步逻辑（已暂停）
            # logger.sync_start("定时同步应用数据...")
            # apps_sync_service = AppsSyncService(db_manager)
            # apps_result = await apps_sync_service.full_sync()
            #
            # if "error" in apps_result:
            #     logger.sync_warning(f"应用同步失败: {apps_result['error']}")
            # else:
            #     logger.sync_success("应用定时同步完成!")
            #     logger.info(f"应用同步统计: {apps_result.get('sync_result', {})}")

            logger.sync_success("剧本定时同步完成!")

        except Exception as e:
            logger.sync_error(f"定时同步异常: {e}")

    def stop(self):
        """停止定时同步服务"""
        if self.stop_event:
            self.stop_event.set()
        if self.sync_thread and self.sync_thread.is_alive():
            self.sync_thread.join(timeout=5)
        logger.info("定时同步服务已停止")


# 全局定时同步服务实例
periodic_sync_service = PeriodicSyncService()


if __name__ == "__main__":
    port = int(os.getenv("SSE_PORT", "12345"))
    admin_port = int(os.getenv("ADMIN_PORT", str(port + 1)))  # 管理端口默认为MCP端口+1
    
    # 启动信息
    logger.server_info(f"启动 SOAR MCP 服务器")
    logger.info("📊 MCP协议:")
    logger.info(f"  🔗 URL: http://127.0.0.1:{port}/ (带token: http://127.0.0.1:{port}/?token=your_token)")
    logger.info("🛠️  剧本管理: list_playbooks_quick, query_playbook_execution_params")
    logger.info("🚀 剧本执行: execute_playbook (真实API调用), query_playbook_execution_status_by_activity_id, query_playbook_execution_result_by_activity_id")
    logger.info("📋 资源: soar://applications, soar://playbooks, soar://executions")
    logger.info("")
    logger.info("🎛️  管理后台:")
    logger.info(f"  🔗 URL: http://127.0.0.1:{admin_port}/admin")
    logger.info("  🛡️  功能: 剧本启用/禁用管理、状态监控")
    
    # 初始化数据库
    logger.database_info("初始化数据库...")
    db_manager.init_db()
    
    # 初始化配置管理器
    logger.info("初始化系统配置...")
    from config_manager import config_manager
    config_manager.init()

    # 初始化认证系统
    logger.info("初始化认证系统...")
    from auth_utils import create_auth_manager
    auth_manager = create_auth_manager()
    admin_password = auth_manager.init_admin_password()

    # 将认证管理器设置到Flask应用中
    admin_app.auth_manager = auth_manager

    # 执行启动同步
    logger.info("启动同步任务...")
    asyncio.run(startup_sync())

    # 启动定时同步服务
    logger.info("启动定时同步服务...")
    periodic_sync_service.start_periodic_sync()

    # 启动管理后台服务器（在后台线程中运行）
    logger.info(f"启动管理后台服务器 (端口 {admin_port})...")
    admin_thread = Thread(target=start_admin_server, args=(admin_port,), daemon=True)
    admin_thread.start()
    
    # 启动服务器前的最后日志
    logger.server_info("启动MCP服务器...")

    # 启动 StreamableHttp 服务器
    # 注意：FastMCP logo会在这里显示
    try:
        import time
        # 在一个单独的线程中延迟打印启动信息和admin password
        def print_startup_info():
            time.sleep(2)  # 等待FastMCP logo显示完毕
            logger.info("")
            logger.info("=" * 80)
            logger.info("🚀 服务器启动完成!")
            logger.info(f"📊 MCP服务: http://127.0.0.1:{port}/mcp (带token参数)")
            logger.info("✅ Cherry Studio等客户端可以使用: http://127.0.0.1:12345/mcp?token=xxx")
            logger.info(f"🎛️  管理后台: http://127.0.0.1:{admin_port}/admin")
            logger.info("📝 同步日志请查看 logs/ 目录下的日志文件")
            logger.info("=" * 80)
            logger.info("")
            if admin_password:
                logger.info("🔑 管理员密码: " + admin_password)
            else:
                logger.info("🔑 管理员密码已存在，请查看之前的启动日志")
            logger.info("")

        import threading
        startup_thread = threading.Thread(target=print_startup_info, daemon=True)
        startup_thread.start()

        # 暂时回到原始方法，但保持认证系统的改进
        logger.info("🔐 使用增强的认证系统 (SOARAuthProvider集成)")
        mcp.run(
            transport="streamable-http",  # 使用 StreamableHTTP 协议以兼容现有客户端
            host="0.0.0.0",
            port=port,
            stateless_http=True,  # 禁用session管理，避免Cherry Studio等客户端的mcp-session-id头验证问题
            path="/mcp",  # 保持/mcp路径以兼容现有客户端
            # 认证现在通过工具函数内部处理，保持向后兼容
        )
    except KeyboardInterrupt:
        logger.info("服务器已停止")