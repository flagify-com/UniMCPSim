#!/usr/bin/env python3
"""
创建 BBScan 扫描器应用示例
可以通过管理后台或此脚本直接在数据库中创建
"""

import json
from models import db_manager, Application

def create_bbscan_app():
    """创建 BBScan 扫描器应用"""

    print("创建 BBScan 扫描器应用...")

    # 定义 BBScan 应用的动作
    actions = [
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
                    "description": "扫描类型：basic(基础扫描)、full(完整扫描)、custom(自定义扫描)"
                },
                {
                    "key": "max_depth",
                    "type": "Integer",
                    "required": False,
                    "default": 2,
                    "description": "扫描深度，默认为2层"
                },
                {
                    "key": "follow_redirects",
                    "type": "Boolean",
                    "required": False,
                    "default": False,
                    "description": "是否跟随重定向"
                },
                {
                    "key": "threads",
                    "type": "Integer",
                    "required": False,
                    "default": 10,
                    "description": "并发线程数"
                }
            ]
        },
        {
            "name": "check_vulnerability",
            "display_name": "检查漏洞",
            "description": "检查目标URL的常见漏洞",
            "parameters": [
                {
                    "key": "target_url",
                    "type": "String",
                    "required": True,
                    "description": "要检查的目标URL"
                },
                {
                    "key": "vulnerability_types",
                    "type": "Array",
                    "required": False,
                    "default": ["sql_injection", "xss", "csrf"],
                    "description": "要检查的漏洞类型列表"
                }
            ]
        },
        {
            "name": "get_scan_report",
            "display_name": "获取扫描报告",
            "description": "获取之前扫描的详细报告",
            "parameters": [
                {
                    "key": "scan_id",
                    "type": "String",
                    "required": True,
                    "description": "扫描ID"
                },
                {
                    "key": "format",
                    "type": "String",
                    "required": False,
                    "default": "json",
                    "options": ["json", "html", "pdf"],
                    "description": "报告格式"
                }
            ]
        },
        {
            "name": "stop_scan",
            "display_name": "停止扫描",
            "description": "停止正在进行的扫描",
            "parameters": [
                {
                    "key": "scan_id",
                    "type": "String",
                    "required": True,
                    "description": "要停止的扫描ID"
                }
            ]
        },
        {
            "name": "list_scans",
            "display_name": "列出扫描任务",
            "description": "列出所有扫描任务",
            "parameters": [
                {
                    "key": "status",
                    "type": "String",
                    "required": False,
                    "options": ["running", "completed", "failed", "all"],
                    "default": "all",
                    "description": "任务状态过滤"
                },
                {
                    "key": "limit",
                    "type": "Integer",
                    "required": False,
                    "default": 10,
                    "description": "返回结果数量限制"
                }
            ]
        }
    ]

    # 创建应用模板
    template = {
        "actions": actions
    }

    # 创建应用
    session = db_manager.get_session()
    try:
        # 检查是否已存在
        existing = session.query(Application).filter_by(
            category="Scanner",
            name="BBScan"
        ).first()

        if existing:
            print("BBScan 应用已存在，更新中...")
            existing.display_name = "BBScan网站扫描器"
            existing.description = "基于Python的网站目录和文件扫描工具，可以快速发现网站的目录结构、敏感文件和潜在漏洞"
            existing.template = template
            existing.enabled = True
            session.commit()
            print("✅ BBScan 应用已更新")
        else:
            app = Application(
                category="Scanner",
                name="BBScan",
                display_name="BBScan网站扫描器",
                description="基于Python的网站目录和文件扫描工具，可以快速发现网站的目录结构、敏感文件和潜在漏洞",
                template=template,
                enabled=True
            )
            session.add(app)
            session.commit()
            print("✅ BBScan 应用创建成功")

        # 获取Demo Token
        from models import Token
        demo_token = session.query(Token).filter_by(name="Demo Token").first()
        if demo_token:
            print(f"\n访问地址: http://127.0.0.1:8080/Scanner/BBScan?token={demo_token.token}")
        else:
            print("\n请在管理后台创建 Token 后访问: http://127.0.0.1:8080/Scanner/BBScan?token=<your-token>")

        print("\n可用的动作:")
        for action in actions:
            print(f"  - {action['name']}: {action['display_name']} - {action['description']}")

    finally:
        session.close()

if __name__ == "__main__":
    create_bbscan_app()

    print("\n" + "="*60)
    print("提示词模板说明")
    print("="*60)
    print("""
当用户调用 BBScan 的任何动作时，系统会：

1. 从数据库获取 'response_simulation' 提示词模板
2. 将以下变量替换到模板中：
   - {app_name} = "BBScan网站扫描器"
   - {action} = 用户调用的动作名（如 "scan_url"）
   - {parameters} = 用户提供的参数（JSON格式）

3. 最终的提示词发送给 OpenAI API
4. OpenAI 返回符合 BBScan 风格的模拟响应

示例提示词（变量替换后）：
----------------------------------------
你是BBScan网站扫描器系统的模拟器。用户调用了scan_url操作，参数如下：
{
  "target_url": "https://example.com",
  "scan_type": "full",
  "max_depth": 3
}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。
----------------------------------------
""")