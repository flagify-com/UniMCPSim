#!/usr/bin/env python3
"""
BBScan 扫描器提示词模板示例演示
展示当用户请求 http://127.0.0.1:8080/Scanner/BBScan?token=xxx 时
系统如何处理提示词模板和变量
"""

import json

def demonstrate_prompt_template():
    """演示提示词模板的工作流程"""

    print("=" * 60)
    print("BBScan 扫描器 - 提示词模板工作流程演示")
    print("=" * 60)
    print()

    # 1. 用户发起请求
    print("【步骤 1: 用户请求】")
    print("URL: http://127.0.0.1:8080/Scanner/BBScan?token=0eb0d5b1-4597-4cc9-a9df-a750455d34fa")
    print("Method: POST")
    print("Body:")
    request_body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "scan_url",
            "arguments": {
                "target_url": "https://example.com",
                "scan_type": "full",
                "max_depth": 3,
                "follow_redirects": True
            }
        },
        "id": 2
    }
    print(json.dumps(request_body, ensure_ascii=False, indent=2))
    print()

    # 2. 系统从数据库获取应用信息
    print("【步骤 2: 数据库查询】")
    print("系统执行以下操作：")
    print("1. 验证 Token: 0eb0d5b1-4597-4cc9-a9df-a750455d34fa")
    print("2. 获取应用: Scanner/BBScan")
    print("3. 获取应用定义：")

    app_definition = {
        "category": "Scanner",
        "name": "BBScan",
        "display_name": "BBScan网站扫描器",
        "description": "基于Python的网站目录和文件扫描工具",
        "template": {
            "actions": [
                {
                    "name": "scan_url",
                    "display_name": "扫描URL",
                    "description": "对目标URL进行目录和文件扫描",
                    "parameters": [
                        {
                            "key": "target_url",
                            "type": "String",
                            "required": True,
                            "description": "要扫描的目标URL"
                        },
                        {
                            "key": "scan_type",
                            "type": "String",
                            "required": False,
                            "default": "basic",
                            "options": ["basic", "full", "custom"],
                            "description": "扫描类型"
                        },
                        {
                            "key": "max_depth",
                            "type": "Integer",
                            "required": False,
                            "default": 2,
                            "description": "扫描深度"
                        },
                        {
                            "key": "follow_redirects",
                            "type": "Boolean",
                            "required": False,
                            "default": False,
                            "description": "是否跟随重定向"
                        }
                    ]
                }
            ]
        }
    }
    print(json.dumps(app_definition, ensure_ascii=False, indent=2))
    print()

    # 3. 系统获取响应模拟提示词模板
    print("【步骤 3: 获取提示词模板】")
    print("从数据库获取 'response_simulation' 模板：")
    print()

    # 这是存储在数据库中的模板
    template_raw = """你是{app_name}系统的模拟器。用户调用了{action}操作，参数如下：
{parameters}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。"""

    print("原始模板内容:")
    print("-" * 40)
    print(template_raw)
    print("-" * 40)
    print()

    # 4. 变量替换
    print("【步骤 4: 模板变量替换】")
    print("系统准备以下变量：")

    template_variables = {
        "app_name": "BBScan网站扫描器",  # 来自 app.display_name
        "action": "scan_url",             # 来自请求的 tool name
        "parameters": json.dumps({        # 来自请求的 arguments
            "target_url": "https://example.com",
            "scan_type": "full",
            "max_depth": 3,
            "follow_redirects": True
        }, ensure_ascii=False, indent=2)
    }

    print(json.dumps(template_variables, ensure_ascii=False, indent=2))
    print()

    # 5. 生成最终提示词
    print("【步骤 5: 生成最终提示词】")
    print("替换后的完整提示词：")
    print("-" * 40)

    final_prompt = template_raw.format(**template_variables)
    print(final_prompt)
    print("-" * 40)
    print()

    # 6. 发送给 OpenAI
    print("【步骤 6: 发送给 OpenAI API】")
    print("系统将以下消息发送给 OpenAI：")

    openai_messages = [
        {
            "role": "system",
            "content": "你是一个API响应模拟器，返回符合规范的JSON数据。"
        },
        {
            "role": "user",
            "content": final_prompt
        }
    ]

    print("Messages:")
    print(json.dumps(openai_messages, ensure_ascii=False, indent=2))
    print()
    print("OpenAI 参数:")
    print(f"- Model: gpt-4o-mini (或配置的模型)")
    print(f"- Temperature: 0.7")
    print(f"- Max Tokens: 1000")
    print()

    # 7. 模拟 AI 响应
    print("【步骤 7: AI 生成的模拟响应】")
    print("OpenAI 返回的模拟响应示例：")
    print("-" * 40)

    simulated_response = {
        "success": True,
        "scan_id": "scan_20240930_154823",
        "target_url": "https://example.com",
        "scan_type": "full",
        "status": "completed",
        "start_time": "2024-09-30T15:48:23Z",
        "end_time": "2024-09-30T15:49:45Z",
        "duration_seconds": 82,
        "statistics": {
            "total_requests": 453,
            "successful_requests": 412,
            "failed_requests": 41,
            "directories_found": 28,
            "files_found": 156,
            "scan_depth": 3
        },
        "vulnerabilities": {
            "high": 2,
            "medium": 5,
            "low": 13,
            "info": 27
        },
        "interesting_findings": [
            {
                "path": "/admin/",
                "status_code": 401,
                "type": "admin_panel",
                "severity": "high",
                "description": "发现管理后台入口，需要认证"
            },
            {
                "path": "/backup.sql",
                "status_code": 200,
                "type": "database_backup",
                "severity": "high",
                "size_bytes": 1048576,
                "description": "发现数据库备份文件，可能包含敏感信息"
            },
            {
                "path": "/.git/config",
                "status_code": 200,
                "type": "version_control",
                "severity": "medium",
                "description": "Git配置文件暴露，可能泄露仓库信息"
            },
            {
                "path": "/phpinfo.php",
                "status_code": 200,
                "type": "information_disclosure",
                "severity": "medium",
                "description": "PHP信息页面暴露，包含服务器配置信息"
            },
            {
                "path": "/robots.txt",
                "status_code": 200,
                "type": "information",
                "severity": "info",
                "description": "发现robots.txt文件"
            }
        ],
        "common_files": [
            {"path": "/index.html", "status": 200, "size": 15234},
            {"path": "/favicon.ico", "status": 200, "size": 4286},
            {"path": "/sitemap.xml", "status": 200, "size": 8912},
            {"path": "/robots.txt", "status": 200, "size": 256}
        ],
        "directories": [
            {"path": "/css/", "status": 200, "files_count": 12},
            {"path": "/js/", "status": 200, "files_count": 23},
            {"path": "/images/", "status": 200, "files_count": 87},
            {"path": "/api/", "status": 401, "requires_auth": True},
            {"path": "/admin/", "status": 401, "requires_auth": True}
        ],
        "recommendations": [
            "移除或限制访问管理后台 /admin/",
            "删除数据库备份文件 /backup.sql",
            "移除 .git 目录，避免版本控制信息泄露",
            "禁用或移除 phpinfo.php 文件",
            "配置适当的访问控制策略"
        ],
        "scan_config": {
            "max_depth": 3,
            "follow_redirects": True,
            "user_agent": "BBScan/1.0",
            "threads": 10,
            "timeout": 10
        }
    }

    print(json.dumps(simulated_response, ensure_ascii=False, indent=2))
    print("-" * 40)
    print()

    # 8. 返回给用户
    print("【步骤 8: 返回给用户】")
    print("最终的 MCP 响应：")

    final_mcp_response = {
        "jsonrpc": "2.0",
        "id": 2,
        "result": {
            "content": [{
                "type": "text",
                "text": json.dumps(simulated_response, ensure_ascii=False, indent=2)
            }]
        }
    }

    print(json.dumps(final_mcp_response, ensure_ascii=False, indent=2))
    print()

    # 总结
    print("=" * 60)
    print("【工作流程总结】")
    print("=" * 60)
    print("""
1. 用户请求 -> 解析路径（Scanner/BBScan）和动作（scan_url）
2. 验证 Token -> 检查权限
3. 获取应用定义 -> 从数据库读取应用模板
4. 获取提示词模板 -> 从 prompt_templates 表获取 'response_simulation' 模板
5. 准备变量 -> app_name, action, parameters
6. 模板替换 -> 使用 Python 的 format() 方法
7. 调用 OpenAI -> 生成模拟响应
8. 返回结果 -> 包装成 MCP 格式返回

关键信息：
- 模板变量：{app_name}, {action}, {parameters}
- 模板存储：数据库 prompt_templates 表
- AI 模型：通过 .env 配置（默认 gpt-4o-mini）
- 响应格式：纯 JSON，由 AI 根据应用类型智能生成
""")

if __name__ == "__main__":
    demonstrate_prompt_template()