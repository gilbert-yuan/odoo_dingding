# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.addons.dingding.ding_api import Dingtalk
from odoo.exceptions import UserError
import random, simplejson


ALLCHAR = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'
ALLCALLBACKTAG = ['user_add_org', 'user_modify_org', 'user_leave_org', 'org_admin_add', 'org_admin_remove',
                  'org_dept_create', 'org_dept_modify', 'org_dept_remove', 'org_remove', 'chat_add_member',
                  'chat_remove_member', 'chat_quit', 'chat_update_owner', 'chat_update_title', 'chat_disband',
                  'chat_disband_microapp', 'check_in', 'bpms_task_change', 'bpms_instance_change', 'label_user_change',
                  'label_conf_add', 'label_conf_modify', 'label_conf_del'
                  ]

class ding_ding(models.Model):
    _name = 'ding.ding'
    _description = u'钉钉账户主要信息设置'

    name = fields.Char(u'钉钉对象')
    #钉钉中的基本的配置
    corpid = fields.Char(u'钉钉corpid', required=True, help=u'由钉钉开放平台提供给开放应用的唯一标识')
    corpsecret = fields.Char(u'钉钉corpsecret', required=True)
    agent_ids = fields.One2many('ding.agent', 'ding_id', string='自建应用（程序主要用于发送消息）', required=True)
    app_ids = fields.One2many('app.agent', 'ding_id', string='用于扫码登陆', required=True)
    eagent_ids = fields.One2many('e.agent', 'ding_id', string='自建e 应用',
                                    help='钉钉新推出了E应用开发，E应用开发是一种全新的开发模式，通过简洁的前端语法写出Native级别的性能体验'
                                         '，支持iOS、安卓等多端（PC端暂不支持）部署。',  required=True)
    # 保存token（和重置） 用的字段
    token = fields.Char(u'token', readonly=True)
    expired_in = fields.Char(u'过期时间', readonly=True)
    # 这一部分字段用于 钉钉审批对接 （钉钉自带应用）事件回调 所用到的字段
    aes_key1 = fields.Char(u'随机字符串', default=lambda self: ''.join(random.sample(ALLCHAR, 43)), readonly=True)
    random_token = fields.Char(u'随机token', default='01234565789')
    call_back_url = fields.Char(u'会调事件URL', default='http:odoo10.tunnel.800890.com/dingding/call_back_url')
    call_back_tags = fields.Char(u'回调事件', default=ALLCALLBACKTAG)
    is_ok_call_back_url = fields.Boolean(u'回调接口设置正常')
    # 钉钉中访问第三方台获取钉钉用户信息 所用到的设置， 及字段
    # 钉钉文档链接https://open-doc.dingtalk.com/docs/doc.htm?spm=a219a.7629140.0.0.USEUsY&treeId=168&articleId=104881&docType=1
    # https://oapi.dingtalk.com/connect/oauth2/sns_authorize?appid=APPID&response_type=code&scope=snsapi_login&state=STATE&redirect_uri=REDIRECT_URI
    # 钉钉中访问第三方平台 ，回调url
    appsecret = fields.Char(u'appsecret', help=u'由钉钉开放平台提供的密钥')
    sns_token = fields.Char(u'snstoken', help=u' 使用appid及appSecret访问如下接口， 获取accesstoken，此处获取的token有效期为2小时，\
    有效期内重复获取，返回相同值，并自动续期，如果在有效期外获取会获得新的token值，建议定时获取本token，不需要用户登录时再获取。')
    sns_token_expired_in = fields.Char(u'过期时间', readonly=True)


    def handler_map(self):
        if getattr(self, 'handlers', None):
            return self.handlers
        return {
            'user_add_org': self.user_add_org,
            #'check_url': self.register_call_back_interface,
            'user_modify_org': self.user_modify_org,
            'user_leave_org': self.user_leave_org,
            'org_admin_add': self.org_admin_add,
            'org_admin_remove': self.org_admin_remove,
            'org_dept_create': self.org_dept_create,
            'org_dept_modify': self.org_dept_modify,
            'org_dept_remove': self.org_dept_remove,
            'org_remove': self.org_remove,
            'label_user_change': self.label_user_change,
            'label_conf_add': self.label_conf_add,
            'label_conf_modify': self.label_conf_modify,
            'label_conf_del': self.label_conf_del,
            'org_change': self.org_change,
            'chat_add_member': self.chat_add_member,
            'chat_remove_member': self.chat_remove_member,
            'chat_quit': self.chat_quit,
            'chat_update_owner': self.chat_update_owner,
            'chat_update_title': self.chat_update_title,
            'chat_disband': self.chat_disband,
            'chat_disband_microapp': self.chat_disband_microapp,
            'check_in': self.check_in,
            'bpms_task_change': self.bpms_task_change,
            'bpms_instance_change': self.bpms_instance_change,
        }

    def chat_disband(self, msg):
        pass

    def chat_update_owner(self, msg):
        """更改群聊 所有者"""
        pass

    def chat_update_title(self, msg):
        """更新群聊 名称"""
        pass

    def chat_disband_microapp(self, msg):
        """解散群聊"""
        pass

    def chat_remove_member(self, msg):
        """删除群聊 中用户"""
        pass

    def chat_quit(self, msg):
        """用户推出群聊"""
        pass

    def org_change(self, msg):
        """ 企业信息发生变更"""
        pass

    def chat_add_member(self, msg):
        """群聊添加 成员"""
        pass

    def user_add_org(self, msg):
        """通讯录用户增加"""
        pass
    def user_modify_org(self, msg):
        """通讯录用户更改"""
        pass

    def user_leave_org(self, msg):
        """通讯录用户离职"""
        pass

    def org_admin_add(self, msg):
        """通讯录用户被设为管理员"""
        pass

    def org_admin_remove(self, msg):
        """通讯录用户被取消设置管理员"""
        pass
    def org_dept_create(self, msg):
        """ 通讯录企业部门创建"""
        pass

    def org_dept_modify(self, msg):
        """通讯录企业部门修改"""
        pass

    def org_dept_remove(self, msg):
        """通讯录企业部门删除"""
        pass

    def org_remove(self, msg):
        """企业被解散"""
        pass

    def label_user_change(self, msg):
        """员工角色信息发生变更"""
        pass

    def label_conf_add(self, msg):
        """增加角色或者角色组"""
        pass
    def label_conf_modify(self, msg):
        """修改角色或者角色组"""
        pass

    def label_conf_del(self, msg):
        """删除角色或者角色组"""
        pass

    def bpms_task_change(self, msg):
        """审批任务开始  审批任务结束 审批任务转交"""
        pass

    def bpms_instance_change(self, msg):
        """审批实例开始  审批实例结束|终止"""
        pass

    def check_in(self, msg):
        pass

    def create_new_approver(self):
        agent_row = self.env.ref("dingding.ding_agent_xml")
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message(agent_row.agent_id)
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        vals = {
            'agent_id': agent_id,
            'process_code': 'PROC-TXEKLZ3V-EJKNZY8FRS05FSWKCBOW1-6CGS3J6J-R',
            'originator_user_id': 'manager1461',
            'dept_id': '44507267',
            'approvers': 'manager1461',
            'cc_list': 'manager1461',
            'cc_position': 'START_FINISH',
            'form_component_values': simplejson.dumps([{"name": u"采购备注", "value": u"买个西瓜 甜瓜"},
                                                 {'name': u'明细', "value": [[{"name": "产品", "value": "西瓜"},
                                                                           {"name":  "数量", "value": "10"},
                                                                           {"name": "价格", "value": "100"}],
                                                                          [{"name": "产品", "value": "甜瓜"},
                                                                           {"name": "数量", "value": "5"},
                                                                           {"name": "价格", "value": "2"},
                                                                           ]
                                                                          ]
                                                  }
                                     ])
        }
        return_vals = ding_obj.create_new_approver(vals)
        if return_vals == '0':
            return True
        else:
            print("error")

    def get_call_fail_record(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        return_vals = ding_obj.get_call_fail_record()
        raise UserError(str(return_vals))

    def register_call_back_interface(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        return_vals = ding_obj.register_call_back_interface(str(self.random_token),
                                                            str(self.aes_key1),
                                                            self.call_back_url,
                                                            eval(self.call_back_tags))
        if return_vals == '0':
            return True
        else:
            print(return_vals)

    def delete_call_back_interface(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        return_vals = ding_obj.delete_call_back_interface()
        if return_vals == '0':
            return True
        else:
            print("error")

    def update_call_back_interface(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(ccorpid=corpid, corpsecret=corpsecret, token=token_dict)
        return_vals = ding_obj.update_call_back_interface(str(self.random_token),
                                                            str(self.aes_key1),
                                                            self.call_back_url,
                                                            eval(self.call_back_tags))
        if return_vals == '0':
            return True
        else:
            print("error")

    def checkout_call_back_interface(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        return_vals = ding_obj.checkout_call_back_interface()
        if return_vals == 0:
            self.is_ok_call_back_url = True
            return True
        else:
            print("error")

    def get_ding_department(self):
        department_obj = self.env['ding.department']
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        department_dict = ding_obj.get_dept_list()
        if not department_dict:
            raise UserError(u'企业号中还没创建部门')
        cr = self.env.cr
        department_row_parent = False
        for department in department_dict:
            if department.get('parentid'):
                department_row_parent = department_obj.search([('department_id', '=', department.get('parentid'))])
            if department.get('id') and department.get('name'):
                department_row = department_obj.search([('department_id', '=', department.get('id'))])
                if not department_row:
                    cr.execute("""INSERT INTO ding_department 
                                  (department_id, name, parent_id) VALUES 
                                  (%s,'%s', %s)""" % (department.get('id'),
                                                      department.get('name'),
                                                      department_row_parent
                                                      and department_row_parent.id or 'NULL'))
        return True

    def get_ding_user(self, user):
        cr = self.env.cr
        if user.get('mobile'):
            department_row = self.env['ding.department'].search([("department_id", '=',
                                                                  (user.get('department')[
                                                                       len(user.get('department')) - 1]))])
            parnter_row = self.env['res.partner'].search([('mobile', '=',  user.get('mobile'))])
            if parnter_row:
                parnter_row.department_id = department_row.id
            if parnter_row.user_ids:
                parnter_row.user_ids[0].oauth_access_token = user.get('unionid')
            cr.execute("""INSERT INTO ding_user 
                          (department_id, name, work_place, ding_id ,mobile_num, email,
                           position, ding_user_id, jobnumber,open_id, ishide, active, unionid, dingding_id) VALUES
                          (%s,'%s', '%s', '%s','%s', '%s', '%s', %s, '%s',  '%s', %s, %s,  '%s', '%s')""" %
                       (department_row.id or 'NULL', user.get('name'),
                        user.get('workPlace') or "NULL", user.get('userid'), user.get('mobile'),
                        user.get('email') or 'NULL', user.get('position') or "NULL",
                        parnter_row and parnter_row.user_ids and parnter_row.user_ids[0].id or 'NULL',
                        user.get('jobnumber'), user.get('openId'), user.get('isHide'), user.get('active'),
                        user.get('unionid'), user.get('dingId')
                        ))
        return True

    def get_dingdinguser(self):
        department_rows = self.env['ding.department'].search([])

        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for department_row in department_rows:
            user_dicts = ding_obj.get_depatment_user_list(department_row.department_id)
            for user in user_dicts:
                if not self.env['ding.user'].search([('ding_id', '=', user.get('userid'))]):
                    self.get_ding_user(user)

    def get_ding_common_message(self, agent_id=False):
        dingding_row = self.env.ref('dingding.ding_ding_xml')
        return (dingding_row.corpid,
                dingding_row.corpsecret,
                agent_id,
                {
                    'access_token': dingding_row.token,
                    'expired_in': dingding_row.expired_in
                })


class ding_agent(models.Model):
    _name = 'ding.agent'
    _description = u'钉钉客户端应用配置'

    name = fields.Char(u'agent名字')
    agent_id = fields.Char(u'agent_id', required=True)
    ding_id = fields.Many2one('ding.ding', u'钉钉主记录')


class AppAgent(models.Model):
    _name = 'app.agent'
    _description = u'钉钉客户端应用配置'

    name = fields.Char(u'app agent名字')
    agent_id = fields.Char(u'app_id', required=True)
    app_secret = fields.Char(u'appSecret', required=True)
    ding_id = fields.Many2one('ding.ding', u'钉钉主记录')
    expired_in = fields.Char(u'过期时间', readonly=True)
    token = fields.Char(u'token', readonly=True)


class EAgent(models.Model):
    _name = 'e.agent'
    _description = u'钉钉客户端应用配置'

    name = fields.Char(u'e agent名字')
    agent_id = fields.Char(u'AgentId', required=True)
    app_secret = fields.Char(u'appSecret', required=True)
    app_key = fields.Char(u'AppKey', required=True)
    ding_id = fields.Many2one('ding.ding', u'钉钉主记录')
    expired_in = fields.Char(u'过期时间', readonly=True)
    token = fields.Char(u'token', readonly=True)


class ding_department(models.Model):
    _name = 'ding.department'
    _description = u'钉钉用户部门同步'
    _rec_name = 'name'
    name = fields.Char(u'部门名字', required=True)
    department_id = fields.Char(u'部门id', readonly=True)
    parent_id = fields.Many2one('ding.department', u'父部门ID')
    ding_id = fields.Char(related='parent_id.department_id', readonly=True, string='Parent name')
    parent_order = fields.Char(string='Parent name')

    @api.model
    def create(self, vals):
        return_vals = super(ding_department, self).create(vals)
        if not self.env.context.get('from_dingding'):
            return_vals.create_department()
        return return_vals

    def create_department(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for deparment in self:
            ding_id = ding_obj.create_dept(deparment.name,
                                           deparment.ding_id, deparment.parent_order)
            deparment.department_id = ding_id
        return True

    @api.multi
    def write(self, vals):
        return_vals = super(ding_department, self).write(vals)
        if not self.env.context.get('from_dingding'):
            self.update_department(vals)
        return return_vals

    def update_department(self, vals):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for deparment in self:
            vals.update({'id': deparment.name})
            ding_obj.update_dept(vals)
        return True

    @api.multi
    def unlink(self):
        return_vals = super(ding_department, self).unlink()
        if not self.env.context.get('from_dingding'):
            self.delete_department()
        return return_vals

    def delete_department(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for deparment in self:
            ding_obj.delete_dept(deparment.name)
        return True


class ding_user(models.Model):
    _name = 'ding.user'
    _description = u'钉钉用户 和客户信息的同步'

    ding_user_id = fields.Many2one('res.users', string=u'系统用户')
    name = fields.Char(u'钉钉用户', required=True)
    sex = fields.Char(u'性别')
    mobile_num = fields.Char(u'钉钉手机号', required=True)
    email = fields.Char(u'邮箱')
    ding_id = fields.Char(u'钉钉用户唯一标识')
    ding_code = fields.Char(u'工号')
    department_id = fields.Many2one('ding.department', u'部门id')
    department_name = fields.Char(related='department_id.name', string=u'部门id')
    work_place = fields.Char(u'办公地点')
    tel = fields.Char(u'电话')
    position = fields.Char(u'职位')
    openid = fields.Char(u'openId')
    ishide = fields.Boolean(u'isHide')
    active = fields.Boolean(u'active')
    unionid = fields.Char(u'unionid')
    jobnumber = fields.Char(u'jobnumber')
    dingding_id = fields.Char(u'dingding_id')
    open_id = fields.Char(u'open_id')

    def create_ding_user(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for user in self:
            user_vals = dict(name=user.name, department=[user.department_id.department_id] or [1],
                             mobile=user.mobile_num, tel=user.tel, email=user.email,
                             workPlace=user.work_place)
            user_id = ding_obj.create_user(user_vals)
            user.ding_id = user_id
            user.ding_user_id.oauth_access_token = user_id
        return True

    def delete_user(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for user in self:
            ding_obj.delete_user(user.ding_id)
        return True

    @api.multi
    def unlink(self):
        return_vals = super(ding_user, self).unlink()
        if not self.env.context.get('from_dingding'):
            self.delete_user()
        return return_vals

    @api.model
    def create(self, vals):
        return_vals = super(ding_user, self).create(vals)
        if not self.env.context.get('from_dingding'):
            return_vals.create_ding_user()
        return return_vals

    @api.multi
    def write(self, vals):
        return_vals = super(ding_user, self).write(vals)
        if not self.env.context.get('from_dingding'):
            self.update_user(vals)
        return return_vals

    def update_user(self, vals):
        """更新用户信息"""
        change_keys = {'name': 'name', 'department_id': 'department_id',
                       'mobile_num': 'mobile', 'tel': 'tel',
                       'work_place': 'workPlace', 'email': 'email'}
        vals = {change_keys.get(key): vals.get(key) for key in change_keys.keys()
                if key in vals}
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict)
        for user in self:
            vals.update({'userid': user.ding_id, 'name': user.name})
            ding_obj.update_user(vals)
        return True

    def send_message(self, message, user_id, agent_id):
        """发送消息必须指定agent_id"""
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message(agent_id)
        ding_obj = Dingtalk(corpid=corpid, corpsecret=corpsecret, token=token_dict, agent_id=agent_id)
        dinguser_row = self.search([('ding_user_id', '=', user_id)])
        ding_obj.send_text_message(message, dinguser_row.ding_id, '')
        return True

    def send_message_test(self):
        """发送测试信息"""
        for ding_user in self:
            for agent in self.env['ding.agent'].search([]):     # 传入不同的agent_id就会有不同的应用向你发送消息
                self.send_message(u'你好呀！%s' % str(random.random()), ding_user.ding_user_id.id, agent.agent_id)


class ResPartner(models.Model):
    _inherit = 'res.partner'
    department_id = fields.Many2one('ding.department', string='钉钉部門')

    @api.multi
    def write(self, vals):
        change_keys = {'name': 'name', 'department_id': 'department_id',
                       'mobile': 'mobile_num', 'phone': 'tel',
                       'street': 'work_place', 'email': 'email'}
        return_vals = super(ResPartner, self).write(vals)
        for partner in self:
            user_row = self.env['ding.user'].search([('ding_user_id.partner_id', '=', partner.id)])
            ding_fields_keys = list(set(change_keys.keys()).intersection(set(vals.keys())))
            if user_row and ding_fields_keys:
                user_row[0].write({change_keys.get(key): vals.get(key) for key in ding_fields_keys})
        return return_vals


class ResUsers(models.Model):
    _inherit = 'res.users'
    have_dingding_account = fields.Boolean(u'钉钉账户')

    @api.model
    def check_credentials(self, password):
        try:
            return super(ResUsers, self).check_credentials(password)
        except Exception:
            res = self.search([('id', '=', self.env.uid), ('oauth_access_token', '=', password)])
            if not res:
                raise

    @api.onchange('have_dingding_account')
    def onchange_have_dingding_account(self):
        if self.have_dingding_account:
            waring = {}
            if self.partner_id:
                if not (self.partner_id.name and self.partner_id.mobile and self.partner_id.department_id):
                    self.have_dingding_account = False
                    waring = {'title': u'错误', 'message': u"请先设置业务伙伴的手机号 钉钉部门！"}
            else:
                self.have_dingding_account = False
                waring = {'title': u'错误', 'message': u"请先设置用户对应的业务伙伴！"}
            return {'warning': waring}

    def create_dingding_account(self, user_row, have_dingding_account):
        if have_dingding_account != 'default_vals' and have_dingding_account:
            self.env['ding.user'].create({
                'ding_user_id': user_row.id,
                'name': user_row.partner_id.name,
                'department_id': user_row.partner_id.department_id.id,
                'mobile_num': user_row.partner_id.mobile,
                'tel': user_row.partner_id.phone,
                'workPlace': user_row.partner_id.street,
                'email': user_row.partner_id.email,
            })
        else:
            ding_user = self.env['ding.user'].search([('ding_user_id', '=', user_row.id)])
            ding_user and ding_user.unlink()
        return True

    @api.multi
    def create(self, vals):
        user_row = super(ResUsers, self).create(vals)
        self.create_dingding_account(user_row, vals.get('have_dingding_account', 'default_vals'))
        return user_row

    @api.multi
    def write(self, vals):
        user_rows = super(ResUsers, self).write(vals)
        for user_row in self:
            self.create_dingding_account(user_row,
                                         vals.get('have_dingding_account',
                                                  'default_vals'))
        return user_rows


class ExamineApprove(models.Model):
    _name = 'examine.approve'

    agent_id = fields.Many2one('ding.agent', u'企业微应用标识')
    process_code = fields.Char(u'审批流的唯一码')
    approvers = fields.Many2many('ding.user', 'user_prove_ref', 'user_id', 'appeove_id', string='审批人列表')
    cc_list = fields.Many2many('ding.user', 'user_prove_ref', 'user_id', 'appeove_id', string='抄送人列表')
    cc_position = fields.Selection([('START', u'审批开始'), ('FINISH', u'审批结束'), ('START_FINISH', u'开始和结束')],
                                   string='抄送时间')

