from odoo import models, fields, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    product_category = fields.Char(related='product_id.categ_id.complete_name', string='Product Category', store=True, readonly=True)
