# -*- coding:utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import base64
import logging

from collections import defaultdict
from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils, convert_file, html2plaintext
from odoo.tools.float_utils import float_compare
from odoo.tools.misc import formatLang, format_date, get_lang
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def action_payslip_done(self):
        for payslip in self:

            loan_line_ids = self.env['hr.employee.loan.line'].search(
                [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'disburse'),
                 ('date_due', '>=', payslip.date_from), ('date_due', '<=', payslip.date_to)])
            # amount = sum(loan_line_ids.mapped('amount_residual'))
            amount = sum(payslip.input_line_ids.filtered(lambda x: x.code == 'LNI').mapped('amount'))

            for loan in loan_line_ids:
                # if loan:
                #    amount += loan.amount_residual
                if amount <= loan.amount_residual:
                    allocation = amount
                else:
                    allocation = loan.amount_residual

                self.env['hr.employee.loan.disburse'].create({
                    'name': _('Disbursed %s %s - %s - %s', loan.employee_loan_id.name,
                              formatLang(self.env, loan.amount_residual, currency_obj=loan.currency_id),
                              payslip.employee_id.name,
                              format_date(self.env, fields.Date.to_string(fields.Date.today()))),
                    'employee_loan_line_id': loan.id,
                    'employee_id': payslip.employee_id.id,
                    'currency_id': loan.currency_id.id,
                    'amount_due': loan.amount_residual,
                    'amount_disburse': allocation,
                    'date_disburse': payslip.date_from,
                    'payslip_id': payslip.id,
                })
                amount -= allocation
        res = super(HRPayslip, self).action_payslip_done()
        return res

    def action_payslip_cancel(self):
        for payslip in self:
            loan_disburse_ids = self.env['hr.employee.loan.disburse'].search([('payslip_id', '=', payslip.id)])
            if loan_disburse_ids:
                loan_disburse_ids.unlink()
        res = super(HRPayslip, self).action_payslip_cancel()
        return res

    def compute_sheet(self):
        input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'LNI')], limit=1)

        for payslip in self:
            amount = allocation = 0
            start_date = end_date = False

            loan_line_ids = self.env['hr.employee.loan.line'].search(
                [('employee_id', '=', payslip.employee_id.id), ('state', '=', 'disburse'),
                 ('date_due', '>=', payslip.date_from), ('date_due', '<=', payslip.date_to)])
            amount = sum(loan_line_ids.mapped('amount_residual'))

            # input_id = self.env['hr.payslip.input']
            for input in payslip.input_line_ids:
                if input.input_type_id.id == input_type_id.id:
                    input.unlink()
            self.env['hr.payslip.input'].create({
                'input_type_id': input_type_id.id,
                'code': 'LN',
                'amount': amount,
                'contract_id': payslip.contract_id.id,
                'payslip_id': payslip.id,
            })

        res = super(HRPayslip, self).compute_sheet()
        return res





