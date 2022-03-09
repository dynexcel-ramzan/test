# -*- coding: utf-8 -*-
{
    'name': "HRMS Loan Management",

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
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_payroll', 'hr', 'account', 'hr_contract', 'mail'],

    # always loaded
    'data': [
        'data/hr_loan_seq.xml',
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/hr_loan_views.xml',
        'views/hr_loan_policy_views.xml',
        'views/hr_loan_proof_views.xml',
        'views/hr_loan_type_views.xml',
        'data/salary_rule_loan.xml',
        'views/hr_payroll_views.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}
