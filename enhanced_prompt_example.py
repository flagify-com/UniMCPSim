#!/usr/bin/env python3
"""
展示增强版提示词模板的完整工作流程
包含动作定义的详细信息
"""

import json

def demonstrate_enhanced_prompt():
    """演示增强版提示词模板"""

    print("=" * 70)
    print("增强版提示词模板系统演示")
    print("=" * 70)
    print()

    # 1. 用户请求
    print("【步骤 1: 用户请求】")
    print("URL: http://127.0.0.1:8080/Scanner/BBScan?token=xxx")

    request_body = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "scan_url",
            "arguments": {
                "target_url": "https://target-app.com",
                "scan_type": "full",
                "max_depth": 3,
                "follow_redirects": True,
                "threads": 15
            }
        },
        "id": 2
    }
    print("请求体:")
    print(json.dumps(request_body, ensure_ascii=False, indent=2))
    print()

    # 2. 系统获取动作定义
    print("【步骤 2: 系统获取动作完整定义】")
    action_definition = {
        "name": "scan_url",
        "display_name": "扫描URL",
        "description": "对目标URL进行目录和文件扫描，发现潜在的安全问题",
        "parameters": [
            {
                "key": "target_url",
                "type": "String",
                "required": True,
                "description": "要扫描的目标URL，必须是有效的HTTP/HTTPS地址"
            },
            {
                "key": "scan_type",
                "type": "String",
                "required": False,
                "default": "basic",
                "options": ["basic", "full", "custom"],
                "description": "扫描类型：basic(基础扫描，快速检查常见路径)、full(完整扫描，深度检查)、custom(自定义扫描)"
            },
            {
                "key": "max_depth",
                "type": "Integer",
                "required": False,
                "default": 2,
                "description": "扫描深度，控制目录遍历的层数，范围1-10"
            },
            {
                "key": "follow_redirects",
                "type": "Boolean",
                "required": False,
                "default": False,
                "description": "是否跟随HTTP重定向，可能会增加扫描时间"
            },
            {
                "key": "threads",
                "type": "Integer",
                "required": False,
                "default": 10,
                "description": "并发线程数，影响扫描速度，范围1-50"
            }
        ]
    }

    print("从数据库获取的动作定义:")
    print(json.dumps(action_definition, ensure_ascii=False, indent=2))
    print()

    # 3. 新版模板变量
    print("【步骤 3: 增强版模板变量】")
    user_params = request_body["params"]["arguments"]

    template_variables = {
        "app_name": "BBScan网站扫描器",
        "action": "scan_url",
        "action_definition": json.dumps(action_definition, ensure_ascii=False, indent=2),
        "parameters": json.dumps(user_params, ensure_ascii=False, indent=2)
    }

    print("模板变量（增强版包含完整动作定义）:")
    for key, value in template_variables.items():
        if key == "action_definition":
            print(f"- {key}: [完整的动作定义JSON，包含参数描述]")
        else:
            print(f"- {key}: {value if len(str(value)) < 50 else str(value)[:50] + '...'}")
    print()

    # 4. 生成的最终提示词
    print("【步骤 4: 生成的增强版提示词】")
    print("=" * 60)

    enhanced_template = """你是{app_name}系统的模拟器。用户调用了{action}操作。

动作完整定义：
{action_definition}

用户提供的参数：
{parameters}

请根据动作定义中的参数描述、类型要求和业务逻辑，生成一个真实的API响应结果（JSON格式）。

响应要求：
1. 符合真实系统的响应格式和业务场景
2. 包含合理且符合逻辑的数据
3. 正确反映操作的成功或失败状态
4. 充分考虑参数的描述、类型、默认值和约束
5. 如果动作定义中有输出结构要求，严格遵循
6. 响应数据要与输入参数相关联，体现真实的业务处理结果

只返回JSON格式的响应，不要任何其他说明文字。"""

    final_prompt = enhanced_template.format(**template_variables)
    print(final_prompt)
    print("=" * 60)
    print()

    # 5. AI 理解的关键信息
    print("【步骤 5: AI 现在能理解的关键信息】")
    print("✅ 参数业务含义:")
    print("  - target_url: 知道这是要扫描的目标，会影响响应中的URL")
    print("  - scan_type='full': 理解需要生成'完整扫描'的深度报告")
    print("  - max_depth=3: 知道要扫描3层深度，会在目录结构中体现")
    print("  - follow_redirects=True: 理解需要处理重定向，可能影响扫描范围")
    print("  - threads=15: 知道并发设置，可能影响扫描性能数据")
    print()

    print("✅ 参数约束和规则:")
    print("  - scan_type 只能是 basic/full/custom 三种")
    print("  - max_depth 范围是 1-10")
    print("  - threads 范围是 1-50")
    print("  - target_url 必须是有效的 HTTP/HTTPS 地址")
    print()

    print("✅ 业务逻辑理解:")
    print("  - full 扫描应该比 basic 扫描包含更多信息")
    print("  - 高深度扫描会发现更多目录和文件")
    print("  - 高并发会影响扫描速度和性能指标")
    print("  - 重定向设置会影响最终扫描的URL范围")
    print()

    # 6. 模拟的 AI 响应
    print("【步骤 6: AI 生成的增强版响应】")
    print("基于完整动作定义，AI 能生成更精确的响应:")
    print("-" * 50)

    enhanced_response = {
        "success": True,
        "scan_id": "scan_20240930_162345",
        "target_url": "https://target-app.com",
        "scan_type": "full",  # 匹配用户输入
        "status": "completed",
        "start_time": "2024-09-30T16:23:45Z",
        "end_time": "2024-09-30T16:25:12Z",
        "duration_seconds": 87,
        "statistics": {
            "total_requests": 768,  # full 扫描，请求数较多
            "successful_requests": 742,
            "failed_requests": 26,
            "directories_found": 45,  # 深度3，目录较多
            "files_found": 234,
            "scan_depth": 3,  # 匹配 max_depth 参数
            "redirects_followed": 12,  # 因为 follow_redirects=True
            "average_response_time": 156
        },
        "vulnerabilities": {
            "critical": 1,
            "high": 3,
            "medium": 8,
            "low": 15,
            "info": 23
        },
        "performance_metrics": {
            "concurrent_threads": 15,  # 匹配 threads 参数
            "requests_per_second": 8.8,
            "average_thread_utilization": "87%"
        },
        "interesting_findings": [
            {
                "path": "/admin/dashboard",
                "status_code": 401,
                "type": "admin_panel",
                "severity": "critical",
                "description": "发现管理后台，需要认证",
                "depth_level": 2  # 体现 max_depth 的影响
            },
            {
                "path": "/api/v2/users",
                "status_code": 200,
                "type": "api_endpoint",
                "severity": "high",
                "description": "API端点可能暴露用户信息",
                "depth_level": 3  # 深度扫描才发现
            },
            {
                "path": "/backup/db.sql",
                "status_code": 200,
                "type": "database_backup",
                "severity": "high",
                "description": "数据库备份文件暴露",
                "original_url": "https://target-app.com/old-backup/db.sql",
                "redirected_from": "/old-backup/db.sql",
                "found_via_redirect": True  # 因为 follow_redirects=True
            }
        ],
        "scan_config": {
            "max_depth": 3,  # 匹配用户参数
            "follow_redirects": True,  # 匹配用户参数
            "concurrent_threads": 15,  # 匹配用户参数
            "scan_type": "full",  # 匹配用户参数
            "timeout_per_request": 10,
            "user_agent": "BBScan/2.0"
        },
        "recommendations": [
            "限制或移除管理后台访问 /admin/dashboard",
            "保护API端点 /api/v2/users，添加认证",
            "删除数据库备份文件 /backup/db.sql",
            "配置适当的URL重定向策略",
            "实施深度防护策略，防止目录遍历"
        ]
    }

    print(json.dumps(enhanced_response, ensure_ascii=False, indent=2))
    print("-" * 50)
    print()

    # 7. 对比优势
    print("【步骤 7: 增强版 vs 原版对比】")
    print("🔥 主要改进:")
    print()

    print("📊 更精确的业务逻辑:")
    print("  ❌ 原版: AI 只知道参数名和值")
    print("  ✅ 新版: AI 知道每个参数的具体作用和业务含义")
    print()

    print("🎯 更符合实际的响应:")
    print("  ❌ 原版: scan_type='full' 可能生成基础响应")
    print("  ✅ 新版: scan_type='full' 必然生成完整的深度扫描报告")
    print()

    print("🔗 参数关联性:")
    print("  ❌ 原版: 参数间没有逻辑关联")
    print("  ✅ 新版: follow_redirects=True 会在结果中体现重定向发现")
    print()

    print("📏 数据一致性:")
    print("  ❌ 原版: max_depth=3 可能生成 depth=1 的结果")
    print("  ✅ 新版: 严格按照 max_depth=3 生成三层深度的目录结构")
    print()

    print("🚀 扩展性:")
    print("  ❌ 原版: 难以添加输出格式要求")
    print("  ✅ 新版: 可在动作定义中添加 output_schema，AI会严格遵循")
    print()

    # 8. 未来扩展示例
    print("【步骤 8: 未来扩展可能】")
    print("可以在动作定义中添加输出结构要求:")

    future_action_def = {
        "name": "scan_url",
        "description": "URL扫描",
        "parameters": [...],
        "output_schema": {
            "type": "object",
            "required": ["success", "scan_id", "statistics", "findings"],
            "properties": {
                "success": {"type": "boolean"},
                "scan_id": {"type": "string", "pattern": "^scan_\\d{8}_\\d{6}$"},
                "statistics": {
                    "type": "object",
                    "required": ["total_requests", "scan_depth"],
                    "properties": {
                        "total_requests": {"type": "integer", "minimum": 1},
                        "scan_depth": {"type": "integer", "minimum": 1, "maximum": 10}
                    }
                }
            }
        }
    }

    print("示例输出结构定义:")
    print(json.dumps(future_action_def["output_schema"], ensure_ascii=False, indent=2))
    print()
    print("这样 AI 就会严格按照 JSON Schema 生成响应！")

if __name__ == "__main__":
    demonstrate_enhanced_prompt()