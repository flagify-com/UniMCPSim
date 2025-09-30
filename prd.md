OPENAI_API_KEY=sk-proj--qovsGBY65AVfTkObHDNFpAeU***
OPENAI_MODEL=gpt-4o-mini
OPENAI_API_BASE_URL=https://api.openai.com/v1

请阅读我提供给你的PRD文档，充分理解我的需求，然后规划好你的开发计划，并逐项完成内容已经在环境变量文件.env里面配置好了相关的参数，你可以通过程序运行的时候读取并调用关于MCP的启动，我是默认支持以Steamble HTTP的方式进行调用。

在你开发完成之后，帮我默认实现五个以上不同产品的MCP模拟器，建议：virustotal威胁情报，微步在线威胁情报threatbook、青腾云HIDS、IM工具企业微信、腾讯电话会议（创建会议获取链接）、Jira工单、华为交换机、Cisco路由器、深信服防火墙……

请在完成后，编写测试用例程序，放在单独的目录，支持自动化测试验证。

不同的MCP Server在请求参数上支持？token=xx，这种，区分不同的调用端。 

推荐使用sqlite数据库管理不同的模拟服务，提供独立的web后台，支持用户创建不同的模拟器，以及管理token。

项目使用 FastMCP 框架实现标准 MCP 协议支持。视觉外观使用以下样式规范：
    --primary-100:#0077C2;
    --primary-200:#59a5f5;
    --primary-300:#c8ffff;
    --accent-100:#00BFFF;
    --accent-200:#00619a;
    --text-100:#333333;
    --text-200:#5c5c5c;
    --bg-100:#FFFFFF;
    --bg-200:#f5f5f5;
    --bg-300:#cccccc;
      
