# from odoo import models, fields, api
#
#
# class AccountMove(models.Model):
#     _inherit = 'account.move'
#
#     c_agent_id = fields.Many2one(related='partner_id.agent_id', string='Agent', store=True, readonly=True)
#     amount_commission = fields.Float(string='CAmount', store=True, readonly=True, compute='_compute_commission')
#
#     def _compute_commission(self):
#         for rec in self:
#             rec.amount_commission = rec.commission
