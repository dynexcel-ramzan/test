from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'hr.payslip'

    basic_wage_amount = fields.Float( string='Basic Wage', store=True, compute='_compute_basic_wage')
    net_amount = fields.Float(string='Net Wage', store=True, compute='_compute_net_wage')

    def _compute_basic_wage(self):
        for rec in self:
            for line in rec.line_ids:
                if line.code == 'Basic':
                    rec.basic_wage_amount = line.amount

    def _compute_net_wage(self):
        for rec in self:
            for line in rec.line_ids:
                if line.code == 'Net':
                    rec.net_amount = line.amount

