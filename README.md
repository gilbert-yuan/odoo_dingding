# odoo_dingding（最新支持11.0）
即将实现功能

## TO-DO-LIST
- [-] 扫码登陆
- [-] 员工同步及公司部门构架同步的完善。



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


