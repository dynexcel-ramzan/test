# from odoo import models, fields, api
# from odoo.exceptions import UserError, ValidationError
#
# class StockPicking(models.Model):
#     _inherit = 'mrp.production'
#
#     # @api.multi
#     def open_produce_product(self):
#         so_no = self.env['stock.picking'].search([('sale_tag','=', self.sale_id)])
#         if not so_no and self.product_id.categ_id.name == 'Stitched':
#             raise UserError("You cannot produce stitch quantity as greige receipt missing sale order reference.")
#
#         self.ensure_one()
#         if self.bom_id.type == 'phantom':
#             raise UserError(_('You cannot produce a MO with a bom kit product.'))
#         action = self.env.ref('mrp.act_mrp_product_produce').read()[0]
#         return action
#
