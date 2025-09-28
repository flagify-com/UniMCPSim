

- [1.文档说明](#1文档说明)
  - [1.1 文档使用对象](#11-文档使用对象)
  - [1.2 文档符号说明](#12-文档符号说明)
  - [1.3 接口URL说明](#13-接口url说明)
  - [1.4 接口认证字段](#14-接口认证字段)
- [2.接口说明](#2接口说明)
  - [2.1 响应体格式](#21-响应体格式)
  - [2.2 常用返回码](#22-常用返回码)
  - [2.3 系统内置的ErrorCode](#23-系统内置的errorcode)
  - [2.4 响应时的公共字段](#24-响应时的公共字段)
  - [2.5 分页查询的响应格式](#25-分页查询的响应格式)
- [3.接口列表](#3接口列表)
  - [3.1 查询所有可用的剧本](#31-查询所有可用的剧本)
      - [请求类型](#请求类型)
      - [请求路径](#请求路径)
      - [路径参数](#路径参数)
      - [请求参数](#请求参数)
      - [请求体](#请求体)
      - [请求示例](#请求示例)
      - [响应示例](#响应示例)
      - [响应字段说明](#响应字段说明)
  - [3.2 查询所有可用的动作](#32-查询所有可用的动作)
      - [请求类型](#请求类型-1)
      - [请求路径](#请求路径-1)
      - [路径参数](#路径参数-1)
      - [请求参数](#请求参数-1)
      - [请求体](#请求体-1)
      - [请求示例](#请求示例-1)
      - [响应示例](#响应示例-1)
      - [响应字段说明](#响应字段说明-1)
  - [3.3 获取单个剧本执行所需要的参数](#33-获取单个剧本执行所需要的参数)
      - [请求类型](#请求类型-2)
      - [请求路径](#请求路径-2)
      - [路径参数](#路径参数-2)
      - [请求参数](#请求参数-2)
      - [请求体](#请求体-2)
      - [请求示例](#请求示例-2)
      - [响应示例](#响应示例-2)
      - [响应字段说明](#响应字段说明-2)
  - [3.4 执行单个剧本或动作](#34-执行单个剧本或动作)
      - [请求类型](#请求类型-3)
      - [请求路径](#请求路径-3)
      - [路径参数](#路径参数-3)
      - [请求参数](#请求参数-3)
      - [请求体](#请求体-3)
      - [请求示例](#请求示例-3)
      - [响应示例](#响应示例-3)
  - [3.5 获取单个动作或剧本的执行状态](#35-获取单个动作或剧本的执行状态)
      - [请求类型](#请求类型-4)
      - [请求路径](#请求路径-4)
      - [路径参数](#路径参数-4)
      - [请求参数](#请求参数-4)
      - [请求体](#请求体-4)
      - [请求示例](#请求示例-4)
      - [响应示例](#响应示例-4)
      - [响应字段说明](#响应字段说明-3)
  - [3.6 创建事件(人工创建事件)](#36-创建事件人工创建事件)
      - [请求类型](#请求类型-5)
      - [请求路径](#请求路径-5)
      - [路径参数](#路径参数-5)
      - [请求参数](#请求参数-5)
      - [请求体](#请求体-5)
      - [请求示例](#请求示例-5)
      - [响应示例](#响应示例-5)
      - [响应字段说明](#响应字段说明-4)
  - [3.7 向作战室拉人](#37-向作战室拉人)
      - [请求类型](#请求类型-6)
      - [请求路径](#请求路径-6)
      - [路径参数](#路径参数-6)
      - [请求参数](#请求参数-6)
      - [请求体](#请求体-6)
      - [请求示例](#请求示例-6)
      - [响应示例](#响应示例-6)
  - [3.8 获取剧本或动作执行结果](#38-获取剧本或动作执行结果)
      - [请求类型](#请求类型-7)
      - [请求路径](#请求路径-7)
      - [路径参数](#路径参数-7)
      - [请求参数](#请求参数-7)
      - [请求体](#请求体-7)
      - [请求示例](#请求示例-7)
      - [响应示例](#响应示例-7)
      - [响应字段说明](#响应字段说明-5)
  - [3.9 获取所有的事件类型](#39-获取所有的事件类型)
      - [请求类型](#请求类型-8)
      - [请求路径](#请求路径-8)
      - [路径参数](#路径参数-8)
      - [请求参数](#请求参数-8)
      - [请求体](#请求体-8)
      - [请求示例](#请求示例-8)
      - [响应示例](#响应示例-8)
      - [响应字段说明](#响应字段说明-6)
  - [3.10 获取所有的用户信息](#310-获取所有的用户信息)
      - [请求类型](#请求类型-9)
      - [请求路径](#请求路径-9)
      - [路径参数](#路径参数-9)
      - [请求参数](#请求参数-9)
      - [请求体](#请求体-9)
      - [请求示例](#请求示例-9)
      - [响应示例](#响应示例-9)
      - [响应字段说明](#响应字段说明-7)
  - [3.11 获取某个事件的详情](#311-获取某个事件的详情)
      - [请求类型](#请求类型-10)
      - [请求路径](#请求路径-10)
      - [路径参数](#路径参数-10)
      - [请求参数](#请求参数-10)
      - [请求体](#请求体-10)
      - [请求示例](#请求示例-10)
      - [响应示例](#响应示例-10)
      - [响应字段说明](#响应字段说明-8)
  - [3.12 获取某一个活动的节点执行结果](#312-获取某一个活动的节点执行结果)
      - [请求类型](#请求类型-11)
      - [请求路径](#请求路径-11)
      - [路径参数](#路径参数-11)
      - [请求参数](#请求参数-11)
      - [请求体](#请求体-11)
      - [请求示例](#请求示例-11)
      - [响应示例](#响应示例-11)
  - [3.13 获取作战室右侧某个事件的成员信息](#313-获取作战室右侧某个事件的成员信息)
      - [请求类型](#请求类型-12)
      - [请求路径](#请求路径-12)
      - [路径参数](#路径参数-12)
      - [请求参数](#请求参数-12)
      - [请求体](#请求体-12)
      - [请求示例](#请求示例-12)
      - [响应示例](#响应示例-12)
  - [3.14 创建事件类型](#314-创建事件类型)
      - [请求类型](#请求类型-13)
      - [请求路径](#请求路径-13)
      - [路径参数](#路径参数-13)
      - [请求参数](#请求参数-13)
      - [请求体](#请求体-13)
      - [请求示例](#请求示例-13)
      - [响应示例](#响应示例-13)
  - [3.15 修改事件类型](#315-修改事件类型)
      - [请求类型](#请求类型-14)
      - [请求路径](#请求路径-14)
      - [路径参数](#路径参数-14)
      - [请求参数](#请求参数-14)
      - [请求体](#请求体-14)
      - [请求示例](#请求示例-14)
      - [响应示例](#响应示例-14)
  - [3.16 修改事件负责人（支持角色）](#316-修改事件负责人支持角色)
      - [请求类型](#请求类型-15)
      - [请求路径](#请求路径-15)
      - [路径参数](#路径参数-15)
      - [请求参数](#请求参数-15)
      - [请求体](#请求体-15)
      - [请求示例](#请求示例-15)
      - [响应示例](#响应示例-15)
  - [3.17  查询所有可用的剧本（不分页）](#317--查询所有可用的剧本不分页)
      - [请求类型](#请求类型-16)
      - [请求路径](#请求路径-16)
      - [路径参数](#路径参数-16)
      - [请求参数](#请求参数-16)
      - [请求体](#请求体-16)
      - [请求示例](#请求示例-16)
      - [响应示例](#响应示例-16)
  - [3.18  添加事件成员（支持单个用户名、ID，数组）](#318--添加事件成员支持单个用户名id数组)
      - [请求类型](#请求类型-17)
      - [请求路径](#请求路径-17)
      - [路径参数](#路径参数-17)
      - [请求参数](#请求参数-17)
      - [请求体](#请求体-17)
      - [请求示例](#请求示例-17)
      - [响应示例](#响应示例-17)
  - [3.19  删除事件成员（支持单个用户名、ID，数组）](#319--删除事件成员支持单个用户名id数组)
      - [请求类型](#请求类型-18)
      - [请求路径](#请求路径-18)
      - [路径参数](#路径参数-18)
      - [请求参数](#请求参数-18)
      - [请求体](#请求体-18)
      - [请求示例](#请求示例-18)
      - [响应示例](#响应示例-18)
  - [3.20  添加事件责任人（仅支持owners数组）](#320--添加事件责任人仅支持owners数组)
      - [请求类型](#请求类型-19)
      - [请求路径](#请求路径-19)
      - [路径参数](#路径参数-19)
      - [请求参数](#请求参数-19)
      - [请求体](#请求体-19)
      - [请求示例](#请求示例-19)
      - [响应示例](#响应示例-19)
  - [3.21  删除事件责任人（仅支持owners数组）](#321--删除事件责任人仅支持owners数组)
      - [请求类型](#请求类型-20)
      - [请求路径](#请求路径-20)
      - [路径参数](#路径参数-20)
      - [请求参数](#请求参数-20)
      - [请求体](#请求体-20)
      - [请求示例](#请求示例-20)
      - [响应示例](#响应示例-20)
  - [3.22  在线人员查询](#322--在线人员查询)
      - [请求类型](#请求类型-21)
      - [请求路径](#请求路径-21)
      - [路径参数](#路径参数-21)
      - [请求参数](#请求参数-21)
      - [请求体](#请求体-21)
      - [请求示例](#请求示例-21)
      - [响应示例](#响应示例-21)

### 1.文档说明
#### 1.1 文档使用对象
本文档仅适用于使用Octomation1.1.0及以上版本的用户。本文档记录将会根据项目需求，保持一定的迭代更新。如有修改请另行拷贝该文档并声明文档的修改版本号，例如：update 1.0.0。
Openapi功能用户第三方系统使用Octomation页面相关功能与token对应的权限有关。
#### 1.2 文档符号说明
文档中使用└来代表该字段是某一类中的重要字段，xxxList这样的一般后面紧跟的是其列表中的类的重要字段
#### 1.3 接口URL说明
默认请求示例中的请求地址为编者自己的服务地址：https://192.168.2.186,客户拷贝时需要修改为自己的服务地址

#### 1.4 接口认证字段
默认所有的请求都要先经过认证的，认证方式为：header请求头里面添加一个hg-token字段（该字段需要从系统中：```系统配置-->认证授权-->Token管理```，新建一个带有角色的token）。该字段是jwt类型的认证信息

```commandline
curl --location --request GET 'https://192.168.2.186/接口URI' \
--header 'hg-token: xxx'
``` 

### 2.接口说明
#### 2.1 响应体格式
```JSON
{
    "code": 500,
    "msg":"执行成功",
    "result":{
      "data":"1.2.3.4"
    }
}
```

| 名称 | 类型      | 是否必须 | 描述 | 示例|
| ----  |---------| ----  | ----  |----  |
| code	| integer |	是|	返回码|	500|
|result| 	json   |	是	|返回结果数据|{"data":"1.2.3.4"}|
|msg	| string	 |否	|返回信息（一般异常时使用）|	执行成功|
#### 2.2 常用返回码

| 返回码 | 描述|
|-----| ----  |
| 200	 |服务器操作成功或者成功返回用户请求的数据|
| 201	 |用户新建或修改数据成功|
| 202 |表示一个请求已经被服务器接收，进入后台排队（异步任务）|
| 204	 |用户删除数据成功|
| 400 |用户发出的请求有错误|
| 401	 |表示用户没有权限（令牌、用户名、密码错误）|
| 404	 |表示用户得到授权，但是访问是被禁止的|
|406|用户发出的请求针对的是不存在的记录，服务器没有进行操作|
|412	|用户请求的资源被永久删除，且不会再得到的|
|413	|用户请求超时|
|500|服务器发生错误，用户将无法判断发出的请求是否成功|

#### 2.3 系统内置的ErrorCode
|编号key|	code|	描述|
| ----  |-----| ----  |
|0|NO|未执行|
|100|	WAITING_DELAY|	延迟节点，等待执行|
|101	|WAITING_APPROVE	|审批节点，等待审批|
|102|	WAITING_VIRTUAL	|人工节点，等待手工执行、确认|
|104|	WAITING_ASYNC|	异步节点，等待下次执行|
|105	|WAITING_COLLECT	|等待收集（收集节点）|
|150|	DELAY_DONE	|延时结束，等待执行|
|151	|APPROVE_DONE	|审批完成|
|200	|SUCCESS|	成功|
|201	|SUCCESS_MOCK|	模拟方式执行，成功|
|202	|FAIL_PARTLY	|节点需要循环执行，部分执行成功，部分执行失败|
|203	|SUCCESS_RE	|执行失败，再次执行成功|
|204	|SUCCESS_PARTLY	|部分成功|
|300	|RUNNING	|执行中|
|400	|COMPLETE_DELAY	|延时,等待任务执行|
|501	|APPROVE_REJECT_BY_USER	|审批拒绝|
|502	|APPROVE_EXPIRED	|审批超时|
|503	|VIRTUAL_REJECT_BY_USER	|人工节点放弃执行|
|504	|VIRTUAL_EXPIRED	|人工节点手工确认超时|
|505	|ASYNC_EXPIRED	|异步节点超时|
|506	|COLLECT_EXPIRED|	信息收集超时|
|200000	|VALIDATION_FAILED|	参数校验失败|
|200002	|BAD_VARIABLE	|变量错误 [%s]|
|200004	|BAD_REQUEST	|请求参数错误 [%s]|
|200101	|ACTION_IN_USE	|动作在系统中被使用 [%s]|
|200201	|ASSET_IN_USE	|资产在系统中被使用 [%s]|
|200300	|CONFIG_BLOCK_ACTION	|配置阻断|
|200301	|PLAYBOOK_IN_USE	|剧本在系统中有用|
|500000	|LOGIN_CONTINUE	|需要继续登录|
|500001	|LOGIN_PWD_ERROR	|用户登录失败：用户名密码错误,超过%d次将会被锁定|
|500002	|TOTP_ERROR	|验证码错误|
|500003	|LOGIN_ACCOUNT_DISABLED	|用户登录失败：账号被禁用|
|500004	|LOGIN_PSWD_EXPIRED	|用户登录失败：密码已过期|
|500005	|LOGIN_TYPE_OFF	|认证此用户类型的方式未开启|
|500006	|NOT_PERMIT	|无权限操作|
|500010	|ACCOUNT_EFFETIVE_TIME	|请在账户有效期内登录[%s]-[%s]|
|500100	|AI_INVOKE_ERROR	|AI服务报错|
|500101	|PLAYBOOK_INVOKE_ERROR	|调用Executor报错|
|503400	|PLAYBOOK_NOT_EXISTS	|剧本不存在，请确认要执行的剧本是否已经创建成功|
|503401	|PLAYBOOK_ASSIGN_PARAM_EXCEPTION	|动作获取执行参数异常，请确认该动作的执行参数配置是否正确|
|503503	|ACTION_HTTP_EXCEPTION	|调用动作引擎异常，请确认动作引擎的url、host配置是否正确,动作引擎服务是否正常|
|503504	|RULE_HTTP_EXCEPTION	|调用规则引擎异常，请确认动作引擎的url、host配置是否正确,动作引擎服务是否正常|
|503506	|PLAYBOOK_SAVE_DATABASE	|保存执行结果失败，请确认数据库服务是否正常|
|503507	|PLAYBOOK_QUERY_DATABASE	|查询数据库失败，请确认数据库服务是否正常|
|503508	|PLAYBOOK_JOB_CREATE_ERROR	|创建定时任务失败，请确认该任务是否已经被创建|
|503509	|PLAYBOOK_APPROVE_CREATE_ERROR	|创建审批失败|
|503510	|ACTION_EXEC_STATUS_SUCCESS	|动作已经执行成功|
|503511	|ACTION_EXEC_STATUS_RUNNING	|动作正在运行|
|503512	|NODE_ALREADY_EXEC_SUCC	|节点已经执行成功|
|503513	|PLAYBOOK_ALREADY_EXECUTED	|剧本已经执行完成|
|503515	|PLAYBOOK_VIRTUAL_CREATE_ERROR	|创建虚拟节点失败，请确认该任务是否已经被创建|
|503516	|ASYNC_NODE_NOT_MEETING_CONDITION	|异步节点执行没有满足设定条件，请确认执行动作、退出条件配置是否正确|
|503517	|PLAYBOOK_VIRTUAL_CREATEE_ERROR	|创建虚拟节点失败，请确认该任务是否已经被创建|
|503518	|STRICT_MODEL_NO_APPROVER	|当前是严格模式，但是没有配置剧本审批人|
|503519	|ACTION_NOT_CORRESPOND_OS	|动作所需的操作没有相应的执行引擎|
|503520	|ACTION_TIMEOUT_EXCEPTION	|调用动作引擎超时，请确认动作的执行的耗时|
|503521	|ACTION_PARAM_VALUE_NOT_MATCH_TYPE	|动作参数的值与类型不匹配|
|503522	|PLAYBOOK_COLLECTION_CREATE_ERROR	|创建信息节点失败，请确认该任务是否已经被创建|
|504400	|RULE_PARAM_ILLEGAL	|规则参数异常，请确认规则配置是否正确|
|504500	|RULE_SESSION_LOAD_EXCEPTION	|规则初始化失败,请确认规则的配置是否正确|
|504501	|RULE_RUN_EXCEPTION	|规则执行异常，请确认规则配置是否正确|
|505000	|ACTION_UNKNOW_EXCEPTION	|动作执行未知错误，请确认动作的功能是否正常或动作的参数、执行资源配置是否正确|
|505410	|ACTION_NOT_EXISTS	|动作不存在，请确认该动作是否已经导入成功或者等待动作加载完成|
|505411	|ACTION_LANGUAGE_NOT_SUPPORTED	|编写应用的语言不支持|
|505500	|ACTION_RESP_FAIL	|执行动作返回失败的错误码|
|505501	|ACTION_RESP_CODE_FAIL	|执行动作，未返回错误码|
|505502	|ACTION_SOURCE_LOAD_FAIL	|加载应用逻辑文件失败|
|505503	|ACTION_FUNCTION_ERROR	|执行动作，未返回结果|
|505504	|PYTHON_HOME_NOT_FOUND	|未找到python路径，请确认系统是否正确安装|
|505505	|ACTION_RESP_BLANK	|执行动作，未返回结果|
|505506	|RULE_RESP_CODE_FAIL	|规则执行完成，但是返回了错误信息|
|505507	|RULE_RESP_NOT_JSON	|规则执行完成，但是返回的结果非json格式|
|505508	|FUNCTION_COMPILE_ERROR	|函数编译错误|
|505509	|FUNCTION_CREATE_SESSION_ERROR	|创建函数环境错误|
|505510	|FUNCTION_INVOKE_ERROR	|调用函数方法错误|
|505600	|FUNC_UNKNOW_EXCEPTION	|函数执行未知错误，请确认动作的功能是否正常或动作的参数、执行资源配置是否正确|
|505601	|FUNC_NOT_EXISTS	|函数不存在，请确认该动作是否已经导入成功或者等待动作加载完成|
|505602	|FUNC_RESP_CODE_FAIL	|执行函数，未返回错误码|
|505603	|FUNC_RESP_BLANK	|执行函数，未返回结果|
|506500	|REPORT_INNER_ERROR	|系统内部异常|
|506501	|REPORT_EXECUTE_ERROR	|数据生成失败|
|506999	|REPORT_UNKOWN_ERROR	|系统错误，数据生成失败|
|510000	|LISENCE_EMPTY	|没有许可，请使用admin用户登陆，并替换许可|
|510010	|LISENCE_EXPIRED	|许可已失效，请使用admin用户登陆，并替换许可|
|510020	|LISENCE_NOT_AVAILABLE	|许可不可用，请替换证书|
|510025	|LISENCE_LIMITED	|超过许可限制|
|510030	|LISENCE_LIMIT_OBJECT_EMPTY	|许可对象为空|
|600000	|DUPTY_OBJECT	|重复的对象|
|900000	|INTERNAL_ERROR	|系统内部错误|
|901001	|ES_ERROR	|系统内部错误: es异常|
|910000	|CACHE_ERROR	|系统内部错误: 缓存异常|
#### 2.4 响应时的公共字段
说明：以下的字段在具体接口中无特殊意义的话，默认省略

| 字段 | 类型      | 描述 | 示例|
| ----  |---------|  ----  |----  |
|createdBy  |       	string|	创建者	|"createdBy": "admin"|
|createdNickName	|string|	创建者昵称|"createdNickName": "雾宝宝"|
|modifiedNickName|string|	修改者昵称	|"modifiedNickName" : "雾宝宝"|
|createTime	|timestamp|	创建时间	|"createTime": "2021-01-27 16:27:31"|
|deleted |	boolean|	是否删除	|"deleted": false|
|modifiedBy |    	string	|修改者	|"modifiedBy": "admin"|
|status|	string|	状态	|"status": "ON"|
|updateTime|	timestamp	|修改时间	|"updateTime": "2021-01-27 17:45:14"|
#### 2.5 分页查询的响应格式
```JSON
{

"code": 200,
    "result": {
        "content": [...],
        "pageable": {
            "sort": {
                "sorted": true,
                "unsorted": false,
                "empty": false
            },
            "offset": 0,
            "pageNumber": 0,
            "pageSize": 2,
            "paged": true,
            "unpaged": false
        },
        "last": false,
        "totalPages": 11566,
        "totalElements": 23132,
        "number": 0,
        "size": 2,
        "sort": {
            "sorted": true,
            "unsorted": false,
            "empty": false
        },
        "numberOfElements": 2,
        "first": true,
        "empty": false
    }
}
```
     说明：   

        a. content是返回的结果数组,其中“[...]”代表省略具体的数据

        b. pageable当中的pageNumber代表当前第几页（第一页是0），pageSize代表每页最大条数

        c. totalElements代表总条数

### 3.接口列表
#### 3.1 查询所有可用的剧本
###### 请求类型
POST
###### 请求路径 
/api/playbooks
###### 路径参数
###### 请求参数

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|page	|int	|是	请求查询的页数|
|size	|int	是	请求查询的每页记录条数|
###### 请求体    
|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|publishStatus	|string|	是	|剧本的发布状态（当该参数的值为ONLINE时，即可查询可用的剧本）|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/api/playbooks?page=1&size=10' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
 "publishStatus":"ONLINE"
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": {
        "content": [
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "admin",
                "createdNickName": "管理员",
                "modifiedNickName": "管理员",
                "createTime": "2021-01-27 15:48:53",
                "updateTime": "2021-01-27 16:23:57",
                "id": 3633676872182754,
                "name": "playbook_dc82dd55efd90941979cfad6a577b39a",
                "drawJson": null,
                "description": "IP信息增强-演示",
                "displayName": "demo_ip情报信息调查",
                "nodeList": null,
                "nodeEdageList": null,
                "sceneList": [
                    {
                        "status": null,
                        "deleted": null,
                        "createdBy": null,
                        "modifiedBy": null,
                        "createTime": null,
                        "updateTime": null,
                        "createdNickName": null,
                        "modifiedNickName": null,
                        "id": null,
                        "name": "scene_important",
                        "display": "重要场景",
                        "severity": null,
                        "effective": null,
                        "dutyRelation": null
                    }
                ],
                "labelList": [
                    {
                        "status": null,
                        "deleted": null,
                        "createdBy": null,
                        "modifiedBy": null,
                        "createTime": null,
                        "updateTime": null,
                        "createdNickName": null,
                        "modifiedNickName": null,
                        "id": null,
                        "name": "必备"
                    }
                ],
                "externalInfoList": [],
                "grade": null,
                "publishStatus": "ONLINE",
                "playbookCategory": "COMMONEVENT"
            }
        ],
        "pageable": {
            "sort": {
                "sorted": true,
                "unsorted": false,
                "empty": false
            },
            "pageSize": 10,
            "pageNumber": 0,
            "offset": 0,
            "paged": true,
            "unpaged": false
        },
        "last": true,
        "totalPages": 1,
        "totalElements": 1,
        "first": true,
        "sort": {
            "sorted": true,
            "unsorted": false,
            "empty": false
        },
        "size": 10,
        "number": 0,
        "numberOfElements": 1,
        "empty": false
    }
}
```
###### 响应字段说明
|参数名称	| 参数类型	   | 描述                                            |
|-----|---------|-----------------------------------------------|
|id| 	long   | 	剧本的ID                                        |
|name	| string  | 	剧本的名字                                        |
|drawJson	| string	 | 剧本的绘图数据                                       |
|description| string  | 	剧本的描述                                        |
|displayName	| string  | 	剧本的展示名                                       |
|publishStatus	| string  | 剧本的发布状态:<br/>DRAFT 草稿，未经校验<br/>ONLINE 上线，校验通过 |
|grade	|         | 剧本的分级                                         |
|└id	|long	|分级ID|
|└name	|string|	分级名称|
|└parentGradeId	|long|	父分级ID|
|playbookCategory	|string	|剧本的类型:<br/>COMMONEVENT 普通事件类型(新建剧本的默认类型)<br/>SIGNINOUT 登陆登出类型<br/>DEPULICATION 去重类型|
|sceneList	|array|	剧本的场景列表|
|└id| long	|场景ID|
|└name	|string|	场景名称|
|└display	|string|	场景展示名|
|└severity	|string|	场景优先级|
|└effective	|boolean|	是否生效为当前场景|
|labelList	|array	|剧本的标签列表|
|└id	|long|	标签ID|
|└name|	string|	标签名|
#### 3.2 查询所有可用的动作
###### 请求类型
POST
###### 请求路径 
/api/apps
###### 路径参数
###### 请求参数
|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|page	|int	|是	请求查询的页数|
|size	|int	是	请求查询的每页记录条数|
###### 请求体
{}
###### 请求示例
````commandline
curl --location --request POST 'https://192.168.2.186/api/apps?page=1&size=10' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
}'
````
###### 响应示例
````json
{
    "code": 200,
    "result": {
        "content": [
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "admin",
                "createdNickName": "管理员",
                "modifiedNickName": "管理员",
                "createTime": "2021-01-27 15:24:01",
                "updateTime": "2021-01-27 15:24:01",
                "id": 3923576105249034,
                "name": "sdktest",
                "description": "SDK测试-java",
                "displayName": null,
                "version": "1.0",
                "readMePath": "app/share/sdktest/1.0/readme.html",
                "iconfilePath": "app/share/sdktest/1.0/sdk.jpg",
                "os": null,
                "logicLanguage": "JAVA",
                "logicLanguageVersion": "",
                "category": "大屏数据统计",
                "assetVariableList": [
                    {
                        "name": "input_string",
                        "required": false,
                        "type": "STRING",
                        "description": "输入rigit,资产执行正确，否则失败",
                        "lable": null,
                        "defaultValue": null,
                        "optionsList": null,
                        "multiSelected": false,
                        "concat": null,
                        "order": 5,
                        "array": false
                    }
                ],
                "appActionList": [
                    {
                        "status": "ON",
                        "deleted": false,
                        "createdBy": "admin",
                        "modifiedBy": "admin",
                        "createdNickName": "管理员",
                        "modifiedNickName": "管理员",
                        "createTime": "2021-01-27 15:24:01",
                        "updateTime": "2021-01-27 15:24:01",
                        "id": 3923576123860691,
                        "appId": null,
                        "name": "SDKSendMessage",
                        "actionType": "ACTION",
                        "readonly": true,
                        "description": "SDK发送作战室消息",
                        "displayName": null,
                        "classify": "N",
                        "os": null,
                        "logicLanguage": "JAVA",
                        "logic": "com.shakespeare.action.sdk.SendMessage",
                        "retryTimes": 0,
                        "sleepSeconds": 0,
                        "quartzEtl": "",
                        "parameterVariableList": [
                            {
                                "name": "msg",
                                "required": true,
                                "type": "STRING",
                                "description": "msg",
                                "lable": null,
                                "defaultValue": null,
                                "optionsList": null,
                                "multiSelected": false,
                                "concat": null,
                                "order": 1,
                                "array": false
                            }
                        ],
                        "resultVariableList": [
                            {
                                "description": "msg",
                                "valueType": "STRING",
                                "dataPath": "action_result.msg",
                                "exampleValues": null
                            }
                        ],
                        "resultDisplayTmptType": "JS",
                        "isTest": false,
                        "resultDisplayTmpt": "<div class=\"ant-table ant-table-default ant-table-bordered\">   <div class=\"ant-table-content\">       <div class=\"ant-table-body\">           <table>               <thead class=\"ant-table-thead\">                   <tr>                       <th>                           <span class=\"ant-table-header-column\">                               <div>                                   <span class=\"ant-table-column-title\">msg</span>                                   <span class=\"ant-table-column-sorter\"></span>                               </div>                           </span>                       </th>                       <th>                           <span class=\"ant-table-header-column\">                               <div>                                   <span class=\"ant-table-column-title\">content</span>                                   <span class=\"ant-table-column-sorter\"></span>                               </div>                           </span>                       </th>                   </tr>               </thead>               <tbody class=\"ant-table-tbody\">               {{each action_results as action_result}}               {{if action_result.data}}                   <tr class=\"ant-table-row\">                       <td>{{action_result.data.msg}}</td>                       <td>{{action_result.data.content}}</td>                   </tr>               {{/if}}               {{/each}}               </tbody>           </table>       </div>   </div></div>",
                        "quartz": false
                    }
                ],
                "appAssetList": [
                    {
                        "status": "ON",
                        "deleted": false,
                        "createdBy": "admin",
                        "modifiedBy": "admin",
                        "createdNickName": "管理员",
                        "modifiedNickName": "管理员",
                        "createTime": "2021-01-27 15:35:03",
                        "updateTime": "2021-01-27 15:35:03",
                        "id": 3923619502927750,
                        "appId": 3923576105249034,
                        "name": "sendMessageToWarroom",
                        "description": "向作战室里面发送一条消息",
                        "productVendor": "雾帜智能",
                        "productName": "honeyguide",
                        "assetSettingList": [
                            {
                                "name": "user",
                                "value": null,
                                "type": "STRING"
                            }
                        ],
                        "actionPermissionMap": {},
                        "lastHealthCheckTime": null,
                        "healthStatus": "NOT_CHECK",
                        "actionEngineType": null
                    }
                ],
                "logicContent": null,
                "requireAsset": false,
                "actionEngineType": null
            }
        ],
        "pageable": {
            "sort": {
                "sorted": true,
                "unsorted": false,
                "empty": false
            },
            "pageSize": 10,
            "pageNumber": 0,
            "offset": 0,
            "paged": true,
            "unpaged": false
        },
        "last": true,
        "totalPages": 1,
        "totalElements": 5,
        "first": true,
        "sort": {
            "sorted": true,
            "unsorted": false,
            "empty": false
        },
        "size": 10,
        "number": 0,
        "numberOfElements": 5,
        "empty": false
    }
}

````
###### 响应字段说明
|参数名称	| 参数类型	     | 描述                                            |
|-----|-----------|-----------------------------------------------|
|id	| long      |	应用的ID|
|name	| string	   |应用的名称|
|description	| string	   |应用的描述|
|displayName	| string	   |应用的展示名|
|version	| string	   |应用的版本|
|readMePath| 	string	  |应用的readMe路径|
|iconfilePath	| string    |	应用的图标文件路径|
|os| 	string   |	应用支持的操作系统|
|logicLanguage| 	string	  |应用所使用的逻辑语言|
|logicLanguageVersion| 	string   |	应用所使用的逻辑语言版本|
|category	| string	   |应用的类别|
|assetVariableList	| array	    |应用的资产变量列表|
|└└name| 	string	  |资产变量的名字|
|└└required| 	boolean	 |资产变量是否必须|
|└└type	| string	   |资产变量的类型|
|└└description	| string    |	资产变量的描述|
|└└lable	| string    |	资产变量的显示名|
|└└defaultValue	| string    |	资产变量的默认值|
|└└optionsList	| string	   |资产变量的可选项列表（字符串形式）|
|└└multiSelected| 	boolean	 |资产变量是否支持多选|
|└└concat	| string	   |资产变量支持多选时可指定的连接符|
|└└order	| int       |	资产变量的序号|
|└└array	| boolean   |	资产变量数组是否支持选择多个值|
|appActionList	| array	    |应用的动作列表|
|└id	| long      |	动作的ID|
|└appId	| long      |	动作所属的应用ID|
|└name	| string    |	动作的名字|
|└actionType| 	string   |	动作的类型|
|└readonly	| boolean   |	动作是否只读|
|└description| 	string	  |动作的描述|
|└displayName	| string	   |动作的展示名|
|└classify	| string	   |动作分类|
|└os	| string    |	动作所支持的操作系统|
|└logicLanguage	| string    |	动作使用的逻辑语言|
|└logic	| string	   |动作的逻辑|
|└retryTimes| 	int      |	动作的重试次数|
|└sleepSeconds| 	int	     |动作的延迟时间|
|└quartzEtl	| string    |	动作的定时执行表达式|
|└parameterVariableList| 	array    |	动作的参数变量列表|
|└└name	| string    |	动作参数名称|
|└└required	| boolean   |	动作参数是否必须|
|└└type	| string	   |动作参数类型|
|└└description| 	string	  |动作参数描述|
|└└lable	| string    |	动作参数显示名|
|└└defaultValue| 	string	  |动作参数的默认值|
|└└optionsList	| string	   |动作参数的可选项列表（字符串形式）|
|└└multiSelected	| boolean   |	动作参数是否支持多选|
|└└concat	| string    |	动作参数支持多选时可指定的连接符|
|└└order	| int	      |动作参数的序号|
|└└array	| boolean   |	动作参数数组是否支持选择多个值|
|└resultVariableList| 	array    |	动作的执行结果变量列表|
|└└description	| string    |	动作执行结果的描述|
|└└valueType	| string	   |动作执行结果的值类型|
|└└dataPath	| string	   |动作执行结果的数据路径|
|└└exampleValues| 	string	  |动作执行结果示例值|
|└resultDisplayTmptType	| string	   |动作执行结果展示模版类型|
|└isTest	| boolean   |	动作是否可测试|
|└resultDisplayTmpt	| string	   |动作执行结果展示模版|
|└quartz	| boolean	  |动作是否开启定时执行|
|appAssetList	| array     |	应用的资产列表|
|└id	| long	     |资产ID|
|└appId	| long	     |资产所属的应用的ID|
|└name	|string|	资产名字|
|└description|	string	|资产描述|
|└productVendor	|string	|资产的产品供应商|
|└productName	|string	|资产的产品名称|
|└assetSettingList	|array	|资产配置属性列表|
|└└name	|string|	配置属性名称|
|└└value	|string	|配置属性的值|
|└└type	|string|	配置属性的类型|
|└actionPermissionMap	|map	|资产的权限控制map|
|└lastHealthCheckTime	|date	|资产上次健康检查时间|
|└healthStatus	|string	|资产的健康状态|
|└actionEngineType	|string	|资产的执行引擎类型|
|logicContent	|string	|应用的逻辑内容|
|requireAsset	|boolean|	应用是否需要有资产|
|actionEngineType	|string	|应用的执行引擎类型|
#### 3.3 获取单个剧本执行所需要的参数
###### 请求类型
POST
###### 请求路径
/api/playbook/param
###### 路径参数
###### 请求参数

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|playbookId|	long|	是|	剧本的ID|
###### 请求体
###### 请求示例
```commandline
curl --location --request --header 'hg-token: xxx' POST 'https://192.168.2.186/api/playbook/param?playbookId=3633676872182754' \


```
###### 响应示例
```json
{
    "code": 200,
    "result": [
        {
            "status": null,
            "deleted": false,
            "createdBy": "william",
            "modifiedBy": "",
            "createdNickName": null,
            "modifiedNickName": null,
            "createTime": "2021-01-05 17:11:24",
            "updateTime": "2021-01-05 17:11:24",
            "id": 236,
            "cefId": "8f49ba3d-11f4-4ae1-961c-d304fde232c6",
            "cefColumn": "src_ipv6",
            "cefDesc": "ipv6源地址",
            "comment": null,
            "valueType": "STRING",
            "paramConfigs": [
                {
                    "name": "cef.src_ipv6",
                    "required": true,
                    "type": "STRING",
                    "description": "ipv6源地址",
                    "lable": null,
                    "defaultValue": null,
                    "optionsList": null,
                    "multiSelected": false,
                    "concat": null,
                    "order": null,
                    "valueGetterType": null,
                    "parameterPath": "CEF.src_ipv6",
                    "sourceValueType": null,
                    "value": null,
                    "loopType": null,
                    "array": false
                }
            ]
        }
    ]
}
```
###### 响应字段说明

|参数名称	| 参数类型	     | 描述                                            |
|-----|-----------|-----------------------------------------------|
|id	| long      |	事件ID|
|cefId| 	long	    |cef的ID|
|cefColumn	| string	   |cef名称(执行剧本或动作时候的参数名)|
|cefDesc	| string    |	cef描述|
|comment	| string	   |cef备注|
|valueType	| string	   |cef的值类型|
|paramConfigs| array	    |cef的相关参数列表|
|└name| 	string   |	cef参数名称(执行剧本或动作的时候需要填写)|
|└required| 	boolean	 |cef参数是否必须|
|└type	| string    |	cef参数类型(执行剧本或动作的时候需要填写)|
|└description	| string	   |cef参数描述|
|└lable	| string	   |cef参数显示名|
|└defaultValue	|string	|cef参数的默认值|
|└optionsList	|string	|cef参数的可选项列表（字符串形式）|
|└multiSelected	|boolean|	cef参数是否支持多选|
|└concat	|string|	cef参数支持多选时可指定的连接符|
|└order	|int|	cef参数的序号|
|└array	|boolean|	cef参数数组是否支持选择多个值|
|└valueGetterType	|string	|cef参数值的获取类型|
|└parameterPath	|string	|cef参数的路径|
|└sourceValueType	|string	|cef参数的源值类型|
|└value	|string	|cef参数的值(执行剧本或动作的时候需要填写)|
#### 3.4 执行单个剧本或动作
###### 请求类型
POST
###### 请求路径
/odp/core/v1/api/event/execution
###### 路径参数
###### 请求参数
###### 请求体
|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventId	|long	|是	|事件ID(如果eventId为0,则表示全局作战室)|
|executorInstanceId	|long|	是|	执行实例ID（剧本ID或者动作ID）|
|executorInstanceName	|string	|否	|执行实例名称（剧本或者动作名字）|
|executorInstanceType	|string	|是|执行实例类型：<br/>PLAYBOOK 剧本类型<br/>ACTION 动作类型<br/>COMMAND 命令类型|
|execMode	|string	|否|执行模式:<br/>NORMAL 正常模式|
|executorActionAssetIds	|string|	否	|动作执行所需的资源ID(多个资源之间使用英文逗号分割)|
|params	|jsonarray|	否	|参数（执行剧本的时候，所需要的参数来源于接口/api/playbook/param的响应参数；<br/>执行动作的时候，所需要的参数来源于动作的参数列表parameterVariableList）<br/>示例：<br/>[{"key":"k1", "value":"v1"},{"key":"k2","value":"v2"}]|
###### 请求示例

执行一个动作：
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event/execution' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "eventId": 3924278287575663,
    "executorInstanceId": 3923576123860691,
    "executorInstanceName": "SDKSendMessage",
    "execMode":"NORMAL",
    "executorInstanceType": "ACTION",
    "executorActionAssetIds": "3923619502927750",
    "params": [
        {
            "key":"msg",
            "value":"fff"
        }
    ]
}'
```
执行一个剧本：
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event/execution' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "eventId": 6641979662513712,
    "executorInstanceId": 4568093796311249,
    "executorInstanceName": "playbook_4c936552aa98c16e0aa59ad211db497f",
    "execMode":"NORMAL",
    "executorInstanceType": "PLAYBOOK",
    "params": [
        {
            "key":"uwws",
            "value":"123"
        },
        {
            "key":"dvcpid",
            "value":"123"
        }
    ]
}'


```

###### 响应示例
说明：result的值为本次执行产生的activityId
```json
{
    "result": "73b595fe-0b95-4740-81f2-ebfcf3f50e22",
    "code"  : 200
}
```

#### 3.5 获取单个动作或剧本的执行状态
###### 请求类型
GET
###### 请求路径
/odp/core/v1/api/activity/{activityId}
###### 路径参数
|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|activityId	|string|	是	|活动ID|
###### 请求参数
###### 请求体
###### 请求示例
```commandline
curl --location --request --header 'hg-token: xxx' GET 'https://192.168.2.186/odp/core/v1/api/activity/93a632c8-e8a0-406c-b915-54d3f7e3c59f'

```
###### 响应示例
```json
{
    "code": 200,
    "result": {
        "status": null,
        "deleted": false,
        "createdBy": "admin",
        "modifiedBy": "",
        "createdNickName": null,
        "modifiedNickName": null,
        "createTime": "2021-01-28 10:34:52",
        "updateTime": "2021-01-28 10:34:52",
        "id": 9286,
        "activityId": "93a632c8-e8a0-406c-b915-54d3f7e3c59f",
        "eventId": 20210128,
        "executorInstanceId": 3633676872182754,
        "executorInstanceName": "playbook_dc82dd55efd90941979cfad6a577b39a",
        "executorInstanceType": "PLAYBOOK",
        "executeStatus": "SUCCESS",
        "execMode": null,
        "postStatus": null,
        "postCode": null,
        "postMsg": null
    }
}
```
###### 响应字段说明

|参数名称	| 参数类型	   | 描述                                            |
|-----|---------|-----------------------------------------------|
|id	|long|	数据库存储ID|
|activityId|	string	|执行ID|
|eventId|	long	|事件ID|
|executorInstanceId	|long	|执行实例ID|
|executorInstanceName|	string|	执行实例名称|
|executorInstanceType	|string	|执行实例类型：<br/>PLAYBOOK 剧本类型<br/>ACTION 动作类型<br/>COMMAND 命令类型|
|excuteStatus	|string	|当前执行状态:<br/>NEW 新建<br/>RUNNING 运行中<br/>SUCCESS 执行成功<br/>SUCCESS_RE 执行错误,再次执行成功<br/>FAIL 执行失败<br/>FAIL_PARTLY 部分失败<br/>WAITING_DELAY 等待延时<br/>DELAY_DONE 延时完成<br/>WAITING_APPROVE 等待审批<br/>APPROVE_DONE 审批完成<br/>WAITING_VIRTUAL 等待虚拟节点执行<br/>WAITING_ASYNC 异步等待下次执行<br/>WAITING_COLLECT 等待收集<br/>WAITING 等待<br/>NO_POST 无后处理<br/>STOP 人工终止<br/>FINISH 执行结束 |
|execMode|	string	|执行模式:<br/>NORMAL 正常模式<br/>SAFE 安全模式<br/>STRICT 严格模式|
|postStatus	|string|	后置处理状态|
|postCode	|int|	后置处理的返回码|
|postMsg|	string|	后置处理的返回信息|
#### 3.6 创建事件(人工创建事件)
###### 请求类型 
POST
###### 请求路径 
/odp/core/v1/api/event
###### 路径参数 
###### 请求参数 
###### 请求体

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventName	|string	|是	|事件名称|
|categoryId	|long|	是	|事件类型ID|
|categoryName|string|	是	|事件类型名称|
|ownerId	|long|	否	|事件责任人ID(如果有值，则事件的责任人为该人；如果没有，则默认以事件类型的责任人作为事件的责任人)|
|eventSummary|	string|	否|	事件概要|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "categoryName": "amos测试用事件类型",
    "eventName": "event_tester",
    "categoryId": 3888628471648608,
    "ownerId": 503293535641792,
    "eventSummary": "该事件是用来进行测试的"
}'
```

###### 响应示例
```json
{
    "result": {
        "status": null,
        "deleted": false,
        "createdBy": "admin",
        "modifiedBy": "",
        "createdNickName": null,
        "modifiedNickName": null,
        "createTime": "2021-01-31 12:11:24",
        "updateTime": "2021-01-31 12:11:24",
        "id": 3945467956730143,
        "categoryId": 3888628471648608,
        "categoryName": "amos_test",
        "eventStatus": "NEW",
        "eventProcessStatus": "ASSIGNED",
        "openTime": null,
        "resolvedTime": null,
        "categoryDisplayName": null,
        "eventName": "event_tester",
        "sceneName": "",
        "ownerId": 503293535641792,
        "logId": "",
        "relationEventId": 0,
        "relationType": "UNKNOWN",
        "eventSource": "MANUAL",
        "bizName": "",
        "eventSummary": "该事件是用来进行测试的",
        "sceneDisplay": null,
        "resolvedBy": "",
        "preBizModel": null,
        "permissions": [
            {
                "status": null,
                "deleted": null,
                "createdBy": null,
                "modifiedBy": null,
                "createTime": null,
                "updateTime": null,
                "createdNickName": null,
                "modifiedNickName": null,
                "id": null,
                "eventId": null,
                "ownerType": null,
                "ownerId": 503293535641792,
                "permissionBy": "EVENT_OWNER",
                "relationId": null
            },
            {
                "status": null,
                "deleted": null,
                "createdBy": null,
                "modifiedBy": null,
                "createTime": null,
                "updateTime": null,
                "createdNickName": null,
                "modifiedNickName": null,
                "id": null,
                "eventId": null,
                "ownerType": null,
                "ownerId": 638391324424324,
                "permissionBy": "EVENT_MEMBER",
                "relationId": null
            }
        ],
        "members": [
            {
                "id": null,
                "eventId": null,
                "userId": 503293535641792,
                "isDeleted": null,
                "createTime": null,
                "updateTime": null,
                "createdBy": null,
                "modifiedBy": null,
                "username": null,
                "eventName": null,
                "follow": true,
                "latestHandleTime": null
            },
            {
                "id": null,
                "eventId": null,
                "userId": 638391324424324,
                "isDeleted": null,
                "createTime": null,
                "updateTime": null,
                "createdBy": null,
                "modifiedBy": null,
                "username": null,
                "eventName": null,
                "follow": true,
                "latestHandleTime": null
            }
        ],
        "logModel": null
    },
    "code": 200
}
```
###### 响应字段说明

| 参数名称	                | 参数类型	    | 描述                                                                                                                                                                                                                   |
|----------------------|----------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| id	                  | long	    | 事件ID                                                                                                                                                                                                                 |
| eventName            | 	string  | 	事件名称                                                                                                                                                                                                                |
| categoryName	        | string	  | 事件类型名称                                                                                                                                                                                                               |
| categoryId	          | long	    | 事件类型ID                                                                                                                                                                                                               |
| ownerId	             | long	    | 事件责任人ID                                                                                                                                                                                                              |
| eventSummary         | 	string  | 	事件概要                                                                                                                                                                                                                |
| eventStatus	         | string	  | 事件状态:<br/>NEW 新建<br/>OPEN 已打开<br/>RESOLVED 已解决                                                                                                                                                                       |
| eventProcessStatus   | 	string  | 事件执行状态:<br/>UNASSIGNED 未分配<br/>ASSIGNED 已分配<br/>OPENED 已打开<br/>PROCESSING 处理中<br/>POCESSED 已处理                                                                                                                       |
| sceneName	           | string   | 	场景名称                                                                                                                                                                                                                |
| sceneDisplay         | 	string	 | 场景展示名                                                                                                                                                                                                                |
| logId                | 	string  | 	日志ID                                                                                                                                                                                                                |
| relationEventId      | 	long    | 	关联事件ID                                                                                                                                                                                                              |
| relationType	        | string   | 	关联类型                                                                                                                                                                                                                |
| eventSource	         | string   | 	事件来源                                                                                                                                                                                                                |
| bizName	             | string	  | 事件的前置名                                                                                                                                                                                                               |
| openTime	            | date	    | 事件打开时间                                                                                                                                                                                                               |
| resolvedTime	        | date	    | 事件解决时间                                                                                                                                                                                                               |
| categoryDisplayName	 | string	  | 事件类型展示名                                                                                                                                                                                                              |
| resolvedBy	          | string   | 	事件解决人                                                                                                                                                                                                               |
| preBizModel	         |          | 事件关联的前置                                                                                                                                                                                                              | 
| └id	                 | long	    | 前置的ID                                                                                                                                                                                                                |
| └name	               | string	  | 前置的名字                                                                                                                                                                                                                |
| └queue	              | string   | 	前置的消息队列名                                                                                                                                                                                                            |
| └regularName         | 	string	 | 前置的正则名                                                                                                                                                                                                               |
| └regular	            | string   | 	前置的正则表达式                                                                                                                                                                                                            |
| └logEx	              | string	  | 前置的日志样例                                                                                                                                                                                                              |
| └mapRelation	        | string	  | 前置的字段映射关系                                                                                                                                                                                                            |
| └bp	                 | string   | 	前置的规则名称                                                                                                                                                                                                             |
| └description	        | string   | 	前置的描述                                                                                                                                                                                                               |
| └servers	            | string   | 	前置使用KAFKA接入的服务器名                                                                                                                                                                                                    |
| └groupId	            | string   | 	前置使用KAFKA接入的组ID                                                                                                                                                                                                     |
| └parseType	          | string   | 前置解析方式：<br/>G grok方式解析<br/>J json方式解析<br/>C cef日志格式解析                                                                                                                                                                |
| └accessType	         | string	  | 接入方式:<br/>KAFKA 以Kafka形式接入<br/>API 以api形式接入                                                                                                                                                                          |
| └eventName	          | string   | 	相关的事件名                                                                                                                                                                                                              |
| └isPreTreat	         | boolean  | 	是否需要预处理                                                                                                                                                                                                             |
| └treatPlaybookId	    | string	  | 预处理执行的剧本ID                                                                                                                                                                                                           |
| └deduplicateFields	  | string   | 	去重字段                                                                                                                                                                                                                |
| └secured	            | boolean  | 	前置使用KAFKA接入，是否打开ssl认证配置                                                                                                                                                                                             |
| └sslFilesPath	       | string	  | 前置使用KAFKA接入，ssl文件路径                                                                                                                                                                                                  |
| └sslMd5	             | string   | 	前置使用KAFKA接入，ssl证书的md5                                                                                                                                                                                               |
| └sslSettingList	     | array	   | 前置使用KAFKA接入，ssl的认证配置信息                                                                                                                                                                                               |
| └└name	              | string	  | 属性名                                                                                                                                                                                                                  |
| └└value	             | string	  | 属性值 |                                                                                                                                                                                                                 |
| └└type               | 	string	 | 属性类型：<br>STRING 字符串<br/>INTEGER 整数类型（int）<br/>LONG 整数类型（long）<br/>DOUBLE 浮点数类型（双精度）<br/>Date日期 <br/>FLOAT 浮点数类型（单精度）<br/>BOOLEAN 布尔类型<br/>OUTSIDE_FILE 外部文件类型<br/>PASSWORD 密码类型<br/>JSON json类型<br/>JSONARRAY json数组类型<br/>RESULT_FILE 结果文件类型 |
|  logModel            |          |事件关联的日志|
| └id	                 | long	    |日志存储ID|
| └logId	              | string	  |日志ID|
| └bizName	            | string	  |日志名字|
| └queue	              | string	  |日志来源于那个消息队列|
| └log	                | string	  |日志内容|
| └cef	                | string	  |日志对应的cef|
| └level               | 	int	    |日志的等级|
| └eventList	          | string	  |日志相关联的事件名列表|
| permissions	         | array	   |事件的权限列表|
| └id	                 | long	    |权限ID|
| └eventId	            | long	    |事件ID|
| └ownerType           | 	string  |	责任人类型|
| └ownerId	            |long	|责任人ID|
| └permissionBy	       |string	|权限类型:<br/>EVENT_MEMBER 事件成员<br/>EVENT_OWNER 事件责任人<br/>EVENT_CREATOR 事件创建人<br/>APPROVOR 事件审批人<br/>MANUAL 人工事件|
| └relationId	         |long	|权限关联ID|
| members	             |array|	事件的成员列表|
| └eventId	            |long|	事件ID|
| └userId              |	long|	用户ID|
| └username            |	string	|用户名|
| └eventName           |	string|	事件名|
| └follow	             |boolean|	是否已经关注|
#### 3.7 向作战室拉人
###### 请求类型 
POST
###### 请求路径 
/odp/core/v1/api/event/assignee
###### 路径参数 
###### 请求参数
###### 请求体

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventId|	long|	是|	事件ID|
|assigneeId|	array|	是	|关注人员ID数组(如果人员不存在，则默认不进行添加，不报异常)|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event/assignee' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
"eventId":3924278287575663,
"assigneeId":[503293535641792]
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": "ok"
}

```
#### 3.8 获取剧本或动作执行结果
###### 请求类型 
GET
###### 请求路径
/odp/core/v1/api/event/activity
###### 路径参数
###### 请求参数

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|activityId	|string	|是	|活动ID|
###### 请求体
###### 请求示例
```commandline
curl --location --header 'hg-token: xxx' --request GET 'https://192.168.2.186/odp/core/v1/api/event/activity?activityId=93a632c8-e8a0-406c-b915-54d3f7e3c59f'

```
######  响应示例
```json
{
    "code": 200,
    "result": {
        "activity": {
            "createTime": "2021-01-28 10:34:52",
            "updateTime": "2021-01-28 10:34:52",
            "eventId": 20210128,
            "executorInstanceId": 3633676872182754,
            "executorActionParams": null,
            "executeStatus": "SUCCESS",
            "execModel": null,
            "displayName": "demo_ip情报信息调查",
            "code": 200,
            "msg": "成功",
            "messageId": "",
            "startTime": "2021-01-28T02:34:52.000+0000",
            "finishTime": "2021-01-28T02:34:53.000+0000"
        },
        "nodeResults": [
            {
                "nodeResultModel": {
                    "createTime": "2021-01-28 10:34:52",
                    "updateTime": "2021-01-28 10:34:52",
                    "pnodeResultId": 0,
                    "mnodeResultId": 0,
                    "playbookId": 3633676872182754,
                    "playbookName": "playbook_dc82dd55efd90941979cfad6a577b39a",
                    "nodeId": 3923811782078075,
                    "nodeName": "node_f7fd9e847ba9c059fdff96a2489",
                    "actionId": 3923576123860691,
                    "actionName": "sdktest.SDKSendMessage",
                    "code": 200,
                    "startTime": "2021-01-28T02:34:53.000+0000",
                    "finishTime": "2021-01-28T02:34:53.000+0000",
                    "msg": null,
                    "displayName": "sendMesssage",
                    "nodeType": "ACTION",
                    "excuteStatus": "SUCCESS",
                    "pname": "",
                    "accasion": null,
                    "loopType": "NO",
                    "levelType": "ROOT"
                },
                "assetResultModels": [
                    {
                        "createTime": "2021-01-28 10:34:52",
                        "updateTime": "2021-01-28 10:34:52",
                        "nodeResultId": 3928101447583409,
                        "assetId": 3923619502927750,
                        "assetName": "sendMessageToWarroom",
                        "code": 200,
                        "msg": null,
                        "displayName": "向作战室里面发送一条消息",
                        "detailSize": 1,
                        "prettyResult": null,
                        "fileData": false,
                        "detailModels": [
                            {
                                "createTime": "2021-01-28 10:34:52",
                                "updateTime": "2021-01-28 10:34:52",
                                "nodeResultId": 3928101447583409,
                                "assetResultId": 3928101448043372,
                                "playbookId": 3633676872182754,
                                "playbookName": "playbook_dc82dd55efd90941979cfad6a577b39a",
                                "nodeId": 3923811782078075,
                                "nodeName": "node_f7fd9e847ba9c059fdff96a2489",
                                "nodeDisplay": null,
                                "actionId": 3923576123860691,
                                "actionName": "SDKSendMessage",
                                "assetId": 3923619502927750,
                                "assetName": "sendMessageToWarroom",
                                "jsonData": {
                                    "msg": "",
                                    "code": 200,
                                    "data": {
                                        "msg": "success",
                                        "content": "这是一条测试消息"
                                    },
                                    "param": {
                                        "msg": "这是一条测试消息"
                                    }
                                },
                                "extend": null,
                                "startTime": "2021-01-28T02:34:53.000+0000",
                                "finishTime": "2021-01-28T02:34:53.000+0000"
                            }
                        ]
                    }
                ]
            }
        ]
    }
}

```
###### 响应字段说明

|参数名称	| 参数类型	    | 描述                                            |
|-----|----------|-----------------------------------------------|
|activity| 	string	 |活动ID|
|└eventId| 	long	   |事件ID|
|└executorInstanceId| 	long    |	执行实例ID|
|└executorActionParams	| string	  |执行动作参数|
|└executeStatus	| string	  |执行状态:<br/>NEW 新建<br/>RUNNING 运行中<br/>SUCCESS 执行成功<br/>SUCCESS_RE 执行错误,再次执行成功<br/>FAIL 执行失败<br/>FAIL_PARTLY 部分失败<br/>WAITING_DELAY 等待延时<br/>DELAY_DONE 延时完成<br/>WAITING_APPROVE 等待审批<br/>APPROVE_DONE 审批完成<br/>WAITING_VIRTUAL 等待虚拟节点执行<br/>WAITING_ASYNC 异步等待下次执行<br/>WAITING_COLLECT 等待收集<br/>WAITING 等待<br/>NO_POST 无后处理<br/>STOP 人工终止<br/>FINISH 执行结束 |
|└execModel	| string	  |执行模式:<br/>NORMAL 正常模式<br/>SAFE 安全模式<br/>STRICT 严格模式|
|└displayName| 	string  |	执行展示名|
|└code	| int      |	返回码|
|└msg| 	string  |	返回信息|
|└messageId	| string   |	关联的消息ID|
|└startTime	| date     |	开始时间|
|└finishTime| 	date    |	结束时间|
|nodeResults	| array    |	节点执行结果列表|
|└nodeResultModel|          |节点执行结果|
|└└pnodeResultId| 	long	   |父节点执行结果ID|
|└└mnodeResultId	| long	    |挂载节点执行结果ID|
|└└playbookId	| long     |	剧本ID|
|└└playbookName| 	string  |	剧本名|
|└└nodeId	| long     |	节点ID|
|└└nodeName	| string   |	节点名称|
|└└actionId	| long     |	动作ID|
|└└actionName	| string	  |动作名称|
|└└code	| int      |	节点执行结果返回码|
|└└msg	| string	  |节点执行结果返回信息|
|└└displayName	| string   |	节点执行结果展示名|
|└└nodeType	| string	  |节点类型:START 开始节点END 结束节点ACTION 动作节点RULE 规则节点<br/>APPROVE 审批节点<br/>VIRTUAL 人工节点<br/>PLAYBOOK 剧本节点<br/>ASYNC 异步节点<br/>FINALLY 后处理节点<br/>VIRTUAL_APPROVE 严格模式下审批节点<br/>GATHERER 聚合节点<br/>COLLECTION 信息收集节点|
|└└executeStatus| 	string	 |节点执行结果的状态:<br/>NEW 新建<br/>RUNNING 运行中<br/>SUCCESS 执行成功<br/>SUCCESS_RE 执行错误,再次执行成功<br/>FAIL 执行失败<br/>FAIL_PARTLY 部分失败<br/>WAITING_DELAY 等待延时<br/>DELAY_DONE 延时完成<br/>WAITING_APPROVE 等待审批<br/>APPROVE_DONE 审批完成<br/>WAITING_VIRTUAL 等待虚拟节点执行<br/>WAITING_ASYNC 异步等待下次执行<br/>WAITING_COLLECT 等待收集<br/>WAITING 等待<br/>NO_POST 无后处理<br/>STOP 人工终止<br/>FINISH 执行结束 |
|└└pname| 	string	 |父节点名称|
|└└accasion| 	string	 |节点执行时机:BEFORE 之前AFTER 之后|
|EXCEPTION |          |异常时|
|└└loopType|	string	|循环类型:<br/>PARAM 参数<br/> NO 不循环 <br/>NEST 嵌套|
|└└levelType	|string	|层级类型:<br/>ROOT 根节点<br/>NEST 嵌套节点<br/>SUB 子节点|
|└└startTime	|date|	节点开始执行时间|
|└└finishTime	|date|	节点结束执行时间|
|└assetResultModels|	array|	资产结果列表|
|└└nodeResultId|	id	|节点执行结果ID|
|└└assetId	|id	|资产ID|
|└└assetName	|string|	资产名|
|└└code|	int	|资产的返回码|
|└└msg|string|	资产的返回信息|
|└└displayName|	string	|资产的展示名|
|└└detailSize|	int|	资产详情列表的大小|
|└└prettyResult	|string	|模版渲染后的执行结果|
|└└fileData	|boolean|	是否结果过大存储在文件中|
|└└detailModels	|array	|资产详情列表|
|└└└nodeResultId	|long	|节点执行结果ID|
|└└└assetResultId	|long|	资产执行结果ID|
|└└└playbookId	|long|	剧本ID|
|└└└playbookName	|string|	剧本名|
|└└└nodeId	|long|	节点ID|
|└└└nodeName	|string|	节点名|
|└└└nodeDisplay	|string	|节点展示名|
|└└└actionId	|long|	动作ID|
|└└└actionName	|string|	动作名|
|└└└assetId	|long|	资产ID|
|└└└assetName	|string|	资产名|
|└└└extend	|string	|扩展结果|
|└└└startTime	|date|	开始执行时间|
|└└└finishTime	|date|	结束执行时间|
|└└└jsonData	|jsonobject|	执行数据|
#### 3.9 获取所有的事件类型
###### 请求类型 
POST
###### 请求路径 
/odp/core/v1/api/event/categories
###### 路径参数 
###### 请求参数

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|page	|int	|是	请求查询的页数|
|size	|int	是	请求查询的每页记录条数|
###### 请求体
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event/categories?page=1&size=10' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{}'

```
###### 响应示例
```json
{
    "code": 200,
    "result": [
        {
            "status": "ON",
            "deleted": false,
            "createdBy": "admin",
            "modifiedBy": "admin",
            "createdNickName": "管理员",
            "createTime": "2020-11-06 11:45:19",
            "updateTime": "2020-11-06 19:07:26",
            "id": 1386001072942565,
            "name": "fdds",
            "description": "dffdf",
            "autoAction": true,
            "slaHour": 0,
            "ownerId": 503293535641792,
            "canEdit":false,
            "eventActionRls": [
                {
                    "status": "ON",
                    "deleted": false,
                    "createdBy": "wupiaoyu",
                    "modifiedBy": null,
                    "createdNickName": null,
                    "createTime": "2019-11-06 19:07:26",
                    "updateTime": "2019-11-06 19:07:26",
                    "id": 1,
                    "eventCategoryId": 1386001072942565,
                    "eventCategoryName": "fdds",
                    "actionId": 1353259107969053,
                    "actionName": "nn",
                    "actionType": "PLAYBOOK"
                }
            ]
        }
    ]
}
```
###### 响应字段说明

|参数名称	| 参数类型	   | 描述                                          |
|----|---------|---------------------------------------------|
|id	|long	| 事件类型id                                      |
|name	|string| 	事件类型名称                                     |
|description|string	| 事件类型描述                                      |
|autoAction|boolean	| 是否自动执行                                      |
|severity|string	| 严重等级                                        |
|sensitivity|string	| 颜色标记                                        |
|slaHour|integer	| 处理时效（0：不限处理时效）                              |
|ownerId|long| 	拥有者id                                      |
|canEdit|	boolean| 	是否可编辑                                      |
|status	|string	| 事件类型的状态（ON：表示可用，OFF： 表示不可用）                 |
|eventActionRls|array	| 绑定的动作数组                                     |
| └id|long	| 事件与动作的关联id                                  |
| └eventCategoryId|long	| 动作关联的事件类型id                                 |
| └eventCategoryName|string| 	动作关联的事件类型名称                                |
| └actionId|long	| 动作的id                                       |
| └actionName|string	| 动作的名称                                       |
| └actionType|string| 	动作的类型：<br/>PLAYBOOK 剧本类型<br/>ACTION 动作类型<br/>COMMAND 命令类型 |
| └status|string	|动作的状态（ON：表示可用，OFF： 表示不可用）|
#### 3.10 获取所有的用户信息
###### 请求类型 
POST
###### 请求路径 
/api/users
###### 路径参数 
###### 请求参数

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|page	|int	|是	请求查询的页数|
|size	|int	是	请求查询的每页记录条数|
###### 请求体
|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|id	|long	|否	|用户ID（可唯一标示一个用户）|
|username|	string|	否|	用户名（可唯一标示一个用户）|
|name	|string	|否	|用户昵称|
|mail|	string|	否	|邮箱|
|mobile|	stirng|	否	|手机号|
######  请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/api/users?page=1&size=10' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": {
        "status": "ON",
        "deleted": false,
        "createdBy": "",
        "modifiedBy": "admin",
        "createdNickName": null,
        "createTime": null,
        "updateTime": "2020-04-09 18:06:39",
        "username": "admin",
        "name": "管理员",
        "mobile": "",
        "mail": "",
        "id": 503293535641792,
        "robot": false,
        "tempUser": false,
        "roles": [
            {
                "status": null,
                "deleted": null,
                "createdBy": null,
                "modifiedBy": null,
                "createdNickName": null,
                "createTime": null,
                "updateTime": null,
                "id": 894031332127760,
                "role": "系统管理员",
                "description": null,
                "rolePermissionModels": null
            }
        ],
        "permissions": [
            "*"
        ],
        "type": "LOCAL",
        "forbidden": false,
        "latestLoginIp": "192.168.2.123",
        "passwordExpireTime": null,
        "sceneList": null
    }
}
```
###### 响应字段说明

|参数名称	| 参数类型	     | 描述                                            |
|----|-----------|-----------------------------------------------|
|id| 	integer	 |用户id|
|username| integer	  |用户登录名|
|name| string	   |用户昵称|
|mail	| string    |	邮箱|
|mobile| 	string   |	手机号|
|robot	| false	    |是否是机器人|
|type	| string	   |账户类型|
|forbidden| boolean   |	是否禁止登录|
|latestLoginIp| string    |	最后一次登录时间|
|passwordExpireTime| date	     |密码过期时间|
|roles| array     |	用户角色|
|└ role.id| 	long     |	角色id|
|└ role.role| 	string	  |角色名称|
|└ role.description	| string    |	角色描述|
|└ role.rolePermissionModels|	array|	角色权限|
|permissions|array	|用户权限(管理员权限默认为"permissions": ["*"])|
|sceneList|array	|用户场景|
|└ id	|long|	场景id|
|└ name	|string|	场景名字|
|└ display	|string|	场景展示名字|
|└ severity	|integer|	场景等级|
|└ effective	|boolean	|场景是否生效|
|tempUser	|boolean|	是否是临时用户|
   
#### 3.11 获取某个事件的详情
###### 请求类型 
GET
###### 请求路径 
/odp/core/v1/api/event/{eventId}/detail
###### 路径参数 

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventId|	long|	事件ID|
###### 请求参数
###### 请求体
###### 请求示例
```commandline
curl --location --request GET 'https://192.168.2.186/odp/core/v1/api/event/56003320210128/detail' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{}'

```
###### 响应示例
```json
{
    "code": 200,
    "result": {
        "status": null,
        "deleted": false,
        "createdBy": "wubaobao",
        "modifiedBy": "lilang",
        "createdNickName": "雾空",
        "modifiedNickName": "leo.li",
        "createTime": "2021-02-04 10:08:22",
        "updateTime": "2021-02-04 10:08:49",
        "id": 3967633401677423,
        "categoryId": 3929798644751320,
        "categoryName": "新建事件类型",
        "eventStatus": "OPEN",
        "eventProcessStatus": "ASSIGNED",
        "openTime": "2021-02-04T02:08:49.000+0000",
        "resolvedTime": null,
        "categoryDisplayName": "新建事件类型描述",
        "eventName": "办公网出口IP地址变化：222.64.220.113-->222.64.220.110_20210204100822284",
        "sceneName": "sceAutotesting20210203122314",
        "ownerId": 0,
        "logId": "3967633395310746",
        "relationEventId": 0,
        "relationType": "UNKNOWN",
        "eventSource": "QUEUE",
        "bizName": "ON_SSL",
        "eventSummary": null,
        "sceneDisplay": "sceAutotesting20210203122315",
        "resolvedBy": "",
        "logModel":null,
        "permissions":null,
        "members":null,
        "preBizModel": {
            "status": "ON",
            "deleted": false,
            "createdBy": "lilang",
            "modifiedBy": "lilang",
            "createdNickName": null,
            "modifiedNickName": null,
            "createTime": "2021-02-04 09:48:05",
            "updateTime": "2021-02-04 10:06:05",
            "id": 3967553609526542,
            "name": "ON_SSL",
            "queue": "ON_SSL",
            "regularName": "",
            "regular": "%{NUMBER:changed}//%{IP:ip_src}//%{IP:dst}//%{GREEDYDATA:msg}",
            "logEx": "//1//222.64.220.113//222.64.220.110//办公网出口IP地址变化：222.64.220.113-->222.64.220.110",
            "mapRelation": "{\"msg\":\"atz\",\"dst\":\"agentTranslatedAddress\",\"IPV6\":null,\"IPV4\":null,\"BASE10NUM\":null,\"ip_src\":\"agentNtDomain\",\"message\":null,\"origin_log\":null,\"changed\":null}",
            "bp": "ON_SSL_173f4eaf46f0454c872b86fa1c83e184",
            "description": "开启SSL认证",
            "servers": "kafka.sp.com:9095",
            "groupId": null,
            "parseType": "G",
            "accessType": "KAFKA",
            "secured": true,
            "sslSettingList": [
                {
                    "name": "security.protocol",
                    "value": "SSL",
                    "type": "STRING"
                },
                {
                    "name": "ssl.key.password",
                    "value": "EVZaDy82tUKXwZxTjgwDkQ==",
                    "type": "PASSWORD"
                },
                {
                    "name": "ssl.truststore.location",
                    "value": "/opt/shakespeare/data/app_files/tmp/none/NONE/a9de4482d90f4906859e65ab9e9aa7b2/server.truststore.jks",
                    "type": "OUTSIDE_FILE"
                },
                {
                    "name": "ssl.truststore.password",
                    "value": "EVZaDy82tUKXwZxTjgwDkQ==",
                    "type": "PASSWORD"
                },
                {
                    "name": "ssl.keystore.location",
                    "value": "/opt/shakespeare/data/app_files/tmp/none/NONE/22cde83d70aa4497806bc393cbb0a4bd/server.keystore.jks",
                    "type": "OUTSIDE_FILE"
                },
                {
                    "name": "ssl.keystore.password",
                    "value": "EVZaDy82tUKXwZxTjgwDkQ==",
                    "type": "PASSWORD"
                }
            ],
            "sslFilesPath": "pre/3967553609526542/3967553609589725/ssl.zip",
            "sslMd5": "db7c2f908105ee93d2e1e4385f843523",
            "eventName": "${atz}",
            "isPreTreat": true,
            "treatPlaybookId": 2367206753262175,
            "deduplicateFields": "atz",
            "ruleSetInfo": "{\"rules\":[{\"content\":{\"conditionExpression\":\"#\",\"conditions\":[{\"variable\":{\"componentType\":null,\"valueType\":\"STRING\",\"type\":\"POINTER\",\"value\":null,\"pointer\":{\"valueType\":\"STRING\",\"type\":\"PROPERTY\",\"variable\":{\"componentType\":null,\"valueType\":\"cef\",\"type\":\"POINTER\",\"value\":null,\"pointer\":{\"valueType\":\"cef\",\"type\":\"SELF\",\"variable\":null,\"variableName\":\"cef\",\"propertyName\":null,\"method\":null,\"frozen\":false},\"expression\":null,\"objects\":null,\"inExpression\":false,\"bindDomain\":null,\"bindType\":null,\"collection\":null,\"frozen\":false,\"uuid\":null},\"variableName\":null,\"propertyName\":\"agentTranslatedAddress\",\"method\":null,\"frozen\":false,\"bindDomain\":null},\"expression\":null,\"objects\":null,\"inExpression\":false,\"bindDomain\":null,\"bindType\":null,\"collection\":null,\"frozen\":false,\"uuid\":null,\"key\":\"5_cef_agentTranslatedAddress\"},\"comparator\":{\"name\":\"ne\",\"type\":\"STRING\",\"label\":\"不等于<字符串>\",\"selectedLabel\":\"不等于 {#1}\",\"params\":[{\"componentType\":null,\"valueType\":\"STRING\",\"type\":\"CONSTANT\",\"value\":\"weq\",\"pointer\":null,\"expression\":null,\"objects\":null,\"inExpression\":false,\"bindType\":\"STRING\",\"collection\":null,\"frozen\":false,\"uuid\":null}],\"paramCount\":1,\"code\":\"!{this}.equals({#1})\",\"key\":\"1_ne\"},\"frozen\":false,\"exp\":\"并且\",\"uuid\":\"f09c8d789c8086359cdc257d0e0ec3f2\"}],\"actions\":[{\"variable\":{\"valueType\":\"RuleExecResult\",\"type\":\"POINTER\",\"value\":null,\"itemType\":null,\"expression\":null,\"inExpression\":false,\"firstObject\":true,\"pointer\":{\"valueType\":\"RuleExecResult\",\"type\":\"SELF\",\"variableName\":\"ruleExecResult\",\"propertyName\":null,\"frozen\":true,\"bindDomain\":null},\"bindDomain\":null,\"bindType\":null,\"follow\":false,\"frozen\":true,\"key\":\"5_RuleExecResult_level\"},\"type\":\"SETPROPERTY\",\"setProperty\":\"level\",\"setValue\":{\"valueType\":\"INTEGER\",\"type\":\"CONSTANT\",\"value\":\"1\",\"itemType\":null,\"expression\":null,\"inExpression\":false,\"firstObject\":false,\"bindDomain\":null,\"bindType\":\"INTEGER\",\"follow\":false,\"frozen\":false},\"selectedLabel\":\"设置\",\"isNotDisplay\":false,\"isScoreCard\":false,\"frozen\":true},{\"variable\":{\"valueType\":\"RuleExecResult\",\"type\":\"POINTER\",\"value\":null,\"itemType\":null,\"expression\":null,\"inExpression\":false,\"firstObject\":true,\"pointer\":{\"valueType\":\"RuleExecResult\",\"type\":\"SELF\",\"variableName\":\"ruleExecResult\",\"propertyName\":null,\"frozen\":true,\"bindDomain\":null},\"bindDomain\":null,\"bindType\":null,\"follow\":false,\"frozen\":true,\"key\":\"5_RuleExecResult_event_list\"},\"type\":\"SETPROPERTY\",\"setProperty\":\"event_list\",\"setValue\":{\"valueType\":\"STRING\",\"type\":\"CONSTANT\",\"value\":\"新建事件类型\",\"itemType\":null,\"expression\":null,\"inExpression\":false,\"firstObject\":false,\"bindDomain\":\"EventCategory\",\"bindType\":\"STRING\",\"follow\":false,\"frozen\":false},\"selectedLabel\":\"设置\",\"isNotDisplay\":false,\"isScoreCard\":false,\"frozen\":true}]},\"mode\":\"NEW\",\"name\":\"node_L_1612403259006\",\"level\":1,\"type\":\"NORMAL\",\"description\":\"node_L_1612403259006\",\"is_template\":\"FALSE\",\"needCheck\":false,\"snapshot\":{\"conditionStr\":\"通用字段的agentTranslatedAddress  不等于  weq   \",\"actionStr\":\"设置 执行结果的事件类型名称 为 新建事件类型  \"},\"chosen\":false,\"selected\":false}],\"ruleType\":\"SIMPLE_RULE\",\"business\":{\"name\":\"ON_SSL_173f4eaf46f0454c872b86fa1c83e184\"}}",
            "sslSettingListJson": "[{\"name\":\"security.protocol\",\"type\":\"STRING\",\"value\":\"SSL\"},{\"name\":\"ssl.key.password\",\"type\":\"PASSWORD\",\"value\":\"EVZaDy82tUKXwZxTjgwDkQ==\"},{\"name\":\"ssl.truststore.location\",\"type\":\"OUTSIDE_FILE\",\"value\":\"/opt/shakespeare/data/app_files/tmp/none/NONE/a9de4482d90f4906859e65ab9e9aa7b2/server.truststore.jks\"},{\"name\":\"ssl.truststore.password\",\"type\":\"PASSWORD\",\"value\":\"EVZaDy82tUKXwZxTjgwDkQ==\"},{\"name\":\"ssl.keystore.location\",\"type\":\"OUTSIDE_FILE\",\"value\":\"/opt/shakespeare/data/app_files/tmp/none/NONE/22cde83d70aa4497806bc393cbb0a4bd/server.keystore.jks\"},{\"name\":\"ssl.keystore.password\",\"type\":\"PASSWORD\",\"value\":\"EVZaDy82tUKXwZxTjgwDkQ==\"}]"
        }
    }
}
```
###### 响应字段说明

|参数名称	| 参数类型	          | 描述                                            |
|-----|----------------|-----------------------------------------------|
|id	| long	          |事件ID|
|eventName	| string         |	事件名称|
|categoryName	| string	        |事件类型名称|
|categoryId	| long	          |事件类型ID|
|ownerId	| long	          |事件责任人ID|
|eventSummary	| string	        |事件概要|
|eventStatus| 	string	       |事件状态:<br/>NEW 新建<br/>OPEN 已打开<br/>RESOLVED 已解决|
|eventProcessStatus| 	string        |事件执行状态:<br/>UNASSIGNED 未分配<br/>ASSIGNED 已分配<br/>OPENED 已打开<br/>PROCESSING 处理中<br/>PROCESSED 已处理|
|sceneName	| string	        |场景名称|
|sceneDisplay| 	string	       |场景展示名|
|logId| 	string	       |日志ID|
|relationEventId	| long           |	关联事件ID|
|relationType	| string         |	关联类型|
|eventSource	| string	        |事件来源|
|bizName	| string	        |事件的前置名|
|openTime	| date	          |事件打开时间|
|resolvedTime	| date	          |事件解决时间|
|categoryDisplayName	| string	        |事件类型展示名|
|resolvedBy	| string	        |事件解决人|
|preBizModel	|                |事件关联的前置|
|└id	| long           |	前置的ID|
|└name	| string         |	前置的名字|
|└queue	| string	        |前置的消息队列名|
|└regularName	| string	        |前置的正则名|
|└regular	| string	        |前置的正则表达式|
|└logEx	| string         |	前置的日志样例|
|└mapRelation| 	string	       |前置的字段映射关系|
|└bp	| string	        |前置的规则名称|
|└description| 	string        |	前置的描述|
|└servers	| string         |	前置使用KAFKA接入的服务器名|
|└groupId	| string	        |前置使用KAFKA接入的组ID|
|└parseType	| string	        |前置解析方式：<br/>G grok方式解析<br/>J json方式解析<br/>C cef日志格式解析|
|└accessType	| string         | 接入方式:<br/>KAFKA 以Kafka形式接入<br/>API 以api形式接入|
|└eventName	| string         |	相关的事件名|
|└isPreTreat| 	boolean	      |是否需要预处理|
|└treatPlaybookId	| string         |	预处理执行的剧本ID|
|└deduplicateFields| 	string        |	去重字段|
|└secured	| boolean        |	前置使用KAFKA接入，是否打开ssl认证配置|
|└sslFilesPath	| string	        |前置使用KAFKA接入，ssl文件路径|
|└sslMd5	| string	        |前置使用KAFKA接入，ssl证书的md5|
|└sslSettingList	| array          |	前置使用KAFKA接入，ssl的认证配置信息|
|└└name	| string         |	属性名|
|└└value	| string	        |属性值|
|└└type	| string	        |属性类型：<br/>STRING 字符串<br/>INTEGER 整数类型（int）<br/>LONG 整数类型（long）<br/>DOUBLE 浮点数类型（双精度）<br/>FLOAT 浮点数类型（单精度）<br/>BOOLEAN 布尔类型<br/>RESOURCE_FILE 资源文件类型<br/>OUTSIDE_FILE 外部文件类型<br/>PASSWORD 密码类型<br/>JSON json类型<br/>JSONARRAY json数组类型<br/>RESULT_FILE 结果文件类型|
|logModel|                |事件关联的日志|
|└id| 	long          |	日志存储ID|
|└logId	| string	        |日志ID|
|└bizName	| string         |	日志名字|
|└queue	| string	        |日志来源于那个消息队列|
|└log	| string	        |日志内容|
|└cef	| string	        |日志对应的cef|
|└level	| int            |	日志的等级|
|└eventList	| string	        |日志相关联的事件名列表|
|permissions	| array	         |事件的权限列表|
|└id	| long           |	权限ID|
|└eventId	| long	          |事件ID|
|└ownerType	| string	        |责任人类型|
|└ownerId	| long           |	责任人ID|
|└permissionBy| 	string	       |权限类型:<br/>EVENT_MEMBER 事件成员<br/>EVENT_OWNER 事件责任人<br/>EVENT_CREATOR 事件创建人<br/>APPROVOR 事件审批人<br/>MANUAL 人工事件|
|└relationId	| long	          |权限关联ID|
|members	| array	         |事件的成员列表|
|└eventId	| long           |	事件ID|
|└userId	| long           |	用户ID|
|└username	| string         |	用户名|
|└eventName	| string         |	事件名|
|└follow	| boolean	是否已经关注 |
#### 3.12 获取某一个活动的节点执行结果
###### 请求类型 
GET
###### 请求路径 
/odp/core/v1/api/activity/{activityId}/node/result
###### 路径参数 

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|activityId	|string	|是|	活动ID|
###### 请求参数
###### 请求体
###### 请求示例
```commandline
curl --location --request --header 'hg-token: xxx' GET 'https://192.168.2.186/odp/core/v1/api/activity/5dff7a77-89b5-4195-b5fb-42c2679f9b15/node/result'

```
###### 响应示例
```json
{
    "code": 200,
    "result": [
        {
            "status": null,
            "deleted": false,
            "createdBy": "",
            "modifiedBy": "",
            "createdNickName": null,
            "modifiedNickName": null,
            "createTime": "2021-03-15 17:43:49",
            "updateTime": "2021-03-15 17:43:49",
            "id": 4190254312538788,
            "pnodeResultId": 0,
            "mnodeResultId": 0,
            "playbookId": 0,
            "playbookName": "",
            "nodeId": 0,
            "nodeName": "default",
            "actionId": 4190244822628159,
            "actionName": "block_ip",
            "activieId": "5dff7a77-89b5-4195-b5fb-42c2679f9b15",
            "code": 200,
            "startTime": "2021-03-15T09:43:48.000+0000",
            "finishTime": "2021-03-15T09:43:49.000+0000",
            "param": null,
            "data": null,
            "extend": null,
            "dataType": "STRING",
            "summary": null,
            "msg": null,
            "tips": "",
            "displayName": null,
            "jsonObjParam": null,
            "paramIndex": "{}",
            "contextInfo": "{\"actionName\":\"block_ip\",\"activieId\":\"5dff7a77-89b5-4195-b5fb-42c2679f9b15\",\"appName\":\"safeline\",\"eventId\":20210315,\"executeTime\":1615801427000,\"executor\":\"yanggaoming\",\"logMode\":false,\"nodeName\":null,\"playbookName\":null}",
            "nodeType": "ACTION",
            "excuteStatus": "SUCCESS",
            "originExcuteStatus": null,
            "mname": "",
            "pname": "",
            "accasion": null,
            "loopType": "NO",
            "levelType": "ROOT"
        }
    ]
}
```
响应字段说明(请参考3.8响应字段说明的nodeResultModel)
#### 3.13 获取作战室右侧某个事件的成员信息
###### 请求类型 
GET
###### 请求路径 
/odp/core/v1/api/event/{eventId}/member
###### 路径参数 

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventId	|long	|是	|事件ID|
###### 请求参数
###### 请求体
###### 请求示例
```commandline
curl --location --request GET 'https://192.168.2.186/odp/core/v1/api/event/4234753528785810/member' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": {
        "eventModel": {
            "status": null,
            "deleted": false,
            "createdBy": "admin",
            "modifiedBy": "chenzhuqing",
            "createdNickName": null,
            "modifiedNickName": null,
            "createTime": "2021-03-23 14:20:32",
            "updateTime": "2021-03-24 10:33:57",
            "id": 4234753528785810,
            "categoryId": 4234752943155907,
            "categoryName": "额",
            "eventStatus": "OPEN",
            "eventProcessStatus": "ASSIGNED",
            "openTime": "2021-03-23T06:20:35.000+0000",
            "resolvedTime": null,
            "categoryDisplayName": "额额",
            "eventName": "额额额",
            "sceneName": "",
            "ownerId": 4235191276364855,
            "logId": "",
            "relationEventId": 0,
            "relationType": "UNKNOWN",
            "eventSource": "MANUAL",
            "bizName": "",
            "eventSummary": "这里填一下该要啊，这里再来一下啊",
            "sceneDisplay": "",
            "resolvedBy": "",
            "preBizModel": null,
            "severity": null
        },
        "userInfoModels": [
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "",
                "modifiedBy": "admin",
                "createdNickName": null,
                "modifiedNickName": null,
                "createTime": null,
                "updateTime": "2021-03-24 16:58:03",
                "id": 503293535641792,
                "username": "admin",
                "name": "管理员",
                "password": null,
                "mobile": "",
                "mail": "",
                "salt": null,
                "robot": false,
                "type": null,
                "secret": null,
                "passwordHistory": null,
                "latestLoginIp": null,
                "latestLoginTime": null,
                "passwordExpireTime": null,
                "passwordErrorTimes": null,
                "forbiddenTime": null,
                "forbidden": false,
                "accountEffectiveTime": null,
                "accountExpireTime": null,
                "sceneList": null,
                "roles": null,
                "userRoles": null,
                "tempUser": null
            },
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "",
                "createdNickName": null,
                "modifiedNickName": null,
                "createTime": "2019-06-27 10:58:20",
                "updateTime": "2021-03-23 13:26:19",
                "id": 638391324424324,
                "username": "wubaobao",
                "name": "雾宝宝",
                "password": null,
                "mobile": "18968066099",
                "mail": "fukui@wuzhi-ai.com",
                "salt": null,
                "robot": true,
                "type": null,
                "secret": null,
                "passwordHistory": null,
                "latestLoginIp": null,
                "latestLoginTime": null,
                "passwordExpireTime": null,
                "passwordErrorTimes": null,
                "forbiddenTime": null,
                "forbidden": false,
                "accountEffectiveTime": null,
                "accountExpireTime": null,
                "sceneList": null,
                "roles": null,
                "userRoles": null,
                "tempUser": null
            },
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "",
                "createdNickName": null,
                "modifiedNickName": null,
                "createTime": "2021-03-23 14:22:25",
                "updateTime": "2021-03-24 16:27:38",
                "id": 4234760960895999,
                "username": "chenzhuqing",
                "name": "额额",
                "password": null,
                "mobile": "",
                "mail": "",
                "salt": null,
                "robot": false,
                "type": null,
                "secret": null,
                "passwordHistory": null,
                "latestLoginIp": null,
                "latestLoginTime": null,
                "passwordExpireTime": null,
                "passwordErrorTimes": null,
                "forbiddenTime": null,
                "forbidden": false,
                "accountEffectiveTime": null,
                "accountExpireTime": null,
                "sceneList": null,
                "roles": null,
                "userRoles": null,
                "tempUser": null
            },
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "",
                "createdNickName": null,
                "modifiedNickName": null,
                "createTime": "2021-03-23 16:11:51",
                "updateTime": "2021-03-24 16:53:38",
                "id": 4235191276364855,
                "username": "chengfengwen",
                "name": "程风文",
                "password": null,
                "mobile": "",
                "mail": "",
                "salt": null,
                "robot": false,
                "type": null,
                "secret": null,
                "passwordHistory": null,
                "latestLoginIp": null,
                "latestLoginTime": null,
                "passwordExpireTime": null,
                "passwordErrorTimes": null,
                "forbiddenTime": null,
                "forbidden": false,
                "accountEffectiveTime": null,
                "accountExpireTime": null,
                "sceneList": null,
                "roles": null,
                "userRoles": null,
                "tempUser": null
            },
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "chenzhuqing",
                "modifiedBy": "",
                "createdNickName": null,
                "modifiedNickName": null,
                "createTime": "2021-03-24 10:29:04",
                "updateTime": "2021-03-24 10:29:04",
                "id": 4239505722403161,
                "username": "user",
                "name": "ceshi de ",
                "password": null,
                "mobile": "",
                "mail": "",
                "salt": null,
                "robot": false,
                "type": null,
                "secret": null,
                "passwordHistory": null,
                "latestLoginIp": null,
                "latestLoginTime": null,
                "passwordExpireTime": null,
                "passwordErrorTimes": null,
                "forbiddenTime": null,
                "forbidden": false,
                "accountEffectiveTime": null,
                "accountExpireTime": null,
                "sceneList": null,
                "roles": null,
                "userRoles": null,
                "tempUser": null
            }
        ]
    }
}
```
响应字段说明（eventModel请参考接口3.11响应字段描述，userInfoModels数组中的model请参考接口3.10响应字段描述）

#### 3.14 创建事件类型
###### 请求类型 
POST
###### 请求路径 
/api/event/category
###### 路径参数 
###### 请求参数
###### 请求体

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|name	|string|	是|	事件名称|
|description|	string|	否	|事件类型描述|
|severity|integer	|否	|事件类型等级|
|ownerId|	long	|否	|事件类型责任人ID|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/api/event/category' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "name": "amos_test_category3",
    "description": "even",
    "severity": null,
    "ownerId": null
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": 1
}
```
#### 3.15 修改事件类型
###### 请求类型 
PUT
###### 请求路径 
/api/event/category
###### 路径参数 
###### 请求参数
###### 请求体

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|id	long|	是|	事件类型ID|
|name	|string|	是|	事件类型名称|
|description	|string|	否	|事件类型描述|
|severity|integer|	否	|事件类型等级|
|ownerId	|long|	否	|事件类型责任人ID|
###### 请求示例
```commandline
curl --location --request PUT 'https://192.168.2.186/api/event/category' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "id": 4558183640570370,
    "name": "amos_test_category",
    "description": "update event category",
    "ownerId": 355818364057033,
    "severity": 5
}'

```
###### 响应示例
```json
{
    "code": 200,
    "result": 1
}
```
#### 3.16 修改事件负责人（支持角色）
###### 请求类型 
POST
###### 请求路径 
/odp/core/v1/api/event/owners
###### 路径参数
###### 请求参数
###### 请求体

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|id	|long|	是	|事件ID|
|owners|array|	是	|责任人的ID数组(如果为空，则代表不设置该事件的责任人)|
|└ownerId|	long|	是|	事件责任人的id，依赖于ownerType；如果ownerType是USER,则代表用户id；如果ownerType是ROLE，则代表角色id|
|└ownerType|	string|	是|	事件责任人的类型，USER代表用户类型，ROLE代表角色类型|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/event/owners' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "id":4750706167694372,
    "owners":
    [
    {"ownerId":4749025813028620,"ownerType":"USER"},
    {"ownerId":1028832090557583,"ownerType":"ROLE"}
    ]
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": "1"
}
```
#### 3.17  查询所有可用的剧本（不分页）
###### 请求类型  
POST
###### 请求路径 
/odp/core/v1/api/playbook/findAll
###### 路径参数
###### 请求参数 
###### 请求体    

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|publishStatus|	string|	是	|剧本的发布状态（当该参数的值为ONLINE时，即可查询可用的剧本）|
###### 请求示例
```commandline
curl --location --request POST 'https://192.168.2.186/odp/core/v1/api/playbook/findAll' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
 "publishStatus":"ONLINE"
}'

```
###### 响应示例
```json
{
    "code": 200,
    "result": [
            {
                "status": "ON",
                "deleted": false,
                "createdBy": "admin",
                "modifiedBy": "admin",
                "createdNickName": "管理员",
                "modifiedNickName": "管理员",
                "createTime": "2021-01-27 15:48:53",
                "updateTime": "2021-01-27 16:23:57",
                "id": 3633676872182754,
                "name": "playbook_dc82dd55efd90941979cfad6a577b39a",
                "drawJson": null,
                "description": "IP信息增强-演示",
                "displayName": "demo_ip情报信息调查",
                "nodeList": null,
                "nodeEdageList": null,
                "sceneList": [
                    {
                        "status": null,
                        "deleted": null,
                        "createdBy": null,
                        "modifiedBy": null,
                        "createTime": null,
                        "updateTime": null,
                        "createdNickName": null,
                        "modifiedNickName": null,
                        "id": null,
                        "name": "scene_important",
                        "display": "重要场景",
                        "severity": null,
                        "effective": null,
                        "dutyRelation": null
                    }
                ],
                "labelList": [
                    {
                        "status": null,
                        "deleted": null,
                        "createdBy": null,
                        "modifiedBy": null,
                        "createTime": null,
                        "updateTime": null,
                        "createdNickName": null,
                        "modifiedNickName": null,
                        "id": null,
                        "name": "必备"
                    }
                ],
                "externalInfoList": [],
                "grade": null,
                "publishStatus": "ONLINE",
                "playbookCategory": "COMMONEVENT"
            }
        ]
}
```
响应字段说明 (请参考3.1)

#### 3.18  添加事件成员（支持单个用户名、ID，数组）
###### 请求类型  
POST
###### 请求路径 
/odp/core/v1/api/event/assignee
###### 路径参数
###### 请求参数 
###### 请求体    

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|eventId	|long|	是|	事件ID|
|userId|	long|	否	|用户ID（优先级最高）|
|username	|string	|否	|用户名（优先级低于userId）|
|assigneeId	|array|	否|	用户ID列表（优先级低于username）|
|assigneeName	|array	|否	|用户名列表（优先级最低）|
######  请求示例
```commandline
curl --location --request POST 'http://192.168.44.18/odp/core/v1/api/event/assignee' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "eventId":5730402598025864,
    "username":"john",
    "userId":5769396124164036,
    "assigneeId":[5769392166967936,5769392166968533],
    "assigneeName":["tom","test"]
}'

```
###### 响应示例
```json
{
    "code": 200,
    "result": "ok"
}
```
#### 3.19  删除事件成员（支持单个用户名、ID，数组）
###### 请求类型  
DELETE
###### 请求路径 
/odp/core/v1/api/event/assignee
###### 路径参数
###### 请求参数 
###### 请求体    

| 参数名称     |	参数类型|	是否必须|	描述|
|----------|---------|  ----  |----  |
| eventId	 |long	|是	|事件ID|
| userId	  |long	|否|	用户ID（优先级最高）|
|username|	string|	否	|用户名（优先级低于userId）|
|assigneeId	|array|	否|	用户ID列表（优先级低于username）|
|assigneeName	|array	|否	|用户名列表（优先级最低）|
###### 请求示例
```commandline
curl --location --request DELETE 'http://192.168.44.18/odp/core/v1/api/event/assignee' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "eventId":5730402598025864,
    "username":"john",
    "userId":5769396124164036,
    "assigneeId":[5769392166967936,5769392166968533],
    "assigneeName":["tom","test"]
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": "ok"
}
```
#### 3.20  添加事件责任人（仅支持owners数组）
###### 请求类型  
PUT
###### 请求路径 
/odp/core/v1/api/event/owners
######  路径参数
###### 请求参数 
######  请求体    

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|id	long|	是|	事件ID|
|owners|	array|	否|	其中ownerId:用户或者角色ID; ownerType: owner类型(默认为USER:用户,ROLE:角色)|
###### 请求示例
```commandline
curl --location --request PUT 'http://192.168.44.18/odp/core/v1/api/event/owners' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "id":5730402598025864,
    "owners":[{"ownerId":5769393782625450,"ownerType":"USER"}]
}'
```
###### 响应示例
```json
{
    "code": 200,
    "result": 1
}
```
#### 3.21  删除事件责任人（仅支持owners数组）
###### 请求类型  
DELETE
###### 请求路径 
/odp/core/v1/api/event/owners
###### 路径参数
###### 请求参数 
###### 请求体    

|参数名称|	参数类型|	是否必须|	描述|
| ----  |---------|  ----  |----  |
|id	|long	|是	|事件ID|
|owners|	array|	否|	其中ownerId:用户或者角色ID; ownerType: owner类型(默认为USER:用户,ROLE:角色)|
###### 请求示例
```commandline
curl --location --request DELETE 'http://192.168.44.18/odp/core/v1/api/event/owners' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx' \
--data-raw '{
    "id":5730402598025864,
    "owners":[{"ownerId":5769393782625450,"ownerType":"USER"}]
}'

```
###### 响应示例
````json
{
    "code": 200,
    "result": 1
}
````
#### 3.22  在线人员查询
###### 请求类型 
 GET
###### 请求路径 
/odp/core/v1/api/userInfo/online
###### 路径参数
###### 请求参数 
###### 请求体    
###### 请求示例
```commandline
curl --location --request 'http://192.168.44.18/odp/core/v1/api/userInfo/online' \
--header 'Content-Type: application/json' \
--header 'hg-token: xxx'
```
###### 响应示例
```json
{
    "code": 200,
    "result": {
            "status":"ON",
            "deleted":false,
            "createdBy":"lilang",
            "modifiedBy":"admin",
            "createdNickName":null,
            "modifiedNickName":null,
            "createTime":"2019-12-03 09:54:43",
            "updateTime":"2022-03-28 15:23:01",
            "username":"chengfengwen",
            "name":"程风文",
            "mobile":"18736158160",
            "mail":"chengfengwen@wuzhi.ai.com",
            "id":1538448551418236,
            "robot":false,
            "roles":[
                {
                    "status":null,
                    "deleted":null,
                    "createdBy":null,
                    "modifiedBy":null,
                    "createdNickName":null,
                    "modifiedNickName":null,
                    "createTime":null,
                    "updateTime":null,
                    "id":894031332127760,
                    "role":"系统管理员",
                    "description":null,
                    "rolePermissionModels":null,
                    "menuFunctions":null
                }
            ],
            "permissions":null,
            "type":"LOCAL",
            "forbidden":false,
            "latestLoginIp":"192.168.205.20",
            "passwordExpireTime":"2021-10-27 10:18:29",
            "accountEffectiveTime":null,
            "accountExpireTime":null,
            "sceneList":null,
            "menus":null,
            "tempUser":false,
            "acPerm":null,
            "twoPhaseAuthSwitch":"OFF"
        }
}
```
