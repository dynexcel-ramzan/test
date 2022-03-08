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

#from datetime import datetime, timedelta
#import datetime

class HREmployeeLoan(models.Model):
    _name = "hr.employee.loan.type"
    _description = "Employee Loan Type"

    @api.model
    def _default_product_id(self):
        product_id = self.env['ir.config_parameter'].sudo().get_param('de_emp_books_loan.default_loan_product_id')
        return self.env['product.product'].browse(int(product_id)).exists()
    
    @api.model
    def _default_journal_id(self):
        journal_id = self.env['ir.config_parameter'].sudo().get_param('de_emp_books_loan.default_loan_journal_id')
        return self.env['account.journal'].browse(int(journal_id)).exists()
    
    
    active = fields.Boolean(default=True)
    name = fields.Char(required=True)
    code = fields.Char(required=True, help="Code is added automatically in the display name of every subscription.")
    description = fields.Text(translate=True, string="Terms and Conditions")
    
    
    product_id = fields.Many2one('product.product', string="Product", required=True, domain="[('type', '=', 'service')]", company_dependent=True, check_company=True, default=_default_product_id)
        
    journal_id = fields.Many2one('account.journal', string="Accounting Journal", required=True, domain="[('type', '=', 'purchase')]", company_dependent=True, check_company=True,default=_default_journal_id)
    company_id = fields.Many2one('res.company', string="Company", default=lambda s: s.env.company, required=True)
    
    
class HREmployeeLoanRule(models.Model):
    _name = "hr.employee.loan.rule"
    _description = "Employee Loan Rule"
    
    name = fields.Char(required=True)
    active = fields.Boolean(default=True)
    rule_basis = fields.Selection([
        ('max', 'Maximum Amount Limit'),
        ('validate', 'Validated'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('close', 'Closed'),
        ('cancel', 'Refused')
    ], string='Status', copy=False, index=True,  compute='_compute_state', store=True, default='draft', help="Status of the Avances.")
            
class HREmployeeLoan(models.Model):
    _name = "hr.employee.loan"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Employee Loan"
    _order = "date desc, id desc"
    _check_company_auto = True
    
    @api.model
    def _default_employee_id(self):
        return self.env.user.employee_id
    
    @api.model
    def _default_journal_id(self):
        """ The journal is determining the company of the accounting entries generated from expense. We need to force journal company and expense sheet company to be the same. """
        default_company_id = self.default_get(['company_id'])['company_id']
        journal = self.env['account.journal'].search([('type', '=', 'purchase'), ('company_id', '=', default_company_id)], limit=1)
        return journal.id
    
    @api.model
    def _default_product_uom_id(self):
        return self.env['uom.uom'].search([], limit=1, order='id')
    
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
    
    name = fields.Char('Description', required=True, copy=False, 
        states={'draft': [('readonly', False)], 'submit': [('readonly', False)], 'cancel': [('readonly', False)]})
    
    ref = fields.Char(string='Reference', required=True, copy=False, readonly=True, index=True, default=lambda self: _('New'))

        
    date = fields.Date(readonly=True, states={'draft': [('readonly', False)],}, required=True, default=fields.Date.context_today, string="Request Date")

    accounting_date = fields.Date(readonly=True, states={'draft': [('readonly', False)], }, default=fields.Date.context_today, string="Accounting Date")
    
    employee_id = fields.Many2one('hr.employee', compute='_compute_employee_id', string="Employee", store=True, required=True, readonly=True, tracking=True, states={'draft': [('readonly', False)]}, default=_default_employee_id, domain=lambda self: self._get_employee_id_domain(), check_company=True)
    

    user_id = fields.Many2one('res.users', 'Manager', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, states={'draft': [('readonly', False)]}, tracking=True, domain=lambda self: [('groups_id', 'in', self.env.ref('de_emp_books_loan.group_hr_loan_team_approver').id)])

    manager_id = fields.Many2one('hr.employee')
    department_id = fields.Many2one('hr.department', compute='_compute_from_employee_id', store=True, readonly=True, copy=False, string='Department' )
    job_id = fields.Many2one('hr.job', related='employee_id.job_id', store=True, readonly=True)
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company)
    currency_id = fields.Many2one('res.currency', string='Currency', readonly=True, states={'draft': [('readonly', False)]}, default=lambda self: self.env.company.currency_id)
    
    loan_type_id = fields.Many2one('hr.employee.loan.type', string='Loan Type', readonly=True, copy=False, states={'draft': [('readonly', False)]})
    product_id = fields.Many2one('product.product', string='Product', compute='_compute_from_loan_type', store=True, required=True, states={'draft': [('readonly', False)]},)
    product_uom_id = fields.Many2one('uom.uom', string='Unit of Measure', required=True, compute='_compute_from_product_id_company_id',
        store=True, states={'draft': [('readonly', False)]},
        default=_default_product_uom_id, domain="[('category_id', '=', product_uom_category_id)]")
    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id', readonly=True, string="UoM Category")

    state = fields.Selection([
        ('draft', 'To Submit'),
        ('validate', 'Validated'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('close', 'Closed'),
        ('cancel', 'Refused')
    ], string='Status', copy=False, index=True,  compute='_compute_state', store=True, default='draft', help="Status of the Loan.")
    
    amount = fields.Monetary("Amount", currency_field='currency_id', tracking=True, required=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    amount_residual = fields.Monetary("Residual Amount", currency_field='currency_id', tracking=True, required=True, readonly=True, copy=False, compute='_compute_all_amount')

    description = fields.Text('Notes...', readonly=True, states={'draft': [('readonly', False)], 'submit': [('readonly', False)], 'cancel': [('readonly', False)]})
    
    interest_rate = fields.Float(string='Interest Rate', required=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    date_start = fields.Date(string='Start Date', required=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    date_end = fields.Date(string='End Date', store=True, compute='_compute_date_end', required=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    installments = fields.Integer(string='Installments', default=1, required=True, readonly=True, copy=False, states={'draft': [('readonly', False)]})
    
    address_id = fields.Many2one('res.partner', compute='_compute_from_employee_id', store=True, copy=True, string="Employee Home Address", check_company=True, readonly=False, states={'done': [('readonly', True)], 'close': [('readonly', True)], 'cancel': [('readonly', True)]})
        
    journal_id = fields.Many2one('account.journal', string='Journal', domain="[('type','=','purchase')]", default=_default_journal_id, readonly=False, states={'done': [('readonly', True)], 'close': [('readonly', True)], 'cancel': [('readonly', True)]})
    account_move_id = fields.Many2one('account.move', string='Journal Entry', ondelete='restrict', copy=False, readonly=True)
    payment_state = fields.Selection('Payment State', related='account_move_id.payment_state')
    can_reset = fields.Boolean('Can Reset', compute='_compute_can_reset')
    
    loan_line = fields.One2many('hr.employee.loan.line', 'employee_loan_id', string='Loan Schedule', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    
    loan_deferred_ids = fields.One2many('hr.employee.loan.deferred', 'employee_loan_id', string='Loan Schedule', copy=False, readonly=True, states={'draft': [('readonly', False)]})
    
    loan_deferred_ids = fields.One2many('hr.employee.loan.deferred', 'employee_loan_id', string='Loan Requests')
    deferred_request_count = fields.Integer(string='Deferred Requests Orders', compute='_compute_loan_deferred_ids')


    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].get('hr.employee.loan') or ' '
        res = super(HREmployeeLoan, self).create(vals)
        return res
    
    @api.depends('company_id')
    def _compute_employee_id(self):
        if not self.env.context.get('default_employee_id'):
            for loan in self:
                loan.employee_id = self.env.user.with_company(loan.company_id).employee_id
                
    @api.depends('employee_id')
    def _compute_from_employee_id(self):
        for loan in self:
            loan.address_id = loan.employee_id.sudo().address_home_id
            loan.department_id = loan.employee_id.department_id
            loan.user_id = loan.employee_id.parent_id.user_id
    
    def _compute_all_amount(self):
        for loan in self:
            loan.amount_residual = sum(loan.loan_line.mapped('amount_residual'))
    
    @api.depends('loan_deferred_ids')
    def _compute_loan_deferred_ids(self):
        for request in self:
            request.deferred_request_count = len(request.loan_deferred_ids)
            
    def _get_responsible_for_approval(self):
        if self.user_id:
            return self.user_id
        elif self.employee_id.parent_id.user_id:
            return self.employee_id.parent_id.user_id
        elif self.employee_id.department_id.manager_id.user_id:
            return self.employee_id.department_id.manager_id.user_id
        return self.env['res.users']
    
    @api.depends('date_start','installments')
    def _compute_date_end(self):
        date_end = False
        for loan in self:
            if loan.date_start:
                date_end = loan.date_start + relativedelta(months=loan.installments)
            #if loan.date_start:
                #date_end = fields.Date.to_string(loan.date_start + timedelta(loan.installments))
            loan.date_end = date_end
    def _compute_can_reset(self):
        is_loan_user = self.user_has_groups('de_emp_books_loan.group_hr_loan_team_approver')
        for loan in self:
            loan.can_reset = is_loan_user if is_loan_user else loan.employee_id.user_id == self.env.user
    
    
    @api.depends('loan_type_id', 'company_id')
    def _compute_from_loan_type(self):
        for loan in self.filtered('loan_type_id'):
            loan.product_id = loan.loan_type_id.product_id
            loan.journal_id = loan.loan_type_id.journal_id
            
    @api.depends('product_id', 'company_id')
    def _compute_from_product_id_company_id(self):
        for loan in self.filtered('product_id'):
            loan.product_uom_id = loan.product_id.uom_id
    
    @api.depends('account_move_id','account_move_id.payment_state')
    def _compute_state(self):
        for request in self:
            status = request.state
            if request.account_move_id:
                if request.payment_state in ['in_payment','paid']:
                    status = 'done'
            else:
                status = request.state
            request.state = status
            
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
        return super(HREmployeeLoan, self)._track_subtype(init_values)

    def _message_auto_subscribe_followers(self, updated_values, subtype_ids):
        res = super(HREmployeeLoan, self)._message_auto_subscribe_followers(updated_values, subtype_ids)
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
    def compute_loan(self):
        date_start = date_end = False
        i = 0
        amount = cumulated_bal = principal = amount_interest = amount_total = 0.0
        for loan in self:
            if loan.loan_line:
                loan.loan_line.unlink()
            date_start = loan.date_start
            amount = loan.amount / loan.installments
            principal = loan.amount
            amount_total = loan.amount + (loan.amount * (loan.interest_rate/100))
            while i < loan.installments:
                cumulated_bal += amount
                date_start = loan.date_start + relativedelta(months=i)
                date_end = date_start + relativedelta(months=1,days=-1)
                date_due = date_start + relativedelta(months=1)
                amount_interest = amount * (loan.interest_rate/100)
                self.env['hr.employee.loan.line'].create({
                    'employee_loan_id': loan.id,
                    'date': date_start,
                    'date_end': date_end,
                    'date_due': date_due,
                    'amount': amount,
                    'amount_principal': principal,
                    'amount_interest': amount_interest,
                    'amount_emi': amount + amount_interest,
                    'amount_total': amount_total,
                    'amount_residual': amount + amount_interest,
                })
                
                #date_start = date_end
                principal -= amount
                amount_total -= (amount + amount_interest)
                i += 1
                
        self.write({'state': 'validate'})
            
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
                raise UserError(_("You can only refuse your department expenses"))

        self.write({'state': 'refused'})
        for loan in self:
            loan.message_post_with_view('de_emp_books_loan.hr_employee_loan_template_refuse_reason', values={'reason': reason, 'is_sheet': True, 'name': loan.name})
        self.activity_update()
    
    def action_refund_loan(self, refund, amount, date, reason):
        amount_refund = amount
        for loan in self.loan_line:
            if amount_refund <= loan.amount_residual:
                allocation = amount_refund
            else:
                allocation = loan.amount_residual
            if allocation > 0:
                self.env['hr.employee.loan.disburse'].create({
                    'name': _('Disbursed %s %s - %s - %s', loan.employee_loan_id.name,formatLang(self.env, loan.amount_residual, currency_obj=loan.currency_id),self.employee_id.name,format_date(self.env, fields.Date.to_string(fields.Date.today()))),
                    'employee_loan_line_id': loan.id,
                    'employee_id': self.employee_id.id,
                    'currency_id': loan.currency_id.id,
                    'amount_due': loan.amount_residual,
                    'amount_disburse': allocation,
                    'date_disburse': date,
                })
            amount_refund -= allocation
        
    def action_create_bill(self):
        if not self.journal_id.id:
            raise UserError(_("Accounting Journal is missing"))
            
        if not self.address_id.id:
            raise UserError(_("Respective partner is missing for employee"))
            
        res = self._create_bill()
        self.update({
            'state' : 'post',
        })
    
    def _create_bill(self):
        invoice = self.env['account.move']
        lines_data = []
        for loan in self:
            lines_data.append([0,0,{
                'name': str(loan.name) + ' ' + str(loan.product_id.name),
                'hr_employee_loan_id': loan.id,
                'price_unit': loan.amount or 0.0,
                'quantity': 1,
                'product_uom_id': loan.product_uom_id.id,
                'product_id': loan.product_id.id,
                'tax_ids': [(6, 0, loan.product_id.supplier_taxes_id.ids)],
            }])
        self.account_move_id = invoice.create({
            'move_type': 'in_invoice',
            'invoice_date': fields.Datetime.now(),
            'partner_id': self.address_id.id,
            'currency_id': self.currency_id.id,
            'journal_id': self.journal_id.id,
            'invoice_origin': self.name,
            'invoice_payment_term_id': self.address_id.property_supplier_payment_term_id.id,
            'narration': self.name,
            'invoice_user_id': self.user_id.id,
            'invoice_line_ids':lines_data,
        })
        self.account_move_id._post()
        return invoice
    

    def action_view_requests(self):
        return self._get_action_view_requests(self.loan_deferred_ids)

    def _get_action_view_requests(self, requests):
        """ This function returns an action that display existing picking orders of given purchase order ids. When only one found, show the picking immediately.
        """
        self.ensure_one()
        result = self.env["ir.actions.actions"]._for_xml_id('de_emp_books_loan.action_hr_employee_loan_deferred')
        # override the context to get rid of the default filtering on operation type
        result['context'] = {'default_employee_id': self.employee_id.id, 'default_employee_loan_id': self.id}
        # choose the view_mode accordingly
        if not requests or len(requests) > 1:
            result['domain'] = [('id', 'in', requests.ids)]
        elif len(requests) == 1:
            res = self.env.ref('de_emp_books_loan.hr_employee_loan_deferred_form_view', False)
            form_view = [(res and res.id or False, 'form')]
            result['views'] = form_view + [(state, view) for state, view in result.get('views', []) if view != 'form']
            result['res_id'] = requests.id
        return result
    

class HREmployeeLoanLine(models.Model):
    _name = "hr.employee.loan.line"
    _description = "Employee Loan Line"
    _order = "date"
    _check_company_auto = True
    
    name = fields.Char(string='Payslip Name', compute='_compute_name', store=True, readonly=True,)
    employee_loan_id = fields.Many2one('hr.employee.loan', string="Employee Loan", readonly=True, copy=False)
    employee_id = fields.Many2one(related='employee_loan_id.employee_id')
    date = fields.Date(string='Start Date')
    date_end = fields.Date(string='End Date')
    date_due = fields.Date(string='Due Date')
    currency_id = fields.Many2one(related='employee_loan_id.currency_id')
    amount = fields.Monetary("Amount", currency_field='currency_id' )
    amount_principal = fields.Monetary("Principal Amount", currency_field='currency_id' )
    amount_interest = fields.Monetary("Interest Amount", currency_field='currency_id' )
    amount_emi = fields.Monetary("Amount EMI", currency_field='currency_id' )
    amount_total = fields.Monetary("Total Amount", currency_field='currency_id' )
    amount_residual = fields.Monetary("Residual Amount", currency_field='currency_id' )
    date_disburse = fields.Date(string='Disburse On', )
    
    state = fields.Selection([
        ('draft', 'To Submit'),
        ('validate', 'Validated'),
        ('submit', 'Submit'),
        ('approved', 'Approved'),
        ('post', 'Posted'),
        ('done', 'Paid'),
        ('partial', 'Partially Disbusrsed'),
        ('disburse', 'Disbusrsed'),
        ('close', 'Closed'),
        ('cancel', 'Refused')
    ], string='Status', copy=False, index=True,  compute='_compute_state', store=True, default='draft', help="Status of the monthly loan line.")
    
    loan_line_disburse_ids = fields.One2many('hr.employee.loan.disburse', 'employee_loan_line_id', string='Loan Schedule', copy=False, readonly=True, states={'draft': [('readonly', False)]})

    @api.depends('employee_loan_id','employee_loan_id.state','loan_line_disburse_ids','loan_line_disburse_ids.amount_residual','loan_line_disburse_ids.payslip_state')
    def _compute_state(self):
        status = 'draft'
        for loan in self:
            state_lst = loan.mapped('loan_line_disburse_ids.payslip_state')
            amount_residual = sum(loan.loan_line_disburse_ids.mapped('amount_residual'))
            if state_lst:
                if state_lst.count('done'):
                    if amount_residual == 0:
                        status = 'disburse'
                    else:
                        status = 'partial'
                    loan.date_disburse = fields.Date.today()
                    loan.amount_residual = sum(loan.loan_line_disburse_ids.mapped('amount_residual'))
            else:
                status = loan.employee_loan_id.state
            
            #amount_disburse = sum(loan.loan_line_disburse_ids.mapped('amount_disburse'))
            #if amount_disburse > 0:
            #    loan.state = 'disburse'
            #else:
                #if loan.employee_loan_id:
            loan.state = status
            
                
    @api.depends('employee_id', 'employee_loan_id')
    def _compute_name(self):
        for loan in self.filtered(lambda p: p.employee_id):
            lang = loan.employee_id.sudo().address_home_id.lang or self.env.user.lang
            context = {'lang': lang}
            loan_name = loan.employee_loan_id.name or _('Loan')
            del context

            loan.name = '%(loan_name)s - %(employee_name)s - %(dates)s' % {
                'loan_name': loan_name,
                'employee_name': loan.employee_id.name,
                'dates': format_date(self.env, loan.date, date_format="MMMM y", lang_code=lang)
            }

            

class HREmployeeLoanDisburse(models.Model):
    _name = "hr.employee.loan.disburse"
    _description = "Employee Loan Disbursement"

    name = fields.Char()
    employee_loan_line_id = fields.Many2one('hr.employee.loan.line', string="Employee Loan Line", readonly=True, copy=False)
    employee_id = fields.Many2one('hr.employee', string='Employee')
    currency_id = fields.Many2one('res.currency', string='Currency')
    amount_due = fields.Monetary("Due Amount", currency_field='currency_id' )
    amount_disburse = fields.Monetary("Amount Disbursed", currency_field='currency_id' )
    amount_residual = fields.Monetary("Residual Amount", currency_field='currency_id', compute='_compute_amount_residual')
    date_disburse = fields.Date(string='Disburse On', )
    payslip_id = fields.Many2one('hr.payslip', string="Payslip", readonly=True, copy=False)
    payslip_state = fields.Selection(related='payslip_id.state')
    
    @api.depends('payslip_id','payslip_id.state','employee_loan_line_id')
    def _compute_state(self):
        for loan in self:
            if loan.payslip_id.state == 'done':
                loan.employee_loan_line_id.state = 'disburse'
                loan.employee_loan_line_id.amount_residual -= loan.amount_disburse
    
    def _compute_amount_residual(self):
        for loan in self:
            loan.amount_residual = loan.amount_due - loan.amount_disburse