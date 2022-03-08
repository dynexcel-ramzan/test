# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class CustomerInvoiceInfo(models.TransientModel):
    _name = "attendance.report.wizard"
    _description = "Daily Attendance Report wizard"

    date = fields.Date(string='Date', required=True)

    def check_report(self):
        data = {}
        data['form'] = self.read(['date'])[0]
        return self._print_report(data)

    def _print_report(self, data):
        data['form'].update(self.read(['date'])[0])
        return self.env.ref('de_hr_attendance_report_pdf.attendance_report_pdf_action').report_action(self, data=data,
                                                                                                      config=False)