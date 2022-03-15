import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips, ResultRules
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_round, date_utils
from odoo.tools.misc import format_date
from odoo.tools.safe_eval import safe_eval
from datetime import date, datetime, timedelta
from odoo import exceptions
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class HrPayslips(models.Model):
    _inherit = 'hr.payslip'

    num_of_days = fields.Float(string='Attendance Days')

    def _compute_basic_net(self):
        for payslip in self:
            basic_amount = net_amount = 0
            for line in payslip.line_ids:
                if line.code == 'Basic' or line.code == 'BASIC 12000':
                    basic_amount = line.amount
                if line.code == 'Net' or line.code == 'NET':
                    net_amount = line.amount
            payslip.basic_wage = basic_amount
            payslip.net_wage = net_amount

    def compute_sheet(self):
        work_day_line = []
        work_days = 0
        work_hours = 0

        """
          Employee Attendance Days
        """
        for payslip in self:
            date_from = payslip.date_from
            date_to = payslip.date_to
            employee = payslip.employee_id
            days = (date_to - date_from).days + 1
            work_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'WORK100')], limit=1)
            ofcal_leaves = self.env['hr.leave'].sudo().search(
                [('employee_id', '=', employee.id), ('request_date_from', '>=', date_from),
                 ('request_date_to', '<=', date_to), ('state', '=', 'validate'),
                 ('holiday_status_id.code', '=', 'Official-Visit')])
            off_leave_count = ofcal_leave_day = 0
            for ofcal in ofcal_leaves:
                off_leave_count += 1
                ofcal_leave_day = ofcal.number_of_days

            emp_attendance = self.env['hr.attendance'].sudo().search(
                [('employee_id', '=', employee.id), ('attendance_date', '>=', date_from),
                 ('attendance_date', '<=', date_to)])
            if payslip.num_of_days >= 1:
                work_days = payslip.num_of_days
            if not payslip.num_of_days >= 1:
                for em_att in emp_attendance:
                    day_hours = 0
                    if em_att.check_out and em_att.check_in:
                        day_hours += em_att.worked_hours
                        #                         if (day_hours > (7.4)):
                        work_days += 1
            if employee.resource_calendar_id:
                work_hours = employee.resource_calendar_id.hours_per_day
            work_day_line.append((0, 0, {
                'work_entry_type_id': work_entry_type.id,
                'name': work_entry_type.name,
                'sequence': work_entry_type.sequence,
                'number_of_days': work_days,
                'number_of_hours': (work_days * work_hours),
            }))
            absent_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'ABS100')], limit=1)
            delta_days = (date_to - date_from).days + 1
            absent_days = delta_days - work_days

            gazetted_day_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'PublicHoliday')],
                                                                                   limit=1)
            rest_day_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'RESTDAY100')], limit=1)
            work_time = self.env['resource.calendar'].sudo().search([('id', '=', employee.resource_calendar_id.id)],
                                                                    limit=1)
            start_date = date_from
            restday_count = 0
            gazetted_day_count = 0
            for day in range(delta_days):
                is_rest_day = False
                for wt in work_time.attendance_ids:
                    # name of week day
                    #                     raise UserError(str(wt.dayofweek)+''+str(start_date.weekday()))
                    if str(wt.dayofweek) == str(start_date.weekday()):
                        is_rest_day = True

                if is_rest_day == False:
                    restday_count += 1
                for gazetted_day in work_time.global_leave_ids:
                    gazetted_date_from = gazetted_day.date_from + relativedelta(hours=+5)
                    gazetted_date_to = gazetted_day.date_to + relativedelta(hours=+5)
                    if str(start_date.strftime('%y-%m-%d')) >= str(gazetted_date_from.strftime('%y-%m-%d')) and str(
                            start_date.strftime('%y-%m-%d')) <= str(gazetted_date_to.strftime('%y-%m-%d')):
                        gazetted_day_count += 1
                start_date = start_date + timedelta(1)
            casual_leaves = self.env['hr.leave'].sudo().search(
                [('employee_id', '=', employee.id), ('request_date_from', '>=', date_from),
                 ('request_date_to', '<=', date_to), ('state', '=', 'validate'), ('holiday_status_id.code', '=', 'CL')])
            cas_leave_count = cas_leave_day = 0
            for casu_leave in casual_leaves:
                cas_leave_count += 1
                cas_leave_day = casu_leave.number_of_days

            sick_leaves = self.env['hr.leave'].sudo().search(
                [('employee_id', '=', employee.id), ('request_date_from', '>=', date_from),
                 ('request_date_to', '<=', date_to), ('state', '=', 'validate'),
                 ('holiday_status_id.code', '=', 'Sick-Leave')])

            sick_leave_count = sick_leave_day = 0
            for sick_leave in sick_leaves:
                sick_leave_count += 1
                sick_leave_day = sick_leave.number_of_days

            work_day_line.append((0, 0, {
                'work_entry_type_id': rest_day_entry_type.id,
                'name': rest_day_entry_type.name,
                'sequence': rest_day_entry_type.sequence,
                'number_of_days': restday_count,
                'number_of_hours': (restday_count * work_hours),
            }))

            work_day_line.append((0, 0, {
                'work_entry_type_id': gazetted_day_entry_type.id,
                'name': gazetted_day_entry_type.name,
                'sequence': gazetted_day_entry_type.sequence,
                'number_of_days': gazetted_day_count,
                'number_of_hours': (gazetted_day_count * work_hours),
            }))

            work_day_line.append((0, 0, {
                'work_entry_type_id': absent_entry_type.id,
                'name': absent_entry_type.name,
                'sequence': absent_entry_type.sequence,
                'number_of_days': absent_days - (
                            restday_count + gazetted_day_count + cas_leave_day + sick_leave_day + ofcal_leave_day),
                'number_of_hours': (absent_days * work_hours),
            }))

            if off_leave_count > 0:
                ofcal_leave_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'officialvisit')],
                                                                                      limit=1)
                work_day_line.append((0, 0, {
                    'work_entry_type_id': ofcal_leave_entry_type.id,
                    'name': ofcal_leave_entry_type.name,
                    'sequence': ofcal_leave_entry_type.sequence,
                    'number_of_days': ofcal_leave_day,
                    'number_of_hours': (ofcal_leave_day * work_hours),
                }))

            if cas_leave_count > 0:
                casual_leave_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'Casual Leaves')],
                                                                                       limit=1)
                work_day_line.append((0, 0, {
                    'work_entry_type_id': casual_leave_entry_type.id,
                    'name': casual_leave_entry_type.name,
                    'sequence': casual_leave_entry_type.sequence,
                    'number_of_days': cas_leave_day,
                    'number_of_hours': (cas_leave_day * work_hours),
                }))
            if sick_leave_count > 0:
                sick_leave_entry_type = self.env['hr.work.entry.type'].sudo().search([('code', '=', 'Sick Leaves')],
                                                                                     limit=1)
                work_day_line.append((0, 0, {
                    'work_entry_type_id': sick_leave_entry_type.id,
                    'name': sick_leave_entry_type.name,
                    'sequence': sick_leave_entry_type.sequence,
                    'number_of_days': sick_leave_day,
                    'number_of_hours': (sick_leave_day * work_hours),
                }))
            if payslip.worked_days_line_ids:
                payslip.worked_days_line_ids.unlink()
            if payslip.employee_id:
                payslip.worked_days_line_ids = work_day_line
        res = super(HrPayslips, self).compute_sheet()
        return res


class HrPayslip(models.Model):
    _inherit = 'hr.attendance'

    attendance_date = fields.Date(string="Attendance Date", store=True, compute='compute_attendance_date')

    def compute_attendance_date(self):
        for rec in self:
            rec.attendance_date = rec.check_in
