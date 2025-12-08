#!/usr/bin/env python3
"""
UniMCPSim 管理后台服务器
"""

import os
import json
from datetime import datetime, timedelta, timezone
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_cors import CORS
from dotenv import load_dotenv
from models import db_manager, User, Token, Application, AppPermission, AuditLog, PromptTemplate
from auth_utils import hash_password, verify_password, login_required, admin_required
from version import get_version
from playground_service import playground_service

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(32)
app.permanent_session_lifetime = timedelta(hours=24)
CORS(app)

# 启动时间（使用本地时区）
START_TIME = datetime.now()

# ===== 页面路由 =====

@app.route('/admin/login')
def login_page():
    """登录页面"""
    return render_template('login.html', version=get_version())

@app.route('/admin/')
@login_required
def dashboard():
    """仪表板"""
    session_db = db_manager.get_session()
    try:
        app_count = session_db.query(Application).filter_by(enabled=True).count()
        token_count = session_db.query(Token).filter_by(enabled=True).count()

        # 今日调用量
        today = datetime.now(timezone.utc).date()
        log_count = session_db.query(AuditLog).filter(
            AuditLog.timestamp >= datetime.combine(today, datetime.min.time())
        ).count()

        # 获取端口配置
        mcp_port = os.getenv('MCP_SERVER_PORT', '9090')

        return render_template('dashboard.html',
                             username=session.get('username'),
                             app_count=app_count,
                             token_count=token_count,
                             log_count=log_count,
                             start_time=START_TIME.strftime('%Y-%m-%d %H:%M:%S'),
                             version=get_version(),
                             mcp_port=mcp_port,
                             active_page='dashboard')
    finally:
        session_db.close()

@app.route('/admin/apps')
@login_required
def apps_page():
    """应用管理页面"""
    mcp_port = os.getenv('MCP_SERVER_PORT', '9090')
    return render_template('apps.html', username=session.get('username'), active_page='apps', mcp_port=mcp_port)

@app.route('/admin/tokens')
@login_required
def tokens_page():
    """Token管理页面"""
    mcp_port = os.getenv('MCP_SERVER_PORT', '9090')
    return render_template('tokens.html', username=session.get('username'), active_page='tokens', mcp_port=mcp_port)

@app.route('/admin/logs')
@login_required
def logs_page():
    """日志页面"""
    return render_template('logs.html', username=session.get('username'), active_page='logs')

@app.route('/admin/prompts')
@login_required
def prompts_page():
    """提示词管理页面"""
    return render_template('prompts.html', username=session.get('username'), active_page='prompts')

@app.route('/admin/change-password')
@login_required
def change_password_page():
    """修改密码页面"""
    return render_template('change_password.html', username=session.get('username'), active_page='change_password')

@app.route('/admin/llm-config')
@login_required
def llm_config_page():
    """大模型配置页面"""
    return render_template('llm_config.html', username=session.get('username'), active_page='llm_config')

@app.route('/admin/playground')
@login_required
def playground_page():
    """Playground 页面"""
    mcp_port = os.getenv('MCP_SERVER_PORT', '9090')
    return render_template('playground.html',
                         username=session.get('username'),
                         active_page='playground',
                         mcp_port=mcp_port)

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
        apps = session_db.query(Application).order_by(Application.id.desc()).all()
        return jsonify([{
            'id': app.id,
            'name': app.name,
            'category': app.category,
            'display_name': app.display_name,
            'description': app.description,
            'ai_notes': app.ai_notes,
            'enabled': app.enabled,
            'created_at': app.created_at.isoformat()
        } for app in apps])
    finally:
        session_db.close()

def validate_app_name(name, field_name='名称'):
    """验证应用名称/类别是否符合URL路径规范"""
    import re
    if not name:
        return False, f'{field_name}不能为空'

    # 只允许字母、数字、下划线、连字符
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        return False, f'{field_name}只能包含字母、数字、下划线和连字符'

    # 长度限制
    if len(name) < 2 or len(name) > 50:
        return False, f'{field_name}长度必须在2-50个字符之间'

    return True, ''

@app.route('/admin/api/apps', methods=['POST'])
@admin_required
def create_app():
    """创建应用"""
    data = request.json
    session_db = db_manager.get_session()
    try:
        # 验证类别名称
        valid, error = validate_app_name(data.get('category', ''), '类别')
        if not valid:
            return jsonify({'error': error}), 400

        # 验证应用名称
        valid, error = validate_app_name(data.get('name', ''), '名称')
        if not valid:
            return jsonify({'error': error}), 400

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
            ai_notes=data.get('ai_notes', ''),
            template=data.get('template', {})
        )
        session_db.add(app)
        session_db.commit()
        return jsonify({
            'id': app.id,
            'message': '应用创建成功!请前往"令牌管理"页面为相关Token绑定此应用的访问权限。'
        })
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
            'ai_notes': app.ai_notes,
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
            # 验证类别名称（如果提供）
            if 'category' in data:
                valid, error = validate_app_name(data['category'], '类别')
                if not valid:
                    return jsonify({'error': error}), 400

            # 验证应用名称（如果提供）
            if 'name' in data:
                valid, error = validate_app_name(data['name'], '名称')
                if not valid:
                    return jsonify({'error': error}), 400

            # 完全更新应用
            app.category = data.get('category', app.category)
            app.name = data.get('name', app.name)
            app.display_name = data.get('display_name', app.display_name)
            app.description = data.get('description', app.description)
            app.ai_notes = data.get('ai_notes', app.ai_notes)
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
            if 'ai_notes' in data:
                app.ai_notes = data['ai_notes']
            if 'category' in data:
                valid, error = validate_app_name(data['category'], '类别')
                if not valid:
                    return jsonify({'error': error}), 400
                app.category = data['category']
            if 'name' in data:
                valid, error = validate_app_name(data['name'], '名称')
                if not valid:
                    return jsonify({'error': error}), 400
                app.name = data['name']
            if 'display_name' in data:
                app.display_name = data['display_name']

        app.updated_at = datetime.now(timezone.utc)
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

@app.route('/admin/api/apps/export', methods=['GET'])
@login_required
def export_apps():
    """导出应用配置"""
    session_db = db_manager.get_session()
    try:
        # 获取可选的ids参数（逗号分隔）
        ids_param = request.args.get('ids', '')

        if ids_param:
            # 导出指定应用
            app_ids = [int(id.strip()) for id in ids_param.split(',') if id.strip().isdigit()]
            apps = session_db.query(Application).filter(Application.id.in_(app_ids)).all()
        else:
            # 导出所有应用
            apps = session_db.query(Application).all()

        # 构建导出数据
        export_data = {
            'version': '1.0',
            'export_time': datetime.now(timezone.utc).isoformat(),
            'count': len(apps),
            'applications': []
        }

        for app in apps:
            export_data['applications'].append({
                'category': app.category,
                'name': app.name,
                'display_name': app.display_name,
                'description': app.description or '',
                'ai_notes': app.ai_notes or '',
                'template': app.template or {},
                'enabled': app.enabled
            })

        return jsonify(export_data)
    finally:
        session_db.close()

@app.route('/admin/api/apps/import', methods=['POST'])
@admin_required
def import_apps():
    """导入应用配置"""
    data = request.json
    session_db = db_manager.get_session()

    try:
        # 验证数据格式
        if not data or 'applications' not in data:
            return jsonify({'error': '无效的导入数据格式'}), 400

        applications = data.get('applications', [])
        if not isinstance(applications, list):
            return jsonify({'error': 'applications字段必须是数组'}), 400

        results = {
            'total': len(applications),
            'created': 0,
            'updated': 0,
            'failed': 0,
            'errors': []
        }

        for idx, app_data in enumerate(applications):
            try:
                # 验证必填字段
                required_fields = ['category', 'name', 'display_name']
                missing_fields = [f for f in required_fields if not app_data.get(f)]
                if missing_fields:
                    raise ValueError(f'缺少必填字段: {", ".join(missing_fields)}')

                # 验证字段格式
                valid, error = validate_app_name(app_data['category'], '类别')
                if not valid:
                    raise ValueError(error)

                valid, error = validate_app_name(app_data['name'], '名称')
                if not valid:
                    raise ValueError(error)

                # 检查是否已存在
                existing = session_db.query(Application).filter_by(
                    category=app_data['category'],
                    name=app_data['name']
                ).first()

                if existing:
                    # 覆盖现有应用
                    existing.display_name = app_data['display_name']
                    existing.description = app_data.get('description', '')
                    existing.ai_notes = app_data.get('ai_notes', '')
                    existing.template = app_data.get('template', {})
                    existing.enabled = app_data.get('enabled', True)
                    existing.updated_at = datetime.now(timezone.utc)
                    results['updated'] += 1
                else:
                    # 创建新应用
                    new_app = Application(
                        category=app_data['category'],
                        name=app_data['name'],
                        display_name=app_data['display_name'],
                        description=app_data.get('description', ''),
                        ai_notes=app_data.get('ai_notes', ''),
                        template=app_data.get('template', {}),
                        enabled=app_data.get('enabled', True)
                    )
                    session_db.add(new_app)
                    results['created'] += 1

            except Exception as e:
                results['failed'] += 1
                results['errors'].append({
                    'index': idx + 1,
                    'app': f"{app_data.get('category', '?')}/{app_data.get('name', '?')}",
                    'error': str(e)
                })

        # 提交所有成功的修改
        session_db.commit()

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        session_db.rollback()
        return jsonify({'error': f'导入失败: {str(e)}'}), 500
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

@app.route('/admin/api/tokens/<int:token_id>/apps', methods=['PUT'])
@login_required
def update_token_apps(token_id):
    """更新Token授权的应用"""
    session_db = db_manager.get_session()
    try:
        data = request.get_json()
        app_ids = data.get('app_ids', [])

        # 删除现有权限
        session_db.query(AppPermission).filter_by(token_id=token_id).delete()

        # 添加新权限
        for app_id in app_ids:
            permission = AppPermission(token_id=token_id, application_id=app_id)
            session_db.add(permission)

        session_db.commit()
        return jsonify({'success': True})
    except Exception as e:
        session_db.rollback()
        return jsonify({'error': str(e)}), 400
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
        # 获取MCP端口配置
        mcp_port = os.getenv('MCP_SERVER_PORT', '9090')
        mcp_url = f'http://127.0.0.1:{mcp_port}/health'

        # 检查本地MCP服务器状态
        print(f"Attempting to connect to MCP server at {mcp_url}")
        response = requests.get(mcp_url, timeout=3, proxies={"http": None, "https": None})
        print(f"MCP health check: status={response.status_code}, content_length={len(response.content)}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"MCP health data: {health_data}")
            return jsonify({
                'status': 'running',
                'message': '运行中',
                'data': health_data
            })
        else:
            print(f"MCP server returned status {response.status_code}")
            return jsonify({
                'status': 'error',
                'message': '已停止',
                'error': f'HTTP {response.status_code}'
            }), 503
    except requests.RequestException as e:
        print(f"MCP health check failed: {e}")
        return jsonify({
            'status': 'error',
            'message': '已停止',
            'error': str(e)
        }), 503
    except Exception as e:
        print(f"Unexpected error in MCP health check: {e}")
        return jsonify({
            'status': 'error',
            'message': '检查失败',
            'error': str(e)
        }), 500

@app.route('/admin/api/generate-actions', methods=['POST'])
@login_required
def generate_actions():
    """使用AI生成动作定义（强制使用提示词模板）"""
    try:
        data = request.json
        category = data.get('category', '')
        name = data.get('name', '')
        display_name = data.get('display_name', '')
        description = data.get('description', '')
        prompt = data.get('prompt', '')

        # 强制使用数据库中的提示词模板调用AI服务
        generated_actions = generate_actions_with_ai(category, name, display_name, description, prompt)

        return jsonify({
            'success': True,
            'actions': generated_actions
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

        # 使用变量替换生成最终的user prompt
        user_prompt = prompt_template.template.format(**variables)

        # 从环境变量读取OpenAI配置
        api_key = os.getenv('OPENAI_API_KEY')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
        # 读取enable_thinking配置,默认为False(禁用)
        enable_thinking = os.getenv('OPENAI_ENABLE_THINKING', 'false').lower() == 'true'
        # 读取stream配置,默认为False(某些模型如qwq-32b强制要求stream=True)
        use_stream = os.getenv('OPENAI_STREAM', 'false').lower() == 'true'

        if not api_key:
            raise Exception("OPENAI_API_KEY not configured")

        # 配置OpenAI客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base
        )

        # 调用OpenAI API
        if use_stream:
            # Stream模式
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的API动作定义生成器，返回符合规范的JSON格式数据。"},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                stream=True,
                # 禁用thinking模式,防止思考过程影响JSON输出格式
                extra_body={"enable_thinking": enable_thinking}
            )

            # 收集stream响应
            content = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
            content = content.strip()
        else:
            # 非Stream模式
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "你是一个专业的API动作定义生成器，返回符合规范的JSON格式数据。"},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=2000,
                # 禁用thinking模式,防止思考过程影响JSON输出格式
                extra_body={"enable_thinking": enable_thinking}
            )

            # 解析返回结果
            content = response.choices[0].message.content.strip()

        # 尝试解析JSON
        try:
            actions = json.loads(content)
            return actions
        except json.JSONDecodeError:
            # 如果解析失败，清理并重试
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            try:
                actions = json.loads(content.strip())
                return actions
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}")
                print(f"原始内容: {content}")
                raise Exception(f"AI返回的JSON格式不正确: {e}")

    except Exception as e:
        print(f"AI生成失败: {e}")
        # 抛出异常让系统使用fallback逻辑
        raise e


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

@app.route('/admin/api/change-password', methods=['POST'])
@login_required
def api_change_password():
    """修改管理员密码"""
    try:
        data = request.get_json()
        current_password = data.get('current_password', '')
        new_password = data.get('new_password', '')
        confirm_password = data.get('confirm_password', '')

        # 验证参数
        if not current_password or not new_password or not confirm_password:
            return jsonify({'error': '所有字段都是必填的'}), 400

        if new_password != confirm_password:
            return jsonify({'error': '新密码与确认密码不一致'}), 400

        if len(new_password) < 6:
            return jsonify({'error': '新密码长度不能少于6位'}), 400

        # 验证当前密码
        username = session.get('username')
        if not db_manager.verify_user_password(username, current_password):
            return jsonify({'error': '当前密码不正确'}), 400

        # 修改密码
        success = db_manager.change_user_password(username, new_password)
        if success:
            # 清除会话，强制重新登录
            session.clear()
            return jsonify({'message': '密码修改成功', 'redirect': '/admin/login'})
        else:
            return jsonify({'error': '密码修改失败'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== LLM配置管理API =====

@app.route('/admin/api/llm-config', methods=['GET'])
@login_required
def api_get_llm_config():
    """获取大模型配置"""
    try:
        config = db_manager.get_llm_config()
        if config:
            # API Key脱敏显示
            masked_key = None
            if config.api_key:
                if len(config.api_key) > 10:
                    masked_key = config.api_key[:6] + '***' + config.api_key[-4:]
                else:
                    masked_key = config.api_key[:3] + '***'

            return jsonify({
                'api_key': masked_key,
                'api_base_url': config.api_base_url,
                'model_name': config.model_name,
                'enable_thinking': config.enable_thinking,
                'enable_stream': config.enable_stream,
                'has_config': bool(config.api_key)
            })
        else:
            # 返回默认值
            return jsonify({
                'api_key': None,
                'api_base_url': 'https://api.openai.com/v1',
                'model_name': 'gpt-4o-mini',
                'enable_thinking': False,
                'enable_stream': False,
                'has_config': False
            })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/llm-config', methods=['POST'])
@login_required
def api_save_llm_config():
    """保存大模型配置"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        api_key = data.get('api_key')
        api_base_url = data.get('api_base_url', 'https://api.openai.com/v1')
        model_name = data.get('model_name', 'gpt-4o-mini')
        enable_thinking = data.get('enable_thinking', False)
        enable_stream = data.get('enable_stream', False)

        # 如果api_key为空字符串或者是脱敏的值（包含***），不更新
        if api_key and '***' in api_key:
            api_key = None

        # 保存配置
        config = db_manager.save_llm_config(
            api_key=api_key,
            api_base_url=api_base_url,
            model_name=model_name,
            enable_thinking=enable_thinking,
            enable_stream=enable_stream
        )

        # 重新加载AI生成器的配置
        from ai_generator import ai_generator
        ai_generator.reload_config()

        return jsonify({
            'success': True,
            'message': '配置保存成功'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/llm-config/test', methods=['POST'])
@login_required
def api_test_llm_config():
    """测试大模型配置"""
    try:
        data = request.get_json()

        # 获取测试配置（可以是临时配置或当前数据库配置）
        api_key = data.get('api_key')
        api_base_url = data.get('api_base_url', 'https://api.openai.com/v1')
        model_name = data.get('model_name', 'gpt-4o-mini')
        enable_thinking = data.get('enable_thinking', False)
        enable_stream = data.get('enable_stream', False)

        # 如果api_key包含***，从数据库读取真实的key
        if api_key and '***' in api_key:
            config = db_manager.get_llm_config()
            if config and config.api_key:
                api_key = config.api_key
            else:
                return jsonify({
                    'success': False,
                    'error': '未配置API Key'
                }), 400

        if not api_key:
            return jsonify({
                'success': False,
                'error': 'API Key不能为空'
            }), 400

        # 使用OpenAI客户端测试连接
        import openai
        import time

        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base_url
        )

        start_time = time.time()

        # 发送测试请求
        test_message = "你是谁？"

        if enable_stream:
            # Stream模式
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": test_message}
                ],
                max_tokens=50,
                stream=True,
                extra_body={"enable_thinking": enable_thinking}
            )

            # 收集stream响应
            result = ""
            for chunk in response:
                if chunk.choices[0].delta.content:
                    result += chunk.choices[0].delta.content
        else:
            # 非Stream模式
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "user", "content": test_message}
                ],
                max_tokens=50,
                extra_body={"enable_thinking": enable_thinking}
            )
            result = response.choices[0].message.content

        duration = time.time() - start_time

        return jsonify({
            'success': True,
            'message': '连接成功',
            'response': result,
            'duration': f'{duration:.2f}秒',
            'model': model_name
        })

    except Exception as e:
        error_msg = str(e)
        return jsonify({
            'success': False,
            'error': f'连接失败: {error_msg}'
        }), 400


# ===== Playground API =====

@app.route('/admin/api/playground/test', methods=['POST'])
@login_required
def api_playground_test():
    """测试 MCP Server 连接"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        config = data.get('config', {})
        if not config:
            return jsonify({'error': 'MCP 配置不能为空'}), 400

        # 使用会话 ID 区分不同用户
        session_id = session.get('user_id', 'default')

        result = playground_service.test_mcp_servers(str(session_id), config)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/playground/chat', methods=['POST'])
@login_required
def api_playground_chat():
    """发送对话消息"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Invalid JSON data'}), 400

        message = data.get('message', '').strip()
        if not message:
            return jsonify({'error': '消息不能为空'}), 400

        system_prompt = data.get('system_prompt')
        session_id = session.get('user_id', 'default')

        result = playground_service.chat(str(session_id), message, system_prompt)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/playground/clear', methods=['POST'])
@login_required
def api_playground_clear():
    """清除对话历史"""
    try:
        session_id = session.get('user_id', 'default')
        playground_service.clear_session(str(session_id))
        return jsonify({'success': True, 'message': '对话已清除'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/playground/history', methods=['GET'])
@login_required
def api_playground_history():
    """获取对话历史"""
    try:
        session_id = session.get('user_id', 'default')
        history = playground_service.get_conversation_history(str(session_id))
        tools = playground_service.get_tools(str(session_id))
        return jsonify({
            'history': history,
            'tools': tools
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/admin/api/playground/system-prompt', methods=['GET'])
@login_required
def api_playground_system_prompt():
    """获取默认系统提示词"""
    try:
        prompt = playground_service.get_default_system_prompt()
        return jsonify({'prompt': prompt})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


def run_admin_server():
    """运行管理后台服务器"""
    # 获取端口配置
    port = int(os.getenv('ADMIN_SERVER_PORT', '9091'))
    print(f"Starting UniMCPSim Admin Server on port {port}...")
    db_manager.create_default_admin()
    app.run(host='0.0.0.0', port=port, debug=False)

if __name__ == "__main__":
    run_admin_server()