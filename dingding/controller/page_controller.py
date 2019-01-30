# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import HttpRequest, request, Response, JsonRequest
from odoo.addons.dingding.dingtalk_crypto.crypto import DingTalkCrypto
import os
import sys
import jinja2
from odoo.tools.safe_eval import safe_eval
from odoo.addons.web.controllers.main import clean_action
from odoo.addons.dingding.ding_api import Dingtalk
# from dingding.ding_api import jsApiList
import requests, simplejson, json

if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.dingding.controller', "html")
env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)


def _json_response(self, result=None, error=None):
    response = {
        'jsonrpc': '2.0',
        'id': self.jsonrequest.get('id')
    }
    if result and isinstance(result, dict) and result.get('msg_signature'):
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


JsonRequest._json_response = _json_response


class PageShow(http.Controller):
    def __init__(self):
        self.login_user = False
        self.login_session = False

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
            print dingding_userid
            dinguser_row = request.env['ding.user'].sudo().search([('ding_id', '=', dingding_userid)])
            print dinguser_row
            if dinguser_row:
                uid = request.session.authenticate(request.session.db, dinguser_row.ding_user_id.login,
                                         dinguser_row.ding_user_id.oauth_access_token)

                print uid
            return request.make_response(res.json())
        except:
             return 'error'

    @http.route('/web/mobile', auth='none', type='http', csrf=False)
    def odoo_mobile_page(self, **args):
        template = env.get_template("odoo_mobile.html")
        return template.render()


    @http.route('/odoo/get_first_level_menu', auth='none', type='http', crsf=False)
    def get_first_level_menu(self, **args):
        menu_rows = []
        for menu_row in request.env['ir.ui.menu'].sudo().search_read([('parent_id', '=', False),('child_id', '!=', False)]):
            second_menus = request.env['ir.ui.menu'].sudo().search_read([('id', 'in', menu_row.get('child_id'))])
            for second_menu in second_menus:
                second_menu.update({'child_menu': request.env['ir.ui.menu'].sudo().search_read([('id', 'in', second_menu.get('child_id', []))])})
            menu_row.update({'child_menu': second_menus})
            menu_rows.append(menu_row)
        print menu_rows
        return request.make_response(simplejson.dumps(menu_rows))

    @http.route('/odoo/get_second_level_menu', auth='none', type='http', crsf=False)
    def get_second_level_menu(self, **args):
        menu_id = request.params.get('parent_id')
        print menu_id
        menu_rows = request.env['ir.ui.menu'].sudo().search_read([('parent_id', '=', int(menu_id)), ('action', '=', False)])
        return request.make_response(simplejson.dumps(menu_rows))

    @http.route('/odoo/get_last_level_menu', auth='none', type='http', crsf=False)
    def get_last_level_menu(self, **args):
        menu_id = int(request.params.get('parent_id'))
        menu_rows = request.env['ir.ui.menu'].sudo().search_read([('parent_id', '=', menu_id), ('action', '!=', False)])
        return request.make_response(simplejson.dumps(menu_rows))

    @http.route('/dingding/call_back_url', auth='none', type="json", csrf=False)
    def dingding_call_back(self, **args):
        ding_rows = request.env['ding.ding'].sudo().search([])
        dingcrypto = DingTalkCrypto(ding_rows[0].aes_key1, str(ding_rows[0].random_token), str(ding_rows[0].corpid))
        rand_str, length, msg, key = dingcrypto.decrypt(request.jsonrequest.get('encrypt'))
        if safe_eval(msg).get('EventType') != 'check_url':
            print safe_eval(msg), "============"
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

    def get_filed_value(self, cr, uid, onefield, context=None):
        return_value = ''
        if onefield.get('type') in ('input', 'textarea'):
            return_value = onefield.get('value')
        elif onefield.get('type') == 'checkbox':
            return_value = [[6, False, onefield.get('value')]]
        else:
            return_value = onefield.get('value')
        if onefield.get('type_detail') == 'number':
            return_value = float(return_value)
        return return_value

    @http.route('/dingding/get_sale_order', auth='none', type='http', methods=['GET'])
    def get_sale_order(self, **args):
        sale_order_rows = request.env['sale.order'].sudo().search([], limit=4)
        return_vals = [{'id': order.id, 'name': order.name}
                       for order in sale_order_rows]
        all_label = [{'name': '订单id', 'prop': 'id', 'invisible': True},{'name': '订单号', 'prop': 'name'}]
        return simplejson.dumps([return_vals, all_label])

    def get_approve_flag(self, cr, uid, leave, context=None):
        if not (leave.is_approve or leave.is_refuse):
            approve_flag = 0
        elif leave.is_approve:
            approve_flag = 1
        elif leave.is_refuse:
            approve_flag = -1
        return approve_flag

    @http.route('/odoo/name_get', type='http', auth="none")
    def name_get(self, **args):
        model = request.params.get('model')
        id = request.params.get('id', '[]')
        record = request.env[model].sudo().browse(eval(id))
        name = record.name_get()
        return request.make_response(simplejson.dumps(name))



    @http.route('/odoo/search_read', type='http', auth="none")
    def search_read(self, **args):
        model = request.params.get('model')
        fields = request.params.get('fields', False)
        offset = eval(request.params.get('offset', '0'))
        limit = eval(request.params.get('limit', '6'))
        domain = request.params.get('domain', '[]')
        sort = request.params.get('sort', None)
        all_record = request.env[model].sudo().search_read(fields=fields, offset=offset,
                                                              limit=limit, domain=eval(domain), order=sort)
        return request.make_response(simplejson.dumps(all_record))

    @http.route('/odoo/fields_get', type='http', auth="none")
    def fields_get(self, **args):
        model = request.params.get('model')
        allfields = request.params.get('allfields', None)
        attributes = request.params.get('attributes', None)
        fields = request.env[model].sudo().fields_get(allfields=allfields, attributes=attributes)
        return request.make_response(simplejson.dumps(fields))

    @http.route('/odoo/load_views', type='http', auth="none")
    def load_views(self, **args):
        model = request.params.get('model')
        views = request.params.get('views', None)
        view = request.env[model].sudo().load_views(views=eval(views.replace('false', 'False')))
        return request.make_response(simplejson.dumps(view))

    @http.route('/odoo/action/load', type='http', auth="none")
    def load(self, **args):
        try:
            action_id = int(request.params.get('action_id'))
            Actions = request.env['ir.actions.actions']
            value = False
            try:
                action_id = int(action_id)
            except ValueError:
                try:
                    action = request.env.sudo().ref(action_id)
                    assert action._name.startswith('ir.actions.')
                    action_id = action.id
                except Exception:
                    action_id = 0   # force failed read

            base_action = Actions.sudo().browse([action_id]).read(['type'])
            if base_action:
                ctx = dict(request.context)
                action_type = base_action[0]['type']
                if action_type == 'ir.actions.report.xml':
                    ctx.update({'bin_size': True})
                request.context = ctx
                action = request.env[action_type].sudo().browse([action_id]).read()
                if action:
                    value = clean_action(action[0])        
            fields = request.env[value.get('res_model')].sudo().fields_get(allfields=None, attributes=None)
            views = request.env[value.get('res_model')].sudo().load_views(views= value.get('views'))
            return request.make_response(simplejson.dumps({'action': value, 'views':views, 'fields': fields }))

        except Exception:
            return request.make_response(simplejson.dumps({}))

