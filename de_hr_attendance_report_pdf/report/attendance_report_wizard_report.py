# -*- coding: utf-8 -*-

import time
from odoo import api, models, _, fields
from dateutil.parser import parse
from odoo.exceptions import UserError
from datetime import date
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class CustomerInvoiceReport(models.AbstractModel):
    _name = 'report.de_hr_attendance_report_pdf.attendance_report_pdf'
    _description = 'Daily Attendance information'

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env['attendance.report.wizard'].browse(self.env.context.get('active_id'))
        attendance_ids = ''
        date = docs.date
        attendance_ids = self.env['hr.attendance'].search([('attendance_date','=', date)])

        return {
            'docs': docs,
            'date': date,
            'attendance_ids': attendance_ids,
        }