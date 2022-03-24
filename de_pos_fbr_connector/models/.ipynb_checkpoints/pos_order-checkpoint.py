# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
import requests
import json
import datetime
import traceback
from datetime import datetime

class POSOrder(models.Model):
    _inherit = 'pos.order'

    fbr_respone = fields.Text("FBR Response")
    fbr_json = fields.Char("FBR JSON")
    post_data_fbr = fields.Boolean("Post Data Successful ?")
    pos_reference = fields.Char(string='Receipt Ref', readonly=True, copy=True)
    invoice_number = fields.Char("Invoice Number")
    logged_user = fields.Many2one('res.users', string='Current Login', compute='_get_current_login_user')

    def _get_current_login_user(self):
        user_obj = self.env['res.users'].search([])
        for user_login in user_obj:
            current_login = self.env.user
            if user_login == current_login:
                self.logged_user = current_login

#     def post_fbr_order(self, pos_order_data):
#         fbr_url = ''
#         invoice_number = ''
#         #to see fbr data in model fields
#         current_order_no = ''
#         current_invoice_no = ''
#         # Content type must be included in the header
#         header = {"Content-Type": "application/json"}
#         
#         if pos_order_data:
#             try:
#                 for pos_order in pos_order_data:
#                     print('================pos_order',pos_order)
#                     order_no = pos_order.get('name').partition(' ')[2]
#                     fbr_record_exist = self.env['fbr.data'].search([('fbr_order_no','=',order_no)])
#                     print('------------------fbr_record_exist',fbr_record_exist)
# 
#                     if not fbr_record_exist:
#                                    
#                         if pos_order.get('state') != 'done' and pos_order.get('post_data_fbr') != True:
#                             
#                             sale_amount = round(pos_order.get('amount_total') - pos_order.get('amount_tax'), 4)
#                             invoice_type =  ''
#                             if sale_amount > 0:
#                                 invoice_type = 1
#                             if sale_amount < 0:
#                                 invoice_type = 3
#     
#                             print('-------------------------inv type fbi',invoice_type)
#     
#                             order_dic = {
#                                 "InvoiceNumber": "",
#                                 "USIN": pos_order.get('name').partition(' ')[2],
#                                 "DateTime": pos_order.get('creation_date'),
#                                 "TotalBillAmount": abs(round(pos_order.get('amount_total'), 4)),
#                                 "TotalSaleValue": abs(round(pos_order.get('amount_total') - pos_order.get('amount_tax'), 4)),
#                                 "TotalTaxCharged": abs(round(pos_order.get('amount_tax'), 4)),
#                                 "PaymentMode": 1,
#                                 "InvoiceType": invoice_type,
#                             }
#                             session = self.env['pos.session'].sudo().search([('id', '=', pos_order.get('pos_session_id'))],limit=1)
#                             if session:
#                                 header.update({'Authorization': session.config_id.fbr_authorization})
#                                 order_dic.update({'POSID': session.config_id.pos_id})
#     
#                             if session.config_id.fbr_url:
#                                 fbr_url = session.config_id.fbr_url
#     
#                             partner = False
#                             if pos_order.get('partner_id'):
#                                 partner = self.env['res.partner'].sudo().search([('id', '=', pos_order.get('partner_id'))],limit=1)
#                                 order_dic.update({
#                                     "BuyerName": partner.name,
#                                     "BuyerPhoneNumber": partner.mobile,
#                                 })
#     
#                             if pos_order.get('lines'):
#     
#                                 items_list = []
#                                 total_qty = 0.0
#     
#                                 for line in pos_order.get('lines'):
#                                     product_dic = line[2]
#                                     total_qty += product_dic.get('qty')
#                                     if 'product_id' in product_dic:
#                                         product = self.env['product.product'].sudo().search(
#                                             [('id', '=', product_dic.get('product_id'))])
#                                         if product:
# #                                             tax_list = product_dic.get('tax_ids')[0][2]
# #                                             tax_ids = self.env['account.tax'].sudo().search([('id', 'in', tax_list)])
#                                             pricelist_id = pos_order.get('pricelist_id')
#                                             pricelist = self.env['product.pricelist'].sudo().browse(pricelist_id)
#                                             price = float(product_dic.get('price_unit')) * (
#                                                         1 - (product_dic.get('discount') or 0.0) / 100.0)
#     
#                                             line_dic = {
#                                                 "ItemCode": product.barcode,
#                                                 "ItemName": product.name,
#                                                 "Quantity": product_dic.get('qty'),
#                                                 "PCTCode": product.pct_code,
#                                                 "TaxRate": 0.0,
#                                                 "SaleValue": abs(round(product_dic.get('price_subtotal'), 4)),
#                                                 "TotalAmount": abs(round(product_dic.get('price_subtotal_incl'), 4)),
#                                                 "TaxCharged": abs(round(product_dic.get('price_subtotal_incl') - product_dic.get('price_subtotal'), 4)),
#                                                 "InvoiceType": invoice_type,
#                                                 "RefUSIN": ""
#                                             }
#                                             items_list.append(line_dic)
#                                 order_dic.update({'Items': items_list, 'TotalQuantity': abs(total_qty)})
#                         payment_response = requests.post(fbr_url, data=json.dumps(order_dic), headers=header, verify=False, timeout=20)
#     
#                         r_json = payment_response.json()
#                         print('---------r json=======',r_json)
#                         invoice_number = r_json.get('InvoiceNumber')
#                         print('==========')
#                         if invoice_number == 'Not Available':
#                             invoice_number = ''
#                         else:
#                             invoice_number = invoice_number
#                         
#                         current_order_no = pos_order.get('name').partition(' ')[2]
#                         current_invoice_no = invoice_number
#                         print('------------current_order_no--',current_order_no)
#                         print('-------current_invoice_no--------',current_invoice_no)
#                         if current_order_no and current_invoice_no:
#                             rec = self.env['fbr.data'].create({
#                                         'fbr_order_no': current_order_no,
#                                         'fbr_invoice_no': current_invoice_no,
#                                     })
#                             print('-------rec-',rec)
#                 
#             except Exception as e:
#                 values = dict(
#                     exception=e,
#                     traceback=traceback.format_exc(),
#                 )
# 
#         return [invoice_number]


    def create(self, vals):
        rec = super(POSOrder, self).create(vals)
        print('pos order create',rec.pos_reference.partition(' ')[2])
        fbr_record_exist = self.env['pos.order.fbr.log'].search([('fbr_order_no','=',rec.pos_reference.partition(' ')[2])])
        
        if fbr_record_exist:
            fbr_record_exist.update({'actual_order_id': rec.id})
        
        return rec

    def post_fbr_order(self, pos_order_data):
        invoice_number = ''
        current_order_no = ''
        
        if pos_order_data:
            try:
                for pos_order in pos_order_data:
                    print('-----------self.id',self.id)
                    current_order_no = pos_order.get('name').partition(' ')[2]
                    fbr_record_exist = self.env['pos.order.fbr.log'].search([('fbr_order_no','=',current_order_no)])
     
                    if not fbr_record_exist:
                        rec = self.env['pos.order.fbr.log'].create({
                                'fbr_order_no': current_order_no,
                                'fbr_json_data': pos_order,
                                })
                        invoice_number = rec.fbr_invoice_no
                      
            except Exception as e:
                values = dict(
                    exception=e,
                    traceback=traceback.format_exc(),
                )

        return [invoice_number]


    def post_data_to_fbr_cron(self):
        for failed_orders in self.search([('post_data_fbr', '=', False)]):
            print('------',failed_orders)
            failed_orders.post_data_to_fbr_action()

    def post_data_to_fbr_action(self):
        orders = []
        for order in self.filtered(lambda x: not x.post_data_fbr):
            orders.append(order.id)
            self.post_data_to_fbr(orders)
    
    def refund(self):
        res = super(POSOrder, self).refund()
        order = self.browse(res.get('res_id'))
        order.write({'fbr_respone': '', 'fbr_json':'', 'post_data_fbr': False, 'invoice_number': '', 'pos_reference': order.pos_reference+'-R'})
        return res
    
    def post_data_to_fbr(self, orders):
        fbr_url = ''
        current_invoice_no = ''
        # Content type must be included in the header
        header = {"Content-Type": "application/json"}
        for order in orders:
            order = self.browse(order)
            print('----------------------order name',order.name)
            try:
                if order and order.session_id and order.session_id.config_id and order.session_id.config_id.fbr_authorization:
                    fbr_url = order.session_id.config_id.fbr_url
                    
                    if order.post_data_fbr != True:
                        header.update({'Authorization': order.session_id.config_id.fbr_authorization})
                        bill_amount = order.amount_total
                        tax_amount = order.amount_tax
                        sale_amount = order.amount_total - order.amount_tax
                        #####################
                        invoice_type =  ''
                        if sale_amount > 0:
                            invoice_type = 1
                        if sale_amount < 0:
                            invoice_type = 3 
                        print('----------sale amt',sale_amount)
                        print('------------invoice typ',invoice_type)
                        order_dic = {
                            "InvoiceNumber": "",
                            "POSID": order.session_id.config_id.pos_id,
                            "USIN": order.pos_reference.partition(' ')[2],
                            "DateTime": datetime.strptime(str(order.date_order),"%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d %H:%M:%S"),                        
                            "TotalBillAmount": abs(round(bill_amount, 4)),
                            "TotalSaleValue": abs(round(sale_amount, 4)),
                            "TotalTaxCharged": abs(round(tax_amount, 4)),
                            "PaymentMode": 1,
                            "InvoiceType": invoice_type,
                        }
                        if order.partner_id:
                            order_dic.update({
                                "BuyerName": order.partner_id.name,
                                "BuyerPhoneNumber": order.partner_id.mobile,
                            })
                        if order.lines:
                            items_list = []
                            total_qty = 0.0
                            for line in order.lines:
                                total_qty += line.qty
                                line_dic = {
                                    "ItemCode": line.product_id.barcode,
                                    "ItemName": line.product_id.name,
                                    "Quantity": abs(line.qty),
                                    "PCTCode": line.product_id.pct_code,
                                    "TaxRate": 0.0,
                                    "SaleValue": abs(round(line.price_subtotal, 4)),
                                    "TotalAmount": abs(round(line.price_subtotal_incl, 4)),
                                    "TaxCharged": abs(round(line.price_subtotal_incl - line.price_subtotal, 4)),
                                    "InvoiceType": invoice_type,
                                    "RefUSIN": ""
                                }
                                items_list.append(line_dic)
                            order_dic.update({
                                "Items": items_list,
                                "TotalQuantity": abs(total_qty)
                            })
                        order.write({'fbr_json': json.dumps(order_dic)})
                        payment_response = requests.post(fbr_url, data=json.dumps(order_dic), headers=header, verify=False,
                                                         timeout=20)
                        r_json = payment_response.json()
                        invoice_number = r_json.get('InvoiceNumber')
                        print('post data fbr--------',r_json)
                        
                        if invoice_number != 'Not Available':
                            order.write({'fbr_respone': r_json, 'post_data_fbr': True, 'invoice_number': invoice_number})
                            
                            current_invoice_no = invoice_number
                            print('----current_invoice_no----',current_invoice_no)
                            order_no = order.pos_reference.partition(' ')[2]
                            fbr_record_exist = self.env['pos.order.fbr.log'].search([('fbr_order_no','=',order_no)])
                            print('------------------fbr_record_exist',fbr_record_exist)
                            if fbr_record_exist:
                                fbr_record_exist.update({'fbr_invoice_no': current_invoice_no})
                                
            except Exception as e:
                values = dict(
                    exception=e,
                    traceback=traceback.format_exc(),
                )
                order.write({'fbr_respone': values})


    @api.model
    def _order_fields(self, ui_order):
        res = super(POSOrder, self)._order_fields(ui_order)
        res['invoice_number'] = ui_order.get('invoice_number', False)
        res['post_data_fbr'] = ui_order.get('post_data_fbr', False)
        return res
