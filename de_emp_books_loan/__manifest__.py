# -*- coding: utf-8 -*-
{
    'name': "Employee Loan",

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
    'depends': ['base','hr_payroll','de_emp_books','account'],

    # always loaded
    'data': [
        'security/hr_loan_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence_data.xml',
        'data/mail_data.xml',
        'data/payroll_data.xml',
        #'report/advance_request_report.xml',
        #'report/advance_report_templates.xml',
        #'views/hr_job_views.xml',
        #'views/hr_employee_views.xml',
        'views/res_config_settings_views.xml',
        'views/loan_menuitems.xml',
        'wizard/hr_loan_refuse_reason_views.xml',
        'wizard/hr_loan_refund_wizard_views.xml',
        'views/loan_views.xml',
        'views/loan_deferred_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
