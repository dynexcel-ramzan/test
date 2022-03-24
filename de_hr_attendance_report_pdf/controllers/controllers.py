# -*- coding: utf-8 -*-
# from odoo import http


# class DeEmployeeAttendance(http.Controller):
#     @http.route('/de_employee_attendance/de_employee_attendance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/de_employee_attendance/de_employee_attendance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('de_employee_attendance.listing', {
#             'root': '/de_employee_attendance/de_employee_attendance',
#             'objects': http.request.env['de_employee_attendance.de_employee_attendance'].search([]),
#         })

#     @http.route('/de_employee_attendance/de_employee_attendance/objects/<model("de_employee_attendance.de_employee_attendance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('de_employee_attendance.object', {
#             'object': obj
#         })
