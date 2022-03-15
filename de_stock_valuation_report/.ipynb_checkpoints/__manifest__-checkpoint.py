# -*- coding: utf-8 -*-
{
    'name': "Stock Valuation (sale Price)",

    'summary': """
        Stock Valuation pdf Report.
        """,

    'description': """
        Features:
        1. Stock Valuation report on sales price
        2. This report only work with Fixed pricelist, Formula based pricelist is not compatible
        3. Support Community/Enterpris Edition
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'warehouse',
    'version': '1.1',

    # any module necessary for this one to work correctly
    'depends': ['base','stock','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'wizard/product_stock_wizard_view.xml',
        'views/product_stock_report.xml',
        'views/product_stock_report_template.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}