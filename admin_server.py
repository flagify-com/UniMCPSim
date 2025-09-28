#!/usr/bin/env python3
"""
UniMCPSim 管理后台服务器
"""

import os
import json
from datetime import datetime, timedelta
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from models import db_manager, User, Token, Application, AppPermission, AuditLog, PromptTemplate
from auth_utils import hash_password, verify_password, login_required, admin_required

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(hours=24)
CORS(app)

# 启动时间
START_TIME = datetime.utcnow()

# ===== 页面路由 =====

@app.route('/admin/login')
def login_page():
    """登录页面"""
    return render_template('login.html')

@app.route('/admin/')
@login_required
def dashboard():
    """仪表板"""
    session_db = db_manager.get_session()
    try:
        app_count = session_db.query(Application).filter_by(enabled=True).count()
        token_count = session_db.query(Token).filter_by(enabled=True).count()

        # 今日调用量
        today = datetime.utcnow().date()
        log_count = session_db.query(AuditLog).filter(
            AuditLog.timestamp >= datetime.combine(today, datetime.min.time())
        ).count()

        return render_template('dashboard.html',
                             username=session.get('username'),
                             app_count=app_count,
                             token_count=token_count,
                             log_count=log_count,
                             start_time=START_TIME.strftime('%Y-%m-%d %H:%M:%S'))
    finally:
        session_db.close()

@app.route('/admin/apps')
@login_required
def apps_page():
    """应用管理页面"""
    return render_template('apps.html', username=session.get('username'))

@app.route('/admin/tokens')
@login_required
def tokens_page():
    """Token管理页面"""
    return render_template('tokens.html', username=session.get('username'))

@app.route('/admin/logs')
@login_required
def logs_page():
    """日志页面"""
    return render_template('logs.html', username=session.get('username'))

@app.route('/admin/prompts')
@login_required
def prompts_page():
    """提示词管理页面"""
    return render_template('prompts.html', username=session.get('username'))

@app.route('/admin/logout')
def logout():
    """退出登录"""
    session.clear()
    return redirect('/admin/login')

# ===== API路由 =====

@app.route('/admin/api/login', methods=['POST'])
def api_login():
    """登录API"""
    data = request.json
    username = data.get('username')
    password = data.get('password')

    session_db = db_manager.get_session()
    try:
        user = session_db.query(User).filter_by(username=username).first()
        if user and verify_password(password, user.password_hash):
            session['user_id'] = user.id
            session['username'] = user.username
            session['is_admin'] = user.is_admin
            session.permanent = True
            return jsonify({'success': True})
        return jsonify({'success': False, 'message': '用户名或密码错误'}), 401
    finally:
        session_db.close()

@app.route('/admin/api/apps', methods=['GET'])
@login_required
def get_apps():
    """获取应用列表"""
    session_db = db_manager.get_session()
    try:
        apps = session_db.query(Application).all()
        return jsonify([{
            'id': app.id,
            'name': app.name,
            'category': app.category,
            'display_name': app.display_name,
            'description': app.description,
            'enabled': app.enabled,
            'created_at': app.created_at.isoformat()
        } for app in apps])
    finally:
        session_db.close()

@app.route('/admin/api/apps', methods=['POST'])
@admin_required
def create_app():
    """创建应用"""
    data = request.json
    session_db = db_manager.get_session()
    try:
        # 检查是否已存在
        existing = session_db.query(Application).filter_by(
            category=data['category'],
            name=data['name']
        ).first()
        if existing:
            return jsonify({'error': '应用已存在'}), 400

        app = Application(
            name=data['name'],
            category=data['category'],
            display_name=data['display_name'],
            description=data.get('description', ''),
            template=data.get('template', {})
        )
        session_db.add(app)
        session_db.commit()
        return jsonify({'id': app.id})
    finally:
        session_db.close()

@app.route('/admin/api/apps/<int:app_id>', methods=['GET'])
@login_required
def get_app_detail(app_id):
    """获取应用详情"""
    session_db = db_manager.get_session()
    try:
        app = session_db.query(Application).filter_by(id=app_id).first()
        if not app:
            return jsonify({"error": "Application not found"}), 404

        return jsonify({
            'id': app.id,
            'category': app.category,
            'name': app.name,
            'display_name': app.display_name,
            'description': app.description,
            'enabled': app.enabled,
            'template': app.template
        })
    finally:
        session_db.close()


@app.route('/admin/api/apps/<int:app_id>', methods=['PATCH', 'PUT'])
@admin_required
def update_app(app_id):
    """更新应用"""
    data = request.json
    session_db = db_manager.get_session()
    try:
        app = session_db.query(Application).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': '应用不存在'}), 404

        # PUT方法用于完全更新，PATCH用于部分更新
        if request.method == 'PUT':
            # 完全更新应用
            app.category = data.get('category', app.category)
            app.name = data.get('name', app.name)
            app.display_name = data.get('display_name', app.display_name)
            app.description = data.get('description', app.description)
            app.template = data.get('template', app.template)
            if 'enabled' in data:
                app.enabled = data['enabled']
        else:
            # 部分更新（PATCH）
            if 'enabled' in data:
                app.enabled = data['enabled']
            if 'template' in data:
                app.template = data['template']
            if 'description' in data:
                app.description = data['description']
            if 'category' in data:
                app.category = data['category']
            if 'name' in data:
                app.name = data['name']
            if 'display_name' in data:
                app.display_name = data['display_name']

        app.updated_at = datetime.utcnow()
        session_db.commit()
        return jsonify({'success': True})
    finally:
        session_db.close()

@app.route('/admin/api/apps/<int:app_id>', methods=['DELETE'])
@admin_required
def delete_app(app_id):
    """删除应用"""
    session_db = db_manager.get_session()
    try:
        app = session_db.query(Application).filter_by(id=app_id).first()
        if not app:
            return jsonify({'error': '应用不存在'}), 404

        session_db.delete(app)
        session_db.commit()
        return jsonify({'success': True})
    finally:
        session_db.close()

@app.route('/admin/api/tokens', methods=['GET'])
@login_required
def get_tokens():
    """获取Token列表"""
    session_db = db_manager.get_session()
    try:
        tokens = session_db.query(Token).all()
        result = []
        for token in tokens:
            app_count = session_db.query(AppPermission).filter_by(token_id=token.id).count()
            result.append({
                'id': token.id,
                'name': token.name,
                'token': token.token,
                'enabled': token.enabled,
                'created_at': token.created_at.isoformat(),
                'last_used': token.last_used.isoformat() if token.last_used else None,
                'app_count': app_count
            })
        return jsonify(result)
    finally:
        session_db.close()

@app.route('/admin/api/tokens', methods=['POST'])
@admin_required
def create_token():
    """创建Token"""
    data = request.json
    session_db = db_manager.get_session()
    try:
        # 创建Token
        token = Token(
            name=data['name'],
            user_id=session['user_id']
        )
        session_db.add(token)
        session_db.flush()

        # 添加应用权限
        for app_id in data.get('app_ids', []):
            perm = AppPermission(token_id=token.id, application_id=app_id)
            session_db.add(perm)

        session_db.commit()
        return jsonify({'token': token.token, 'id': token.id})
    finally:
        session_db.close()

@app.route('/admin/api/tokens/<int:token_id>', methods=['PATCH'])
@admin_required
def update_token(token_id):
    """更新Token"""
    data = request.json
    session_db = db_manager.get_session()
    try:
        token = session_db.query(Token).filter_by(id=token_id).first()
        if not token:
            return jsonify({'error': 'Token不存在'}), 404

        if 'enabled' in data:
            token.enabled = data['enabled']

        session_db.commit()
        return jsonify({'success': True})
    finally:
        session_db.close()

@app.route('/admin/api/tokens/<int:token_id>', methods=['DELETE'])
@admin_required
def delete_token(token_id):
    """删除Token"""
    session_db = db_manager.get_session()
    try:
        token = session_db.query(Token).filter_by(id=token_id).first()
        if not token:
            return jsonify({'error': 'Token不存在'}), 404

        session_db.delete(token)
        session_db.commit()
        return jsonify({'success': True})
    finally:
        session_db.close()

@app.route('/admin/api/tokens/<int:token_id>/apps', methods=['GET'])
@login_required
def get_token_apps(token_id):
    """获取Token授权的应用"""
    session_db = db_manager.get_session()
    try:
        apps = session_db.query(Application).join(AppPermission).filter(
            AppPermission.token_id == token_id
        ).all()
        return jsonify([{
            'id': app.id,
            'display_name': app.display_name,
            'category': app.category,
            'name': app.name
        } for app in apps])
    finally:
        session_db.close()

@app.route('/admin/api/logs', methods=['GET'])
@login_required
def get_logs():
    """获取操作日志"""
    session_db = db_manager.get_session()
    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))

        logs = session_db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(per_page).offset((page - 1) * per_page).all()

        result = []
        for log in logs:
            app = session_db.query(Application).filter_by(id=log.application_id).first() if log.application_id else None
            result.append({
                'id': log.id,
                'app_name': app.display_name if app else 'N/A',
                'action': log.action,
                'parameters': log.parameters,
                'response': log.response,
                'ip_address': log.ip_address,
                'timestamp': log.timestamp.isoformat()
            })

        return jsonify(result)
    finally:
        session_db.close()

# MCP服务器状态检查API
@app.route('/admin/api/mcp-status', methods=['GET'])
@login_required
def check_mcp_status():
    """检查MCP服务器状态 - 后端调用避免CORS"""
    import requests

    try:
        # 检查本地MCP服务器状态
        response = requests.get('http://localhost:8080/health', timeout=3)
        if response.status_code == 200:
            return jsonify({
                'status': 'running',
                'message': '运行中',
                'data': response.json()
            })
        else:
            return jsonify({
                'status': 'error',
                'message': '已停止',
                'error': f'HTTP {response.status_code}'
            })
    except requests.RequestException as e:
        return jsonify({
            'status': 'error',
            'message': '已停止',
            'error': str(e)
        })

@app.route('/admin/api/generate-actions', methods=['POST'])
@login_required
def generate_actions():
    """使用AI生成动作定义"""
    try:
        data = request.json
        category = data.get('category', '')
        name = data.get('name', '')
        display_name = data.get('display_name', '')
        description = data.get('description', '')
        prompt = data.get('prompt', '')

        # 构建系统提示词
        # 调用本地AI服务生成动作定义
        try:
            # 这里使用一个简化的生成逻辑，您可以后续集成实际的AI服务
            generated_actions = generate_actions_with_ai(category, name, display_name, description, prompt)

            return jsonify({
                'success': True,
                'actions': generated_actions
            })

        except Exception as ai_error:
            # 如果AI服务不可用，返回基于模板的生成结果
            fallback_actions = generate_fallback_actions(category, name, prompt)
            return jsonify({
                'success': True,
                'actions': fallback_actions,
                'note': '使用模板生成，建议根据实际需求调整'
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_actions_with_ai(category, name, display_name, description, prompt):
    """调用AI服务生成动作定义"""
    try:
        import openai
        import os
        import json

        # 从数据库获取提示词模板
        prompt_template = db_manager.get_prompt_template('action_generation')
        if not prompt_template:
            raise Exception("未找到动作生成提示词模板")

        # 准备变量替换
        variables = {
            'prompt': prompt,
            'category': category,
            'name': name,
            'display_name': display_name,
            'description': description
        }

        # 使用变量替换生成最终的system prompt
        system_prompt = prompt_template.template.format(**variables)

        # 从环境变量读取OpenAI配置
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')

        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")

        # 配置OpenAI客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base
        )

        # 调用OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        # 解析返回结果
        content = response.choices[0].message.content.strip()

        # 尝试解析JSON
        try:
            # 移除可能的markdown代码块标记
            if content.startswith('```json'):
                content = content[7:]
            if content.startswith('```'):
                content = content[3:]
            if content.endswith('```'):
                content = content[:-3]

            actions = json.loads(content.strip())
            return actions
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始内容: {content}")
            # 如果JSON解析失败，抛出异常让系统使用fallback
            raise Exception(f"AI返回的JSON格式不正确: {e}")

    except Exception as e:
        print(f"AI生成失败: {e}")
        # 抛出异常让系统使用fallback逻辑
        raise e

def generate_fallback_actions(category, name, prompt):
    """生成基于模板的动作定义"""
    import re

    # 解析用户输入的工具描述
    lines = prompt.strip().split('\n')
    actions = []

    for i, line in enumerate(lines):
        if not line.strip():
            continue

        # 尝试解析"工具X: 描述"格式
        match = re.match(r'工具\d+[：:]\s*(.*)', line.strip())
        if match:
            action_desc = match.group(1).strip()
        else:
            action_desc = line.strip()

        # 智能解析生成更合理的动作名称和参数
        action = parse_action_intelligently(action_desc, i+1)
        if action:
            actions.append(action)

    # 如果没有解析到任何动作，提供默认模板
    if not actions:
        actions = [{
            "name": "default_action",
            "display_name": "默认动作",
            "description": "根据应用需求自定义的动作",
            "parameters": [
                {
                    "key": "input",
                    "type": "String",
                    "required": True,
                    "description": "输入参数"
                }
            ]
        }]

    return actions

def parse_action_intelligently(action_desc, index):
    """智能解析动作描述生成合理的参数"""
    action_desc_lower = action_desc.lower()

    # 防火墙相关功能
    if '防火墙' in action_desc and '健康' in action_desc and '状态' in action_desc:
        return {
            "name": "check_firewall_health",
            "display_name": "查询防火墙健康状态",
            "description": action_desc,
            "parameters": [
                {
                    "key": "check_type",
                    "type": "String",
                    "required": False,
                    "description": "检查类型(basic/detailed)"
                }
            ]
        }
    elif ('封禁' in action_desc or '屏蔽' in action_desc) and 'ip' in action_desc_lower:
        return {
            "name": "block_ip_address",
            "display_name": "封禁IP地址",
            "description": action_desc,
            "parameters": [
                {
                    "key": "ip_address",
                    "type": "String",
                    "required": True,
                    "description": "要封禁的IP地址"
                },
                {
                    "key": "duration",
                    "type": "Integer",
                    "required": False,
                    "description": "封禁时长(分钟，0表示永久)"
                },
                {
                    "key": "reason",
                    "type": "String",
                    "required": False,
                    "description": "封禁原因"
                }
            ]
        }
    elif ('解封' in action_desc or '解除' in action_desc) and 'ip' in action_desc_lower:
        return {
            "name": "unblock_ip_address",
            "display_name": "解封IP地址",
            "description": action_desc,
            "parameters": [
                {
                    "key": "ip_address",
                    "type": "String",
                    "required": True,
                    "description": "要解封的IP地址"
                }
            ]
        }
    elif '查询' in action_desc and 'ip' in action_desc_lower and ('封禁' in action_desc or '状态' in action_desc):
        return {
            "name": "query_ip_status",
            "display_name": "查询IP封禁状态",
            "description": action_desc,
            "parameters": [
                {
                    "key": "ip_address",
                    "type": "String",
                    "required": True,
                    "description": "要查询的IP地址"
                }
            ]
        }

    # 消息发送相关
    elif '发送' in action_desc and '消息' in action_desc:
        if '群' in action_desc:
            return {
                "name": "send_group_message",
                "display_name": "发送群消息",
                "description": action_desc,
                "parameters": [
                    {
                        "key": "group_id",
                        "type": "String",
                        "required": True,
                        "description": "群聊ID或群名称"
                    },
                    {
                        "key": "message_content",
                        "type": "String",
                        "required": True,
                        "description": "消息内容"
                    },
                    {
                        "key": "at_users",
                        "type": "Array",
                        "required": False,
                        "description": "@用户列表"
                    }
                ]
            }
        else:
            return {
                "name": "send_private_message",
                "display_name": "发送私人消息",
                "description": action_desc,
                "parameters": [
                    {
                        "key": "recipient",
                        "type": "String",
                        "required": True,
                        "description": "接收者用户名或ID"
                    },
                    {
                        "key": "message_content",
                        "type": "String",
                        "required": True,
                        "description": "消息内容"
                    }
                ]
            }
    elif '发送' in action_desc and '图片' in action_desc:
        return {
            "name": "send_image_message",
            "display_name": "发送图片消息",
            "description": action_desc,
            "parameters": [
                {
                    "key": "recipient",
                    "type": "String",
                    "required": True,
                    "description": "接收者用户名或群ID"
                },
                {
                    "key": "image_path",
                    "type": "String",
                    "required": True,
                    "description": "图片文件路径或URL"
                },
                {
                    "key": "caption",
                    "type": "String",
                    "required": False,
                    "description": "图片说明文字"
                }
            ]
        }

    # 查询相关
    elif '查询' in action_desc and ('列表' in action_desc or '清单' in action_desc):
        return {
            "name": "query_data_list",
            "display_name": "查询数据列表",
            "description": action_desc,
            "parameters": [
                {
                    "key": "list_type",
                    "type": "String",
                    "required": True,
                    "description": "列表类型"
                },
                {
                    "key": "filter_criteria",
                    "type": "Object",
                    "required": False,
                    "description": "过滤条件"
                },
                {
                    "key": "page_size",
                    "type": "Integer",
                    "required": False,
                    "description": "每页显示数量"
                }
            ]
        }
    elif '查询' in action_desc:
        return {
            "name": "query_information",
            "display_name": "查询信息",
            "description": action_desc,
            "parameters": [
                {
                    "key": "query_keyword",
                    "type": "String",
                    "required": True,
                    "description": "查询关键词"
                },
                {
                    "key": "search_scope",
                    "type": "String",
                    "required": False,
                    "description": "搜索范围"
                }
            ]
        }

    # 创建相关
    elif '创建' in action_desc or '新建' in action_desc:
        return {
            "name": "create_new_item",
            "display_name": "创建新项目",
            "description": action_desc,
            "parameters": [
                {
                    "key": "item_name",
                    "type": "String",
                    "required": True,
                    "description": "项目名称"
                },
                {
                    "key": "item_description",
                    "type": "String",
                    "required": False,
                    "description": "项目描述"
                },
                {
                    "key": "item_config",
                    "type": "Object",
                    "required": False,
                    "description": "项目配置参数"
                }
            ]
        }

    # 删除相关
    elif '删除' in action_desc or '移除' in action_desc:
        return {
            "name": "delete_item",
            "display_name": "删除项目",
            "description": action_desc,
            "parameters": [
                {
                    "key": "item_id",
                    "type": "String",
                    "required": True,
                    "description": "要删除的项目ID"
                },
                {
                    "key": "confirm_delete",
                    "type": "Boolean",
                    "required": False,
                    "description": "确认删除"
                }
            ]
        }

    # 更新/修改相关
    elif '更新' in action_desc or '修改' in action_desc or '编辑' in action_desc:
        return {
            "name": "update_item",
            "display_name": "更新项目",
            "description": action_desc,
            "parameters": [
                {
                    "key": "item_id",
                    "type": "String",
                    "required": True,
                    "description": "要更新的项目ID"
                },
                {
                    "key": "update_data",
                    "type": "Object",
                    "required": True,
                    "description": "更新的数据内容"
                }
            ]
        }

    # 通用动作（当无法智能识别时）
    else:
        # 从描述中提取关键动词作为动作名
        verbs = ['执行', '运行', '处理', '操作', '管理', '控制', '监控', '分析']
        action_verb = next((verb for verb in verbs if verb in action_desc), '执行')

        # 生成简洁的显示名称
        display_name = action_desc[:15] + "..." if len(action_desc) > 15 else action_desc

        return {
            "name": f"custom_action_{index}",
            "display_name": display_name,
            "description": action_desc,
            "parameters": [
                {
                    "key": "action_input",
                    "type": "String",
                    "required": True,
                    "description": "操作输入参数"
                },
                {
                    "key": "action_options",
                    "type": "Object",
                    "required": False,
                    "description": "操作选项配置"
                }
            ]
        }

# 默认路由重定向
@app.route('/')
def index():
    return redirect('/admin/')

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
            "service": "UniMCPSim-Admin",
            "timestamp": datetime.now().isoformat()
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


# ===== 提示词管理API =====

@app.route('/admin/api/prompts', methods=['GET'])
@login_required
def api_get_prompts():
    """获取所有提示词模板"""
    try:
        prompts = db_manager.get_all_prompt_templates()
        result = []
        for prompt in prompts:
            result.append({
                'id': prompt.id,
                'name': prompt.name,
                'display_name': prompt.display_name,
                'description': prompt.description,
                'template': prompt.template,
                'variables': prompt.variables or [],
                'enabled': prompt.enabled,
                'created_at': prompt.created_at.isoformat(),
                'updated_at': prompt.updated_at.isoformat()
            })
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/prompts/<name>', methods=['GET'])
@login_required
def api_get_prompt(name):
    """获取单个提示词模板"""
    try:
        prompt = db_manager.get_prompt_template(name)
        if not prompt:
            return jsonify({'error': 'Prompt template not found'}), 404

        return jsonify({
            'id': prompt.id,
            'name': prompt.name,
            'display_name': prompt.display_name,
            'description': prompt.description,
            'template': prompt.template,
            'variables': prompt.variables or [],
            'enabled': prompt.enabled,
            'created_at': prompt.created_at.isoformat(),
            'updated_at': prompt.updated_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/prompts', methods=['POST'])
@login_required
def api_save_prompt():
    """保存提示词模板"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        required_fields = ['name', 'display_name', 'template']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400

        prompt = db_manager.save_prompt_template(
            name=data['name'],
            display_name=data['display_name'],
            description=data.get('description', ''),
            template=data['template'],
            variables=data.get('variables', [])
        )

        return jsonify({
            'id': prompt.id,
            'name': prompt.name,
            'display_name': prompt.display_name,
            'description': prompt.description,
            'template': prompt.template,
            'variables': prompt.variables or [],
            'enabled': prompt.enabled,
            'created_at': prompt.created_at.isoformat(),
            'updated_at': prompt.updated_at.isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/api/prompts/<name>', methods=['DELETE'])
@login_required
def api_delete_prompt(name):
    """删除提示词模板"""
    try:
        success = db_manager.delete_prompt_template(name)
        if success:
            return jsonify({'message': 'Prompt template deleted successfully'})
        else:
            return jsonify({'error': 'Prompt template not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_admin_server():
    """运行管理后台服务器"""
    print("Starting UniMCPSim Admin Server on port 8081...")
    db_manager.create_default_admin()
    app.run(host='0.0.0.0', port=8081, debug=False)

if __name__ == "__main__":
    run_admin_server()