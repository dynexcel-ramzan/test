# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    department_id = fields.Many2one(related='employee_id.department_id', string="Department", store=True, readonly=True)
