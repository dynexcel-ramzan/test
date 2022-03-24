# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import models, api


class HRPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        for slip in self:
            amount = 0
            start_date = end_date = False
            advance_ids = self.env['hr.employee.advance'].search(
                [('employee_id', '=', slip.employee_id.id), ('state', '=', 'done'), ('date', '>=', slip.date_from),
                 ('date', '<=', slip.date_to)])
            for adv in advance_ids:
                if adv:
                    amount += adv.amount

            input_type_id = self.env['hr.payslip.input.type'].search([('code', '=', 'ADVI')], limit=1)
            input_id = self.env['hr.payslip.input']
            for input in self.input_line_ids:
                if input.input_type_id.id == input_type_id.id:
                    input.unlink()
            self.env['hr.payslip.input'].create({
                'input_type_id': input_type_id.id,
                'code': 'ADV',
                'amount': amount,
                'contract_id': slip.contract_id.id,
                'payslip_id': slip.id,
            })

        res = super(HRPayslip, self).compute_sheet()
        return res
