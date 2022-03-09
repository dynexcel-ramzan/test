from odoo import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    submit_to_approve = fields.Boolean(string='Submit To Approve')
    is_approve = fields.Boolean(string='Is Approve')
    is_lock = fields.Boolean(string='Is Lock')
    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('submit', 'Submit To Approve'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, tracking=3, default='draft')

    def action_approval(self):
        if self.state == 'draft':
            self.write({'submit_to_approve': False})

        self.action_confirm()
        self.write({'state': 'submit', 'submit_to_approve': True})

    def action_approve(self):
        if self.submit_to_approve == True:
            self.write({'state': 'sale', 'is_approve': True, 'is_lock': True})

    def action_unlock(self):
        self.write({'is_lock': False})

    def action_lock(self):
        if self.state == 'draft':
            self.write({'is_lock': False})

        self.write({'is_lock': True})

