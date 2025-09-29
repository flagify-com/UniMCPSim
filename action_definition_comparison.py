#!/usr/bin/env python3
"""
对比有无 action_definition 的 AI 提示词差异
展示升级前后的具体变化
"""

import json

def show_before_after_comparison():
    """展示升级前后的对比"""

    print("=" * 80)
    print("升级前后 AI 提示词对比")
    print("=" * 80)
    print()

    # 用户参数
    user_params = {
        "target_url": "https://example.com",
        "scan_type": "full",
        "max_depth": 3,
        "follow_redirects": True,
        "threads": 15
    }

    # 真实的动作定义
    action_definition = {
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
    }

    print("🔍 用户请求的参数:")
    print(json.dumps(user_params, ensure_ascii=False, indent=2))
    print()

    print("📊 升级前后的提示词对比:")
    print("=" * 80)

    # 原版提示词（没有动作定义）
    print("【原版提示词】（AI 只知道参数名和值）")
    print("-" * 60)

    old_prompt = f"""你是BBScan网站扫描器系统的模拟器。用户调用了scan_url操作，参数如下：
{json.dumps(user_params, ensure_ascii=False, indent=2)}

请生成一个真实的API响应结果（JSON格式）。响应应该：
1. 符合真实系统的响应格式
2. 包含合理的数据
3. 反映操作的成功或失败状态

直接返回JSON，不要任何其他说明文字。"""

    print(old_prompt)
    print("-" * 60)
    print()

    # 新版提示词（包含动作定义）
    print("【新版提示词】（AI 能理解每个参数的具体含义）")
    print("-" * 60)

    new_prompt = f"""你是BBScan网站扫描器系统的模拟器。用户调用了scan_url操作。

动作完整定义：
{json.dumps(action_definition, ensure_ascii=False, indent=2)}

用户提供的参数：
{json.dumps(user_params, ensure_ascii=False, indent=2)}

请根据动作定义中的参数描述、类型要求和业务逻辑，生成一个真实的API响应结果（JSON格式）。

响应要求：
1. 符合真实系统的响应格式和业务场景
2. 包含合理且符合逻辑的数据
3. 正确反映操作的成功或失败状态
4. 充分考虑参数的描述、类型、默认值和约束
5. 如果动作定义中有输出结构要求，严格遵循
6. 响应数据要与输入参数相关联，体现真实的业务处理结果

只返回JSON格式的响应，不要任何其他说明文字。"""

    print(new_prompt)
    print("-" * 60)
    print()

    # 对比分析
    print("🔍 详细对比分析:")
    print("=" * 80)

    comparisons = [
        {
            "parameter": "scan_type: 'full'",
            "old_understanding": "AI 只知道这是一个字符串值 'full'",
            "new_understanding": "AI 知道这表示'完整扫描'，相对于'basic'基础扫描，需要生成更详细的报告",
            "impact": "新版会生成更完整的漏洞报告、更多的发现信息"
        },
        {
            "parameter": "max_depth: 3",
            "old_understanding": "AI 只知道这是数字 3",
            "new_understanding": "AI 知道这是'扫描深度'，默认值是2，用户设置了比默认值更深的扫描",
            "impact": "新版会在目录结构中严格体现3层深度，而不是随意的层数"
        },
        {
            "parameter": "follow_redirects: true",
            "old_understanding": "AI 只知道这是布尔值 true",
            "new_understanding": "AI 知道这表示'是否跟随重定向'，默认是false，用户启用了重定向跟踪",
            "impact": "新版可能在扫描结果中包含通过重定向发现的内容"
        },
        {
            "parameter": "threads: 15",
            "old_understanding": "AI 只知道这是数字 15",
            "new_understanding": "AI 知道这是'并发线程数'，默认值是10，用户设置了较高的并发",
            "impact": "新版会在性能指标中体现高并发带来的性能提升"
        }
    ]

    for i, comp in enumerate(comparisons, 1):
        print(f"{i}. 参数: {comp['parameter']}")
        print(f"   ❌ 原版理解: {comp['old_understanding']}")
        print(f"   ✅ 新版理解: {comp['new_understanding']}")
        print(f"   🎯 实际影响: {comp['impact']}")
        print()

def show_concrete_response_difference():
    """展示具体的响应差异"""

    print("=" * 80)
    print("AI 响应的具体差异示例")
    print("=" * 80)
    print()

    print("同样的用户参数: scan_type='full', max_depth=3, threads=15")
    print()

    print("【原版 AI 可能的响应】（缺乏业务逻辑理解）")
    print("-" * 60)

    old_response = {
        "success": True,
        "scan_id": "scan_123",
        "target_url": "https://example.com",
        "status": "completed",
        "files_found": 50,  # 随意的数量
        "directories": ["/css", "/js"],  # 简单的目录列表
        "scan_depth": 2,  # 可能忽略用户的 max_depth=3 设置
        "scan_type": "basic"  # 可能忽略用户的 scan_type='full' 设置
    }

    print(json.dumps(old_response, ensure_ascii=False, indent=2))
    print("-" * 60)
    print()

    print("【新版 AI 的响应】（基于完整业务逻辑理解）")
    print("-" * 60)

    new_response = {
        "success": True,
        "scan_id": "scan_20240930_163025",
        "target_url": "https://example.com",
        "scan_type": "full",  # ✅ 严格匹配用户输入
        "status": "completed",
        "start_time": "2024-09-30T16:30:25Z",
        "end_time": "2024-09-30T16:31:42Z",
        "duration_seconds": 77,
        "statistics": {
            "total_requests": 445,  # full 扫描，请求数较多
            "successful_requests": 412,
            "failed_requests": 33,
            "directories_found": 28,
            "files_found": 187,
            "scan_depth": 3,  # ✅ 严格匹配 max_depth=3
            "average_response_time": 173
        },
        "vulnerabilities": {  # ✅ full 扫描包含详细漏洞信息
            "critical": 2,
            "high": 4,
            "medium": 9,
            "low": 16,
            "info": 25
        },
        "performance_metrics": {  # ✅ 体现 threads=15 的性能影响
            "concurrent_threads": 15,
            "requests_per_second": 5.8,
            "average_thread_utilization": "92%"
        },
        "directories": [  # ✅ 体现 max_depth=3 的层次结构
            {"path": "/css/", "depth": 1, "files_count": 12},
            {"path": "/js/", "depth": 1, "files_count": 23},
            {"path": "/admin/", "depth": 1, "files_count": 8},
            {"path": "/admin/modules/", "depth": 2, "files_count": 15},
            {"path": "/admin/modules/users/", "depth": 3, "files_count": 7},  # 第3层
            {"path": "/api/v1/", "depth": 2, "files_count": 11},
            {"path": "/api/v1/internal/", "depth": 3, "files_count": 4}  # 第3层
        ],
        "interesting_findings": [  # ✅ full 扫描的详细发现
            {
                "path": "/admin/config.php",
                "status_code": 200,
                "type": "config_file",
                "severity": "high",
                "depth_level": 2,
                "description": "配置文件可能包含敏感信息"
            },
            {
                "path": "/api/v1/internal/debug",
                "status_code": 200,
                "type": "debug_endpoint",
                "severity": "medium",
                "depth_level": 3,  # ✅ 深度扫描才能发现
                "description": "调试端点暴露，可能泄露系统信息"
            }
        ],
        "scan_config": {  # ✅ 完整反映用户的所有配置
            "max_depth": 3,
            "follow_redirects": True,
            "concurrent_threads": 15,
            "scan_type": "full",
            "timeout_per_request": 10
        }
    }

    print(json.dumps(new_response, ensure_ascii=False, indent=2))
    print("-" * 60)
    print()

    print("🎯 关键差异总结:")
    print("=" * 50)
    print("✅ 数据一致性: scan_depth=3 严格匹配用户的 max_depth")
    print("✅ 业务逻辑: scan_type='full' 生成完整的漏洞和发现报告")
    print("✅ 性能关联: threads=15 体现在性能指标中")
    print("✅ 层次结构: 目录结构严格按照3层深度组织")
    print("✅ 功能完整: full 扫描包含 vulnerabilities、findings 等完整信息")

if __name__ == "__main__":
    show_before_after_comparison()
    print("\n" + "="*80 + "\n")
    show_concrete_response_difference()