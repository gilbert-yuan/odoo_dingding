# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import os, sys
import jinja2
if hasattr(sys, 'frozen'):
    # When running on compiled windows binary, we don't have access to package loader.
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'html'))
    loader = jinja2.FileSystemLoader(path)
else:
    loader = jinja2.PackageLoader('odoo.addons.dingding', "html")
env = jinja2.Environment('<%', '%>', '${', '}', '%', loader=loader, autoescape=True)

class PageShow(http.Controller):
    def __init__(self):
        self.login_user = False
        self.login_session = False

    @http.route('/dingding/firstpage', auth='public', csrf=False)
    def wechat_pulling(self, **args):
        template = env.get_template("sale_order.html")
        return template.render({
            'user_id': '',
            'title': ''
        })

