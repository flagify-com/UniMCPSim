#!/usr/bin/env python3
"""
认证工具
"""

import hashlib
import jwt
import secrets
from datetime import datetime, timedelta, timezone
from typing import Optional
from functools import wraps
from flask import request, jsonify, session, redirect, url_for

SECRET_KEY = secrets.token_hex(32)  # 生产环境应从环境变量读取

def hash_password(password: str) -> str:
    """哈希密码"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return hash_password(password) == hashed

def create_jwt_token(user_id: int, username: str, is_admin: bool = False) -> str:
    """创建JWT Token"""
    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'username': username,
        'is_admin': is_admin,
        'exp': now + timedelta(hours=24),
        'iat': now
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def decode_jwt_token(token: str) -> Optional[dict]:
    """解码JWT Token"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def login_required(f):
    """登录装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            # 检查是否是API请求
            if request.path.startswith('/admin/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            # 对于页面请求，跳转到登录页面
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """管理员装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        if not session.get('is_admin', False):
            return jsonify({'error': 'Admin privileges required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_token() -> str:
    """生成随机Token"""
    return secrets.token_hex(32)