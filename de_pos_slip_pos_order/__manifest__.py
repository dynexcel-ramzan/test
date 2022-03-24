# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    "name": "POS slip on POS Order",
    "category": 'POS Order',
    "summary": 'POS Order Receipt',
    "description": """
                        This module is about pos slip on pos order
                    """,
    "sequence": 1,
    "web_icon":"static/description/icon.png",
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '13.0.0.0',
    "depends": ['sale','point_of_sale'],
    "data": [
        'report/pos_slip_report.xml',
        'report/pos_slip_sale_order_report.xml',
    ],
}