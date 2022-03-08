from odoo import models, fields, api


class HREmployeeExtend(models.Model):
    _inherit = 'hr.employee'

    father_name = fields.Char(string="Father Name")
    permanent_address = fields.Char(string="Permanent Address")
    qualification = fields.Char(string="Qualifiation")
    number_of_department = fields.Char(string="Number Of Department")
    emergency_contact_lines = fields.One2many('hr.employee.emergency.contact', 'hr_employee_id',
                                              string='Emergency Contact Lines', copy=True, auto_join=True)


class HrEmergencyCOntact(models.Model):
    _name = 'hr.employee.emergency.contact'
    _description = "Employee Emergency Contact"

    hr_employee_id = fields.Many2one('hr.employee', string='Employee Reference', required=False, ondelete='cascade',
                                     index=True, copy=False, readonly=True)
    name = fields.Char(string="Name")
    relation = fields.Char(string="Relation")
    mobile_number = fields.Char(string="Mobile Number")
    address = fields.Char(string="Address")
