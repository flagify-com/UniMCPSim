#!/usr/bin/env python3
"""
SOAR 剧本同步服务
支持异步API调用和数据同步
"""

import asyncio
import json
import ssl
import time
from datetime import datetime
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin

import httpx
from dotenv import load_dotenv
import os

from models import DatabaseManager, PlaybookData, PlaybookParam, AppData, ActionData, ActionParam, ActionResult
from logger_config import logger
from config_manager import config_manager

# 加载环境变量
load_dotenv()

# SSL设置
ssl._create_default_https_context = ssl._create_unverified_context


class SOARAPIClient:
    """SOAR API客户端"""
    
    def __init__(self):
        # 从配置管理器获取配置
        self.base_url = config_manager.get_api_url()
        self.token = config_manager.get_api_token()
        self.timeout = config_manager.get_timeout()
        self.ssl_verify = config_manager.get_ssl_verify()
        self.labels = config_manager.get_labels()
        
        # 验证必要的配置项
        if not self.base_url:
            raise ValueError("SOAR API地址未配置，请在管理后台系统配置中设置")
        if not self.token:
            raise ValueError("API Token未配置，请在管理后台系统配置中设置")
        
        # 调试信息：显示Token前几个字符
        logger.sync_debug(f"API配置: URL={self.base_url}, Token={self.token[:10]}..., SSL={self.ssl_verify}, Labels={self.labels}")
        
        # 临时禁用代理环境变量
        old_http_proxy = os.environ.pop('HTTP_PROXY', None)
        old_https_proxy = os.environ.pop('HTTPS_PROXY', None)
        
        # 配置HTTP客户端
        self.headers = {
            "hg-token": self.token,
            "Content-Type": "application/json"
        }
        
        # 创建异步HTTP客户端
        # httpx的verify参数：True(验证)，False(不验证)，或证书路径
        verify_setting = self.ssl_verify if self.ssl_verify is not False else False
        
        self.client = httpx.AsyncClient(
            headers=self.headers,
            verify=verify_setting,
            timeout=float(self.timeout)
        )
        
        # 恢复代理环境变量
        if old_http_proxy:
            os.environ['HTTP_PROXY'] = old_http_proxy
        if old_https_proxy:
            os.environ['HTTPS_PROXY'] = old_https_proxy
    
    async def get_all_playbooks(self) -> List[Dict[str, Any]]:
        """获取所有剧本列表，支持标签过滤"""
        url = urljoin(self.base_url, "/odp/core/v1/api/playbook/findAll")
        
        try:
            # 构建请求体，包含发布状态，如果有标签则添加标签过滤
            request_body = {
                "publishStatus": "ONLINE"
            }

            # 只有当标签列表不为空时才添加 labelList 参数
            if self.labels:
                request_body["labelList"] = [{"name": label} for label in self.labels]
            
            logger.sync_debug(f"剧本查询请求: URL={url}, Body={request_body}")
            
            # API需要POST请求并传递标签筛选条件
            response = await self.client.post(url, json=request_body)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != 200:
                raise Exception(f"API返回错误: {data.get('message', '未知错误')}")
            
            playbooks = data.get("result", [])
            logger.sync_success(f"获取剧本列表成功: {len(playbooks)} 个剧本 (标签: {', '.join(self.labels)})")
            return playbooks
            
        except Exception as e:
            logger.sync_error(f"获取剧本列表失败: {e}")
            raise
    
    async def get_playbook_params(self, playbook_id: int) -> List[PlaybookParam]:
        """获取单个剧本的参数"""
        url = urljoin(self.base_url, f"/api/playbook/param?playbookId={playbook_id}")
        
        try:
            response = await self.client.post(url)
            response.raise_for_status()
            
            data = response.json()
            if data.get("code") != 200:
                # 某些剧本可能没有参数，返回空列表
                return []
            
            result = data.get("result", [])
            params = []
            
            for item in result:
                # 计算参数是否必填：如果任何一个 paramConfig 的 required=true，则整个参数 required=true
                param_configs = item.get("paramConfigs", [])
                is_required = False
                
                for config in param_configs:
                    if config.get("required", False) is True:
                        is_required = True
                        break
                
                params.append(PlaybookParam(
                    cef_column=item.get("cefColumn", ""),
                    cef_desc=item.get("cefDesc", ""),
                    value_type=item.get("valueType", ""),
                    required=is_required
                ))
            
            return params
            
        except Exception as e:
            logger.sync_warning(f"获取剧本参数失败 {playbook_id}: {e}")
            return []  # 失败时返回空列表，不阻断同步
    
    async def get_all_apps(self) -> List[Dict[str, Any]]:
        """获取所有应用列表（分页获取）"""
        all_apps = []
        page = 0
        page_size = 100
        
        while True:
            try:
                url = urljoin(self.base_url, "/api/apps")
                params = {
                    "page": page,
                    "size": page_size
                }
                
                logger.debug(f"获取应用列表: page={page}, size={page_size}")
                response = await self.client.post(url, params=params, json={})
                response.raise_for_status()
                
                data = response.json()
                if data.get("code") != 200:
                    raise Exception(f"API返回错误: {data.get('message', '未知错误')}")
                
                result = data.get("result", {})
                apps = result.get("content", [])
                
                if not apps:
                    break
                
                all_apps.extend(apps)
                logger.debug(f"获取第 {page+1} 页应用: {len(apps)} 个")
                
                # 检查是否还有更多页
                if len(apps) < page_size or result.get("last", True):
                    break
                
                page += 1
                
            except Exception as e:
                logger.sync_error(f"获取应用列表失败 (page={page}): {e}")
                if page == 0:
                    raise  # 第一页失败则直接抛出异常
                else:
                    break  # 后续页失败则停止分页
        
        logger.sync_success(f"获取应用列表成功: {len(all_apps)} 个应用")
        return all_apps
    
    async def close(self):
        """关闭HTTP客户端"""
        await self.client.aclose()


class PlaybookSyncService:
    """剧本同步服务"""
    
    def __init__(self, db_manager: DatabaseManager, max_concurrent: int = 20):
        self.db_manager = db_manager
        self.max_concurrent = max_concurrent
        self.api_client = SOARAPIClient()
        
    async def sync_single_playbook(self, playbook_data: Dict[str, Any]) -> bool:
        """同步单个剧本"""
        try:
            playbook_id = playbook_data.get("id")
            if not playbook_id:
                return False
            
            # 获取剧本参数
            params = await self.api_client.get_playbook_params(playbook_id)
            
            # 解析时间字段
            create_time = None
            update_time = None
            remote_update_time = None
            
            if playbook_data.get("createTime"):
                try:
                    # 处理不同的时间格式
                    time_str = playbook_data["createTime"]
                    if isinstance(time_str, str):
                        if "T" in time_str:  # ISO格式
                            create_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        else:  # 本地格式 "2020-10-19 10:16:29"
                            create_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    else:
                        logger.sync_warning(f"createTime不是字符串 {playbook_data.get('id')}: {time_str}")
                except Exception as e:
                    logger.sync_warning(f"解析createTime失败 {playbook_data.get('id')}: {e}, 原值: {time_str}")
            
            if playbook_data.get("updateTime"):
                try:
                    # 处理不同的时间格式
                    time_str = playbook_data["updateTime"]
                    if isinstance(time_str, str):
                        if "T" in time_str:  # ISO格式
                            update_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                        else:  # 本地格式 "2021-02-10 09:34:45"
                            update_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        remote_update_time = update_time  # 使用updateTime作为远程更新时间
                    else:
                        logger.sync_warning(f"updateTime不是字符串 {playbook_data.get('id')}: {time_str}")
                except Exception as e:
                    logger.sync_warning(f"解析updateTime失败 {playbook_data.get('id')}: {e}, 原值: {time_str}")
            
            # 创建PlaybookData对象
            playbook = PlaybookData(
                id=playbook_id,
                name=playbook_data.get("name", ""),
                display_name=playbook_data.get("displayName"),
                playbook_category=playbook_data.get("playbookCategory"),
                description=playbook_data.get("description"),
                create_time=create_time,
                update_time=update_time,
                remote_update_time=remote_update_time,
                playbook_params=params
            )
            
            # 保存到数据库
            success = self.db_manager.save_playbook(playbook)
            if success:
                logger.debug(f"同步剧本成功: {playbook_id} - {playbook.name}")
            
            return success
            
        except Exception as e:
            logger.sync_error(f"同步剧本失败 {playbook_data.get('id', 'unknown')}: {e}")
            return False
    
    async def sync_playbooks_batch(self, playbooks: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量同步剧本（控制并发）"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def sync_with_limit(playbook_data):
            async with semaphore:
                return await self.sync_single_playbook(playbook_data)
        
        logger.sync_start(f"开始批量同步 {len(playbooks)} 个剧本，最大并发: {self.max_concurrent}")
        start_time = time.time()

        # 创建所有任务
        tasks = [sync_with_limit(playbook) for playbook in playbooks]

        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        ignored_count = sum(1 for result in results if result == "ignored")
        success_count = sum(1 for result in results if result is True or result == "ignored")  # 忽略也算成功
        failed_count = sum(1 for result in results if isinstance(result, Exception) or result is False)
        
        elapsed_time = time.time() - start_time
        
        logger.sync_success(f"批量同步完成: 成功 {success_count}, 忽略 {ignored_count}, 失败 {failed_count}, 耗时 {elapsed_time:.2f}秒")
        
        return {
            "total": len(playbooks),
            "success": success_count,
            "ignored": ignored_count,
            "failed": failed_count,
            "elapsed_time": elapsed_time
        }
    
    async def full_sync(self) -> Dict[str, Any]:
        """执行完整同步"""
        try:
            logger.sync_start("开始剧本完整同步...")
            
            # 初始化数据库
            self.db_manager.init_db()
            
            # 获取所有剧本
            playbooks = await self.api_client.get_all_playbooks()
            
            if not playbooks:
                return {"error": "未获取到剧本数据"}
            
            # 批量同步
            sync_result = await self.sync_playbooks_batch(playbooks)
            
            # 获取同步统计
            stats = self.db_manager.get_sync_stats()
            
            # 更新最后同步时间到系统配置
            self.db_manager.update_last_sync_time()

            result = {
                "sync_time": datetime.now().isoformat(),
                "source_count": len(playbooks),
                "sync_result": sync_result,
                "database_stats": stats
            }

            logger.sync_success("剧本完整同步完成!")
            return result
            
        except Exception as e:
            error_msg = f"剧本同步失败: {e}"
            logger.sync_error(error_msg)
            return {"error": error_msg}
        
        finally:
            await self.api_client.close()
    
    async def get_sync_status(self) -> Dict[str, Any]:
        """获取同步状态"""
        try:
            stats = self.db_manager.get_sync_stats()
            return {
                "status": "success",
                "data": stats
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }


class AppsSyncService:
    """应用同步服务"""
    
    def __init__(self, db_manager: DatabaseManager, max_concurrent: int = 10):
        self.db_manager = db_manager
        self.max_concurrent = max_concurrent
        self.api_client = SOARAPIClient()
    
    async def sync_single_app(self, app_data: Dict[str, Any]) -> bool:
        """同步单个应用"""
        try:
            app_id = app_data.get("id")
            if not app_id:
                return False
            
            
            # 解析时间字段
            update_time = None
            remote_update_time = None
            
            if app_data.get("updateTime"):
                try:
                    time_str = app_data["updateTime"]
                    if "T" in time_str:  # ISO格式
                        update_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                    else:  # 本地格式
                        update_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                    remote_update_time = update_time
                except Exception as e:
                    logger.sync_warning(f"解析updateTime失败 {app_id}: {e}")
            
            # 解析appAssetList
            app_asset_list = []
            if app_data.get("appAssetList"):
                app_asset_list = app_data["appAssetList"]
            
            # 创建AppData对象 - 直接使用API返回的字段
            try:
                app = AppData(**app_data)
            except Exception as validation_error:
                logger.sync_error(f"AppData验证失败 {app_id}: {validation_error}")
                return False
            
            # 保存应用到数据库（增量同步）
            app_updated = self.db_manager.save_app(app)
            
            if app_updated:
                # 解析并保存Actions
                actions_data = []
                for action_item in app_data.get("appActionList", []):
                    # 解析参数列表
                    parameter_variables = []
                    for param in action_item.get("parameterVariableList", []):
                        parameter_variables.append(ActionParam(
                            name=param.get("name", ""),
                            display_name=param.get("displayName"),
                            description=param.get("description"),
                            param_type=param.get("type"),
                            required=param.get("required", False),
                            default_value=param.get("defaultValue")
                        ))
                    
                    # 解析结果列表
                    result_variables = []
                    for result in action_item.get("resultVariableList", []):
                        result_variables.append(ActionResult(
                            name=result.get("name", ""),
                            display_name=result.get("displayName"),
                            description=result.get("description"),
                            result_type=result.get("type")
                        ))
                    
                    # 解析Action更新时间
                    action_update_time = None
                    if action_item.get("updateTime"):
                        try:
                            time_str = action_item["updateTime"]
                            if "T" in time_str:
                                action_update_time = datetime.fromisoformat(time_str.replace("Z", "+00:00"))
                            else:
                                action_update_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
                        except Exception as e:
                            logger.sync_warning(f"解析Action updateTime失败 {action_item.get('id')}: {e}")
                    
                    action = ActionData(
                        id=action_item.get("id"),
                        app_id=app_id,
                        name=action_item.get("name", ""),
                        display_name=action_item.get("displayName"),
                        description=action_item.get("description"),
                        action_type=action_item.get("actionType"),
                        classify=action_item.get("classify"),
                        logic_language=action_item.get("logicLanguage"),
                        parameter_variables=parameter_variables,
                        result_variables=result_variables,
                        update_time=action_update_time
                    )
                    actions_data.append(action)
                
                # 删除旧Actions并保存新的
                self.db_manager.delete_actions_by_app_id(app_id)
                if actions_data:
                    self.db_manager.batch_save_actions(actions_data)
                
                logger.debug(f"同步应用成功: {app_id} - {app.name} ({len(actions_data)} 个动作)")
                return True  # 成功更新
            else:
                return "ignored"  # 被跳过
            
        except Exception as e:
            logger.sync_error(f"同步应用失败 {app_data.get('id', 'unknown')}: {e}")
            return False
    
    async def sync_apps_batch(self, apps: List[Dict[str, Any]]) -> Dict[str, int]:
        """批量同步应用（控制并发）"""
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def sync_with_limit(app_data):
            async with semaphore:
                return await self.sync_single_app(app_data)
        
        logger.sync_start(f"开始批量同步 {len(apps)} 个应用，最大并发: {self.max_concurrent}")
        start_time = time.time()

        # 创建所有任务
        tasks = [sync_with_limit(app) for app in apps]

        # 执行所有任务
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 统计结果
        ignored_count = sum(1 for result in results if result == "ignored")
        success_count = sum(1 for result in results if result is True or result == "ignored")  # 忽略也算成功
        failed_count = sum(1 for result in results if isinstance(result, Exception) or result is False)
        
        elapsed_time = time.time() - start_time
        
        logger.sync_success(f"批量同步完成: 成功 {success_count}, 忽略 {ignored_count}, 失败 {failed_count}, 耗时 {elapsed_time:.2f}秒")
        
        return {
            "total": len(apps),
            "success": success_count,
            "ignored": ignored_count,
            "failed": failed_count,
            "elapsed_time": elapsed_time
        }
    
    async def full_sync(self) -> Dict[str, Any]:
        """执行完整同步"""
        try:
            logger.sync_start("开始应用完整同步...")
            
            # 获取所有应用
            apps = await self.api_client.get_all_apps()
            
            if not apps:
                return {"error": "未获取到应用数据"}
            
            # 批量同步
            sync_result = await self.sync_apps_batch(apps)
            
            # 获取同步统计
            stats = self.db_manager.get_apps_stats()

            # 更新最后同步时间到系统配置
            self.db_manager.update_last_sync_time()

            result = {
                "sync_time": datetime.now().isoformat(),
                "source_count": len(apps),
                "sync_result": sync_result,
                "database_stats": stats
            }

            logger.sync_success("应用完整同步完成!")
            return result
            
        except Exception as e:
            error_msg = f"应用同步失败: {e}"
            logger.sync_error(error_msg)
            return {"error": error_msg}
        
        finally:
            await self.api_client.close()


# 便捷函数
async def sync_playbooks() -> Dict[str, Any]:
    """执行剧本同步的便捷函数"""
    db_manager = DatabaseManager()
    sync_service = PlaybookSyncService(db_manager)
    return await sync_service.full_sync()


async def sync_apps() -> Dict[str, Any]:
    """执行应用同步的便捷函数"""
    db_manager = DatabaseManager()
    sync_service = AppsSyncService(db_manager)
    return await sync_service.full_sync()


if __name__ == "__main__":
    async def main():
        result = await sync_playbooks()
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    
    asyncio.run(main())