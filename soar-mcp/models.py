#!/usr/bin/env python3
"""
SOAR MCP 数据模型
使用SQLAlchemy + Pydantic实现
"""

import json
from datetime import datetime
from typing import List, Optional, Dict, Any, Union

from sqlalchemy import Column, Integer, BigInteger, String, DateTime, Text, Boolean, create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel, Field, ConfigDict
from logger_config import logger

Base = declarative_base()


class PlaybookModel(Base):
    """剧本数据库模型"""
    __tablename__ = "playbooks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    playbook_category = Column(String(100), index=True)
    description = Column(Text)  # JSON string
    create_time = Column(DateTime)
    update_time = Column(DateTime)  # 本地更新时间
    remote_update_time = Column(DateTime, index=True)  # 远程更新时间 (用于增量同步)
    playbook_params = Column(Text)  # JSON array
    sync_time = Column(DateTime, default=datetime.now)  # 同步时间
    enabled = Column(Boolean, default=True, index=True)  # 剧本启用状态
    
    def __repr__(self):
        return f"<Playbook(id={self.id}, name='{self.name}')>"


class AppModel(Base):
    """应用数据库模型"""
    __tablename__ = "apps"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    version = Column(String(100))
    category = Column(String(100), index=True)
    update_time = Column(DateTime)  # 本地更新时间
    remote_update_time = Column(DateTime, index=True)  # 远程更新时间 (用于增量同步)
    require_asset = Column(String(10))  # 是否需要资源配置
    app_asset_list = Column(Text)  # JSON array
    sync_time = Column(DateTime, default=datetime.now)  # 同步时间
    
    def __repr__(self):
        return f"<App(id={self.id}, name='{self.name}')>"


class ActionModel(Base):
    """动作数据库模型"""
    __tablename__ = "actions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    app_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255))
    description = Column(Text)
    action_type = Column(String(50))  # 动作类型
    classify = Column(String(50))  # 分类
    logic_language = Column(String(50))  # 逻辑语言
    parameter_variables = Column(Text)  # JSON array，输入参数
    result_variables = Column(Text)  # JSON array，输出参数
    update_time = Column(DateTime)  # 更新时间
    sync_time = Column(DateTime, default=datetime.now)  # 同步时间
    
    def __repr__(self):
        return f"<Action(id={self.id}, name='{self.name}', app_id={self.app_id})>"


class SystemConfigModel(Base):
    """系统配置数据库模型"""
    __tablename__ = "system_config"

    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True, index=True)  # 配置键
    value = Column(Text, nullable=False)  # 配置值
    description = Column(String(500))  # 配置描述
    created_time = Column(DateTime, default=datetime.now)
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<SystemConfig(key='{self.key}', value='{self.value}')>"


class AdminPasswordModel(Base):
    """管理员密码数据库模型"""
    __tablename__ = "admin_passwords"

    id = Column(Integer, primary_key=True, autoincrement=True)
    password_hash = Column(String(200), nullable=False)  # 密码哈希值
    description = Column(String(500))  # 密码描述
    is_active = Column(Boolean, default=True)  # 是否启用
    created_time = Column(DateTime, default=datetime.now)
    updated_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    def __repr__(self):
        return f"<AdminPassword(id={self.id}, active={self.is_active})>"


class UserTokenModel(Base):
    """用户Token数据库模型"""
    __tablename__ = "user_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    token = Column(String(100), unique=True, nullable=False, index=True)  # Token值
    name = Column(String(255), nullable=False)  # Token描述名称
    description = Column(String(500))  # Token描述
    is_active = Column(Boolean, default=True, index=True)  # 是否启用
    permissions = Column(Text)  # 权限信息
    created_time = Column(DateTime)  # 历史字段：创建时间
    updated_time = Column(DateTime)  # 历史字段：更新时间
    last_used_time = Column(DateTime)  # 历史字段：最后使用时间
    usage_count = Column(Integer, default=0)  # 使用次数
    created_at = Column(DateTime, default=datetime.now)  # 创建时间
    expires_at = Column(DateTime)  # 过期时间（可选）
    last_used_at = Column(DateTime)  # 最后使用时间

    def __repr__(self):
        return f"<UserToken(id={self.id}, name='{self.name}', active={self.is_active})>"


class AuditLogModel(Base):
    """审计日志数据库模型"""
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.now, index=True)  # 操作时间
    token_id = Column(Integer, index=True)  # 关联的Token ID
    token_name = Column(String(100))  # Token名称（冗余存储便于查询）
    action = Column(String(100), nullable=False, index=True)  # 操作类型
    resource = Column(String(200))  # 访问的资源
    parameters = Column(Text)  # 操作参数（JSON格式）
    result = Column(String(50))  # 操作结果（success/error）
    error_message = Column(Text)  # 错误信息（如果有）
    ip_address = Column(String(45))  # 客户端IP地址
    user_agent = Column(String(500))  # 用户代理

    def __repr__(self):
        return f"<AuditLog(id={self.id}, action='{self.action}', result='{self.result}')>"


class PlaybookParam(BaseModel):
    """剧本参数 Pydantic 模型"""
    cef_column: str = Field(..., description="CEF字段名")
    cef_desc: str = Field(..., description="CEF字段描述")
    value_type: str = Field(..., description="值类型")
    required: bool = Field(default=False, description="是否必填")


class PlaybookData(BaseModel):
    """剧本数据 Pydantic 模型"""
    id: int
    name: str
    display_name: Optional[str] = None
    playbook_category: Optional[str] = None
    description: Optional[str] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None
    remote_update_time: Optional[datetime] = None  # 远程更新时间
    playbook_params: List[PlaybookParam] = Field(default_factory=list)
    sync_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class ActionParam(BaseModel):
    """动作参数 Pydantic 模型"""
    name: Optional[str] = Field(default="", description="参数名称")
    required: Optional[bool] = Field(default=False, description="是否必须")
    type: Optional[str] = Field(default="", description="参数类型")
    description: Optional[str] = Field(default="", description="参数描述")
    default_value: Optional[str] = Field(default="", description="默认值")
    order: Optional[int] = Field(default=0, description="顺序")
    
    model_config = ConfigDict(extra="allow")


class ActionResult(BaseModel):
    """动作结果 Pydantic 模型"""
    description: Optional[str] = Field(default="", description="结果描述")
    value_type: Optional[str] = Field(default="", description="值类型")
    data_path: Optional[str] = Field(default="", description="数据路径")
    
    model_config = ConfigDict(extra="allow")


class AppData(BaseModel):
    """应用数据 Pydantic 模型"""
    id: Union[int, str]  # 兼容不同类型
    name: Optional[str] = None
    description: Optional[str] = None
    version: Optional[str] = None
    category: Optional[str] = None
    updateTime: Optional[str] = None  # API返回的是字符串，我们在解析时转换
    requireAsset: Optional[Union[str, bool, int]] = None  # 兼容不同类型
    appAssetList: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    appActionList: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    # 设置所有字段为可选，并允许多种类型
    createdBy: Optional[Union[int, str]] = None
    modifiedBy: Optional[Union[int, str]] = None
    createdNickName: Optional[str] = None
    modifiedNickName: Optional[str] = None
    createTime: Optional[str] = None
    status: Optional[Union[int, str]] = None
    deleted: Optional[Union[bool, str, int]] = None
    displayName: Optional[str] = None
    readMePath: Optional[str] = None
    iconfilePath: Optional[str] = None
    os: Optional[str] = None
    logicLanguage: Optional[str] = None
    logicLanguageVersion: Optional[str] = None
    assetVariableList: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    logicContent: Optional[str] = None
    actionEngineType: Optional[str] = None
    favState: Optional[Union[int, str]] = None
    
    # 允许任何额外的字段
    model_config = ConfigDict(extra="allow")
    usedTimes: Optional[int] = None
    appCategoryList: List[Dict[str, Any]] = Field(default_factory=list)
    appPackageFile: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class ActionData(BaseModel):
    """动作数据 Pydantic 模型"""
    id: int
    app_id: int
    name: str
    display_name: Optional[str] = None
    description: Optional[str] = None
    action_type: Optional[str] = None
    classify: Optional[str] = None
    logic_language: Optional[str] = None
    parameter_variables: List[ActionParam] = Field(default_factory=list)
    result_variables: List[ActionResult] = Field(default_factory=list)
    update_time: Optional[datetime] = None
    sync_time: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class SystemConfigData(BaseModel):
    """系统配置数据 Pydantic 模型"""
    soar_api_url: str = Field(..., description="SOAR服务器API地址")
    soar_api_token: str = Field(..., description="SOAR API Token")
    soar_timeout: int = Field(default=30, description="API超时时间(秒)")
    sync_interval: int = Field(default=14400, description="同步周期(秒)")
    soar_labels: List[str] = Field(default=["MCP"], description="剧本抓取标签列表")
    
    model_config = ConfigDict(from_attributes=True)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_path: str = "soar_mcp.db"):
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def init_db(self):
        """初始化数据库表"""
        Base.metadata.create_all(bind=self.engine)
        logger.database_info(f"数据库初始化完成: {self.db_path}")
    
    def get_session(self):
        """获取数据库会话"""
        session = self.SessionLocal()
        try:
            return session
        except Exception:
            session.close()
            raise
    
    def save_playbook(self, playbook_data: PlaybookData, force_update: bool = False) -> Union[bool, str]:
        """保存剧本数据
        
        Args:
            playbook_data: 剧本数据
            force_update: 强制更新，忽略时间比较
            
        Returns:
            True: 成功保存/更新
            False: 保存失败
            "ignored": 跳过（无需更新）
        """
        session = self.get_session()
        try:
            # 序列化参数为JSON
            params_json = json.dumps([
                {
                    "cefColumn": param.cef_column,
                    "cefDesc": param.cef_desc,
                    "valueType": param.value_type,
                    "required": param.required
                } for param in playbook_data.playbook_params
            ], ensure_ascii=False)
            
            # 查找现有记录
            existing = session.query(PlaybookModel).filter_by(id=playbook_data.id).first()
            
            if existing:
                # 检查是否需要更新 (比较远程更新时间)
                if not force_update and existing.remote_update_time and playbook_data.remote_update_time:
                    if playbook_data.remote_update_time == existing.remote_update_time:
                        logger.sync_skip(f"跳过剧本 {playbook_data.id}: 无需更新 (远程: {playbook_data.remote_update_time}, 本地: {existing.remote_update_time})")
                        return "ignored"
                    elif playbook_data.remote_update_time < existing.remote_update_time:
                        logger.sync_warning(f"异常情况：远程时间早于本地时间 {playbook_data.id} (远程: {playbook_data.remote_update_time}, 本地: {existing.remote_update_time})")
                        # 异常情况也跳过，避免数据倒退
                        return "ignored"
                
                # 更新现有记录
                existing.name = playbook_data.name
                existing.display_name = playbook_data.display_name
                existing.playbook_category = playbook_data.playbook_category
                existing.description = playbook_data.description
                existing.create_time = playbook_data.create_time
                existing.update_time = playbook_data.update_time
                existing.remote_update_time = playbook_data.remote_update_time
                existing.playbook_params = params_json
                existing.sync_time = datetime.now()
                logger.sync_success(f"更新剧本 {playbook_data.id}: {playbook_data.name}")
            else:
                # 创建新记录
                new_playbook = PlaybookModel(
                    id=playbook_data.id,
                    name=playbook_data.name,
                    display_name=playbook_data.display_name,
                    playbook_category=playbook_data.playbook_category,
                    description=playbook_data.description,
                    create_time=playbook_data.create_time,
                    update_time=playbook_data.update_time,
                    remote_update_time=playbook_data.remote_update_time,
                    playbook_params=params_json,
                    sync_time=datetime.now()
                )
                session.add(new_playbook)
                logger.sync_success(f"新增剧本 {playbook_data.id}: {playbook_data.name}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.sync_error(f"保存剧本失败 {playbook_data.id}: {e}")
            return False
        finally:
            session.close()
    
    def get_playbook(self, playbook_id: int) -> Optional[PlaybookData]:
        """获取单个剧本"""
        session = self.get_session()
        try:
            playbook = session.query(PlaybookModel).filter_by(id=playbook_id).first()
            if not playbook:
                return None
            
            # 解析JSON参数
            params = []
            if playbook.playbook_params:
                try:
                    param_list = json.loads(playbook.playbook_params)
                    params = [
                        PlaybookParam(
                            cef_column=p.get("cefColumn", ""),
                            cef_desc=p.get("cefDesc", ""),
                            value_type=p.get("valueType", ""),
                            required=p.get("required", False)
                        ) for p in param_list
                    ]
                except json.JSONDecodeError:
                    pass
            
            return PlaybookData(
                id=playbook.id,
                name=playbook.name,
                display_name=playbook.display_name,
                playbook_category=playbook.playbook_category,
                description=playbook.description,
                create_time=playbook.create_time,
                update_time=playbook.update_time,
                remote_update_time=playbook.remote_update_time,
                playbook_params=params,
                sync_time=playbook.sync_time
            )
            
        except Exception as e:
            logger.error(f"获取剧本失败 {playbook_id}: {e}")
            return None
        finally:
            session.close()
    
    def get_playbooks(self, category: Optional[str] = None, limit: int = 100) -> List[PlaybookData]:
        """获取剧本列表（只返回启用的剧本）"""
        session = self.get_session()
        try:
            query = session.query(PlaybookModel)
            
            # 过滤启用的剧本
            query = query.filter(PlaybookModel.enabled == True)
            
            if category:
                query = query.filter(PlaybookModel.playbook_category == category)
            
            playbooks = query.limit(limit).all()
            
            result = []
            for playbook in playbooks:
                # 解析JSON参数
                params = []
                if playbook.playbook_params:
                    try:
                        param_list = json.loads(playbook.playbook_params)
                        params = [
                            PlaybookParam(
                                cef_column=p.get("cefColumn", ""),
                                cef_desc=p.get("cefDesc", ""),
                                value_type=p.get("valueType", ""),
                                required=p.get("required", False)
                            ) for p in param_list
                        ]
                    except json.JSONDecodeError:
                        pass
                
                result.append(PlaybookData(
                    id=playbook.id,
                    name=playbook.name,
                    display_name=playbook.display_name,
                    playbook_category=playbook.playbook_category,
                    description=playbook.description,
                    create_time=playbook.create_time,
                    update_time=playbook.update_time,
                    remote_update_time=playbook.remote_update_time,
                    playbook_params=params,
                    sync_time=playbook.sync_time
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"获取剧本列表失败: {e}")
            return []
        finally:
            session.close()
    
    def get_sync_stats(self) -> Dict[str, Any]:
        """获取同步统计信息"""
        session = self.get_session()
        try:
            total_count = session.query(PlaybookModel).count()
            latest_sync = session.query(PlaybookModel.sync_time).order_by(
                PlaybookModel.sync_time.desc()
            ).first()
            
            return {
                "total_playbooks": total_count,
                "latest_sync_time": latest_sync[0] if latest_sync else None
            }
        except Exception as e:
            logger.error(f"获取同步统计失败: {e}")
            return {"total_playbooks": 0, "latest_sync_time": None}
        finally:
            session.close()
    
    def save_app(self, app_data: AppData, force_update: bool = False) -> Union[bool, str]:
        """保存应用数据
        
        Args:
            app_data: 应用数据
            force_update: 强制更新，忽略时间比较
            
        Returns:
            True: 成功保存/更新
            False: 保存失败
            "ignored": 跳过（无需更新）
        """
        session = self.get_session()
        try:
            # 序列化资源列表为JSON  
            asset_list_json = json.dumps(app_data.appAssetList, ensure_ascii=False)
            
            # 解析updateTime字符串为datetime对象
            update_time = None
            remote_update_time = None
            if app_data.updateTime:
                try:
                    if isinstance(app_data.updateTime, str) and "T" in app_data.updateTime:  # ISO格式
                        update_time = datetime.fromisoformat(app_data.updateTime.replace("Z", "+00:00"))
                        remote_update_time = update_time
                    elif isinstance(app_data.updateTime, (int, float, str)):  # 可能是时间戳
                        timestamp = int(app_data.updateTime) / 1000  # 假设是毫秒时间戳
                        update_time = datetime.fromtimestamp(timestamp)
                        remote_update_time = update_time
                except (ValueError, TypeError):
                    pass
            
            # 查找现有记录
            existing = session.query(AppModel).filter_by(id=app_data.id).first()
            
            if existing:
                # 检查是否需要更新 (比较远程更新时间)
                if not force_update:
                    # 如果API没有时间信息，跳过更新（认为没有变化）
                    if remote_update_time is None:
                        logger.sync_skip(f"跳过应用 {app_data.id}: API无时间信息，推定无变化")
                        return "ignored"
                        
                    # 如果本地有时间且与远程时间相等，跳过更新    
                    if existing.remote_update_time and remote_update_time == existing.remote_update_time:
                        logger.sync_skip(f"跳过应用 {app_data.id}: 无需更新 (远程: {remote_update_time}, 本地: {existing.remote_update_time})")
                        return "ignored"
                    elif existing.remote_update_time and remote_update_time < existing.remote_update_time:
                        logger.sync_warning(f"异常情况：应用远程时间早于本地时间 {app_data.id} (远程: {remote_update_time}, 本地: {existing.remote_update_time})")
                        return "ignored"
                
                # 更新现有记录
                existing.name = app_data.name
                existing.description = app_data.description
                existing.version = app_data.version
                existing.category = app_data.category
                existing.update_time = update_time
                existing.remote_update_time = remote_update_time
                existing.require_asset = app_data.requireAsset
                existing.app_asset_list = asset_list_json
                existing.sync_time = datetime.now()
                logger.sync_success(f"更新应用 {app_data.id}: {app_data.name}")
            else:
                # 创建新记录
                new_app = AppModel(
                    id=app_data.id,
                    name=app_data.name,
                    description=app_data.description,
                    version=app_data.version,
                    category=app_data.category,
                    update_time=update_time,
                    remote_update_time=remote_update_time,
                    require_asset=app_data.requireAsset,
                    app_asset_list=asset_list_json,
                    sync_time=datetime.now()
                )
                session.add(new_app)
                logger.sync_success(f"新增应用 {app_data.id}: {app_data.name}")
            
            session.commit()
            return True
            
        except Exception as e:
            session.rollback()
            logger.sync_error(f"保存应用失败 {app_data.id}: {e}")
            return False
        finally:
            session.close()
    
    def delete_actions_by_app_id(self, app_id: int) -> int:
        """删除指定应用的所有动作
        
        Args:
            app_id: 应用ID
            
        Returns:
            删除的动作数量
        """
        session = self.get_session()
        try:
            deleted_count = session.query(ActionModel).filter_by(app_id=app_id).delete()
            session.commit()
            return deleted_count
        except Exception as e:
            session.rollback()
            logger.sync_error(f"删除应用动作失败 {app_id}: {e}")
            return 0
        finally:
            session.close()
    
    def batch_save_actions(self, actions_data: List[ActionData]) -> int:
        """批量保存动作数据
        
        Args:
            actions_data: 动作数据列表
            
        Returns:
            成功保存的动作数量
        """
        session = self.get_session()
        try:
            success_count = 0
            for action_data in actions_data:
                # 序列化参数为JSON
                parameter_vars_json = json.dumps([
                    {
                        "name": param.name,
                        "required": param.required,
                        "type": param.type,
                        "description": param.description,
                        "defaultValue": param.default_value,
                        "order": param.order
                    } for param in action_data.parameter_variables
                ], ensure_ascii=False)
                
                result_vars_json = json.dumps([
                    {
                        "description": result.description,
                        "valueType": result.value_type,
                        "dataPath": result.data_path
                    } for result in action_data.result_variables
                ], ensure_ascii=False)
                
                new_action = ActionModel(
                    id=action_data.id,
                    app_id=action_data.app_id,
                    name=action_data.name,
                    display_name=action_data.display_name,
                    description=action_data.description,
                    action_type=action_data.action_type,
                    classify=action_data.classify,
                    logic_language=action_data.logic_language,
                    parameter_variables=parameter_vars_json,
                    result_variables=result_vars_json,
                    update_time=action_data.update_time,
                    sync_time=datetime.now()
                )
                session.add(new_action)
                success_count += 1
            
            session.commit()
            return success_count
            
        except Exception as e:
            session.rollback()
            logger.sync_error(f"批量保存动作失败: {e}")
            return 0
        finally:
            session.close()
    
    def get_apps_stats(self) -> Dict[str, Any]:
        """获取应用统计信息"""
        session = self.get_session()
        try:
            total_apps = session.query(AppModel).count()
            total_actions = session.query(ActionModel).count()
            latest_sync = session.query(AppModel.sync_time).order_by(
                AppModel.sync_time.desc()
            ).first()
            
            return {
                "total_apps": total_apps,
                "total_actions": total_actions,
                "latest_sync_time": latest_sync[0] if latest_sync else None
            }
        except Exception as e:
            logger.error(f"获取应用统计失败: {e}")
            return {"total_apps": 0, "total_actions": 0, "latest_sync_time": None}
        finally:
            session.close()
    
    def get_playbooks_stats(self) -> Dict[str, Any]:
        """获取剧本统计信息"""
        session = self.get_session()
        try:
            total_playbooks = session.query(PlaybookModel).count()
            enabled_playbooks = session.query(PlaybookModel).filter_by(enabled=True).count()
            disabled_playbooks = total_playbooks - enabled_playbooks
            
            return {
                "total_playbooks": total_playbooks,
                "enabled_playbooks": enabled_playbooks,
                "disabled_playbooks": disabled_playbooks
            }
        except Exception as e:
            logger.error(f"获取剧本统计失败: {e}")
            return {"total_playbooks": 0, "enabled_playbooks": 0, "disabled_playbooks": 0}
        finally:
            session.close()
    
    def get_last_sync_time(self) -> Optional[str]:
        """获取最后同步时间（优先从系统配置获取全局同步时间，其次从数据表获取）"""
        try:
            # 首先尝试从系统配置获取最后同步时间
            last_sync_config = self.get_system_config("last_sync_time")
            if last_sync_config:
                if isinstance(last_sync_config, str):
                    try:
                        # 尝试解析时间字符串
                        last_sync_dt = datetime.fromisoformat(last_sync_config.replace("Z", "+00:00"))
                        # 返回格式化的字符串，确保前端正确显示
                        return last_sync_dt.strftime("%Y/%m/%d %H:%M:%S")
                    except ValueError:
                        pass  # 如果解析失败，继续使用旧方法
                elif isinstance(last_sync_config, datetime):
                    # 返回格式化的字符串，确保前端正确显示
                    return last_sync_config.strftime("%Y/%m/%d %H:%M:%S")

            # 如果系统配置中没有记录，则从数据表获取（兼容旧版本）
            session = self.get_session()
            try:
                # 获取剧本最后同步时间
                playbook_sync = session.query(PlaybookModel.sync_time).order_by(
                    PlaybookModel.sync_time.desc()
                ).first()

                # 获取应用最后同步时间
                app_sync = session.query(AppModel.sync_time).order_by(
                    AppModel.sync_time.desc()
                ).first()

                playbook_time = playbook_sync[0] if playbook_sync else None
                app_time = app_sync[0] if app_sync else None

                # 返回最新的时间
                latest_time = None
                if playbook_time and app_time:
                    latest_time = max(playbook_time, app_time)
                elif playbook_time:
                    latest_time = playbook_time
                elif app_time:
                    latest_time = app_time

                # 如果有时间，格式化返回
                if latest_time:
                    return latest_time.strftime("%Y/%m/%d %H:%M:%S")
                else:
                    return None

            finally:
                session.close()

        except Exception as e:
            logger.error(f"获取最后同步时间失败: {e}")
            return None

    def update_last_sync_time(self) -> bool:
        """更新最后同步时间到系统配置"""
        try:
            current_time = datetime.now()
            return self.set_system_config(
                "last_sync_time",
                current_time.isoformat(),
                "最后一次数据同步的时间"
            )
        except Exception as e:
            logger.error(f"更新最后同步时间失败: {e}")
            return False

    def get_playbooks_admin(self, category: Optional[str] = None, limit: int = 1000) -> List[Dict]:
        """获取所有剧本列表（用于管理界面），包含启用状态
        注意：这里返回所有剧本，包括通过标签过滤同步进来的剧本
        """
        session = self.get_session()
        try:
            query = session.query(PlaybookModel)
            
            if category:
                query = query.filter(PlaybookModel.playbook_category == category)
            
            playbooks = query.order_by(PlaybookModel.id).limit(limit).all()
            
            result = []
            for playbook in playbooks:
                result.append({
                    "id": str(playbook.id),  # 转换为字符串格式
                    "name": playbook.name,
                    "displayName": playbook.display_name or playbook.name,
                    "playbookCategory": playbook.playbook_category or "未分类",
                    "description": playbook.description or "",
                    "enabled": playbook.enabled if playbook.enabled is not None else True,
                    "createTime": playbook.create_time.isoformat() if playbook.create_time else None,
                    "updateTime": playbook.update_time.isoformat() if playbook.update_time else None,
                    "syncTime": playbook.sync_time.isoformat() if playbook.sync_time else None
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取剧本管理列表失败: {e}")
            return []
        finally:
            session.close()
    
    def get_playbook_by_id(self, playbook_id: int) -> Optional[Dict]:
        """根据ID获取单个剧本详情"""
        session = self.get_session()
        try:
            playbook = session.query(PlaybookModel).filter_by(id=playbook_id).first()
            if not playbook:
                return None
            
            return {
                "id": str(playbook.id),  # 转换为字符串格式
                "name": playbook.name,
                "displayName": playbook.display_name or playbook.name,
                "playbookCategory": playbook.playbook_category or "未分类",
                "description": playbook.description or "",
                "enabled": playbook.enabled if playbook.enabled is not None else True,
                "playbookParams": playbook.playbook_params or "[]",
                "createTime": playbook.create_time.isoformat() if playbook.create_time else None,
                "updateTime": playbook.update_time.isoformat() if playbook.update_time else None,
                "syncTime": playbook.sync_time.isoformat() if playbook.sync_time else None,
                "remoteUpdateTime": playbook.remote_update_time.isoformat() if playbook.remote_update_time else None
            }
            
        except Exception as e:
            logger.error(f"获取剧本详情失败 {playbook_id}: {e}")
            return None
        finally:
            session.close()

    def update_playbook_status(self, playbook_id: int, enabled: bool) -> bool:
        """更新剧本启用状态"""
        session = self.get_session()
        try:
            playbook = session.query(PlaybookModel).filter_by(id=playbook_id).first()
            if not playbook:
                logger.warning(f"未找到剧本 ID: {playbook_id}")
                return False
            
            playbook.enabled = enabled
            playbook.update_time = datetime.now()
            session.commit()
            
            logger.info(f"剧本 {playbook_id} ({playbook.name}) 状态已更新为: {'启用' if enabled else '禁用'}")
            return True
            
        except Exception as e:
            logger.error(f"更新剧本状态失败: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_system_config(self, key: str, default_value: Any = None) -> Any:
        """获取系统配置值"""
        session = self.get_session()
        try:
            config = session.query(SystemConfigModel).filter_by(key=key).first()
            if config:
                # 尝试解析JSON值
                try:
                    return json.loads(config.value)
                except json.JSONDecodeError:
                    return config.value
            return default_value
        except Exception as e:
            logger.error(f"获取系统配置失败 {key}: {e}")
            return default_value
        finally:
            session.close()
    
    def set_system_config(self, key: str, value: Any, description: str = None) -> bool:
        """设置系统配置值"""
        session = self.get_session()
        try:
            # 序列化值为JSON字符串
            if isinstance(value, (dict, list)):
                value_str = json.dumps(value, ensure_ascii=False)
            else:
                value_str = str(value)
            
            # 查找现有配置
            config = session.query(SystemConfigModel).filter_by(key=key).first()
            
            if config:
                # 更新现有配置
                config.value = value_str
                config.updated_time = datetime.now()
                if description:
                    config.description = description
            else:
                # 创建新配置
                config = SystemConfigModel(
                    key=key,
                    value=value_str,
                    description=description or ""
                )
                session.add(config)
            
            session.commit()
            # 对敏感信息进行打码处理
            if key in ['soar_api_token', 'jwt_secret_key', 'admin_password']:
                display_value = str(value)
                if len(display_value) > 10:
                    display_value = display_value[:6] + '*' * (len(display_value) - 10) + display_value[-4:]
                else:
                    display_value = '*' * len(display_value)
                logger.info(f"系统配置已更新: {key} = {display_value}")
            else:
                logger.info(f"系统配置已更新: {key} = {value}")
            return True
        except Exception as e:
            logger.error(f"设置系统配置失败 {key}: {e}")
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_all_system_configs(self) -> Dict[str, Any]:
        """获取所有系统配置"""
        session = self.get_session()
        try:
            configs = session.query(SystemConfigModel).all()
            result = {}
            for config in configs:
                try:
                    result[config.key] = json.loads(config.value)
                except json.JSONDecodeError:
                    result[config.key] = config.value
            return result
        except Exception as e:
            logger.error(f"获取所有系统配置失败: {e}")
            return {}
        finally:
            session.close()

    def create_admin_password(self, password_hash: str, description: str = None) -> bool:
        """创建管理员密码"""
        session = self.get_session()
        try:
            # 删除现有的密码记录（只保留一个有效密码）
            session.query(AdminPasswordModel).delete()

            new_password = AdminPasswordModel(
                password_hash=password_hash,
                description=description,
                is_active=True
            )
            session.add(new_password)
            session.commit()
            logger.info("创建管理员密码成功")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"创建管理员密码失败: {e}")
            return False
        finally:
            session.close()

    def get_admin_password_hash(self) -> Optional[str]:
        """获取第一个有效的管理员密码哈希"""
        session = self.get_session()
        try:
            password_obj = session.query(AdminPasswordModel).filter(AdminPasswordModel.is_active == True).first()
            return password_obj.password_hash if password_obj else None
        except Exception as e:
            logger.error(f"获取管理员密码失败: {e}")
            return None
        finally:
            session.close()

    def verify_admin_password(self, password_hash: str) -> bool:
        """验证管理员密码是否有效"""
        session = self.get_session()
        try:
            password_obj = session.query(AdminPasswordModel).filter(
                AdminPasswordModel.password_hash == password_hash,
                AdminPasswordModel.is_active == True
            ).first()
            return password_obj is not None
        except Exception as e:
            logger.error(f"验证管理员密码失败: {e}")
            return False
        finally:
            session.close()

    def init_default_configs(self):
        """初始化默认系统配置"""
        try:
            # 检查是否已有配置
            existing_configs = self.get_all_system_configs()

            # 如果没有配置，则设置默认值
            if not existing_configs:
                logger.info("初始化默认系统配置...")

                # 尝试从.env文件读取配置进行迁移
                import os
                from dotenv import load_dotenv

                # 加载.env文件（如果存在）
                env_path = ".env"
                if os.path.exists(env_path):
                    load_dotenv(env_path)
                    logger.info("从.env文件迁移配置到数据库")

                # 设置默认配置
                default_configs = {
                    "soar_api_url": os.getenv("API_URL", ""),  # 首次运行时为空，需用户配置
                    "soar_api_token": os.getenv("API_TOKEN", ""),  # 首次运行时为空，需用户配置
                    "soar_timeout": int(os.getenv("SOAR_TIMEOUT", "30")),  # 超时参数可有默认值
                    "sync_interval": int(os.getenv("SYNC_INTERVAL", "14400")),  # 同步周期可有默认值（4小时）
                    "soar_labels": ["MCP"],  # 标签参数可有默认值
                    "ssl_verify": os.getenv("SSL_VERIFY", "0") != "0"  # SSL验证默认关闭，避免证书问题
                }

                for key, value in default_configs.items():
                    self.set_system_config(key, value, f"系统默认配置: {key}")

                logger.info("默认系统配置初始化完成")
            else:
                logger.info("系统配置已存在，跳过初始化")

        except Exception as e:
            logger.error(f"初始化默认系统配置失败: {e}")

    def create_user_token(self, name: str, expires_in_days: int = None) -> Optional[str]:
        """创建用户Token

        Args:
            name: Token描述名称
            expires_in_days: 过期天数，None表示永不过期

        Returns:
            Token字符串，创建失败返回None
        """
        session = self.get_session()
        try:
            import secrets
            from datetime import timedelta

            # 生成随机token
            token = secrets.token_urlsafe(32)

            # 计算过期时间
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)

            new_token = UserTokenModel(
                token=token,
                name=name,
                expires_at=expires_at,
                is_active=True
            )
            session.add(new_token)
            session.commit()

            logger.info(f"创建用户Token成功: {name} ({token[:8]}...)")
            return token

        except Exception as e:
            session.rollback()
            logger.error(f"创建用户Token失败: {e}")
            return None
        finally:
            session.close()

    def get_user_tokens(self) -> List[Dict]:
        """获取所有用户Token列表"""
        session = self.get_session()
        try:
            tokens = session.query(UserTokenModel).order_by(UserTokenModel.created_at.desc()).all()

            result = []
            for token in tokens:
                result.append({
                    "id": token.id,
                    "token": token.token,
                    "name": token.name,
                    "description": token.description,
                    "is_active": token.is_active,
                    "permissions": token.permissions,
                    "created_time": token.created_time.isoformat() if token.created_time else None,
                    "updated_time": token.updated_time.isoformat() if token.updated_time else None,
                    "last_used_time": token.last_used_time.isoformat() if token.last_used_time else None,
                    "usage_count": token.usage_count or 0,
                    "created_at": token.created_at.isoformat() if token.created_at else None,
                    "expires_at": token.expires_at.isoformat() if token.expires_at else None,
                    "last_used_at": token.last_used_at.isoformat() if token.last_used_at else None
                })

            return result

        except Exception as e:
            logger.error(f"获取用户Token列表失败: {e}")
            return []
        finally:
            session.close()

    def verify_token(self, token: str) -> bool:
        """验证Token是否有效

        Args:
            token: 要验证的token

        Returns:
            True表示token有效，False表示无效
        """
        session = self.get_session()
        try:
            token_obj = session.query(UserTokenModel).filter(
                UserTokenModel.token == token,
                UserTokenModel.is_active == True
            ).first()

            if not token_obj:
                return False

            # 检查是否过期
            if token_obj.expires_at and datetime.now() > token_obj.expires_at:
                return False

            # 更新最后使用时间和使用次数
            now = datetime.now()
            token_obj.last_used_at = now

            # 兼容性处理：如果数据库中有last_used_time字段，也更新它
            try:
                if hasattr(token_obj, 'last_used_time'):
                    token_obj.last_used_time = now
            except Exception as e:
                logger.debug(f"更新last_used_time字段失败（可能不存在）: {e}")

            # 更新使用次数
            if token_obj.usage_count is None:
                token_obj.usage_count = 1
            else:
                token_obj.usage_count += 1

            session.commit()

            return True

        except Exception as e:
            logger.error(f"验证Token失败: {e}")
            return False
        finally:
            session.close()

    def delete_user_token(self, token_id: int) -> bool:
        """删除用户Token"""
        session = self.get_session()
        try:
            token = session.query(UserTokenModel).filter_by(id=token_id).first()
            if not token:
                return False

            session.delete(token)
            session.commit()

            logger.info(f"删除用户Token成功: {token.name}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"删除用户Token失败: {e}")
            return False
        finally:
            session.close()

    def update_token_status(self, token_id: int, is_active: bool) -> bool:
        """更新Token启用状态"""
        session = self.get_session()
        try:
            token = session.query(UserTokenModel).filter_by(id=token_id).first()
            if not token:
                return False

            token.is_active = is_active
            session.commit()

            logger.info(f"Token状态更新成功: {token.name} -> {'启用' if is_active else '禁用'}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"更新Token状态失败: {e}")
            return False
        finally:
            session.close()

    def log_audit_event(self, action: str, resource: str = None, parameters: dict = None,
                       result: str = "success", error_message: str = None,
                       token_info: dict = None, ip_address: str = None, user_agent: str = None) -> bool:
        """记录审计日志

        Args:
            action: 操作类型（如：list_playbooks, execute_playbook等）
            resource: 访问的资源
            parameters: 操作参数
            result: 操作结果（success/error）
            error_message: 错误信息
            token_info: Token信息（包含id和name）
            ip_address: 客户端IP地址
            user_agent: 用户代理

        Returns:
            True: 记录成功，False: 记录失败
        """
        session = self.get_session()
        try:
            # 序列化参数
            params_json = None
            if parameters:
                import json
                params_json = json.dumps(parameters, ensure_ascii=False)

            audit_log = AuditLogModel(
                action=action,
                resource=resource,
                parameters=params_json,
                result=result,
                error_message=error_message,
                token_id=token_info.get('id') if token_info else None,
                token_name=token_info.get('name') if token_info else None,
                ip_address=ip_address,
                user_agent=user_agent
            )

            session.add(audit_log)
            session.commit()

            logger.debug(f"审计日志记录成功: {action} -> {result}")
            return True

        except Exception as e:
            session.rollback()
            logger.error(f"记录审计日志失败: {e}")
            return False
        finally:
            session.close()

    def get_audit_logs(self, limit: int = 100, token_id: int = None, action: str = None) -> List[Dict]:
        """获取审计日志列表

        Args:
            limit: 限制返回数量
            token_id: 过滤特定Token的日志
            action: 过滤特定操作类型

        Returns:
            审计日志列表
        """
        session = self.get_session()
        try:
            query = session.query(AuditLogModel)

            if token_id:
                query = query.filter(AuditLogModel.token_id == token_id)

            if action:
                query = query.filter(AuditLogModel.action == action)

            logs = query.order_by(AuditLogModel.timestamp.desc()).limit(limit).all()

            result = []
            for log in logs:
                params = None
                if log.parameters:
                    try:
                        import json
                        params = json.loads(log.parameters)
                    except:
                        params = log.parameters

                result.append({
                    "id": log.id,
                    "timestamp": log.timestamp.isoformat() if log.timestamp else None,
                    "token_id": log.token_id,
                    "token_name": log.token_name,
                    "action": log.action,
                    "resource": log.resource,
                    "parameters": params,
                    "result": log.result,
                    "error_message": log.error_message,
                    "ip_address": log.ip_address,
                    "user_agent": log.user_agent
                })

            return result

        except Exception as e:
            logger.error(f"获取审计日志失败: {e}")
            return []
        finally:
            session.close()

    def get_token_by_value(self, token: str) -> Optional[Dict]:
        """根据Token值获取Token信息"""
        session = self.get_session()
        try:
            token_obj = session.query(UserTokenModel).filter(
                UserTokenModel.token == token,
                UserTokenModel.is_active == True
            ).first()

            if not token_obj:
                return None

            # 检查是否过期
            if token_obj.expires_at and datetime.now() > token_obj.expires_at:
                return None

            return {
                "id": token_obj.id,
                "name": token_obj.name,
                "token": token_obj.token,
                "description": token_obj.description,
                "is_active": token_obj.is_active,
                "permissions": token_obj.permissions,
                "created_time": token_obj.created_time.isoformat() if token_obj.created_time else None,
                "updated_time": token_obj.updated_time.isoformat() if token_obj.updated_time else None,
                "last_used_time": token_obj.last_used_time.isoformat() if token_obj.last_used_time else None,
                "usage_count": token_obj.usage_count or 0,
                "created_at": token_obj.created_at.isoformat() if token_obj.created_at else None,
                "expires_at": token_obj.expires_at.isoformat() if token_obj.expires_at else None,
                "last_used_at": token_obj.last_used_at.isoformat() if token_obj.last_used_at else None
            }

        except Exception as e:
            logger.error(f"获取Token信息失败: {e}")
            return None
        finally:
            session.close()


# 全局数据库管理器实例
db_manager = DatabaseManager()