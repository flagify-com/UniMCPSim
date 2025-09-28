#!/usr/bin/env python3
"""
Debug script to test action generation
"""

import os
import sys
import json
import openai
from dotenv import load_dotenv
from models import DatabaseManager

# Load environment variables from .env file
load_dotenv()

def test_action_generation():
    """测试动作生成功能"""

    # 初始化数据库管理器
    db_manager = DatabaseManager()

    # 获取提示词模板
    prompt_template = db_manager.get_prompt_template('action_generation')
    if not prompt_template:
        print("ERROR: action_generation template not found")
        return

    print(f"Template found: {prompt_template.name}")
    print(f"Template content length: {len(prompt_template.template)}")

    # 准备测试数据
    category = "Security"
    name = "firewall-manager"
    display_name = "防火墙管理器"
    description = "专业的网络防火墙管理工具"
    prompt = "需要实现以下功能：1. 查询防火墙健康状态 2. 封禁IP地址 3. 解封IP地址 4. 查询IP封禁状态"

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
    print(f"Generated user prompt length: {len(user_prompt)}")
    print("=== User Prompt Preview ===")
    print(user_prompt[:500] + "..." if len(user_prompt) > 500 else user_prompt)
    print("=== End Prompt Preview ===")

    # 从环境变量读取OpenAI配置
    api_key = os.getenv('OPENAI_API_KEY')
    model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
    api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')

    print(f"API Key: {'*' * 20 + api_key[-10:] if api_key else 'NOT SET'}")
    print(f"Model: {model}")
    print(f"API Base: {api_base}")

    if not api_key:
        print("ERROR: OPENAI_API_KEY not configured")
        return

    try:
        # 配置OpenAI客户端
        client = openai.OpenAI(
            api_key=api_key,
            base_url=api_base
        )

        print("Making API call...")

        # 调用OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "你是一个专业的API动作定义生成器，返回符合规范的JSON格式数据。"},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )

        print("API call successful!")

        # 解析返回结果
        content = response.choices[0].message.content.strip()
        print(f"Raw response length: {len(content)}")
        print("=== Raw API Response ===")
        print(repr(content[:1000]))  # Use repr to see escape characters
        print("=== End Raw Response ===")

        # 尝试解析JSON
        try:
            actions = json.loads(content)
            print("JSON parsing successful!")
            print(f"Number of actions: {len(actions) if isinstance(actions, list) else 'Not a list'}")
            return actions
        except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Error at position: {e.pos}")
            print(f"Error context: {repr(content[max(0, e.pos-50):e.pos+50])}")

            # 尝试清理并重试
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            if content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]

            print("=== Cleaned Content ===")
            print(repr(content[:1000]))
            print("=== End Cleaned Content ===")

            try:
                actions = json.loads(content.strip())
                print("JSON parsing successful after cleaning!")
                return actions
            except json.JSONDecodeError as e2:
                print(f"JSON parsing failed even after cleaning: {e2}")
                print(f"Error at position: {e2.pos}")
                print(f"Error context: {repr(content[max(0, e2.pos-50):e2.pos+50])}")
                raise Exception(f"AI返回的JSON格式不正确: {e2}")

    except Exception as e:
        print(f"Error: {e}")
        raise e

if __name__ == "__main__":
    test_action_generation()