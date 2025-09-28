#!/usr/bin/env python3
"""
测试脚本：查询所有可用剧本
获取OctoMation平台的剧本列表，并将结果保存到JSON文件
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

def get_playbooks(config):
    """
    获取所有可用剧本（非草稿状态）
    使用 findAll 接口一次性获取所有在线剧本
    """
    url = f"{config['api_url']}/odp/core/v1/api/playbook/findAll"
    
    headers = {
        "hg-token": config["api_token"],
        "Content-Type": "application/json"
    }
    
    # 请求参数 - 只获取已发布的剧本
    params = {
        "publishStatus": "ONLINE"
    }
    
    try:
        print(f"正在请求: {url}")
        print(f"请求参数: {params}")
        print(f"SSL验证: {config['ssl_verify']}")
        
        # 直接使用requests.post，完全禁用SSL验证
        response = requests.post(
            url,
            json=params,
            headers=headers,
            verify=False,
            timeout=30
        )
        
        print(f"响应状态码: {response.status_code}")
        print(f"响应头: {dict(response.headers)}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"API响应结构: {list(response_data.keys())}")
            if "result" in response_data:
                # 检查result的结构
                result = response_data["result"]
                if isinstance(result, list):
                    print(f"result是数组，包含 {len(result)} 个剧本")
                else:
                    print(f"result字段结构: {list(result.keys())}")
            return response_data
        else:
            print(f"请求失败: {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
        return None

def get_all_playbooks(config):
    """
    获取所有已发布的剧本（使用findAll接口）
    """
    print(f"\n--- 获取所有已发布剧本 ---")
    result = get_playbooks(config)
    
    if not result:
        print("获取剧本失败")
        return {
            "total_count": 0,
            "playbooks": [],
            "metadata": {
                "source": "OctoMation API",
                "endpoint": "/odp/core/v1/api/playbook/findAll",
                "timestamp": str(Path().cwd())
            }
        }
        
    # 检查响应格式
    if "result" in result:
        playbooks = result.get("result", [])
        print(f"获取到 {len(playbooks)} 个已发布剧本")
        
        return {
            "total_count": len(playbooks),
            "playbooks": playbooks,
            "metadata": {
                "source": "OctoMation API",
                "endpoint": "/odp/core/v1/api/playbook/findAll",
                "timestamp": str(Path().cwd())
            }
        }
    else:
        # 如果响应格式不符合预期，直接返回
        print("响应格式不符合预期，直接保存结果")
        return result

def save_to_json(data, filename="soar-playbooks.json"):
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
    print("=== OctoMation 剧本查询测试 ===\n")
    
    try:
        # 加载配置
        config = load_env_config()
        print(f"API URL: {config['api_url']}")
        print(f"SSL验证: {config['ssl_verify']}")
        print(f"Token前缀: {config['api_token'][:20]}...")
        
        # 获取剧本数据
        playbooks_data = get_all_playbooks(config)
        
        if playbooks_data:
            # 保存到JSON文件
            if save_to_json(playbooks_data):
                print(f"\n✅ 成功获取并保存剧本数据")
                if isinstance(playbooks_data, dict) and "total_count" in playbooks_data:
                    print(f"📊 总计获取 {playbooks_data['total_count']} 个剧本")
            else:
                print("❌ 保存文件失败")
        else:
            print("❌ 未获取到剧本数据")
            
    except Exception as e:
        print(f"❌ 程序执行异常: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()