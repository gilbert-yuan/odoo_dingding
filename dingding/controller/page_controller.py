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
import werkzeug
from urllib import parse
from odoo.tools.safe_eval import safe_eval
from odoo.addons.dingding.ding_api import Dingtalk
import requests
from odoo.addons.web.controllers.main import Home


if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.dingding.controller', "html")
env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


class DingDingLogin(Home):

    @http.route()
    def web_login(self, *args, **kw):
        registry = odoo.registry(request.db)

        with registry.cursor() as cr:
            env = odoo.api.Environment(cr, odoo.SUPERUSER_ID, {})
            appid = env.ref('dingding.ding_ding_xml')
            host_url = 'https://oapi.dingtalk.com/connect/oauth2/sns_authorize'
            redirect_uri = 'http://jdvop.tunnel.800890.com/dingding/login'
            appid = 'dingoaosarn9kswmozjldq'
            origin_url = ("{host_url}?appid={appid}&response_type=code&scope=snsapi_login"
                                  "&state=STATE&redirect_uri={redirect_uri}".format(host_url=host_url,
                                                                                    appid=appid,
                                                                        redirect_uri=redirect_uri))
            url = parse.quote(origin_url, 'utf-8')
            request.params.setdefault('redirect_url_quote',  url)
            request.params.setdefault('origin_url',  origin_url)

        response = super(DingDingLogin, self).web_login(*args, **kw)
        return response


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
                        ding_obj = Dingtalk(corpid=ding_config_row.corpid, corpsecret=ding_config_row.corpsecret)
                        token_dcit = ding_obj.get_token()
                        if token_dcit.get('errcode') == 0 and token_dcit.get('access_token'):
                            ding_config_row.token = token_dcit.get('access_token')
                            ding_config_row.expired_in = int(token_dcit.get('expired_in'))
                            env.cr.commit()
                    else:
                        expired_in = int(float(ding_config_row.expired_in) - time.time())
                    for app in ding_config_row.app_ids:
                        if float(app.expired_in or 0) <= time.time():
                            ding_obj = Dingtalk(appkey=app.agent_id, appsecret=app.app_secret)
                            token_dcit = ding_obj.app_get_token()
                            if token_dcit.get('errcode') == 0 and token_dcit.get('access_token'):
                                app.token = token_dcit.get('access_token')
                                app.expired_in = int(token_dcit.get('expired_in'))
                                env.cr.commit()
                        else:
                            expired_in = min(int(float(ding_config_row.expired_in) - time.time()), expired_in)
                time.sleep(expired_in)

    @http.route('/dingding/firstpage', auth='none', type="http", csrf=False)
    def dingding_pulling(self, **args):
        template = env.get_template("apps.html")
        corpid, corpsecret, agent_id, token_dict = request.env['ding.ding'].sudo().get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, agent_id=agent_id, token=token_dict)
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
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, agent_id=agent_id, token=token_dict)
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

    @http.route('/dingding/login', auth='none', type="http", csrf=False)
    def dingding_login(self, **kwargs):
        for app_agent in request.env['app.agent'].sudo().search([]):
            ding_obj = Dingtalk(token={'access_token': app_agent.token})
            persistent_code_dict = ding_obj.get_persistent_code(kwargs.get('code'))
            sns_token_dict = ding_obj.get_sns_token(persistent_code_dict.get('openid'),
                                                          persistent_code_dict.get('persistent_code'))
            user_info_dict = ding_obj.get_user_info_by_sns_token(sns_token_dict.get('sns_token'))
            for user in request.env['ding.user'].sudo().search([('unionid', '=', user_info_dict.get('user_info', {}).get('unionid'))]):
                request.session.authenticate(request.session.db, user.ding_user_id.login, user.ding_user_id.oauth_access_token)
                return http.local_redirect('/web/')
            return werkzeug.utils.redirect('/web')

