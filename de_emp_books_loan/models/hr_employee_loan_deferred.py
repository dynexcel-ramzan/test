# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import re
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import email_split, float_is_zero
from odoo.tools.misc import formatLang, format_date, get_lang


class HREmployeeLoanDeferred(models.Model):
    _name = "hr.employee.loan.deferred"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Loan EMI Deferred Request"
    _order = "date desc, id desc"
    _check_company_auto = True
    
    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id
        
    @api.model
    def _get_employee_id_domain(self):
        res = [('id', '=', 0)] # Nothing accepted by domain, by default
        if self.user_has_groups('de_emp_books_loan.group_hr_loan_user') or self.user_has_groups('account.group_account_user'):
            res = "['|', ('company_id', '=', False), ('company_id', '=', company_id)]"  # Then, domain accepts everything
        elif self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver') and self.env.user.employee_ids:
            user = self.env.user
            employee = self.env.user.employee_id
            res = [
                '|', '|', '|',
                ('department_id.manager_id', '=', employee.id),
                ('parent_id', '=', employee.id),
                ('id', '=', employee.id),
                ('loan_manager_id', '=', user.id),
                '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id),
            ]
        elif self.env.user.employee_id:
            employee = self.env.user.employee_id
            res = [('id', '=', employee.id), '|', ('company_id', '=', False), ('company_id', '=', employee.company_id.id)]
        return res
    
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)],}, required=True, default=fields.Date.context_today, string="Request Date")    
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True, required=True, readonly=True, tracking=True, states={'draft': [('readonly', False)]}, default=_default_employee_id, domain=lambda self: self._get_employee_id_domain(), check_company=True)
    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, states={'draft': [('readonly', False)]}, tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('de_emp_books_loan.group_hr_loan_team_approver').id)])
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, string='Department' )
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company.currency_id)
    
    employee_loan_id = fields.Many2one('hr.employee.loan', string='Loan', readonly=True, copy=False, states={'draft': [('readonly', False)]}, domain="[('employee_id','=',employee_id),('state','=','done')]")
    amount_loan = fields.Monetary("Amount", currency_field='currency_id', store=True, readonly=True, copy=False, compute='_compute_all_loan' )
    amount_residual_loan = fields.Monetary("Residual Amount", currency_field='currency_id', store=True, readonly=True, copy=False, compute='_compute_all_loan' )
    
    deferred_period = fields.Integer(string='Deferred Period', default=1, required=True)
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('submit', 'Submit'),
        ('done', 'Approved'),
        ('cancel', 'Refused')
    ], string='Status', copy=False, index=True,  default='draft', help="Status of request.")
    
    description = fields.Text('Notes...', readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)], 'cancel': [('readonly', False)]})
    

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].get('hr.employee.loan.deferred') or ' '
        res = super(HREmployeeLoanDeferred, self).create(vals)
        return res
    
    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for loan in self:
                loan.employee_id = self.env.user.with_company(loan.company_id).employee_id
                
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for loan in self:
            loan.department_id = loan.employee_id.department_id
            loan.user_id = loan.employee_id.parent_id.user_id
            
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
    
    @api.depends('employee_loan_id')
    def _compute_all_loan(self):
        for loan in self:
            loan.amount_loan = sum(loan.employee_loan_id.loan_line.mapped('amount_total'))
            loan.amount_residual_loan = sum(loan.employee_loan_id.loan_line.mapped('amount_residual'))
    # --------------------------------------------
    # Mail Thread
    # --------------------------------------------

    @api.model
    def message_new(self, msg_dict, custom_values=None):
        email_address = email_split(msg_dict.get('email_from', False))[0]

        employee = self.env['hr.employee'].search([
            '|',
            ('work_email', 'ilike', email_address),
            ('user_id.email', 'ilike', email_address)
        ], limit=1)

        loan_description = msg_dict.get('subject', '')

        if employee.user_id:
            company = employee.user_id.company_id
            currencies = company.currency_id | employee.user_id.company_ids.mapped('currency_id')
        else:
            company = employee.company_id
            currencies = company.currency_id

        if not company:  # ultimate fallback, since company_id is required on expense
            company = self.env.company

        # The expenses alias is the same for all companies, we need to set the proper context
        # To select the product account
        self = self.with_company(company)

        product, price, currency_id, loan_description = self._parse_expense_subject(loan_description, currencies)
        vals = {
            'employee_id': employee.id,
            'name': loan_description,
            'loan_type': price,
            'amount': product.id if product else None,
            'installments': product.uom_id.id,
            'quantity': 1,
            'company_id': company.id,
            'currency_id': currency_id.id
        }

        account = product.product_tmpl_id._get_product_accounts()['expense']
        if account:
            vals['account_id'] = account.id

        expense = super(HrExpense, self).message_new(msg_dict, dict(custom_values or {}, **vals))
        self._send_expense_success_mail(msg_dict, expense)
        return expense
    
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'approve':
            return self.env.ref('de_emp_books_loan.mt_loan_approved')
        elif 'state' in init_values and self.state == 'cancel':
            return self.env.ref('de_emp_books_loan.mt_loan_refused')
        elif 'state' in init_values and self.state == 'done':
            return self.env.ref('de_emp_books_loan.mt_loan_paid')
        return super(HREmployeeLoanDeferred, self)._track_subtype(init_values)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super(HREmployeeLoanDeferred, self)._message_auto_subscribe_followers(updated_values, subtype_ids)
        if updated_values.get('employee_id'):
            employee = self.env['hr.employee'].browse(updated_values['employee_id'])
            if employee.user_id:
                res.append((employee.user_id.partner_id.id, subtype_ids, False))
        return res

    
    def activity_update(self):
        for adv in self.filtered(lambda adv: adv.state == 'submit'):
            self.activity_schedule(
                'de_emp_books_loan.mail_act_loan_approval',
                user_id=adv.sudo()._get_responsible_for_approval().id or self.env.user.id)
        self.filtered(lambda hol: hol.state == 'approve').activity_feedback(['de_emp_books_loan.mail_act_loan_approval'])
        self.filtered(lambda hol: hol.state in ('draft', 'cancel')).activity_unlink(['de_emp_books_loan.mail_act_loan_approval'])
                
    # --------------------------------------------
    # Action Buttons
    # --------------------------------------------
    def action_submit_request(self):
        if self.amount ==0:
            raise UserError(_("The request cannot submit for 0 amount."))
        elif self.amount < 0:
            raise UserError(_("The request cannot submit for negative amount."))
                
        self.write({'state': 'submit'})
        self.activity_update()
    
    def reset_request(self):
        if not self.can_reset:
            raise UserError(_("Only HR Officers or the concerned employee can reset to draft."))
        self.write({'state': 'draft'})
        self.activity_update()
        return True
        
    def approve_request(self):
        if not self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve advances"))
        elif not self.user_has_groups('de_emp_books_loan.group_hr_loan_manager'):
            current_managers = self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot approve your own advance request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_emp_books_loan.group_hr_loan_user') and self.employee_id.parent_id.user_id != self.env.user:
                raise UserError(_("You can only approve your department loans"))
        
        notification = {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('There are no advance requests to approve.'),
                'type': 'warning',
                'sticky': False,  #True/False will display for few seconds if false
            },
        }
        state = ''
        filtered_loan = self.filtered(lambda s: s.state in ['submit', 'draft'])
        if not filtered_loan:
            return notification
        for loan in filtered_loan:
            loan.write({
                'state': 'approved', 
                'user_id': loan.user_id.id or self.env.user.id
            })
        notification['params'].update({
            'title': _('The advance requests were successfully approved.'),
            'type': 'success',
            'next': {'type': 'ir.actions.act_window_close'},
        })
            
        self.activity_update()
        return notification
    
    def action_refuse_loan(self, reason):
        if not self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver'):
            raise UserError(_("Only Managers and HR Officers can approve loan"))
        elif not self.user_has_groups('de_emp_books_loan.group_hr_loan_manager'):
            current_managers = self.employee_id.loan_manager_id | self.employee_id.parent_id.user_id | self.employee_id.department_id.manager_id.user_id

            if self.employee_id.user_id == self.env.user:
                raise UserError(_("You cannot refuse your own request"))

            if not self.env.user in current_managers and not self.user_has_groups('de_emp_books_loan.group_hr_loan_user') and self.employee_id.loan_manager_id != self.env.user:
                raise UserError(_("You can only refuse your department loan requests"))

        self.write({'state': 'refused'})
        for loan in self:
            loan.message_post_with_view('de_emp_books_loan.hr_employee_loan_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': loan.name})
        self.activity_update()
        
    def action_create_bill(self):
        if not self.journal_id.id:
            raise UserError(_("Accounting Journal is missing"))
                        
        res = self._create_bill()
        self.update({
            'state' : 'post',
        })


