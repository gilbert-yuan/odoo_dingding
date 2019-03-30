# odoo_dingding（最新支持11.0）
即将实现功能
```
··重点  记得配置  钉钉应用里面的白名单 ‘服务器公网出口IP名单’ 否则不能正常的访问
```
## 简单配置（暂时只支持单个应用）上面钉钉里面配置对应odoo里面配置 
```python
钉钉开发这用户  /E应用/应用开发 中单个应用               AppKey         AppSecret      AgentId     
odoo中         /配置/用户/钉钉             表单        钉钉AppKey    钉钉AppSecret    agent_id
```
点击获取 => 获取部门  =>  点击获取用户 如果钉钉里面有部门和用户的话你就可以在 odoo中菜单 /配置/用户/钉钉部门 /配置/用户/钉钉用户中看到对应的信息
在钉钉用户 记录信息的最后有一个按钮，如果你 绑定的有系统用户的话点击发消息给他，相应的用户就会收到一条随机消息。-参考发消息的按钮的方法就可以学会如何用钉钉发消息了。




## 最新发现钉钉更新了API 按照目前的设计不符合新的API 请注意。（10.0 分支已更新部分功能，master待更新）
```xml
从2018.12.17开始，企业内部开发进行账号升级，不再支持创建corpSecret（已有的corpSecret可以继续使用）。企业内部开发后续可以通过创建应用来自动生成appKey和appSecret，然后开发者可以获取access_token，具体详情参考以下文档。
```

## TO-DO-LIST
- [X] 扫码登陆( 已完成 |master ) 
- [ ] 员工同步及公司部门构架同步的完善（初步功能已经完成|master|10.0）。（待完善）
     - [ ] 钉钉上新建员工同步到系统中（通过回调实现，在企业微信中，启用员工api管理后就关闭了企业微信后台修改新建的权限，所以这点是钉钉的不方便的地方，双向同步比较麻烦）。（待完善）
     - [ ] 部门和同步，新建删除【具体设计待定，具体和系统部门绑定关系怎么处理待定】。（待完善）
 
- [X] 支持多个agent。（已完成|master）
- [X] 单独开启线程获取token 不是用的时候才去获取。（已完成|master）
- [X] 可以用多个agent 进行发送消息。（已完成|master）
- [X] 注册钉钉回调事件。（已完成|master|10.0）
- [X] 代码发起钉钉相关的审批。（已完成|master|10.0）
- [X] 代码监控（通过回调）审批单据的状态。（已完成|master|10.0）
- [X] 钉钉中jsAPi 相关的代码（包含， jsapi 中要用的签名等信息，本代码中没有提供完整示例|master|10.0）。（已完成）
- [ ]  对接钉钉E应用基本代码及demo。（待完善|master|10.0）
- [ ]  尽可能对接更多的钉钉提供api的功能具体对接什么看心情吧。（待完善）

---------------------------------------------------
odoo10 对接钉钉部分功能
功能仅供参考，如要进行实际应用请，核对后再进行操作。
效果图参见ISSUE（审批模版是要钉钉配置创建的）https://github.com/gilbert-yuan/odoo_dingding/issues/5
 
1.详细说明及使用介绍参见 https://github.com/gilbert-yuan/odoo_dingding/blob/master/dingding/钉钉使用手册.docx


2.. 要使用钉钉比较高级的功能 如回调 则 要自己探索了。上传的时候，一些功能已经不能用了（懒得修正了。后面的修改导致的。简单功能没问题。仅供参考）

3.加密部分代码来源于 https://github.com/zgs225/dingtalk_crypto 经过部分修改。

4.注意事项，钉钉注册回调事件时总会报出 返回字符串 success。
深究其原因，就发现是odoo json请求自动把返回的内容进行包装加上一层 "id": 622213306, "jsonrpc": "2.0", "result":
```json
{"id": 622213306, "jsonrpc": "2.0", "result": [{"type": "ir.actions.server", "link_field_id": false, "name": "\u5b9a\u65f6\u83b7\u53d6\u6700\u65b0\u4ea7\u54c1\u4fe1\u606f", "active": false, "numbercall": -1, "channel_ids": [], "interval_number": 10, "model_id": [113, "\u8bfb\u53d6\u4eac\u4e1c\u7684\u4ea7\u54c1\u5206\u7c7b\u8bb0\u5f55\u4e0b\u6765\uff0c\u7136\u540e\u8fdb\u884c\u548c\u4ea7\u54c1\u7684\u5173\u8054\uff0c\u5206\u7c7bID\u548c\u4eac\u4e1c\u4e00\u81f4"], "doall": false, "model_name": "jd.category", "id": 15, "fields_lines": [], "priority": 8, "child_ids": [], "interval_type": "minutes", "template_id": false, "crud_model_id": false, "crud_model_name": false, "nextcall": "2018-03-15 02:56:20", "code": "model.all_search_and_write_new_info('all')", "display_name": "\u5b9a\u65f6\u83b7\u53d6\u6700\u65b0\u4ea7\u54c1\u4fe1\u606f", "user_id": [1, "Administrator"], "state": "code", "partner_ids": [], "binding_model_id": false}]}
```
这样的结果而钉钉不能识别odoo的这种格式所以 要继承下面方法 把这一层包装去掉。 （测试临时修改，如需正式环境使用请用继承方式) 直接替换掉系统中这个方法
```python
 
    def _json_response(self, result=None, error=None):
        response = {
            'jsonrpc': '2.0',
            'id': self.jsonrequest.get('id')
            }
        if result and isinstance(result, dict)and result.get('msg_signature'):
            mime = 'application/json'
            body = json.dumps(result)
            return Response(
                body, headers=[('Content-Type', mime),
                               ('Content-Length', len(body))])
        if error is not None:
            response['error'] = error
        if result is not None:
            response['result'] = result

        if self.jsonp:
            # If we use jsonp, that's mean we are called from another host
            # Some browser (IE and Safari) do no allow third party cookies
            # We need then to manage http sessions manually.
            response['session_id'] = self.session.sid
            mime = 'application/javascript'
            body = "%s(%s);" % (self.jsonp, json.dumps(response),)
        else:
            mime = 'application/json'
            body = json.dumps(response)

        return Response(
                    body, headers=[('Content-Type', mime),
                                   ('Content-Length', len(body))])

```


附录：钉钉官方解决 字符串不匹配 问题 方法 集合
```
：字符串不匹配？
  • 1.在创建套件过程中、在使用套件回调url接收各种回调处理过程中，会遇到钉钉提示 “返回字符串不匹配”。
  • 2.仔细阅读文档,确认你是按照文档的要求返回的字符串，有的场景要求返回加密“success”，有的地方要返回加密的random对应的key值。
  • 3.确定你的url是不是需要登录的。
  • 4.确定你的url返回的值是json(注意不是返回json.toString)，而不是jsonp格式。
  • 5.对于nodejs，要设置 setAutoPadding 为 false，在进行 PKCS7 补全。
  • 6.终极大招：使用postman，既然你能够收到消息并返回,那么请你用log打印出你接接收的参数并贴在postman中。如图：

```


