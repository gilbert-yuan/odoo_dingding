# -*- coding: utf-8 -*-
from odoo import http, api
from odoo.http import HttpRequest, request
from odoo.addons.dingding.dingtalk_crypto.crypto import DingTalkCrypto
import os
import sys
import jinja2
import threading
import odoo
import time
from odoo.tools.safe_eval import safe_eval
from odoo.addons.dingding.ding_api import Dingtalk
import requests

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.dingding.controller', "html")
env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class PageShow(http.Controller):
    def __init__(self):
        self.login_user = False
        self.login_session = False
        db_name = request.db
        self.threaded_token = threading.Thread(target=self.create_agent_token, args=(db_name,))  # 开启一个新的线程专门来跑redis 消费者
        self.threaded_token.setDaemon(True)
        self.threaded_token.start()

    def create_agent_token(self, db_name):
        # redis 生产者消费者模式中的消费者部分的代码
        registry = odoo.registry(db_name)
        with api.Environment.manage(), registry.cursor() as cr:
            env = api.Environment(cr, odoo.SUPERUSER_ID, {})
            expired_in = 10
            while True:
                ding_config_row = env.ref('dingding.ding_ding_xml')
                if ding_config_row:
                    if float(ding_config_row.expired_in or 0) <= time.time():
                        ding_obj = Dingtalk(ding_config_row.corpid, ding_config_row.corpsecret, False, {})
                        token_dcit = ding_obj.get_token()
                        if token_dcit.get('errcode') == 0 and token_dcit.get('access_token'):
                            ding_config_row.token = token_dcit.get('access_token')
                            ding_config_row.expired_in = int(token_dcit.get('expired_in'))
                            # expired_in = int(token_dcit.get('expired_in') - time.time())
                            env.cr.commit()
                    else:
                        expired_in = int(float(ding_config_row.expired_in) - time.time())
                time.sleep(expired_in)

    @http.route('/dingding/firstpage', auth='none', type="http", csrf=False)
    def dingding_pulling(self, **args):
        template = env.get_template("apps.html")
        corpid, corpsecret, agent_id, token_dict = request.env['ding.ding'].sudo().get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        signature, timestamp, nonceStr = ding_obj.get_js_api_params(str(request.httprequest.base_url), '1234')
        return template.render({
            'corpId': corpid,
            'timeStamp': timestamp,
            'agentId': agent_id,
            'nonceStr': nonceStr,
            'accessToken': token_dict.get("access_token"),
            'title': u'钉钉测试',
            'signature': signature,
        })

    @http.route('/dingding/getdingdingconfig', auth='none', type="json", csrf=False)
    def getdingdingconfig(self, **args):
        corpid, corpsecret, agent_id, token_dict = request.env['ding.ding'].sudo().get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        signature, timestamp, nonceStr = ding_obj.get_js_api_params(str(request.httprequest.base_url), '1234')
        return {
            'corpId': corpid,
            'timeStamp': timestamp,
            'agentId': agent_id,
            'nonceStr': nonceStr,
            'accessToken': token_dict.get("access_token"),
            'title': u'钉钉测试',
            'signature': signature,
            # 'jsApiList': jsApiList
        }

    @http.route('/get_user_info', auth='none', type="http", csrf=False)
    def dingding_get_user_info(self, **args):
        res = requests.get('https://oapi.dingtalk.com/user/getuserinfo', params=args)
        try:
            dingding_userid = res.json()['userid']
            dinguser_row = request.env['ding.user'].sudo().search([('ding_id', '=', dingding_userid)])
            if dinguser_row:
                uid = request.session.authenticate(request.session.db, dinguser_row.ding_user_id.login,
                                         dinguser_row.ding_user_id.oauth_access_token)
            return request.make_response(res.json())
        except:
             return 'error'

    @http.route('/dingding/call_back_url', auth='none', type="json", csrf=False)
    def dingding_call_back(self, **args):
        ding_rows = request.env['ding.ding'].sudo().search([])
        dingcrypto = DingTalkCrypto(ding_rows[0].aes_key1, str(ding_rows[0].random_token), str(ding_rows[0].corpid))
        rand_str, length, msg, key = dingcrypto.decrypt(request.jsonrequest.get('encrypt'))
        if safe_eval(msg).get('EventType') != 'check_url':
            ding_rows.handler_map().get(safe_eval(msg).get('EventType'), None)(safe_eval(msg))
        signature_get, timestamp_get, nonce_get = request.httprequest.args.get('signature'),\
                                      request.httprequest.args.get('timestamp'), request.httprequest.args.get('nonce')

        dingcrypto = DingTalkCrypto(ding_rows[0].aes_key1, str(ding_rows[0].random_token), str(ding_rows[0].corpid))
        encrypt = dingcrypto.encrypt("success")
        signature, timestamp, nonce = dingcrypto.sign(encrypt, timestamp_get, nonce_get)
        script_response = {
            'msg_signature': signature,
            'timeStamp': timestamp_get,
            'nonce': nonce_get,
            'encrypt': encrypt
        }
        return script_response
