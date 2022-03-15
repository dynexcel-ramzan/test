# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015 Dynexcel (<http://dynexcel.com/>).
#
##############################################################################

import time

from odoo import fields,api,models
from dateutil import parser
from dateutil.relativedelta import relativedelta
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ProductStock(models.TransientModel):
    _name = 'product.stock.valuation.wizard'
    _description = 'Stock Valuation Wizard'

    dated = fields.Datetime(required=True, default=fields.Datetime.now)
    
    product_id = fields.Many2one('product.product', string='Product', required=False, help='Select Product for movement')
    categ_ids = fields.Many2many('product.category', string='Categories')
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', required=False,help='Select Pricelist')
    
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    location_id = fields.Many2one('stock.location', string='Location',required=True)
    

    @api.multi
    def print_report(self, data):
        data = {'product_id': self.product_id.id,'categ_ids':[p.id for p in self.categ_ids], 'pricelist_id':self.pricelist_id.id, 'dated': self.dated, 'warehouse_id':self.warehouse_id.id, 'location_id':self.location_id.id}
        return self.env.ref('de_stock_valuation_report.stock_valuation_pdf').report_action(self, data=data)
    
    @api.multi
    def action_print_xlsx_report(self,data):
        data = {'product_id': self.product_id.id,'categ_ids':[p.id for p in self.categ_ids], 'pricelist_id':self.pricelist_id.id, 'dated': self.dated, 'warehouse_id':self.warehouse_id.id, 'location_id':self.location_id.id}
        return self.env.ref('de_stock_valuation_report.stock_valuation_xlsx').report_action(self, data=data)
