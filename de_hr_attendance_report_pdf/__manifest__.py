# -*- coding: utf-8 -*-
{
    'name': "Daily Attendance Report (PDF)",

    'summary': """
        Daily Employee Attendance Information in given data from wizard


        """,

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "http://www.dynaxel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Attendance',
    'version': '14.0.1',

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
    'application': True,
    'installation': True,
    'auto_install': False,
}
