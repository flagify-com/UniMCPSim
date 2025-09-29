#!/usr/bin/env python3
"""
测试脚本：查询所有可用动作和应用
获取OctoMation平台的动作列表，并将结果保存到JSON文件
"""

import os
import sys
import json
import requests
import urllib3
import ssl
from pathlib import Path
from dotenv import load_dotenv

# 禁用SSL警告（因为SSL_VERIFY=0）
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 更彻底地禁用SSL验证
ssl._create_default_https_context = ssl._create_unverified_context

def load_env_config():
    """加载环境配置"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent
    env_path = project_root / ".env"
    
    # 加载.env文件
    load_dotenv(env_path)
    
    config = {
        "api_url": os.getenv("API_URL"),
        "api_token": os.getenv("API_TOKEN"),
        "ssl_verify": os.getenv("SSL_VERIFY", "1").lower() in ("1", "true", "yes")
    }
    
    # 验证必需的配置
    if not config["api_url"]:
        raise ValueError("API_URL 未配置")
    if not config["api_token"]:
        raise ValueError("API_TOKEN 未配置")
    
    return config

def get_applications(config):
    """
    获取所有应用列表
    根据API文档，查询应用的接口是 POST /api/apps
    """
    url = f"{config['api_url']}/api/apps"
    
    headers = {
        "hg-token": config["api_token"],
        "Content-Type": "application/json"
    }
    
    # 请求参数 - 获取大量数据
    params = {
        "page": 1,
        "size": 1000  # 设置较大的页面大小
    }
    
    try:
        print(f"正在请求应用列表: {url}")
        print(f"请求参数: {params}")
        
        response = requests.post(
            url,
            json=params,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"API响应结构: {list(response_data.keys())}")
            if "result" in response_data:
                result = response_data["result"]
                if isinstance(result, dict) and "content" in result:
                    apps = result["content"]
                    print(f"获取到 {len(apps)} 个应用")
                else:
                    print(f"result结构: {list(result.keys()) if isinstance(result, dict) else type(result)}")
            return response_data
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

def organize_actions_by_app(applications_data):
    """
    按应用整合动作数据
    """
    organized_data = {
        "total_applications": 0,
        "total_actions": 0,
        "applications": []
    }
    
    if not applications_data or "result" not in applications_data:
        return organized_data
    
    result = applications_data["result"]
    if isinstance(result, dict) and "content" in result:
        apps = result["content"]
    else:
        apps = result if isinstance(result, list) else []
    
    organized_data["total_applications"] = len(apps)
    
    for app in apps:
        app_info = {
            "id": app.get("id"),
            "name": app.get("name"),
            "displayName": app.get("displayName"),
            "category": app.get("category"),
            "vendor": app.get("vendor"),
            "description": app.get("description"),
            "status": app.get("status"),
            "actions": []
        }
        
        # 从应用中提取动作列表
        if "appActionList" in app and app["appActionList"]:
            for action in app["appActionList"]:
                action_info = {
                    "id": action.get("id"),
                    "name": action.get("name"),
                    "displayName": action.get("displayName"),
                    "description": action.get("description"),
                    "category": action.get("category"),
                    "parameterList": action.get("parameterVariableList", [])
                }
                app_info["actions"].append(action_info)
                organized_data["total_actions"] += 1
        
        # 检查是否有资产配置
        if "assetList" in app and app["assetList"]:
            app_info["assets"] = []
            for asset in app["assetList"]:
                asset_info = {
                    "id": asset.get("id"),
                    "name": asset.get("name"),
                    "config": asset.get("config"),
                    "isDefault": len(app_info["assets"]) == 0  # 第一个设为默认
                }
                app_info["assets"].append(asset_info)
        
        organized_data["applications"].append(app_info)
    
    return organized_data

def save_to_json(data, filename="soar-actions.json"):
    """保存数据到JSON文件"""
    project_root = Path(__file__).parent.parent
    output_path = project_root / filename
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"\n数据已保存到: {output_path}")
        return True
    except Exception as e:
        print(f"保存文件失败: {e}")
        return False

def main():
    """主函数"""
    print("=== OctoMation 动作和应用查询测试 ===\n")
    
    try:
        # 加载配置
        config = load_env_config()
        print(f"API URL: {config['api_url']}")
        print(f"SSL验证: {config['ssl_verify']}")
        print(f"Token前缀: {config['api_token'][:20]}...")
        
        # 获取应用和动作数据
        print("\n--- 获取应用和动作列表 ---")
        applications_data = get_applications(config)
        
        if applications_data:
            # 按应用整合动作数据
            organized_data = organize_actions_by_app(applications_data)
            
            # 添加原始数据用于调试
            final_data = {
                "summary": {
                    "total_applications": organized_data["total_applications"],
                    "total_actions": organized_data["total_actions"]
                },
                "organized_data": organized_data,
                "raw_data": applications_data,
                "metadata": {
                    "source": "OctoMation API",
                    "endpoint": "/api/apps",
                    "timestamp": str(Path().cwd())
                }
            }
            
            # 保存到JSON文件
            if save_to_json(final_data):
                print(f"✅ 成功获取并保存数据")
                print(f"📊 总计 {organized_data['total_applications']} 个应用")
                print(f"📊 总计 {organized_data['total_actions']} 个动作")
            else:
                print("❌ 保存文件失败")
        else:
            print("❌ 未获取到应用数据")
            
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()