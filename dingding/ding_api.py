#!/usr/bin/env python
# -*- coding:utf-8 -*-
# __author__ = '懒懒的天空'

import requests
import time
import json
import datetime
from odoo.exceptions import UserError

requests.packages.urllib3.disable_warnings()
DEFAULT_SERVER_DATE_FORMAT = "%Y-%m-%d"
DEFAULT_SERVER_TIME_FORMAT = "%H:%M:%S"
DEFAULT_SERVER_DATETIME_FORMAT = "%s %s" % (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_TIME_FORMAT)
import aip

class Singleton(object):
    def __init__(cls, name, bases, dict):
        super(Singleton, cls).__init__(name, bases, dict)
        cls._instance = None

    def __call__(cls, *args, **kw):
        if cls._instance is None:
            cls._instance = super(Singleton, cls).__call__(*args, **kw)
        return cls._instance


class Dingtalk(Singleton):

    def __init__(self, corpid, corpsecret,
                 agent_id, token={}):  # 初始化的时候需要获取corpid和corpsecret，
        # 需要从管理后台获取 , corpid, corpsecret, agent_id
        self.__params = {
            'corpid': corpid,  # 'ding95b28951cc12e7d835c2f4657eb6378f' ,
            # #ding95b28951cc12e7d835c2f4657eb6378f
            'corpsecret': corpsecret,
            # mYZM01r9Zj3lMj2x5KdBMcA0v842pP6_GIw_FNNolc1zCujCUzA4eUyuLYflp7CT
        }
        self.token_dict = {
                           'access_token': token.get('access_token')
                          }
        self._header = {'content-type': 'application/json'}
        self._agent_id = agent_id,
        self.url_get_token = 'https://oapi.dingtalk.com/gettoken'
        self.get_sso_token = 'https://oapi.dingtalk.com/sso/gettoken'
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
        self.isv_common_url = 'https://eco.taobao.com/router/rest'
        self.isv_common_header = {'Content-Type': 'application/x-www-form-urlencoded',
                                  'charset': 'utf-8'}
        self.url_delete_user = 'https://oapi.dingtalk.com/user/delete'

    def __raise_error(self, res):
        raise UserError(u'错误代码: %s,详细错误信息: %s' % (res.json()['errcode'], res.json()['errmsg']))
        global senderr
        sendstatus = False
        senderr = 'error code: %s,error message: %s' % (res.json()['errcode'], res.json()['errmsg'])

    def get_token(self):
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
        params = self.token_dict
        params.update({'userid': user_id})
        res = requests.get(self.url_delete_user, params=params)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)



    def create_user(self, user_vals):
        res = requests.post(self.url_create_user,
                            headers=self._header,
                            params=self.token_dict,
                            data=json.dumps(self.remove_False_vals(user_vals)))
        try:
            return res.json()['userid']
        except:
            self.__raise_error(res)

    def update_user(self, user_vals):
        print user_vals
        res = requests.post(self.url_update_user,
                            params=self.token_dict,
                            data=json.dumps(user_vals))
        print res.json(),"==========="
        try:
            return res.json()['errmsg']
        except:
            self.__raise_error(res)

    def update_dept(self, dept_vals):
        res = requests.post(self.url_update_dept,
                            params=self.token_dict,
                            data=json.dumps(dept_vals))
        try:
            return res.json()['errmsg']
        except:
            self.__raise_error(res)

    def get_dept_list(self):
        res = requests.get(self.url_get_dept_list,
                           params=self.token_dict)
        try:
            return res.json()['department']
        except:
            self.__raise_error(res)

    def get_depatment_user_list(self, department_id):
        params = self.token_dict
        params.update({'department_id': department_id})
        res = requests.get(self.url_user_list,
                           params=params)
        try:
            return res.json()['userlist']
        except:
            self.__raise_error(res)

    def get_dept_detail(self, dept_id):
        params = self.token_dict
        params.update({'id': dept_id})
        res = requests.get(self.url_get_dept_detail,
                           params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def create_dept(self, name, parentid, orderid, createdeptgroup=True):
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
        params = self.token_dict
        params.update({'id': dept_id})
        res = requests.get(self.url_delete_dept, params=params)
        try:
            return res.json()['errcode']
        except:
            self.__raise_error(res)

    def get_userid_by_unionid(self, unionid):
        params = self.token_dict
        params.update({'unionid': unionid})
        res = requests.get(self.url_get_user_id_by_unionid, params=params)
        try:
            return res.json()['userid']
        except:
            self.__raise_error(res)

    def get_user_detail(self, userid):
        params = self.token_dict
        params.update({'userid': userid})
        res = requests.get(self.url_get_user_detail, params=params)
        try:
            return res.json()
        except:
            self.__raise_error(res)

    def remove_False_vals(self, dict_vals={}):
        keys = [key for key, vals in dict_vals.iteritems() if not dict_vals.get(key)]
        for key in keys:
            del dict_vals[key]
        return dict_vals

    def send_message(self, messages, userid_list='', dept_id_list='',
                     msgtype='text', to_all_user='false'):
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
        params = self.token_dict
        params.update({'onlyActive': only_active})
        res = requests.get(self.url_get_user_count, params=params)
        try:
            return res.json()['count']
        except:
            self.__raise_error(res)

    def send_oa_message(self, message, userid_list='', dept_id_list='', to_all_user='false'):
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
        self.send_message({"content": message},
                          userid_list=userid_list,
                          dept_id_list=dept_id_list,
                          msgtype='text', )
        return True
