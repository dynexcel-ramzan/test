# -*- coding: utf-8 -*-
{
    'name': "Daily Attendance Report (PDF",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_attendance'],

    # always loaded
    'data': [
        # 'report/de_employee_attendance_header.xml',
        'security/ir.model.access.csv',
        'wizard/attendance_report_wizard_view.xml',
        'report/attendance_report_wizard_template.xml',
        'report/attendance_report_wizard_view.xml',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
