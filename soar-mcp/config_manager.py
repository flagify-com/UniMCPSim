#!/usr/bin/env python3
"""
SOAR MCP 配置管理器
统一管理系统配置，支持缓存和实时更新
"""

import time
from typing import Any, Dict, List, Optional
from threading import Lock
from models import db_manager, SystemConfigData
from logger_config import logger


class ConfigManager:
    """系统配置管理器"""
    
    def __init__(self):
        self._config_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 60  # 缓存有效期60秒
        self._lock = Lock()
    
    def _refresh_cache(self, force: bool = False):
        """刷新配置缓存"""
        current_time = time.time()
        
        with self._lock:
            if not force and (current_time - self._cache_timestamp < self._cache_ttl):
                return  # 缓存仍有效
            
            try:
                self._config_cache = db_manager.get_all_system_configs()
                self._cache_timestamp = current_time
                logger.info("配置缓存已刷新")
            except Exception as e:
                logger.error(f"刷新配置缓存失败: {e}")
    
    def get(self, key: str, default_value: Any = None) -> Any:
        """获取配置值"""
        self._refresh_cache()
        
        with self._lock:
            return self._config_cache.get(key, default_value)
    
    def set(self, key: str, value: Any, description: str = None) -> bool:
        """设置配置值"""
        try:
            success = db_manager.set_system_config(key, value, description)
            if success:
                # 立即刷新缓存
                self._refresh_cache(force=True)
            return success
        except Exception as e:
            logger.error(f"设置配置失败 {key}: {e}")
            return False
    
    def get_all(self) -> Dict[str, Any]:
        """获取所有配置"""
        self._refresh_cache()
        
        with self._lock:
            return self._config_cache.copy()
    
    def get_soar_config(self) -> SystemConfigData:
        """获取SOAR相关配置"""
        config = self.get_all()
        
        return SystemConfigData(
            soar_api_url=config.get("soar_api_url", "https://hg.wuzhi-ai.com"),
            soar_api_token=config.get("soar_api_token", ""),
            soar_timeout=config.get("soar_timeout", 30),
            sync_interval=config.get("sync_interval", 14400),
            soar_labels=config.get("soar_labels", ["MCP"])
        )
    
    def update_soar_config(self, config_data: SystemConfigData) -> bool:
        """更新SOAR配置"""
        try:
            success = True
            success &= self.set("soar_api_url", config_data.soar_api_url, "SOAR服务器API地址")
            success &= self.set("soar_api_token", config_data.soar_api_token, "SOAR API Token")
            success &= self.set("soar_timeout", config_data.soar_timeout, "API超时时间(秒)")
            success &= self.set("sync_interval", config_data.sync_interval, "同步周期(秒)")
            success &= self.set("soar_labels", config_data.soar_labels, "剧本抓取标签列表")

            if success:
                logger.info("SOAR配置更新成功")
            else:
                logger.error("SOAR配置更新失败")

            return success
        except Exception as e:
            logger.error(f"更新SOAR配置失败: {e}")
            return False
    
    def get_api_url(self) -> str:
        """获取API地址"""
        return self.get("soar_api_url", "https://hg.wuzhi-ai.com")
    
    def get_api_token(self) -> str:
        """获取API Token"""
        return self.get("soar_api_token", "")
    
    def get_timeout(self) -> int:
        """获取超时时间"""
        return self.get("soar_timeout", 30)
    
    def get_labels(self) -> List[str]:
        """获取标签列表"""
        return self.get("soar_labels", ["MCP"])
    
    def get_ssl_verify(self) -> bool:
        """获取SSL验证设置"""
        value = self.get("ssl_verify", True)
        # 处理字符串类型的布尔值
        if isinstance(value, str):
            return value.lower() in ("true", "1", "yes", "on")
        return bool(value)
    
    def validate_config(self) -> Dict[str, Any]:
        """验证配置完整性"""
        config = self.get_soar_config()
        issues = []

        # 检查必填项
        if not config.soar_api_url:
            issues.append("API地址不能为空")

        if not config.soar_api_token:
            issues.append("API Token不能为空")

        if config.soar_timeout <= 0:
            issues.append("超时时间必须大于0")

        if config.sync_interval <= 0:
            issues.append("同步周期必须大于0")

        # 标签列表可以为空（表示同步所有标签）

        # URL格式检查
        if config.soar_api_url and not (config.soar_api_url.startswith('http://') or config.soar_api_url.startswith('https://')):
            issues.append("API地址格式不正确，需要以http://或https://开头")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": config.model_dump()
        }
    
    def is_first_run(self) -> bool:
        """
        检测是否为首次运行
        当SOAR API地址和Token都为空时认为是首次运行
        """
        try:
            config = self.get_soar_config()

            # 检查关键配置是否为空
            api_url_empty = not config.soar_api_url or config.soar_api_url.strip() == ""
            token_empty = not config.soar_api_token or config.soar_api_token.strip() == ""

            # 如果API地址和Token都为空，则认为是首次运行
            is_first = api_url_empty and token_empty

            if is_first:
                logger.info("检测到首次运行：SOAR配置未完成")
            else:
                logger.debug("检测到已配置运行：SOAR配置已存在")

            return is_first

        except Exception as e:
            logger.warning(f"检测首次运行状态失败: {e}")
            return True  # 异常时默认认为是首次运行，确保安全启动

    def get_missing_required_configs(self) -> List[str]:
        """
        获取缺失的必需配置项列表
        """
        try:
            config = self.get_soar_config()
            missing = []

            if not config.soar_api_url or config.soar_api_url.strip() == "":
                missing.append("SOAR API地址")

            if not config.soar_api_token or config.soar_api_token.strip() == "":
                missing.append("SOAR API Token")

            return missing

        except Exception as e:
            logger.error(f"检查配置完整性失败: {e}")
            return ["配置检查异常"]

    def test_connection(self) -> Dict[str, Any]:
        """测试API连接"""
        try:
            import requests
            
            config = self.get_soar_config()
            headers = {
                "hg-token": config.soar_api_token,
                "Content-Type": "application/json"
            }
            
            # 测试连接
            test_url = f"{config.soar_api_url.rstrip('/')}/odp/core/v1/api/playbook/findAll"
            test_data = {
                "publishStatus": "ONLINE"
            }

            # 只有当标签列表不为空时才添加标签过滤（测试时使用第一个标签）
            if config.soar_labels:
                test_data["labelList"] = [{"name": label} for label in config.soar_labels[:1]]
            
            response = requests.post(
                test_url,
                json=test_data,
                headers=headers,
                timeout=config.soar_timeout,
                verify=self.get_ssl_verify()
            )
            
            if response.status_code == 200:
                data = response.json()
                # 检查SOAR API的业务状态码
                if data.get("code") == 200:
                    result_data = data.get("result", [])
                    return {
                        "success": True,
                        "message": "连接成功",
                        "response_code": response.status_code,
                        "api_code": data.get("code"),
                        "data_count": len(result_data) if isinstance(result_data, list) else 0
                    }
                else:
                    return {
                        "success": False,
                        "message": f"API业务错误: {data.get('message', '未知错误')}",
                        "response_code": response.status_code,
                        "api_code": data.get("code"),
                        "error": str(data)
                    }
            else:
                return {
                    "success": False,
                    "message": f"API返回错误: {response.status_code}",
                    "response_code": response.status_code,
                    "error": response.text[:200]
                }
        
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "message": "连接超时",
                "error": "请检查网络连接和超时设置"
            }
        except requests.exceptions.ConnectionError:
            return {
                "success": False,
                "message": "连接失败",
                "error": "请检查API地址是否正确"
            }
        except Exception as e:
            return {
                "success": False,
                "message": "测试连接时发生错误",
                "error": str(e)
            }
    
    def init(self):
        """初始化配置管理器"""
        try:
            # 初始化数据库默认配置
            db_manager.init_default_configs()
            
            # 刷新缓存
            self._refresh_cache(force=True)
            
            logger.info("配置管理器初始化完成")
            
            # 记录当前配置状态
            validation_result = self.validate_config()
            if validation_result["valid"]:
                logger.info("系统配置验证通过")
            else:
                logger.warning(f"系统配置存在问题: {', '.join(validation_result['issues'])}")
                
        except Exception as e:
            logger.error(f"配置管理器初始化失败: {e}")


# 全局配置管理器实例
config_manager = ConfigManager()