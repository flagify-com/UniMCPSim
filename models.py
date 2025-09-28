#!/usr/bin/env python3
"""
数据库模型定义
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean, Integer, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel, Field

Base = declarative_base()

class User(Base):
    """用户模型"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    tokens = relationship("Token", back_populates="user", cascade="all, delete-orphan")


class Token(Base):
    """Token模型"""
    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True)
    token = Column(String(64), unique=True, nullable=False, default=lambda: str(uuid.uuid4()))
    name = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_used = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="tokens")
    app_permissions = relationship("AppPermission", back_populates="token", cascade="all, delete-orphan")


class Application(Base):
    """应用模型"""
    __tablename__ = 'applications'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)  # e.g., "WeChat"
    category = Column(String(50), nullable=False)  # e.g., "IM"
    display_name = Column(String(100), nullable=False)
    description = Column(Text)
    template = Column(JSON)  # 存储应用的动作和参数定义
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    permissions = relationship("AppPermission", back_populates="application", cascade="all, delete-orphan")
    logs = relationship("AuditLog", back_populates="application")


class AppPermission(Base):
    """应用权限关联表"""
    __tablename__ = 'app_permissions'

    id = Column(Integer, primary_key=True)
    token_id = Column(Integer, ForeignKey('tokens.id'), nullable=False)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=False)

    token = relationship("Token", back_populates="app_permissions")
    application = relationship("Application", back_populates="permissions")


class AuditLog(Base):
    """审计日志"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True)
    token_id = Column(Integer, ForeignKey('tokens.id'), nullable=True)
    application_id = Column(Integer, ForeignKey('applications.id'), nullable=True)
    action = Column(String(100), nullable=False)
    parameters = Column(JSON)
    response = Column(JSON)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

    application = relationship("Application", back_populates="logs")


class PromptTemplate(Base):
    """提示词模板"""
    __tablename__ = 'prompt_templates'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)  # action_generation, response_simulation
    display_name = Column(String(200), nullable=False)
    description = Column(Text)
    template = Column(Text, nullable=False)  # 提示词模板内容
    variables = Column(JSON)  # 可用变量定义 [{"name": "prompt", "description": "用户输入的需求描述"}]
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Pydantic模型
class ActionParameter(BaseModel):
    """动作参数定义"""
    key: str
    type: str  # String, Integer, Boolean, Array, Object
    required: bool = False
    default: Optional[Any] = None
    description: Optional[str] = None
    options: Optional[List[Any]] = None  # 可选值列表


class Action(BaseModel):
    """动作定义"""
    name: str
    display_name: str
    description: Optional[str] = None
    parameters: List[ActionParameter] = []


class ApplicationTemplate(BaseModel):
    """应用模板"""
    name: str
    category: str
    display_name: str
    description: Optional[str] = None
    actions: List[Action] = []


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_url: str = 'sqlite:///data/unimcp.db'):
        self.engine = create_engine(db_url, echo=False)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    def create_default_admin(self):
        """创建默认管理员账户和提示词模板"""
        from auth_utils import hash_password

        session = self.get_session()
        try:
            admin = session.query(User).filter_by(username='admin').first()
            if not admin:
                admin = User(
                    username='admin',
                    password_hash=hash_password('admin123'),
                    is_admin=True
                )
                session.add(admin)
                session.commit()
                print("Created default admin user (username: admin, password: admin123)")
        finally:
            session.close()

        # 创建默认提示词模板
        self.create_default_prompts()

    def validate_token(self, token_str: str) -> Optional[dict]:
        """验证Token，返回Token信息字典"""
        session = self.get_session()
        try:
            token = session.query(Token).filter_by(token=token_str, enabled=True).first()
            if token:
                token.last_used = datetime.utcnow()
                session.commit()
                # 返回Token的基本信息而不是对象，避免session问题
                return {
                    'id': token.id,
                    'token': token.token,
                    'name': token.name,
                    'user_id': token.user_id
                }
            return None
        finally:
            session.close()

    def get_token_applications(self, token_str: str) -> List[Application]:
        """获取Token可访问的应用列表"""
        session = self.get_session()
        try:
            token = session.query(Token).filter_by(token=token_str, enabled=True).first()
            if not token:
                return []

            # 获取Token关联的应用
            apps = session.query(Application).join(AppPermission).filter(
                AppPermission.token_id == token.id,
                Application.enabled == True
            ).all()

            return apps
        finally:
            session.close()

    def get_application_by_path(self, category: str, name: str) -> Optional[Application]:
        """根据路径获取应用"""
        session = self.get_session()
        try:
            app = session.query(Application).filter_by(
                category=category,
                name=name,
                enabled=True
            ).first()
            return app
        finally:
            session.close()

    def log_action(self, token_id: Optional[int], app_id: Optional[int],
                   action: str, params: Dict, response: Dict, ip: Optional[str] = None):
        """记录操作日志"""
        session = self.get_session()
        try:
            log = AuditLog(
                token_id=token_id,
                application_id=app_id,
                action=action,
                parameters=params,
                response=response,
                ip_address=ip
            )
            session.add(log)
            session.commit()
        finally:
            session.close()

    def get_prompt_template(self, name: str) -> Optional[PromptTemplate]:
        """根据名称获取提示词模板"""
        session = self.get_session()
        try:
            template = session.query(PromptTemplate).filter_by(name=name, enabled=True).first()
            return template
        finally:
            session.close()

    def get_all_prompt_templates(self) -> List[PromptTemplate]:
        """获取所有提示词模板"""
        session = self.get_session()
        try:
            templates = session.query(PromptTemplate).all()
            return templates
        finally:
            session.close()

    def save_prompt_template(self, name: str, display_name: str, description: str,
                           template: str, variables: List[Dict[str, str]]) -> PromptTemplate:
        """保存或更新提示词模板"""
        session = self.get_session()
        try:
            existing = session.query(PromptTemplate).filter_by(name=name).first()
            if existing:
                existing.display_name = display_name
                existing.description = description
                existing.template = template
                existing.variables = variables
                existing.updated_at = datetime.utcnow()
                result = existing
            else:
                result = PromptTemplate(
                    name=name,
                    display_name=display_name,
                    description=description,
                    template=template,
                    variables=variables
                )
                session.add(result)

            session.commit()
            return result
        finally:
            session.close()

    def delete_prompt_template(self, name: str) -> bool:
        """删除提示词模板"""
        session = self.get_session()
        try:
            template = session.query(PromptTemplate).filter_by(name=name).first()
            if template:
                session.delete(template)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def change_user_password(self, username: str, new_password: str) -> bool:
        """修改用户密码"""
        from auth_utils import hash_password

        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                user.password_hash = hash_password(new_password)
                user.updated_at = datetime.utcnow()
                session.commit()
                return True
            return False
        finally:
            session.close()

    def verify_user_password(self, username: str, password: str) -> bool:
        """验证用户密码"""
        from auth_utils import verify_password

        session = self.get_session()
        try:
            user = session.query(User).filter_by(username=username).first()
            if user:
                return verify_password(password, user.password_hash)
            return False
        finally:
            session.close()

    def reset_admin_password(self, new_password: str = 'admin123') -> bool:
        """重置管理员密码"""
        return self.change_user_password('admin', new_password)

    def create_default_prompts(self):
        """创建默认提示词模板"""
        session = self.get_session()
        try:
            # 检查是否已存在默认模板
            if session.query(PromptTemplate).count() > 0:
                return

            # 动作生成提示词模板
            action_generation_template = """你是一个专业的MCP工具定义生成助手。请根据用户提供的应用信息生成JSON格式的动作定义。

目标应用信息：
- 应用分类：{category}
- 应用名称：{name}
- 应用显示名称：{display_name}
- 应用描述：{description}

要创建的动作，参考此处用户的要求设计：
{prompt}

请为"{display_name}"（{category}类应用）生成相应的MCP工具动作。根据应用类型和用户需求，设计能够实现具体功能的动作定义。

动作设计原则：
1. name: 使用snake_case命名，要准确反映动作功能（如：start_meeting, block_ip_address, query_firewall_status）
2. display_name: 使用简洁的中文名称，体现在{display_name}中的功能
3. description: 详细说明动作的功能和用途，要与{display_name}应用场景相符
4. parameters: 根据动作实际需求决定，可以有参数，也可以没有参数
5. key: 参数名要有实际指导意义，便于理解和调用
6. description: 参数说明要具体，包括数据格式、必要性等信息

请生成符合以下格式的JSON数组，包含用户描述的所有动作：

[
  {{
    "name": "具体动作的英文名称，使用snake_case命名，要能准确表达动作功能",
    "display_name": "动作的中文显示名称，简洁明了",
    "description": "动作的详细描述，说明此动作在{display_name}中的具体功能和用途",
    "parameters": [
      {{
        "key": "参数的英文键名，使用snake_case，要能清楚表达参数含义",
        "type": "参数类型：String|Number|Boolean|Object|Array",
        "required": true,
        "description": "参数的详细说明，包括格式要求、取值范围等"
      }}
    ]
  }}
]

参考示例（防火墙管理）：
[
  {{
    "name": "check_firewall_health",
    "display_name": "查询防火墙健康状态",
    "description": "检查防火墙系统的运行状态和健康情况",
    "parameters": []
  }},
  {{
    "name": "block_ip_address",
    "display_name": "封禁IP地址",
    "description": "将指定IP地址加入防火墙黑名单进行封禁",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要封禁的IP地址，格式如：192.168.1.100"
      }},
      {{
        "key": "duration_minutes",
        "type": "Number",
        "required": false,
        "description": "封禁时长（分钟），0表示永久封禁，默认60分钟"
      }},
      {{
        "key": "reason",
        "type": "String",
        "required": false,
        "description": "封禁原因说明"
      }}
    ]
  }},
  {{
    "name": "unblock_ip_address",
    "display_name": "解封IP地址",
    "description": "将指定IP地址从防火墙黑名单中移除",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要解封的IP地址"
      }}
    ]
  }},
  {{
    "name": "query_ip_block_status",
    "display_name": "查询IP封禁状态",
    "description": "查询指定IP地址的封禁状态和相关信息",
    "parameters": [
      {{
        "key": "ip_address",
        "type": "String",
        "required": true,
        "description": "要查询的IP地址"
      }}
    ]
  }}
]

要求：
1. 严格按照以上格式和原则生成
2. 根据用户描述的每个工具生成对应的动作
3. 只返回JSON数组，不要其他文字

请严格按照JSON格式返回，不要包含任何其他说明文字。"""

            # 响应模拟提示词模板
            response_simulation_template = """你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。"""

            # 创建模板
            action_template = PromptTemplate(
                name="action_generation",
                display_name="动作生成提示词",
                description="用于根据用户需求生成应用动作JSON定义的提示词模板",
                template=action_generation_template,
                variables=[
                    {"name": "prompt", "description": "用户输入的需求描述"},
                    {"name": "category", "description": "应用分类"},
                    {"name": "name", "description": "应用名称"},
                    {"name": "display_name", "description": "应用显示名称"},
                    {"name": "description", "description": "应用描述"}
                ]
            )

            response_template = PromptTemplate(
                name="response_simulation",
                display_name="响应模拟提示词",
                description="用于模拟MCP工具调用响应的提示词模板",
                template=response_simulation_template,
                variables=[
                    {"name": "app_name", "description": "应用名称"},
                    {"name": "action", "description": "动作名称"},
                    {"name": "parameters", "description": "调用参数JSON字符串"}
                ]
            )

            session.add(action_template)
            session.add(response_template)
            session.commit()
            print("Created default prompt templates")
        finally:
            session.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()