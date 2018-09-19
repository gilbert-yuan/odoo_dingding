#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = '懒懒的天空'

import requests
import time
import json
import datetime
from odoo.exceptions import UserError
import hashlib
import urllib
import simplejson

# 这个设置可以去除 urllib3的不必要的 warning
requests.packages.urllib3.disable_warnings()

DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = "%s %s" % (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_TIME_FORMAT)

"""
单例模式 的其中一种写法
"""


class Singleton(object):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance

# 所有的回调事件
# 'user_add_org', 'user_modify_org', 'user_leave_org','org_admin_add', 'org_admin_remove', 'org_dept_create',
# 'org_dept_modify', 'org_dept_remove', 'org_remove','label_user_change', 'label_conf_add', 'label_conf_modify',
# 'label_conf_del','org_change', 'chat_add_member', 'chat_remove_member', 'chat_quit', 'chat_update_owner',
# 'chat_update_title', 'chat_disband', 'chat_disband_microapp','check_in','bpms_task_change','bpms_instance_change'

class Dingtalk(Singleton):
    def __init__(self, corpid=None, corpsecret=None,
                 agent_id=None, token={}, appkey=None, appsecret=None):  # 初始化的时候需要获取corpid和corpsecret，
        # 需要从管理后台获取 , corpid, corpsecret, agent_id
        self.__params = {
            'corpid': corpid,
            'corpsecret': corpsecret,
        }
        self.__app_params = {
            'appid': appkey,
            'appsecret': appsecret,
        }
        self.token_dict = {
            'access_token': token.get('access_token')
        }
        self._header = {'Content-Type': 'application/json'}  # 全局固定用的 请求的 header 个别的不一样要单独写
        self._agent_id = agent_id,

        self._url_jsapi_ticket = 'https://oapi.dingtalk.com/get_jsapi_ticket'
        self.url_get_token = 'https://oapi.dingtalk.com/gettoken'
        self.url_get_app_token = 'https://oapi.dingtalk.com/sns/gettoken'
        self.get_sso_token = 'https://oapi.dingtalk.com/sso/gettoken'
        self.url_get_sns_token = 'https://oapi.dingtalk.com/sns/get_sns_token'
        self.url_get_dept_list = 'https://oapi.dingtalk.com/department/list'
        self.url_get_dept_detail = 'https://oapi.dingtalk.com/department/get'
        self.url_create_dept = 'https://oapi.dingtalk.com/department/create'
        self.url_delete_dept = 'https://oapi.dingtalk.com/department/delete'
        self.url_update_dept = 'https://oapi.dingtalk.com/department/update'
        self.url_get_user_id_by_unionid = 'https://oapi.dingtalk.com/user/getUseridByUnionid'
        self.url_get_user_detail = 'https://oapi.dingtalk.com/user/get'
        self.url_send_message = 'https://oapi.dingtalk.com/message/send_to_conversation'
        self.url_send = 'https://eco.taobao.com/router/rest'
        self.url_create_user = 'https://oapi.dingtalk.com/user/create'
        self.url_update_user = 'https://oapi.dingtalk.com/user/update'
        self.url_user_list = 'https://oapi.dingtalk.com/user/list'
        self.url_get_user_count = 'https://oapi.dingtalk.com/user/get_org_user_count'
        self.url_get_persistent_code = "https://oapi.dingtalk.com/sns/get_persistent_code"
        self.url_get_user_info_by_sns_token = 'https://oapi.dingtalk.com/sns/getuserinfo'
        self.url_delete_user = 'https://oapi.dingtalk.com/user/delete'
        self.url_register_call_back_interface = "https://oapi.dingtalk.com/call_back/register_call_back"
        self.url_update_call_back_interface = "https://oapi.dingtalk.com/call_back/update_call_back"
        self.url_delete_call_back_interface = "https://oapi.dingtalk.com/call_back/delete_call_back"
        self.url_checkout_call_back_interface = "https://oapi.dingtalk.com/call_back/get_call_back"
        self.url_get_call_fail_record = 'https://oapi.dingtalk.com/call_back/get_call_back_failed_result'

        self.approver_common_url = 'https://eco.taobao.com/router/rest'
        self.approver_common_header = {'Content-Type': 'application/x-www-form-urlencoded',
                                       'charset': 'utf-8'}
        self.method_approver_create_processinstance = 'dingtalk.smartwork.bpms.processinstance.create'

    def get_call_fail_record(self):
        res = requests.get(self.url_get_call_fail_record,
                           headers=self._header,
                           params=self.token_dict)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_user_info_by_sns_token(self, sns_token):
        params = {
            'sns_token': sns_token
        }
        params.update(self.token_dict)
        res = requests.get(self.url_get_user_info_by_sns_token,
                           headers=self._header,
                           params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_persistent_code(self, code):
        params = {
            'tmp_auth_code': code
        }
        res = requests.post(self.url_get_persistent_code,
                           headers=self._header,
                           params=self.token_dict,
                            data=json.dumps(params))
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_sns_token(self, openid, persistent_code):
        params = {
            'openid': openid,
            'persistent_code': persistent_code,
        }
        res = requests.post(self.url_get_sns_token,
                           headers=self._header,
                           params=self.token_dict,
                           data=json.dumps(params))
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def delete_call_back_interface(self):
        """
        删除回调接口 链接 :return:
        """
        res = requests.get(self.url_delete_call_back_interface,
                           headers=self._header,
                           params=self.token_dict)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def update_call_back_interface(self, token, aes_key, url, call_back_tags):
        """
            更新回调接口 链接 :return:
        """
        data = {
            "call_back_tag": call_back_tags,
            "token": token,
            "aes_key": aes_key,
            "url": url
        }
        res = requests.post(self.url_update_call_back_interface,
                            headers=self._header,
                            params=self.token_dict,
                            data=json.dumps(data))
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def register_call_back_interface(self, token, aes_key, url, call_back_tags):
        """
        注册回调接口
        :param token: 在钉钉模型上的 token 随机填写
        :param aes_key:  在钉钉模型上的 aes_key 随机生成的 43位 aes_key
        :param url:  ‘填写要回调的URL   地址’
        :param call_back_tags: ‘填写要回调的 事件’
        :return:
        """
        data = {
            "call_back_tag": call_back_tags,
            "token": token,
            "aes_key": aes_key,
            "url": url
        }
        res = requests.post(self.url_register_call_back_interface,
                            headers=self._header,
                            params=self.token_dict,
                            data=json.dumps(data))
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def checkout_call_back_interface(self):
        """
        检查是否回调事件注册成功
        :return:
        """
        res = requests.get(self.url_checkout_call_back_interface,
                           headers=self._header,
                           params=self.token_dict)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def __raise_error(self, res):
        """
        弹出事件返回的报错信息
        :param res:
        :return:
        """
        raise UserError(u'错误代码: %s,详细错误信息: %s' % (res.json()['errcode'], res.json()['errmsg']))

    def app_get_token(self):
        """
        获取大部分时间的token(有的事件链接还要单独获取不同的token)
        :return: token 并取得token 获取token的时间
        """
        print(self.__params, self._header)
        res = requests.get(self.url_get_app_token, headers=self._header, params=self.__app_params)
        try:
            token_vals = res.json()
            token_vals.update({'expired_in': (time.time() + 7200)})
            return token_vals
        except:
            self.__raise_error(res)

    def get_token(self):
        """
        获取大部分时间的token(有的事件链接还要单独获取不同的token)
        :return: token 并取得token 获取token的时间
        """
        print(self.__params, self._header)
        res = requests.get(self.url_get_token, headers=self._header, params=self.__params)
        try:
            token_vals = res.json()
            token_vals.update({'expired_in': (time.time() + 7200)})
            return token_vals
        except:
            self.__raise_error(res)

    def get_common_param(self, method):
        date_now = datetime.datetime.now()
        common_param = dict(v='2.0',
                            format='json',
                            session=(self.token_dict).get('access_token'),
                            method=method,
                            partner_id='apidoc',
                            timestamp=date_now.strftime('%Y-%m-%d %H:%M:%S'),
                            )
        return common_param

    def delete_user(self, user_id):
        """
        删除用户
        :param user_id:
        :return:
        """
        params = self.token_dict
        params.update({'userid': user_id})
        res = requests.get(self.url_delete_user, params=params)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def create_user(self, user_vals):
        """
        新建用户
        :param user_vals:
        :return:
        """
        res = requests.post(self.url_create_user,
                            headers=self._header,
                            params=self.token_dict,
                            data=json.dumps(self.remove_False_vals(user_vals)))
        try:
            return res.json()['userid']
        except:
            self.__raise_error(res)

    def update_user(self, user_vals):
        """
        更新用户信息
        :param user_vals:
        :return:
        """
        res = requests.post(self.url_update_user,
                            params=self.token_dict,
                            data=json.dumps(user_vals))
        try:
            return res.json()['errmsg']
        except:
            self.__raise_error(res)

    def update_dept(self, dept_vals):
        """
        更新部门的信息
        :param dept_vals:
        :return:
        """
        res = requests.post(self.url_update_dept,
                            params=self.token_dict,
                            data=json.dumps(dept_vals))
        try:
            return res.json()['errmsg']
        except:
            self.__raise_error(res)

    def get_dept_list(self):
        """
        获取部门列表
        :return:
        """
        res = requests.get(self.url_get_dept_list,
                           params=self.token_dict)
        try:
            return res.json()['department']
        except:
            self.__raise_error(res)

    def get_depatment_user_list(self, department_id):
        """
        获取部门的 用户列表
        :param department_id:
        :return:
        """
        params = self.token_dict
        params.update({'department_id': department_id})
        res = requests.get(self.url_user_list,
                           params=params)
        try:
            return res.json()['userlist']
        except:
            self.__raise_error(res)

    def get_dept_detail(self, dept_id):
        """
        获取部门的详细情况
        :param dept_id:
        :return:
        """
        params = self.token_dict
        params.update({'id': dept_id})
        res = requests.get(self.url_get_dept_detail,
                           params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def create_dept(self, name, parentid, orderid, createdeptgroup=True):
        """
        创建新的部门
        :param name:
        :param parentid:
        :param orderid:
        :param createdeptgroup:
        :return:
        """
        payload = {
            'name': name,
            'parentid': parentid or '1',
            'orderid': orderid,
            'createDeptGroup': createdeptgroup,
        }
        res = requests.post(self.url_create_dept,
                            headers=self._header,
                            params=self.token_dict,
                            data=json.dumps(payload))
        try:
            return res.json()['id']
        except:
            self.__raise_error(res)

    def delete_dept(self, dept_id):
        """
        删除部门
        :param dept_id:
        :return:
        """
        params = self.token_dict
        params.update({'id': dept_id})
        res = requests.get(self.url_delete_dept, params=params)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def get_userid_by_unionid(self, unionid):
        """
        获取用户详细情况 通过 unionid
        :param unionid:
        :return:
        """
        params = self.token_dict
        params.update({'unionid': unionid})
        res = requests.get(self.url_get_user_id_by_unionid, params=params)
        try:
            return res.json()['userid']
        except:
            self.__raise_error(res)

    def get_js_api_ticket(self):
        """
        获取 jsapi 的访问 票据
        :return:
        """
        res = requests.get(self._url_jsapi_ticket, params=self.token_dict)
        try:
            return res.json()['ticket']
        except:
            self.__raise_error(res)

    def get_signature(self, vals={}):
        """
        对jsapi 参数进行处理获取 对应参数的 signature
        :param vals:
        :return:
        """
        sorted_vals = sorted(vals.items(), lambda x, y: cmp(x[1], y[1]))
        url_vals = urllib.urlencode(sorted_vals)
        signature = hashlib.sha1(url_vals).hexdigest()  # sha 加密
        return signature

    def get_js_api_params(self, url, nonceStr):
        """
        处理 数据 去的 jsapi 需要的 各种参数
        :param url:
        :param nonceStr:
        :return: 返回各种需要的参数 在 jsapi 中
        """
        jsapi_ticket = self.get_js_api_ticket()
        timestamp = int(time.time())
        signature_vals = {
            'noncestr': nonceStr,
            'jsapi_ticket': jsapi_ticket,
            'url': url,
            'timestamp': timestamp,
        }
        signature = self.get_signature(signature_vals)
        try:
            return signature, timestamp, nonceStr
        except:
            self.__raise_error({"error": u'错误！'})

    def get_user_detail(self, userid):
        params = self.token_dict
        params.update({'userid': userid})
        res = requests.get(self.url_get_user_detail, params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def remove_False_vals(self, dict_vals={}):
        """
        取出没有修改的地方的内容
        :param dict_vals:
        :return:
        """
        keys = [key for key, vals in dict_vals.items() if not dict_vals.get(key)]
        for key in keys:
            del dict_vals[key]
        return dict_vals

    def send_message(self, messages, userid_list='', dept_id_list='',
                     msgtype='text', to_all_user='false'):
        """
        发送消息
        :param messages: 消息体内容
        :param userid_list: 接受消息的用户列表
        :param dept_id_list: 接受消息的部门列表
        :param msgtype: 消息的类型
        :param to_all_user: 是否发送给每一个人
        :return:
        """
        payload = {
            'agent_id': self._agent_id[0],
            "msgtype": msgtype,
            'userid_list': userid_list,
            'dept_id_list': dept_id_list,
            'to_all_user': to_all_user,
            "msgcontent": json.dumps(messages)
        }
        params = {'v': 2.0,
                  'method': 'dingtalk.corp.message.corpconversation.asyncsend',
                  'format': 'json',
                  'session': (self.token_dict).get('access_token'),
                  'timestamp': datetime.datetime.now()}

        res = requests.post(self.url_send,
                            headers={'Content-Type':
                                         'application/x-www-form-urlencoded;\charset=utf-8'},
                            params=params,
                            data=self.remove_False_vals(payload))
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def get_user_count(self, only_active=0):
        """
        获取 用户的
        :param only_active:
        :return:
        """
        params = self.token_dict
        params.update({'onlyActive': only_active})
        res = requests.get(self.url_get_user_count, params=params)
        try:
            return res.json()['count']
        except:
            self.__raise_error(res)

    def send_oa_message(self, message, userid_list='', dept_id_list='', to_all_user='false'):
        """
        发送 固定格式的消息的一个格式的设定
        :param message:
        :param userid_list:
        :param dept_id_list:
        :param to_all_user:
        :return:
        """
        message = {"message_url": message.get("message_url"),
                   "head": {"bgcolor": message.get('bgcolor'),
                            "text": message.get('head')},
                   "body": {"title": message.get('title'),
                            "form": message.get('form'),
                            # [{"key": "姓名:","value": "张三"}, {"key": "爱好:","value": "打球、听音乐"}]
                            "rich": message.get('rich'),
                            # {"num": "15.6","unit": "元"},
                            "content": message.get('content'),
                            # "大段文本大段文本大段文本大段文本大段文本大段文本大段文本大段文本大段文本大段文本大段文本大段文本",
                            "image": message.get('image'),
                            # "@lADOADmaWMzazQKA",
                            "file_count": message.get('file_count'),
                            # "3",
                            "author": message.get('author'),
                            # "李四 "}
                            }}
        self.send_message(message,
                          userid_list=userid_list,
                          dept_id_list=dept_id_list,
                          msgtype='oa',
                          to_all_user=to_all_user)
        return True

    def send_text_message(self, message, userid_list, dept_id_list):
        """
        发送普通消息的 简化参数
        :param message: 消息内容
        :param userid_list: 发送用户 列表
        :param dept_id_list: 发送部门的列表
        :return:
        """
        self.send_message({"content": message},
                          userid_list=userid_list,
                          dept_id_list=dept_id_list,
                          msgtype='text', )
        return True

    def create_new_approver(self, vals):
        print(json.dumps(vals))
        vals.update(self.get_common_param(self.method_approver_create_processinstance))
        res = requests.post(self.approver_common_url,
                            headers=self.approver_common_header,
                            params=vals)
        all_response = res.json()['dingtalk_smartwork_bpms_processinstance_create_response']
        if all_response.get('result').get('is_success'):
            return True
        else:
            raise UserError(all_response.get('result').get('error_msg'))


jsApiList = ['device.notification.alert',
             'device.notification.confirm',
             'device.notification.prompt',
             'device.notification.vibrate',
             'device.accelerometer.watchShake',
             'device.accelerometer.clearShake',
             'device.notification.toast',
             'device.notification.actionSheet',
             'device.notification.showPreloader',
             'device.notification.hidePreloader',
             'biz.navigation.setLeft',
             'biz.navigation.setRight',
             'biz.navigation.setTitle',
             'device.connection.getNetworkType',
             'biz.util.openLink',
             'biz.util.datepicker',
             'biz.util.timepicker',
             'biz.util.datetimepicker',
             'biz.navigation.goBack',
             'biz.navigation.close',
             'biz.navigation.setMenu',
             'biz.navigation.replace',
             'biz.util.previewImage',
             'biz.util.chosen',
             'ui.input.plain',
             'ui.progressBar.setColors',
             'ui.pullToRefresh.enable',
             'ui.pullToRefresh.disable',
             'ui.pullToRefresh.stop',
             'ui.webViewBounce.disable',
             'ui.webViewBounce.enable',
             'runtime.permission.requestAuthCode',
             'device.notification.modal',
             'biz.util.scan',
             'biz.navigation.setIcon',
             'ui.nav.preload',
             'ui.nav.go',
             'ui.nav.recycle',
             'ui.nav.getCurrentId',
             'ui.nav.close',
             'ui.nav.backTo',
             'ui.nav.push',
             'ui.nav.pop',
             'ui.nav.quit',
             'device.base.getSettings',
             'device.nfc.nfcRead',
             'util.domainStorage.setItem',
             'util.domainStorage.getItem',
             'util.domainStorage.removeItem',
             'service.request.httpOverLwp',
             'device.geolocation.get',
             'device.base.getUUID',
             'device.base.getInterface',
             'device.launcher.checkInstalledApps',
             'device.launcher.launchApp',
             'biz.util.open',
             'biz.util.share',
             'biz.contact.choose',
             'biz.user.get',
             'biz.util.uploadImage',
             'biz.ding.post',
             'biz.telephone.call',
             'biz.telephone.showCallMenu',
             'biz.chat.chooseConversation',
             'biz.contact.createGroup',
             'biz.map.locate',
             'biz.map.search',
             'biz.map.view',
             'device.geolocation.openGps',
             'biz.util.uploadImageFromCamera',
             'biz.customContact.multipleChoose',
             'biz.customContact.choose',
             'biz.contact.complexPicker',
             'biz.contact.departmentsPicker',
             'biz.contact.setRule',
             'biz.contact.externalComplexPicker',
             'biz.contact.externalEditForm',
             'biz.chat.pickConversation',
             'biz.chat.chooseConversationByCorpId',
             'biz.chat.openSingleChat',
             'biz.chat.toConversation',
             'biz.cspace.saveFile',
             'biz.cspace.preview',
             'biz.cspace.chooseSpaceDir',
             'biz.util.uploadAttachment',
             'biz.clipboardData.setData',
             'biz.intent.fetchData',
             'biz.chat.locationChatMessage',
             'device.audio.startRecord',
             'device.audio.stopRecord',
             'device.audio.onRecordEnd',
             'device.audio.download',
             'device.audio.play',
             'device.audio.pause',
             'device.audio.resume',
             'device.audio.stop',
             'device.audio.onPlayEnd',
             'device.audio.translateVoice',
             'biz.util.fetchImageData',
             'biz.alipay.auth',
             'biz.alipay.pay',
             'device.nfc.nfcWrite',
             'biz.util.encrypt',
             'biz.util.decrypt',
             'runtime.permission.requestOperateAuthCode',
             'biz.util.scanCard', ]
