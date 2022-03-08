# -*- coding: utf-8 -*-

from datetime import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError, Warning


from odoo.addons import decimal_precision as dp

class AccountMaster(models.Model):
    _name = 'account.summary.master'
    
    name = fields.Char('Name',required=True)
    #accounts_total = fields.Float(string='Total',compute='_compute_accounts_total', readonly=True)
    accounts_total = fields.Float(string='Total', store=True, readonly=True, compute='_compute_accounts_total')
    #accounts_total = fields.Float('Total')
    
    account_summary_line_ids = fields.One2many('account.summary.account', 'account_summary_id', string='Account Summary Lines', copy=True, auto_join=True)
    
    @api.depends('account_summary_line_ids')
    def _compute_accounts_total(self):
        for rs in self:
            for line in rs.account_summary_line_ids:
                rs.accounts_total += line.balance
                
    def action_recompute(self):
        total = 0
        for rs in self.account_summary_line_ids:
            rs._compute_balance()
            #account_move_lines = self.env['account.move.line'].search([('account_id', '=', rs.account_id.id)])
            bal = 0
            #for line in account_move_lines:
                #if line.move_id.state == 'posted':
                    #bal = bal + (line.debit - line.credit)
            #rs.update({'balance': bal })
            #total += bal
            total += rs.balance
        self.accounts_total = total
        

class Account(models.Model):
    _name = 'account.summary.account'
    
    account_summary_id = fields.Many2one('account.summary.master', string='Account Summary', index=True, required=True, ondelete='cascade')
    
    account_id = fields.Many2one('account.account', string='Account', required=True, index=True, ondelete="cascade", domain=[('deprecated', '=', False)], default=lambda self: self._context.get('account_id', False))
    
    balance = fields.Monetary(string='Balance', currency_field='company_currency_id', store=True, readonly=True, compute='_compute_balance',)
    company_currency_id = fields.Many2one('res.currency', string="Company Currency", related='company_id.currency_id', readonly=True, help='Utility field to express amount currency')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env['res.company']._company_default_get('account.summary.account'))
    
    #@api.depends('account_id')
    @api.multi
    @api.depends('account_id','balance')
    def _compute_balance(self):
        
        for rs in self:
            account_move_lines = self.env['account.move.line'].search([('account_id', '=', rs.account_id.id)])
            bal = 0
            for line in account_move_lines:
                if line.move_id.state == 'posted':
                    bal = bal + (line.debit - line.credit)
            rs.update({'balance': bal })
    
    @api.multi
    @api.onchange('account_id')
    def onchange_account_id(self):
        for rs in self:
            account_move_lines = self.env['account.move.line'].search([('account_id', '=', rs.account_id.id)])