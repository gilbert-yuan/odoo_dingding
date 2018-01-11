# -*- coding: utf-8 -*-
from odoo import models, fields, api
from ding_api import Dingtalk
from odoo.exceptions import UserError
import random
import time

class ding_ding(models.Model):
    _name = 'ding.ding'
    _description = u'钉钉账户主要信息设置'
    name = fields.Char(u'钉钉对象')
    corpid = fields.Char(u'钉钉corpid', required=True)
    corpsecret = fields.Char(u'钉钉corpsecret', required=True)
    agent_ids = fields.One2many('ding.agent', 'ding_id', string='应用ID', required=True)
    token = fields.Char(u'token', readonly=True)
    expired_in = fields.Char(u'过期时间', readonly=True)

    def get_ding_department(self):
        department_obj = self.env['ding.department']
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
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
                                  (%s,'%s', %s)"""%(department.get('id'),
                                                    department.get('name'),
                                                    department_row_parent
                                                    and department_row_parent.id or 'NULL'))
        return True

    def get_ding_user(self, user):
        cr = self.env.cr
        if user.get('mobile'):
            department_row = self.env['ding.department'].search([("department_id", '=',
                                (user.get('department')[len(user.get('department'))-1]))])
            cr.execute("""INSERT INTO ding_user 
                          (department_id, name, work_place, ding_id ,mobile_num, email, position) VALUES 
                          (%s,'%s', '%s', '%s','%s', '%s', '%s')""" %
                       (department_row.id or 'NULL',  user.get('name'),
                        user.get('workPlace') or "NULL", user.get('userid'), user.get('mobile'),
                        user.get('email') or 'NULL', user.get('position') or "NULL",
                        ))
        return True

    def get_dingdinguser(self):
        department_rows = self.env['ding.department'].search([])
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        for department_row in department_rows:
            user_dicts = ding_obj.get_depatment_user_list(department_row.department_id)
            for user in user_dicts:
                if not self.env['ding.user'].search([('ding_id', '=', user.get('userid'))]):
                    self.create_ding_user(user)

    def get_ding_common_message(self):
        dingding_row = self.env.ref('dingding.ding_ding_xml')
        if not dingding_row.token or float(dingding_row.expired_in) <= time.time():
            ding_obj = Dingtalk(dingding_row.corpid, dingding_row.corpsecret,
                                dingding_row.agent_ids[0].agent_id, {})
            token_dcit = ding_obj.get_token()
            dingding_row.token = token_dcit.get('access_token')
            dingding_row.expired_in = token_dcit.get('expired_in')
        return (dingding_row.corpid,
                dingding_row.corpsecret,
                dingding_row.agent_ids[0].agent_id,
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
        return_vals.create_department()
        return return_vals

    def create_department(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        for deparment in self:
            ding_id = ding_obj.create_dept(deparment.name,
                                           deparment.ding_id, deparment.parent_order)
            deparment.department_id = ding_id
        return True

    @api.multi
    def write(self, vals):
        return_vals = super(ding_department, self).write(vals)
        self.update_department(vals)
        return return_vals

    def update_department(self, vals):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        for deparment in self:
            vals.update({'id': deparment.name})
            ding_obj.update_dept(vals)
        return True

    @api.multi
    def unlink(self):
        return_vals = super(ding_department, self).unlink()
        self.delete_department()
        return return_vals

    def delete_department(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
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

    def create_ding_user(self):
         corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
         ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
         for user in self:
            user_vals = dict(name=user.name, department=[user.department_id.department_id] or [1],
                             mobile=user.mobile_num, tel=user.tel, email=user.email,
                             workPlace=user.work_place)
            user_id = ding_obj.create_user(user_vals)
            user.ding_id = user_id
         return True

    def delete_user(self):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        for user in self:
            ding_obj.delete_user(user.ding_id)
        return True

    @api.multi
    def unlink(self):
        return_vals = super(ding_user, self).unlink()
        self.delete_user()
        return return_vals

    @api.model
    def create(self, vals):
        return_vals = super(ding_user, self).create(vals)
        return_vals.create_ding_user()
        return return_vals

    @api.multi
    def write(self, vals):
        return_vals = super(ding_user, self).write(vals)
        self.update_user(vals)
        return return_vals
    
    def update_user(self, vals):
        change_keys = {'name': 'name', 'department_id': 'department_id',
                       'mobile_num': 'mobile', 'tel': 'tel',
                       'work_place': 'workPlace', 'email': 'email'}
        vals = {change_keys.get(key): vals.get(key) for key in change_keys.keys()
                if key in vals}
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        for user in self:
            vals.update({'userid': user.ding_id, 'name': user.name})
            ding_obj.update_user(vals)
        return True

    def send_message(self, message, user_id):
        corpid, corpsecret, agent_id, token_dict = self.env['ding.ding'].get_ding_common_message()
        ding_obj = Dingtalk(corpid, corpsecret, agent_id, token_dict)
        dinguser_row = self.search([('ding_user_id', '=', user_id)])
        ding_obj.send_text_message(message, dinguser_row.ding_id, '')
        return True

    def send_message_test(self):
        for ding_user in self:
            self.send_message(u'你好呀！%s'%str(random.random()), ding_user.ding_user_id.id)

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

    @api.onchange('have_dingding_account')
    def onchange_have_dingding_account(self):
        if self.have_dingding_account:
            waring = {}
            if self.partner_id:
                if not(self.partner_id.name and self.partner_id.mobile and self.partner_id.department_id):
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
                'department_id':  user_row.partner_id.department_id.id,
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

