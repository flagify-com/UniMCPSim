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

        # 检查是否已有应用数据,如果有则跳过初始化
        app_count = session.query(Application).count()
        if app_count > 0:
            print(f"数据库中已有 {app_count} 个应用,跳过初始化")
            session.close()
            return

        # 定义默认模拟器 (从JSON转换为Python dict)
        simulators = json.loads(r"""[
  {
    "category": "HIDS",
    "name": "QingTengYun-HIDS",
    "display_name": "青藤云HIDS",
    "description": "青藤云主机入侵检测系统，支持查看Windows/Linux主机的安全信息，包括：进程、端口、服务、用户、漏洞、补丁等等信息。",
    "template": {
      "actions": [
        {
          "description": "根据IP获取主机ID",
          "display_name": "根据青藤云客户端的主机IP查询对应的主机ID",
          "name": "get_host_id_from_ip",
          "parameters": [
            {
              "description": "安装了青藤云客户端的主机IP",
              "key": "host_ip",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "获取主机安全告警信息",
          "display_name": "获取安全告警",
          "name": "get_security_alerts_from_host_id",
          "parameters": [
            {
              "description": "安装了青藤云客户端的主机ID",
              "key": "host_id",
              "required": true,
              "type": "String"
            },
            {
              "default": 10,
              "description": "最大返回数量，默认：10",
              "key": "limit",
              "required": false,
              "type": "Integer"
            },
            {
              "default": "24h",
              "description": "时间范围",
              "key": "time_range",
              "options": [
                "1h",
                "6h",
                "24h",
                "7d"
              ],
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "隔离受感染或可疑的主机",
          "display_name": "主机隔离",
          "name": "isolate_host",
          "parameters": [
            {
              "description": "主机ID",
              "key": "host_id",
              "required": true,
              "type": "String"
            },
            {
              "description": "隔离原因",
              "key": "reason",
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "解除主机隔离状态",
          "display_name": "解除主机隔离",
          "name": "release_host",
          "parameters": [
            {
              "description": "主机ID",
              "key": "host_id",
              "required": true,
              "type": "String"
            },
            {
              "description": " 解除隔离原因",
              "key": "reason",
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "获取主机的安全状态和基础信息，报错：操作系统、主机名、进程、端口、用户列表等",
          "display_name": "获取主机状态",
          "name": "get_host_status",
          "parameters": [
            {
              "description": "主机ID",
              "key": "host_id",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": "主机ID是8个数字字母大小写字母的组合。同时，操作系统分Widnows/Linux，且还分具体的发行版。"
  },
  {
    "category": "Meeting",
    "name": "TencentMeeting",
    "display_name": "腾讯会议",
    "description": "在线会议平台",
    "template": {
      "actions": [
        {
          "description": "快速创建并开始即时会议",
          "display_name": "创建即时会议",
          "name": "create_instant_meeting",
          "parameters": [
            {
              "description": "会议主题",
              "key": "subject",
              "required": true,
              "type": "String"
            },
            {
              "description": "会议密码",
              "key": "password",
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "预约未来的会议",
          "display_name": "预约会议",
          "name": "schedule_meeting",
          "parameters": [
            {
              "description": "会议主题",
              "key": "subject",
              "required": true,
              "type": "String"
            },
            {
              "description": "开始时间(ISO格式,GMT+8时间)",
              "key": "start_time",
              "required": true,
              "type": "String"
            },
            {
              "default": 30,
              "description": "持续时间(分钟)，默认30",
              "key": "duration",
              "required": false,
              "type": "Integer"
            },
            {
              "description": "会议密码",
              "key": "password",
              "required": false,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": "参考格式：\n会议主题：XXX会议\n会议时间：2025/10/16 09:30-11:00 (GMT+08:00) 中国标准时间 - 北京\n\n点击链接入会，或添加至会议列表：\nhttps://meeting.tencent.com/dm/GuQjXXIqxxhL"
  },
  {
    "category": "Ticket",
    "name": "Jira",
    "display_name": "Jira工单系统",
    "description": "项目管理和问题跟踪系统",
    "template": {
      "actions": [
        {
          "description": "创建新的工单",
          "display_name": "创建工单",
          "name": "create_issue",
          "parameters": [
            {
              "description": "工单标题",
              "key": "summary",
              "required": true,
              "type": "String"
            },
            {
              "description": "工单描述",
              "key": "description",
              "required": true,
              "type": "String"
            },
            {
              "description": "指派人",
              "key": "assignee",
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "转换工单状态",
          "display_name": "更新工单状态",
          "name": "update_issue_status",
          "parameters": [
            {
              "description": "工单标识符",
              "key": "issue_id",
              "required": true,
              "type": "String"
            },
            {
              "description": "状态转换",
              "key": "transition",
              "options": [
                "To Do",
                "In Progress",
                "Done",
                "Blocked",
                "Resolved",
                "Closed"
              ],
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "将工单分配给指定用户",
          "display_name": "分配工单",
          "name": "assign_issue",
          "parameters": [
            {
              "description": "工单标识符",
              "key": "issue_id",
              "required": true,
              "type": "String"
            },
            {
              "description": "指派人用户名或邮箱",
              "key": "assignee",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "为工单添加评论",
          "display_name": "添加评论",
          "name": "add_comment",
          "parameters": [
            {
              "description": "工单标识符",
              "key": "issue_id",
              "required": true,
              "type": "String"
            },
            {
              "description": "评论内容",
              "key": "comment",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "获取工单的详细信息",
          "display_name": "获取工单详情",
          "name": "get_issue_details",
          "parameters": [
            {
              "description": "工单标识符",
              "key": "issue_id",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": "- 创建工单后，会返回一个数字字母大小写8个字符组成的工单ID。在输出结果中明确工单ID:issue_id，\n- 对指定工单做操作的动作，如果工单id不符合要求，可以返回错误或者失败的消息，提醒用户使用issue_id"
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
            {
              "key": "interface_type",
              "type": "String",
              "required": false,
              "description": "接口类型过滤",
              "options": [
                "ethernet",
                "gigabitethernet",
                "10ge",
                "all"
              ]
            }
          ]
        },
        {
          "name": "display_interface_detail",
          "display_name": "显示接口详细信息",
          "description": "显示指定接口的详细信息",
          "parameters": [
            {
              "key": "interface",
              "type": "String",
              "required": true,
              "description": "接口名称 (如: GigabitEthernet0/0/1)"
            }
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
            {
              "key": "vlan_id",
              "type": "Integer",
              "required": true,
              "description": "VLAN ID (1-4094)"
            },
            {
              "key": "description",
              "type": "String",
              "required": false,
              "description": "VLAN描述"
            }
          ]
        },
        {
          "name": "configure_interface_vlan",
          "display_name": "配置接口VLAN",
          "description": "配置接口的VLAN成员关系",
          "parameters": [
            {
              "key": "interface",
              "type": "String",
              "required": true,
              "description": "接口名称"
            },
            {
              "key": "access_vlan",
              "type": "Integer",
              "required": false,
              "description": "Access VLAN ID"
            },
            {
              "key": "trunk_vlans",
              "type": "String",
              "required": false,
              "description": "Trunk允许的VLAN列表 (如: 1,10,20)"
            },
            {
              "key": "port_mode",
              "type": "String",
              "required": true,
              "description": "端口模式",
              "options": [
                "access",
                "trunk",
                "hybrid"
              ]
            }
          ]
        },
        {
          "name": "display_mac_address_table",
          "display_name": "显示MAC地址表",
          "description": "显示MAC地址学习表",
          "parameters": [
            {
              "key": "vlan_id",
              "type": "Integer",
              "required": false,
              "description": "指定VLAN ID"
            },
            {
              "key": "interface",
              "type": "String",
              "required": false,
              "description": "指定接口"
            }
          ]
        },
        {
          "name": "configure_stp",
          "display_name": "配置STP",
          "description": "配置生成树协议",
          "parameters": [
            {
              "key": "mode",
              "type": "String",
              "required": true,
              "description": "STP模式",
              "options": [
                "stp",
                "rstp",
                "mstp"
              ]
            },
            {
              "key": "enable",
              "type": "Boolean",
              "required": true,
              "description": "是否启用"
            }
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
            {
              "key": "section",
              "type": "String",
              "required": false,
              "description": "配置段落",
              "options": [
                "interface",
                "vlan",
                "stp",
                "all"
              ]
            }
          ]
        },
        {
          "name": "reboot_device",
          "display_name": "重启设备",
          "description": "重启交换机设备",
          "parameters": [
            {
              "key": "confirm",
              "type": "Boolean",
              "required": true,
              "description": "确认重启"
            },
            {
              "key": "save_config",
              "type": "Boolean",
              "required": false,
              "default": true,
              "description": "重启前是否保存配置"
            }
          ]
        }
      ]
    },
    "ai_notes": null
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
            {
              "key": "vlan_id",
              "type": "Integer",
              "required": true,
              "description": "VLAN ID (1-4094)"
            },
            {
              "key": "name",
              "type": "String",
              "required": false,
              "description": "VLAN名称"
            },
            {
              "key": "ports",
              "type": "Array",
              "required": true,
              "description": "端口列表 (如: ['Fa0/1', 'Fa0/2'])"
            }
          ]
        },
        {
          "name": "configure_port",
          "display_name": "配置端口",
          "description": "配置交换机端口",
          "parameters": [
            {
              "key": "interface",
              "type": "String",
              "required": true,
              "description": "接口名称 (如: FastEthernet0/1)"
            },
            {
              "key": "mode",
              "type": "String",
              "required": true,
              "description": "端口模式",
              "options": [
                "access",
                "trunk"
              ]
            },
            {
              "key": "vlan",
              "type": "Integer",
              "required": false,
              "description": "VLAN ID (access模式使用)"
            },
            {
              "key": "allowed_vlans",
              "type": "String",
              "required": false,
              "description": "允许的VLAN (trunk模式使用, 如: '1,10,20')"
            }
          ]
        }
      ]
    },
    "ai_notes": null
  },
  {
    "category": "IT",
    "name": "LDAP",
    "display_name": "Windows LDAP Client",
    "description": "微软Windows AD的LDAP信息查询客户端",
    "template": {
      "actions": [
        {
          "description": "根据输入的AD账号，查询并返回该用户在Windows Active Directory中的基本信息，包括姓名、邮箱、部门等属性。",
          "display_name": "查询AD用户信息",
          "name": "query_ad_user_info",
          "parameters": [
            {
              "description": "AD用户账号（sAMAccountName），例如：zhangsan",
              "key": "ad_account",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "根据指定的AD账号，在Windows Active Directory中禁用（冻结）该用户账户，使其无法登录系统或访问资源。",
          "display_name": "冻结AD用户",
          "name": "disable_ad_user",
          "parameters": [
            {
              "description": "要冻结的AD用户账号（sAMAccountName），例如：zhangsan",
              "key": "ad_account",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "根据指定的AD账号，在Windows Active Directory中启用（解冻）该用户账户，恢复其登录和访问权限。",
          "display_name": "解冻AD用户",
          "name": "enable_ad_user",
          "parameters": [
            {
              "description": "要解冻的AD用户账号（sAMAccountName），例如：zhangsan",
              "key": "ad_account",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": null
  },
  {
    "category": "IT",
    "name": "cmdb",
    "display_name": "CMDB资产管理系统",
    "description": "企业内部CMDB资产管理",
    "template": {
      "actions": [
        {
          "description": "根据指定IP地址查询其所在的运行环境（如生产、测试、研发、云平台）、所属业务系统以及系统负责人的AD用户名等信息，其中系统名、负责人AD用户名必须提供",
          "display_name": "根据IP查询运行环境信息",
          "name": "query_ip_environment_info",
          "parameters": [
            {
              "description": "要查询的IP地址，格式如：192.168.1.100",
              "key": "ip_address",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "根据系统负责人的AD用户名查询其名下所有资产信息，以数组形式返回多个资产记录",
          "display_name": "根据AD用户名查询资产信息",
          "name": "query_assets_by_ad_username",
          "parameters": [
            {
              "description": "AD系统中的用户名，用于标识资产负责人",
              "key": "ad_username",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": null
  },
  {
    "category": "Firewall",
    "name": "USGFirewall",
    "display_name": "华为USG防火墙",
    "description": "公司部署在边界的华为USG防火墙，可用于拦截内外部通讯。",
    "template": {
      "actions": [
        {
          "description": "将指定的IPv4地址加入防火墙的黑名单中，阻止其与内部网络的通信，返回操作成功或失败结果",
          "display_name": "封禁IP地址",
          "name": "block_ip_address",
          "parameters": [
            {
              "description": "要封禁的IPv4地址，格式如：192.168.1.100",
              "key": "ip_address",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "将指定的IPv4地址从防火墙的黑名单中移除，恢复其正常通信权限，返回操作成功或失败结果",
          "display_name": "解封IP地址",
          "name": "unblock_ip_address",
          "parameters": [
            {
              "description": "要解封的IPv4地址，格式如：192.168.1.100",
              "key": "ip_address",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": ""
  },
  {
    "category": "ThreatIntelligence",
    "name": "Threatbook",
    "display_name": "微步在线威胁情报",
    "description": "支持查询网络安全威胁情报领域的文件MD5、域名、ip等各类ioc信息",
    "template": {
      "actions": [
        {
          "description": "查询指定IP地址的威胁情报信息，包括信誉度、威胁标签、地理位置、网络运营商等基础情报数据",
          "display_name": "查询IP威胁情报信息",
          "name": "query_ip_threat_intel",
          "parameters": [
            {
              "description": "需要查询的IP地址（IPv4/IPv6格式）",
              "key": "ip_address",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "查询指定域名的威胁情报信息，包含信誉度、威胁标签、解析IP列表、注册信息等详细数据",
          "display_name": "查询域名威胁情报信息",
          "name": "query_domain_threat_intel",
          "parameters": [
            {
              "description": "需要查询的域名（格式：example.com）",
              "key": "domain_name",
              "required": true,
              "type": "String"
            }
          ]
        },
        {
          "description": "根据MD5哈希值查询文件的威胁情报信息，包括文件类型、检测引擎结果、恶意行为描述等技术细节",
          "display_name": "查询MD5威胁情报信息",
          "name": "query_md5_threat_intel",
          "parameters": [
            {
              "description": "需要查询的32位MD5哈希值（格式：a1b2c3d4e5f6...）",
              "key": "md5_hash",
              "required": true,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": "1.中文返回信息\n2.结构化体现信息\n3.同级别信息可以使用json array"
  },
  {
    "category": "IM",
    "name": "WeWork",
    "display_name": "腾讯企业微信",
    "description": "企业微信IM工具，支持向群机器人推送消息，支持纯文本和Markdown",
    "template": {
      "actions": [
        {
          "description": "通过企业微信群机器人接口向指定群聊发送纯文本格式的消息内容，适用于日常通知或简单信息推送",
          "display_name": "发送纯文本消息",
          "name": "send_plain_text_message",
          "parameters": [
            {
              "description": "需要发送的纯文本消息内容，最大长度2048字符",
              "key": "message_content",
              "required": true,
              "type": "String"
            },
            {
              "description": "目标群机器人的chat_id，不填写时使用默认配置的机器人",
              "key": "chat_id",
              "required": false,
              "type": "String"
            }
          ]
        },
        {
          "description": "通过企业微信群机器人接口发送支持Markdown格式的消息，可实现复杂排版和超链接功能",
          "display_name": "发送Markdown消息",
          "name": "send_markdown_message",
          "parameters": [
            {
              "description": "符合企业微信Markdown规范的格式内容，支持标题/列表/链接等元素",
              "key": "markdown_text",
              "required": true,
              "type": "String"
            },
            {
              "description": "目标群机器人的chat_id，不填写时使用默认配置的机器人",
              "key": "chat_id",
              "required": false,
              "type": "String"
            }
          ]
        }
      ]
    },
    "ai_notes": ""
  }
]""")

        # 添加模拟器到数据库 (一次性批量添加)
        print(f"开始初始化 {len(simulators)} 个应用...")
        for sim_data in simulators:
            app = Application(
                category=sim_data['category'],
                name=sim_data['name'],
                display_name=sim_data['display_name'],
                description=sim_data['description'],
                template=sim_data['template'],
                ai_notes=sim_data.get('ai_notes'),
                enabled=True
            )
            session.add(app)
            print(f"  - 创建应用: {sim_data['display_name']}")

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

            print(f"\n创建演示Token: {demo_token.token}")

        session.commit()
        print("\n初始化完成!")

    except Exception as e:
        session.rollback()
        print(f"初始化过程中出错: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    init_default_simulators()
