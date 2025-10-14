#!/usr/bin/env python3
"""
AI响应生成器
"""

import os
import json
import random
import time
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from models import DatabaseManager
from logger_utils import mcp_logger

load_dotenv()

class AIResponseGenerator:
    """AI响应生成器"""

    def __init__(self):
        api_key = os.getenv('OPENAI_API_KEY')
        api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
        model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        # 读取enable_thinking配置,默认为False(禁用)
        enable_thinking = os.getenv('OPENAI_ENABLE_THINKING', 'false').lower() == 'true'
        # 读取stream配置,默认为False(某些模型如qwq-32b强制要求stream=True)
        use_stream = os.getenv('OPENAI_STREAM', 'false').lower() == 'true'

        if api_key:
            self.client = OpenAI(api_key=api_key, base_url=api_base)
            self.model = model
            self.enabled = True
            self.enable_thinking = enable_thinking
            self.use_stream = use_stream
        else:
            self.client = None
            self.enabled = False
            self.enable_thinking = False
            self.use_stream = False

        # 初始化数据库管理器
        self.db_manager = DatabaseManager()

    def generate_response(self, app_name: str, action: str, parameters: Dict[str, Any], action_def: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
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
                    'parameters': json.dumps(parameters, ensure_ascii=False, indent=2),
                    'action_definition': json.dumps(action_def, ensure_ascii=False, indent=2) if action_def else 'null'
                }

                # 使用变量替换生成最终的prompt
                prompt = prompt_template.template.format(**variables)
            else:
                # 如果没有找到模板，使用原来的硬编码提示词（包含动作定义）
                action_def_str = json.dumps(action_def, ensure_ascii=False, indent=2) if action_def else 'null'
                prompt = f"""你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{json.dumps(parameters, ensure_ascii=False, indent=2)}

动作完整定义：
{action_def_str}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态
4. 考虑参数的描述和类型要求

直接返回JSON，不要任何其他说明文字。"""

            start_time = time.time()

            try:
                if self.use_stream:
                    # Stream模式处理
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "你是一个API响应模拟器,返回符合规范的JSON数据。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000,
                        stream=True,
                        # 禁用thinking模式,防止思考过程影响JSON输出格式
                        extra_body={"enable_thinking": self.enable_thinking}
                    )

                    # 收集stream响应
                    result = ""
                    for chunk in response:
                        if chunk.choices[0].delta.content:
                            result += chunk.choices[0].delta.content

                    duration = time.time() - start_time
                else:
                    # 非Stream模式处理
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "你是一个API响应模拟器,返回符合规范的JSON数据。"},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        max_tokens=1000,
                        # 禁用thinking模式,防止思考过程影响JSON输出格式
                        extra_body={"enable_thinking": self.enable_thinking}
                    )

                    duration = time.time() - start_time

                    # 解析响应
                    result = response.choices[0].message.content

                # 记录成功的 AI 调用
                # Stream模式下无法获取usage信息
                usage = None
                if not self.use_stream and hasattr(response, 'usage') and response.usage:
                    usage = {
                        'prompt_tokens': response.usage.prompt_tokens,
                        'completion_tokens': response.usage.completion_tokens,
                        'total_tokens': response.usage.total_tokens
                    }

                mcp_logger.log_ai_call(
                    provider="OpenAI",
                    model=self.model,
                    prompt=prompt,
                    response=result,
                    success=True,
                    duration=duration,
                    usage=usage
                )

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
                duration = time.time() - start_time
                error_msg = str(e)

                # 记录失败的 AI 调用
                mcp_logger.log_ai_call(
                    provider="OpenAI",
                    model=self.model,
                    prompt=prompt,
                    success=False,
                    error=error_msg,
                    duration=duration
                )

                # 返回错误响应而不是抛出异常
                return {
                    "success": False,
                    "error": "AI generation failed",
                    "error_detail": error_msg,
                    "code": 500,
                    "app": app_name,
                    "action": action,
                    "fallback": "Consider using default response or check AI configuration"
                }

        except Exception as e:
            mcp_logger.error(f"AI generation failed: {e}", exc_info=True)
            # 返回错误响应而不是默认成功响应
            return {
                "success": False,
                "error": "AI generation failed",
                "error_detail": str(e),
                "code": 500,
                "app": app_name,
                "action": action,
                "fallback": "Consider using default response or check AI configuration"
            }

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