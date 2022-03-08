# -*- coding: utf-8 -*-
from odoo import http

# class DeAccountBalance(http.Controller):
#     @http.route('/de_account_balance/de_account_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_account_balance/de_account_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_account_balance.listing', {
#             'root': '/de_account_balance/de_account_balance',
#             'objects': http.request.env['de_account_balance.de_account_balance'].search([]),
#         })

#     @http.route('/de_account_balance/de_account_balance/objects/<model("de_account_balance.de_account_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_account_balance.object', {
#             'object': obj
#         })