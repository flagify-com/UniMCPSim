#!/usr/bin/env python3
"""
AI响应生成器
"""

import os
import json
import random
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from models import DatabaseManager

load_dotenv()

class AIResponseGenerator:
    """AI响应生成器"""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.model = model
            self.enabled = True
        else:
            self.client = None
            self.enabled = False

        # 初始化数据库管理器
        self.db_manager = DatabaseManager()

    def generate_response(self, app_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """生成模拟响应"""

        # 如果AI未启用，返回默认响应
        if not self.enabled:
            return self._generate_default_response(app_name, action, parameters)

        try:
            # 从数据库获取响应生成提示词模板
            prompt_template = self.db_manager.get_prompt_template('response_simulation')
            if prompt_template:
                # 准备变量替换
                variables = {
                    'app_name': app_name,
                    'action': action,
                    'parameters': json.dumps(parameters, ensure_ascii=False, indent=2)
                }

                # 使用变量替换生成最终的prompt
                prompt = prompt_template.template.format(**variables)
            else:
                # 如果没有找到模板，使用原来的硬编码提示词
                prompt = f"""你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{json.dumps(parameters, ensure_ascii=False, indent=2)}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个API响应模拟器，返回符合规范的JSON数据。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )

            # 解析响应
            result = response.choices[0].message.content
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # 如果解析失败，清理并重试
                result = result.strip()
                if result.startswith("```json"):
                    result = result[7:]
                if result.endswith("```"):
                    result = result[:-3]
                return json.loads(result.strip())

        except Exception as e:
            print(f"AI generation failed: {e}")
            return self._generate_default_response(app_name, action, parameters)

    def _generate_default_response(self, app_name: str, action: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """生成默认响应"""

        # 默认响应模板库
        templates = {
            "send_message": {
                "success": True,
                "message_id": f"msg_{random.randint(100000, 999999)}",
                "timestamp": "2024-01-01T00:00:00Z",
                "status": "delivered"
            },
            "check_ip": {
                "ip": parameters.get("ip", "0.0.0.0"),
                "reputation": random.choice(["clean", "suspicious", "malicious"]),
                "score": random.randint(0, 100),
                "country": random.choice(["US", "CN", "RU", "UK", "JP"]),
                "detections": random.randint(0, 10)
            },
            "create_ticket": {
                "success": True,
                "ticket_id": f"TICKET-{random.randint(1000, 9999)}",
                "status": "open",
                "priority": parameters.get("priority", "medium"),
                "assigned_to": "system"
            },
            "execute_command": {
                "success": True,
                "output": f"Command executed: {parameters.get('command', 'unknown')}",
                "return_code": 0
            },
            "get_status": {
                "status": random.choice(["online", "offline", "maintenance"]),
                "uptime": f"{random.randint(0, 365)}d {random.randint(0, 23)}h {random.randint(0, 59)}m",
                "connections": random.randint(0, 1000),
                "cpu_usage": f"{random.randint(0, 100)}%",
                "memory_usage": f"{random.randint(0, 100)}%"
            }
        }

        # 根据动作名称选择模板
        for key in templates:
            if key in action.lower():
                response = templates[key].copy()
                response["app"] = app_name
                response["action"] = action
                return response

        # 默认成功响应
        return {
            "success": True,
            "app": app_name,
            "action": action,
            "data": parameters,
            "message": f"Action {action} completed successfully"
        }


# 全局生成器实例
ai_generator = AIResponseGenerator()