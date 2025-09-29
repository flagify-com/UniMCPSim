#!/usr/bin/env python3
"""
初始化默认模拟器
"""

import json
from models import db_manager, Application, Token, AppPermission, User
from auth_utils import hash_password

def init_default_simulators():
    """初始化默认模拟器"""
    session = db_manager.get_session()

    try:
        # 创建默认管理员
        admin = session.query(User).filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                password_hash=hash_password('admin123'),
                is_admin=True
            )
            session.add(admin)
            session.flush()

        # 确保提示词模板存在（调用DatabaseManager的方法）
        session.commit()  # 先提交admin用户
        session.close()  # 关闭当前session
        db_manager.create_default_prompts()  # 使用DatabaseManager的方法
        session = db_manager.get_session()  # 重新获取session

        # 重新获取admin用户引用
        admin = session.query(User).filter_by(username='admin').first()

        # 定义默认模拟器
        simulators = [
            {
                "category": "Security",
                "name": "VirusTotal",
                "display_name": "VirusTotal威胁情报",
                "description": "病毒和恶意软件扫描服务",
                "template": {
                    "actions": [
                        {
                            "name": "scan_file",
                            "display_name": "文件扫描",
                            "description": "上传文件进行病毒扫描",
                            "parameters": [
                                {"key": "file_path", "type": "String", "required": True, "description": "文件路径或URL"},
                                {"key": "scan_type", "type": "String", "required": False, "default": "full", "description": "扫描类型", "options": ["quick", "full", "deep"]}
                            ]
                        },
                        {
                            "name": "scan_url",
                            "display_name": "URL扫描",
                            "description": "扫描URL是否恶意",
                            "parameters": [
                                {"key": "url", "type": "String", "required": True, "description": "要扫描的URL地址"}
                            ]
                        },
                        {
                            "name": "get_file_report",
                            "display_name": "获取文件报告",
                            "description": "根据哈希值获取文件扫描报告",
                            "parameters": [
                                {"key": "hash", "type": "String", "required": True, "description": "文件MD5/SHA1/SHA256哈希值"},
                                {"key": "verbose", "type": "Boolean", "required": False, "default": False, "description": "是否返回详细信息"}
                            ]
                        },
                        {
                            "name": "scan_ip",
                            "display_name": "IP地址分析",
                            "description": "分析IP地址的威胁情报",
                            "parameters": [
                                {"key": "ip", "type": "String", "required": True, "description": "要分析的IP地址"}
                            ]
                        },
                        {
                            "name": "get_domain_report",
                            "display_name": "域名报告",
                            "description": "获取域名的威胁情报报告",
                            "parameters": [
                                {"key": "domain", "type": "String", "required": True, "description": "域名"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Security",
                "name": "ThreatBook",
                "display_name": "微步在线威胁情报",
                "description": "威胁情报分析平台",
                "template": {
                    "actions": [
                        {
                            "name": "query_ip_reputation",
                            "display_name": "IP信誉查询",
                            "description": "查询IP地址信誉和威胁情报",
                            "parameters": [
                                {"key": "ip", "type": "String", "required": True, "description": "IP地址"},
                                {"key": "lang", "type": "String", "required": False, "default": "zh", "description": "语言", "options": ["zh", "en"]}
                            ]
                        },
                        {
                            "name": "query_domain_reputation",
                            "display_name": "域名信誉查询",
                            "description": "查询域名信誉和威胁分类",
                            "parameters": [
                                {"key": "domain", "type": "String", "required": True, "description": "域名"},
                                {"key": "include_subdomains", "type": "Boolean", "required": False, "default": False, "description": "是否包含子域名"}
                            ]
                        },
                        {
                            "name": "query_file_reputation",
                            "display_name": "文件信誉查询",
                            "description": "查询文件哈希的威胁情报",
                            "parameters": [
                                {"key": "hash", "type": "String", "required": True, "description": "文件哈希值(MD5/SHA1/SHA256)"},
                                {"key": "hash_type", "type": "String", "required": False, "default": "auto", "description": "哈希类型", "options": ["auto", "md5", "sha1", "sha256"]}
                            ]
                        },
                        {
                            "name": "query_url_reputation",
                            "display_name": "URL信誉查询",
                            "description": "查询URL的威胁情报",
                            "parameters": [
                                {"key": "url", "type": "String", "required": True, "description": "要查询的URL"}
                            ]
                        },
                        {
                            "name": "get_threat_intelligence",
                            "display_name": "获取威胁情报",
                            "description": "获取最新威胁情报摘要",
                            "parameters": [
                                {"key": "threat_type", "type": "String", "required": False, "description": "威胁类型过滤", "options": ["malware", "phishing", "botnet", "apt"]},
                                {"key": "time_range", "type": "String", "required": False, "default": "24h", "description": "时间范围", "options": ["1h", "24h", "7d", "30d"]}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Security",
                "name": "QingTengHIDS",
                "display_name": "青藤云HIDS",
                "description": "主机入侵检测系统",
                "template": {
                    "actions": [
                        {
                            "name": "get_security_alerts",
                            "display_name": "获取安全告警",
                            "description": "获取主机安全告警信息",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": False, "description": "主机ID(可选,不填则获取所有主机)"},
                                {"key": "severity", "type": "String", "required": False, "description": "告警级别", "options": ["low", "medium", "high", "critical"]},
                                {"key": "limit", "type": "Integer", "required": False, "default": 20, "description": "返回数量"},
                                {"key": "time_range", "type": "String", "required": False, "default": "24h", "description": "时间范围", "options": ["1h", "6h", "24h", "7d"]}
                            ]
                        },
                        {
                            "name": "isolate_host",
                            "display_name": "主机隔离",
                            "description": "隔离受感染或可疑的主机",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": True, "description": "主机ID"},
                                {"key": "isolation_type", "type": "String", "required": False, "default": "network", "description": "隔离类型", "options": ["network", "process", "full"]},
                                {"key": "reason", "type": "String", "required": False, "description": "隔离原因"}
                            ]
                        },
                        {
                            "name": "release_host",
                            "display_name": "解除隔离",
                            "description": "解除主机隔离状态",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": True, "description": "主机ID"}
                            ]
                        },
                        {
                            "name": "get_host_status",
                            "display_name": "获取主机状态",
                            "description": "获取主机的安全状态和基础信息",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": True, "description": "主机ID"}
                            ]
                        },
                        {
                            "name": "scan_host_vulnerabilities",
                            "display_name": "主机漏洞扫描",
                            "description": "对指定主机进行漏洞扫描",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": True, "description": "主机ID"},
                                {"key": "scan_type", "type": "String", "required": False, "default": "basic", "description": "扫描类型", "options": ["basic", "comprehensive", "quick"]}
                            ]
                        },
                        {
                            "name": "get_process_info",
                            "display_name": "获取进程信息",
                            "description": "获取主机上的进程信息",
                            "parameters": [
                                {"key": "host_id", "type": "String", "required": True, "description": "主机ID"},
                                {"key": "process_name", "type": "String", "required": False, "description": "进程名称(可选)"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "IM",
                "name": "WeChat",
                "display_name": "企业微信",
                "description": "企业即时通讯工具",
                "template": {
                    "actions": [
                        {
                            "name": "send_text_message",
                            "display_name": "发送文本消息",
                            "description": "发送文本消息给用户或群组",
                            "parameters": [
                                {"key": "to_user", "type": "String", "required": False, "description": "接收用户ID(二选一)"},
                                {"key": "to_group", "type": "String", "required": False, "description": "接收群组ID(二选一)"},
                                {"key": "content", "type": "String", "required": True, "description": "消息内容"},
                                {"key": "at_users", "type": "Array", "required": False, "description": "@用户ID列表(群消息可用)"}
                            ]
                        },
                        {
                            "name": "send_markdown_message",
                            "display_name": "发送Markdown消息",
                            "description": "发送富文本Markdown格式消息",
                            "parameters": [
                                {"key": "to_user", "type": "String", "required": False, "description": "接收用户ID(二选一)"},
                                {"key": "to_group", "type": "String", "required": False, "description": "接收群组ID(二选一)"},
                                {"key": "markdown_content", "type": "String", "required": True, "description": "Markdown内容"}
                            ]
                        },
                        {
                            "name": "send_image_message",
                            "display_name": "发送图片消息",
                            "description": "发送图片消息",
                            "parameters": [
                                {"key": "to_user", "type": "String", "required": False, "description": "接收用户ID(二选一)"},
                                {"key": "to_group", "type": "String", "required": False, "description": "接收群组ID(二选一)"},
                                {"key": "image_url", "type": "String", "required": True, "description": "图片URL或文件路径"}
                            ]
                        },
                        {
                            "name": "send_file_message",
                            "display_name": "发送文件消息",
                            "description": "发送文件消息",
                            "parameters": [
                                {"key": "to_user", "type": "String", "required": False, "description": "接收用户ID(二选一)"},
                                {"key": "to_group", "type": "String", "required": False, "description": "接收群组ID(二选一)"},
                                {"key": "file_url", "type": "String", "required": True, "description": "文件URL或路径"},
                                {"key": "file_name", "type": "String", "required": True, "description": "文件名称"}
                            ]
                        },
                        {
                            "name": "create_group_chat",
                            "display_name": "创建群聊",
                            "description": "创建新的群聊",
                            "parameters": [
                                {"key": "group_name", "type": "String", "required": True, "description": "群聊名称"},
                                {"key": "members", "type": "Array", "required": True, "description": "成员用户ID列表"},
                                {"key": "description", "type": "String", "required": False, "description": "群聊描述"}
                            ]
                        },
                        {
                            "name": "add_group_members",
                            "display_name": "添加群成员",
                            "description": "向群聊中添加新成员",
                            "parameters": [
                                {"key": "group_id", "type": "String", "required": True, "description": "群组ID"},
                                {"key": "members", "type": "Array", "required": True, "description": "要添加的用户ID列表"}
                            ]
                        },
                        {
                            "name": "get_group_members",
                            "display_name": "获取群成员",
                            "description": "获取群聊成员列表",
                            "parameters": [
                                {"key": "group_id", "type": "String", "required": True, "description": "群组ID"}
                            ]
                        },
                        {
                            "name": "get_user_info",
                            "display_name": "获取用户信息",
                            "description": "获取企业用户详细信息",
                            "parameters": [
                                {"key": "user_id", "type": "String", "required": True, "description": "用户ID"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Meeting",
                "name": "TencentMeeting",
                "display_name": "腾讯会议",
                "description": "在线会议平台",
                "template": {
                    "actions": [
                        {
                            "name": "create_instant_meeting",
                            "display_name": "创建即时会议",
                            "description": "快速创建并开始即时会议",
                            "parameters": [
                                {"key": "subject", "type": "String", "required": True, "description": "会议主题"},
                                {"key": "password", "type": "String", "required": False, "description": "会议密码"},
                                {"key": "waiting_room", "type": "Boolean", "required": False, "default": False, "description": "是否开启等候室"}
                            ]
                        },
                        {
                            "name": "schedule_meeting",
                            "display_name": "预约会议",
                            "description": "预约未来的会议",
                            "parameters": [
                                {"key": "subject", "type": "String", "required": True, "description": "会议主题"},
                                {"key": "start_time", "type": "String", "required": True, "description": "开始时间(ISO格式)"},
                                {"key": "duration", "type": "Integer", "required": True, "description": "持续时间(分钟)"},
                                {"key": "invitees", "type": "Array", "required": False, "description": "受邀用户列表"},
                                {"key": "password", "type": "String", "required": False, "description": "会议密码"},
                                {"key": "recurring", "type": "Boolean", "required": False, "default": False, "description": "是否周期性会议"}
                            ]
                        },
                        {
                            "name": "join_meeting",
                            "display_name": "加入会议",
                            "description": "加入指定会议",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"},
                                {"key": "password", "type": "String", "required": False, "description": "会议密码"}
                            ]
                        },
                        {
                            "name": "end_meeting",
                            "display_name": "结束会议",
                            "description": "结束正在进行的会议",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"}
                            ]
                        },
                        {
                            "name": "get_meeting_details",
                            "display_name": "获取会议详情",
                            "description": "获取会议的详细信息",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"}
                            ]
                        },
                        {
                            "name": "invite_participants",
                            "display_name": "邀请参会者",
                            "description": "向会议邀请新的参会者",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"},
                                {"key": "invitees", "type": "Array", "required": True, "description": "受邀用户ID或邮箱列表"}
                            ]
                        },
                        {
                            "name": "get_participant_list",
                            "display_name": "获取参会者列表",
                            "description": "获取会议的参会者列表",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"}
                            ]
                        },
                        {
                            "name": "start_recording",
                            "display_name": "开始录制",
                            "description": "开始录制会议",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"},
                                {"key": "record_type", "type": "String", "required": False, "default": "cloud", "description": "录制类型", "options": ["cloud", "local"]}
                            ]
                        },
                        {
                            "name": "stop_recording",
                            "display_name": "停止录制",
                            "description": "停止会议录制",
                            "parameters": [
                                {"key": "meeting_id", "type": "String", "required": True, "description": "会议ID"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Ticket",
                "name": "Jira",
                "display_name": "Jira工单系统",
                "description": "项目管理和问题跟踪系统",
                "template": {
                    "actions": [
                        {
                            "name": "create_issue",
                            "display_name": "创建工单",
                            "description": "创建新的工单",
                            "parameters": [
                                {"key": "project_key", "type": "String", "required": True, "description": "项目标识符"},
                                {"key": "issue_type", "type": "String", "required": True, "description": "工单类型", "options": ["Bug", "Story", "Task", "Epic", "Subtask"]},
                                {"key": "summary", "type": "String", "required": True, "description": "工单标题"},
                                {"key": "description", "type": "String", "required": True, "description": "工单描述"},
                                {"key": "priority", "type": "String", "required": False, "default": "Medium", "description": "优先级", "options": ["Lowest", "Low", "Medium", "High", "Highest"]},
                                {"key": "assignee", "type": "String", "required": False, "description": "指派人"},
                                {"key": "labels", "type": "Array", "required": False, "description": "标签列表"},
                                {"key": "components", "type": "Array", "required": False, "description": "组件列表"}
                            ]
                        },
                        {
                            "name": "update_issue_status",
                            "display_name": "更新工单状态",
                            "description": "转换工单状态",
                            "parameters": [
                                {"key": "issue_key", "type": "String", "required": True, "description": "工单标识符"},
                                {"key": "transition", "type": "String", "required": True, "description": "状态转换", "options": ["To Do", "In Progress", "Done", "Blocked", "Resolved", "Closed"]}
                            ]
                        },
                        {
                            "name": "assign_issue",
                            "display_name": "分配工单",
                            "description": "将工单分配给指定用户",
                            "parameters": [
                                {"key": "issue_key", "type": "String", "required": True, "description": "工单标识符"},
                                {"key": "assignee", "type": "String", "required": True, "description": "指派人用户名或邮箱"}
                            ]
                        },
                        {
                            "name": "add_comment",
                            "display_name": "添加评论",
                            "description": "为工单添加评论",
                            "parameters": [
                                {"key": "issue_key", "type": "String", "required": True, "description": "工单标识符"},
                                {"key": "comment", "type": "String", "required": True, "description": "评论内容"}
                            ]
                        },
                        {
                            "name": "get_issue_details",
                            "display_name": "获取工单详情",
                            "description": "获取工单的详细信息",
                            "parameters": [
                                {"key": "issue_key", "type": "String", "required": True, "description": "工单标识符"}
                            ]
                        },
                        {
                            "name": "search_issues",
                            "display_name": "搜索工单",
                            "description": "使用JQL搜索工单",
                            "parameters": [
                                {"key": "jql", "type": "String", "required": False, "description": "JQL查询语句"},
                                {"key": "project", "type": "String", "required": False, "description": "项目标识符"},
                                {"key": "assignee", "type": "String", "required": False, "description": "指派人"},
                                {"key": "status", "type": "String", "required": False, "description": "状态"},
                                {"key": "limit", "type": "Integer", "required": False, "default": 50, "description": "结果数量限制"}
                            ]
                        },
                        {
                            "name": "create_subtask",
                            "display_name": "创建子任务",
                            "description": "为现有工单创建子任务",
                            "parameters": [
                                {"key": "parent_issue_key", "type": "String", "required": True, "description": "父工单标识符"},
                                {"key": "summary", "type": "String", "required": True, "description": "子任务标题"},
                                {"key": "description", "type": "String", "required": False, "description": "子任务描述"},
                                {"key": "assignee", "type": "String", "required": False, "description": "指派人"}
                            ]
                        },
                        {
                            "name": "add_attachment",
                            "display_name": "添加附件",
                            "description": "为工单添加附件",
                            "parameters": [
                                {"key": "issue_key", "type": "String", "required": True, "description": "工单标识符"},
                                {"key": "file_path", "type": "String", "required": True, "description": "文件路径或URL"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Network",
                "name": "HuaweiSwitch",
                "display_name": "华为交换机",
                "description": "华为网络交换机管理",
                "template": {
                    "actions": [
                        {
                            "name": "display_interface_brief",
                            "display_name": "显示接口简要信息",
                            "description": "显示所有接口的简要状态信息",
                            "parameters": [
                                {"key": "interface_type", "type": "String", "required": False, "description": "接口类型过滤", "options": ["ethernet", "gigabitethernet", "10ge", "all"]}
                            ]
                        },
                        {
                            "name": "display_interface_detail",
                            "display_name": "显示接口详细信息",
                            "description": "显示指定接口的详细信息",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": True, "description": "接口名称 (如: GigabitEthernet0/0/1)"}
                            ]
                        },
                        {
                            "name": "display_vlan_all",
                            "display_name": "显示所有VLAN",
                            "description": "显示交换机上配置的所有VLAN信息",
                            "parameters": []
                        },
                        {
                            "name": "create_vlan",
                            "display_name": "创建VLAN",
                            "description": "创建新的VLAN",
                            "parameters": [
                                {"key": "vlan_id", "type": "Integer", "required": True, "description": "VLAN ID (1-4094)"},
                                {"key": "description", "type": "String", "required": False, "description": "VLAN描述"}
                            ]
                        },
                        {
                            "name": "configure_interface_vlan",
                            "display_name": "配置接口VLAN",
                            "description": "配置接口的VLAN成员关系",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": True, "description": "接口名称"},
                                {"key": "access_vlan", "type": "Integer", "required": False, "description": "Access VLAN ID"},
                                {"key": "trunk_vlans", "type": "String", "required": False, "description": "Trunk允许的VLAN列表 (如: 1,10,20)"},
                                {"key": "port_mode", "type": "String", "required": True, "description": "端口模式", "options": ["access", "trunk", "hybrid"]}
                            ]
                        },
                        {
                            "name": "display_mac_address_table",
                            "display_name": "显示MAC地址表",
                            "description": "显示MAC地址学习表",
                            "parameters": [
                                {"key": "vlan_id", "type": "Integer", "required": False, "description": "指定VLAN ID"},
                                {"key": "interface", "type": "String", "required": False, "description": "指定接口"}
                            ]
                        },
                        {
                            "name": "configure_stp",
                            "display_name": "配置STP",
                            "description": "配置生成树协议",
                            "parameters": [
                                {"key": "mode", "type": "String", "required": True, "description": "STP模式", "options": ["stp", "rstp", "mstp"]},
                                {"key": "enable", "type": "Boolean", "required": True, "description": "是否启用"}
                            ]
                        },
                        {
                            "name": "save_configuration",
                            "display_name": "保存配置",
                            "description": "保存当前配置到存储器",
                            "parameters": []
                        },
                        {
                            "name": "display_current_configuration",
                            "display_name": "显示当前配置",
                            "description": "显示设备当前运行配置",
                            "parameters": [
                                {"key": "section", "type": "String", "required": False, "description": "配置段落", "options": ["interface", "vlan", "stp", "all"]}
                            ]
                        },
                        {
                            "name": "reboot_device",
                            "display_name": "重启设备",
                            "description": "重启交换机设备",
                            "parameters": [
                                {"key": "confirm", "type": "Boolean", "required": True, "description": "确认重启"},
                                {"key": "save_config", "type": "Boolean", "required": False, "default": True, "description": "重启前是否保存配置"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Network",
                "name": "CiscoRouter",
                "display_name": "Cisco路由器",
                "description": "Cisco路由器管理",
                "template": {
                    "actions": [
                        {
                            "name": "show_ip_route",
                            "display_name": "显示IP路由表",
                            "description": "显示路由表信息",
                            "parameters": [
                                {"key": "protocol", "type": "String", "required": False, "description": "路由协议过滤", "options": ["connected", "static", "ospf", "eigrp", "bgp", "rip"]}
                            ]
                        },
                        {
                            "name": "show_ip_interface_brief",
                            "display_name": "显示接口简要信息",
                            "description": "显示所有接口的IP配置和状态",
                            "parameters": []
                        },
                        {
                            "name": "configure_static_route",
                            "display_name": "配置静态路由",
                            "description": "添加或删除静态路由",
                            "parameters": [
                                {"key": "destination_network", "type": "String", "required": True, "description": "目标网络 (如: 192.168.1.0)"},
                                {"key": "subnet_mask", "type": "String", "required": True, "description": "子网掩码 (如: 255.255.255.0)"},
                                {"key": "next_hop", "type": "String", "required": True, "description": "下一跳IP地址"},
                                {"key": "action", "type": "String", "required": False, "default": "add", "description": "操作类型", "options": ["add", "remove"]},
                                {"key": "administrative_distance", "type": "Integer", "required": False, "description": "管理距离 (1-255)"}
                            ]
                        },
                        {
                            "name": "configure_interface_ip",
                            "display_name": "配置接口IP",
                            "description": "配置接口IP地址",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": True, "description": "接口名称 (如: GigabitEthernet0/0)"},
                                {"key": "ip_address", "type": "String", "required": True, "description": "IP地址"},
                                {"key": "subnet_mask", "type": "String", "required": True, "description": "子网掩码"},
                                {"key": "description", "type": "String", "required": False, "description": "接口描述"}
                            ]
                        },
                        {
                            "name": "configure_ospf",
                            "display_name": "配置OSPF",
                            "description": "配置OSPF路由协议",
                            "parameters": [
                                {"key": "process_id", "type": "Integer", "required": True, "description": "OSPF进程ID"},
                                {"key": "router_id", "type": "String", "required": False, "description": "路由器ID"},
                                {"key": "network", "type": "String", "required": True, "description": "网络地址"},
                                {"key": "wildcard_mask", "type": "String", "required": True, "description": "通配符掩码"},
                                {"key": "area", "type": "String", "required": True, "description": "OSPF区域"}
                            ]
                        },
                        {
                            "name": "configure_acl",
                            "display_name": "配置访问控制列表",
                            "description": "配置标准或扩展ACL",
                            "parameters": [
                                {"key": "acl_number", "type": "String", "required": True, "description": "ACL编号或名称"},
                                {"key": "action", "type": "String", "required": True, "description": "动作", "options": ["permit", "deny"]},
                                {"key": "source", "type": "String", "required": True, "description": "源地址 (IP或any)"},
                                {"key": "destination", "type": "String", "required": False, "description": "目标地址 (扩展ACL)"},
                                {"key": "protocol", "type": "String", "required": False, "description": "协议类型", "options": ["tcp", "udp", "icmp", "ip"]}
                            ]
                        },
                        {
                            "name": "show_running_config",
                            "display_name": "显示运行配置",
                            "description": "显示当前运行的配置",
                            "parameters": [
                                {"key": "section", "type": "String", "required": False, "description": "配置段落", "options": ["interface", "router", "access-list", "all"]}
                            ]
                        },
                        {
                            "name": "copy_running_startup",
                            "display_name": "保存配置",
                            "description": "将运行配置保存到启动配置",
                            "parameters": []
                        },
                        {
                            "name": "ping",
                            "display_name": "Ping测试",
                            "description": "执行ping连通性测试",
                            "parameters": [
                                {"key": "destination", "type": "String", "required": True, "description": "目标IP地址或主机名"},
                                {"key": "count", "type": "Integer", "required": False, "default": 5, "description": "ping次数"},
                                {"key": "source", "type": "String", "required": False, "description": "源接口或IP"}
                            ]
                        },
                        {
                            "name": "traceroute",
                            "display_name": "路由跟踪",
                            "description": "执行traceroute路径跟踪",
                            "parameters": [
                                {"key": "destination", "type": "String", "required": True, "description": "目标IP地址或主机名"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Network",
                "name": "Cisco3750",
                "display_name": "Cisco 3750交换机",
                "description": "Cisco Catalyst 3750系列交换机",
                "template": {
                    "actions": [
                        {
                            "name": "show_version",
                            "display_name": "显示版本信息",
                            "description": "获取交换机版本信息",
                            "parameters": []
                        },
                        {
                            "name": "show_interfaces",
                            "display_name": "显示接口状态",
                            "description": "获取所有接口状态信息",
                            "parameters": []
                        },
                        {
                            "name": "configure_vlan",
                            "display_name": "配置VLAN",
                            "description": "配置VLAN设置",
                            "parameters": [
                                {"key": "vlan_id", "type": "Integer", "required": True, "description": "VLAN ID (1-4094)"},
                                {"key": "name", "type": "String", "required": False, "description": "VLAN名称"},
                                {"key": "ports", "type": "Array", "required": True, "description": "端口列表 (如: ['Fa0/1', 'Fa0/2'])"}
                            ]
                        },
                        {
                            "name": "configure_port",
                            "display_name": "配置端口",
                            "description": "配置交换机端口",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": True, "description": "接口名称 (如: FastEthernet0/1)"},
                                {"key": "mode", "type": "String", "required": True, "description": "端口模式", "options": ["access", "trunk"]},
                                {"key": "vlan", "type": "Integer", "required": False, "description": "VLAN ID (access模式使用)"},
                                {"key": "allowed_vlans", "type": "String", "required": False, "description": "允许的VLAN (trunk模式使用, 如: '1,10,20')"}
                            ]
                        }
                    ]
                }
            },
            {
                "category": "Firewall",
                "name": "Sangfor",
                "display_name": "深信服防火墙",
                "description": "深信服下一代防火墙",
                "template": {
                    "actions": [
                        {
                            "name": "add_security_policy",
                            "display_name": "添加安全策略",
                            "description": "创建新的安全策略规则",
                            "parameters": [
                                {"key": "policy_name", "type": "String", "required": True, "description": "策略名称"},
                                {"key": "source_zone", "type": "String", "required": True, "description": "源安全域"},
                                {"key": "dest_zone", "type": "String", "required": True, "description": "目标安全域"},
                                {"key": "source_address", "type": "String", "required": True, "description": "源地址对象"},
                                {"key": "dest_address", "type": "String", "required": True, "description": "目标地址对象"},
                                {"key": "service", "type": "String", "required": True, "description": "服务对象"},
                                {"key": "action", "type": "String", "required": True, "description": "动作", "options": ["permit", "deny", "ipsec"]},
                                {"key": "enable_ips", "type": "Boolean", "required": False, "default": False, "description": "启用入侵防护"},
                                {"key": "enable_av", "type": "Boolean", "required": False, "default": False, "description": "启用病毒防护"}
                            ]
                        },
                        {
                            "name": "block_ip_address",
                            "display_name": "封禁IP地址",
                            "description": "将IP地址加入黑名单",
                            "parameters": [
                                {"key": "ip_address", "type": "String", "required": True, "description": "要封禁的IP地址"},
                                {"key": "duration", "type": "Integer", "required": False, "default": 3600, "description": "封禁时长(秒)"},
                                {"key": "reason", "type": "String", "required": False, "description": "封禁原因"},
                                {"key": "block_type", "type": "String", "required": False, "default": "both", "description": "封禁方向", "options": ["inbound", "outbound", "both"]}
                            ]
                        },
                        {
                            "name": "unblock_ip_address",
                            "display_name": "解封IP地址",
                            "description": "从黑名单中移除IP地址",
                            "parameters": [
                                {"key": "ip_address", "type": "String", "required": True, "description": "要解封的IP地址"}
                            ]
                        },
                        {
                            "name": "get_threat_events",
                            "display_name": "获取威胁事件",
                            "description": "获取威胁防护事件日志",
                            "parameters": [
                                {"key": "time_range", "type": "String", "required": False, "default": "1h", "description": "时间范围", "options": ["15m", "1h", "6h", "24h", "7d"]},
                                {"key": "threat_type", "type": "String", "required": False, "description": "威胁类型", "options": ["virus", "trojan", "worm", "spyware", "adware", "dos", "scan", "intrusion"]},
                                {"key": "severity", "type": "String", "required": False, "description": "严重级别", "options": ["info", "low", "medium", "high", "critical"]},
                                {"key": "limit", "type": "Integer", "required": False, "default": 50, "description": "返回数量"}
                            ]
                        },
                        {
                            "name": "get_traffic_statistics",
                            "display_name": "获取流量统计",
                            "description": "获取网络流量统计信息",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": False, "description": "接口名称"},
                                {"key": "time_range", "type": "String", "required": False, "default": "1h", "description": "统计时间范围", "options": ["5m", "1h", "6h", "24h"]}
                            ]
                        },
                        {
                            "name": "update_ips_signatures",
                            "display_name": "更新IPS特征库",
                            "description": "更新入侵防护系统特征库",
                            "parameters": [
                                {"key": "auto_update", "type": "Boolean", "required": False, "default": True, "description": "是否自动更新"}
                            ]
                        },
                        {
                            "name": "configure_url_filtering",
                            "display_name": "配置URL过滤",
                            "description": "配置URL过滤策略",
                            "parameters": [
                                {"key": "category", "type": "String", "required": True, "description": "URL分类", "options": ["social", "entertainment", "shopping", "gambling", "adult", "malware"]},
                                {"key": "action", "type": "String", "required": True, "description": "过滤动作", "options": ["allow", "block", "warn"]},
                                {"key": "apply_to_users", "type": "Array", "required": False, "description": "应用到用户组"}
                            ]
                        },
                        {
                            "name": "get_bandwidth_usage",
                            "display_name": "获取带宽使用情况",
                            "description": "获取带宽使用统计",
                            "parameters": [
                                {"key": "interface", "type": "String", "required": False, "description": "接口名称"},
                                {"key": "top_n", "type": "Integer", "required": False, "default": 10, "description": "返回Top N用户/应用"}
                            ]
                        },
                        {
                            "name": "backup_configuration",
                            "display_name": "备份配置",
                            "description": "备份防火墙配置文件",
                            "parameters": [
                                {"key": "backup_name", "type": "String", "required": True, "description": "备份文件名称"},
                                {"key": "include_logs", "type": "Boolean", "required": False, "default": False, "description": "是否包含日志"}
                            ]
                        },
                        {
                            "name": "system_reboot",
                            "display_name": "系统重启",
                            "description": "重启防火墙系统",
                            "parameters": [
                                {"key": "confirm", "type": "Boolean", "required": True, "description": "确认重启"},
                                {"key": "scheduled_time", "type": "String", "required": False, "description": "计划重启时间 (可选)"}
                            ]
                        }
                    ]
                }
            }
        ]

        # 添加模拟器到数据库
        for sim_data in simulators:
            # 检查是否已存在
            existing = session.query(Application).filter_by(
                category=sim_data['category'],
                name=sim_data['name']
            ).first()

            if not existing:
                app = Application(
                    category=sim_data['category'],
                    name=sim_data['name'],
                    display_name=sim_data['display_name'],
                    description=sim_data['description'],
                    template=sim_data['template'],
                    enabled=True
                )
                session.add(app)
                print(f"Created simulator: {sim_data['display_name']}")
            else:
                # Update existing application with new template
                existing.display_name = sim_data['display_name']
                existing.description = sim_data['description']
                existing.template = sim_data['template']
                print(f"Updated simulator: {sim_data['display_name']}")

        # 创建演示Token
        demo_token = session.query(Token).filter_by(name='Demo Token').first()
        if not demo_token:
            demo_token = Token(
                name='Demo Token',
                user_id=admin.id,
                enabled=True
            )
            session.add(demo_token)
            session.flush()

            # 授权所有应用给演示Token
            apps = session.query(Application).all()
            for app in apps:
                perm = AppPermission(token_id=demo_token.id, application_id=app.id)
                session.add(perm)

            print(f"Created demo token: {demo_token.token}")

        session.commit()
        print("Initialization completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error during initialization: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    init_default_simulators()