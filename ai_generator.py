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
        # 初始化数据库管理器
        self.db_manager = DatabaseManager()

        # 配置版本追踪（用于检测配置变化）
        self._config_id = None
        self._config_updated_at = None

        # 加载配置（数据库优先，环境变量兜底）
        self._load_config()

    def _load_config(self):
        """加载LLM配置（数据库优先，环境变量兜底）"""
        # 尝试从数据库读取配置
        db_config = self.db_manager.get_llm_config()

        if db_config and db_config.api_key:
            # 使用数据库配置
            api_key = db_config.api_key
            api_base = db_config.api_base_url or 'https://api.openai.com/v1'
            model = db_config.model_name or 'gpt-4o-mini'
            enable_thinking = db_config.enable_thinking
            use_stream = db_config.enable_stream
            # 记录配置版本
            self._config_id = db_config.id
            self._config_updated_at = db_config.updated_at
        else:
            # 回退到环境变量配置
            api_key = os.getenv('OPENAI_API_KEY')
            api_base = os.getenv('OPENAI_API_BASE_URL', 'https://api.openai.com/v1')
            model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
            # 读取enable_thinking配置,默认为False(禁用)
            enable_thinking = os.getenv('OPENAI_ENABLE_THINKING', 'false').lower() == 'true'
            # 读取stream配置,默认为False(某些模型如qwq-32b强制要求stream=True)
            use_stream = os.getenv('OPENAI_STREAM', 'false').lower() == 'true'
            self._config_id = None
            self._config_updated_at = None

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

    def _check_and_reload_config(self):
        """检查配置是否有更新，如有则重新加载"""
        db_config = self.db_manager.get_llm_config()
        if db_config:
            # 检查是否切换了配置或配置有更新
            if (db_config.id != self._config_id or
                db_config.updated_at != self._config_updated_at):
                self._load_config()
        elif self._config_id is not None:
            # 数据库配置被删除，重新加载（回退到环境变量）
            self._load_config()

    def reload_config(self):
        """重新加载配置（用于配置更新后立即生效）"""
        self._load_config()

    def _parse_json_response(self, result: str) -> Dict[str, Any]:
        """解析 AI 返回的 JSON 响应，处理各种格式问题

        Args:
            result: AI 返回的原始字符串

        Returns:
            解析后的 JSON 对象

        Raises:
            json.JSONDecodeError: 无法解析为有效 JSON
        """
        if not result or not result.strip():
            raise json.JSONDecodeError("Empty response", "", 0)

        result = result.strip()

        # 移除 markdown 代码块
        if result.startswith("```json"):
            result = result[7:]
        elif result.startswith("```"):
            result = result[3:]
        if result.endswith("```"):
            result = result[:-3]
        result = result.strip()

        # 尝试直接解析
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            pass

        # 尝试提取第一个完整的 JSON 对象
        start = result.find('{')
        if start != -1:
            depth = 0
            in_string = False
            escape_next = False
            for i, char in enumerate(result[start:], start):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\' and in_string:
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        try:
                            return json.loads(result[start:i+1])
                        except json.JSONDecodeError:
                            break

        # 最后尝试：直接解析（会抛出原始错误）
        return json.loads(result)

    def generate_response(self, app_info: Dict[str, Any], action: str, parameters: Dict[str, Any], action_def: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成模拟响应

        Args:
            app_info: 应用信息字典，包含 category, name, display_name, description
            action: 动作名称
            parameters: 用户调用参数
            action_def: 动作完整定义
        """

        # 检查配置是否有更新（支持多进程场景下的配置热切换）
        self._check_and_reload_config()

        # 提取应用信息
        app_name = app_info.get('display_name', app_info.get('name', 'Unknown'))

        # 如果AI未启用，返回默认响应
        if not self.enabled:
            return self._generate_default_response(app_name, action, parameters)

        try:
            # 从数据库获取响应生成提示词模板
            prompt_template = self.db_manager.get_prompt_template('response_simulation')
            if prompt_template:
                # 准备变量替换
                ai_notes = app_info.get('ai_notes', '')
                # 如果有 ai_notes，保留原文；如果没有，使用默认提示
                if not ai_notes or ai_notes.strip() == '':
                    ai_notes = '无特殊要求'

                variables = {
                    'app_category': app_info.get('category', ''),
                    'app_name': app_info.get('name', ''),
                    'app_display_name': app_info.get('display_name', ''),
                    'app_description': app_info.get('description', ''),
                    'ai_notes': ai_notes,
                    'action': action,
                    'parameters': json.dumps(parameters, ensure_ascii=False, indent=2),
                    'action_definition': json.dumps(action_def, ensure_ascii=False, indent=2) if action_def else 'null'
                }

                # 使用变量替换生成最终的prompt
                prompt = prompt_template.template.format(**variables)
            else:
                # 如果没有找到模板，使用原来的硬编码提示词（包含应用完整信息）
                action_def_str = json.dumps(action_def, ensure_ascii=False, indent=2) if action_def else 'null'
                ai_notes = app_info.get('ai_notes', '')
                if not ai_notes or ai_notes.strip() == '':
                    ai_notes = '无特殊要求'

                prompt = f"""你是{app_info.get('display_name', app_name)}系统的模拟器。

# 应用信息
- 分类: {app_info.get('category', 'Unknown')}
- 名称: {app_info.get('name', 'Unknown')}
- 显示名称: {app_info.get('display_name', app_name)}
- 描述: {app_info.get('description', '无描述')}

# 用户特殊要求
{ai_notes}

# 调用信息
用户调用了 {action} 操作，参数如下：
{json.dumps(parameters, ensure_ascii=False, indent=2)}

# 动作完整定义
{action_def_str}

# 任务要求
请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态
4. 考虑应用描述中的业务场景
5. 考虑动作定义中的描述和参数要求
6. 如果用户提供了特殊要求，严格遵守这些要求

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
                        max_tokens=4096,
                        stream=True,
                        # 禁用thinking模式,防止思考过程影响JSON输出格式
                        extra_body={"enable_thinking": self.enable_thinking}
                    )

                    # 收集stream响应
                    result = ""
                    reasoning = ""
                    for chunk in response:
                        if chunk.choices and len(chunk.choices) > 0:
                            delta = chunk.choices[0].delta
                            if hasattr(delta, 'content') and delta.content:
                                result += delta.content
                            # 智谱等模型的思考内容
                            if hasattr(delta, 'reasoning_content') and delta.reasoning_content:
                                reasoning += delta.reasoning_content
                    # 如果 content 为空但有 reasoning，使用 reasoning
                    if not result and reasoning:
                        result = reasoning

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
                        max_tokens=4096,
                        # 禁用thinking模式,防止思考过程影响JSON输出格式
                        extra_body={"enable_thinking": self.enable_thinking}
                    )

                    duration = time.time() - start_time

                    # 解析响应 - 优先使用 content，如果为空则尝试 reasoning_content（智谱等模型）
                    message = response.choices[0].message
                    result = message.content or ""
                    if not result and hasattr(message, 'reasoning_content') and message.reasoning_content:
                        result = message.reasoning_content

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

                # 使用增强的 JSON 解析方法
                return self._parse_json_response(result)

            except Exception as e:
                duration = time.time() - start_time
                error_msg = str(e)

                # 检测空响应问题，可能需要启用 stream 模式
                hint = ""
                if "Empty response" in error_msg or "column 1" in error_msg:
                    hint = f" (模型 {self.model} 可能需要启用 Stream 模式)"

                # 记录失败的 AI 调用
                mcp_logger.log_ai_call(
                    provider="OpenAI",
                    model=self.model,
                    prompt=prompt,
                    success=False,
                    error=error_msg + hint,
                    duration=duration
                )

                # 返回错误响应而不是抛出异常
                return {
                    "success": False,
                    "error": "AI generation failed",
                    "error_detail": error_msg + hint,
                    "code": 500,
                    "app": app_name,
                    "action": action,
                    "model": self.model,
                    "stream_enabled": self.use_stream,
                    "fallback": "Consider enabling Stream mode for reasoning models like deepseek-reasoner, qwq-32b"
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