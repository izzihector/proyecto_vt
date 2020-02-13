# -*- coding: utf-8 -*-
{
    'name': "Payslip Batch Confirm",

    'summary': """
        Payslip Batch Confirm.
        """,

    'description': """
        Confirm all payslips in batch.
    """,

    'author': "Mohsin Shoaib Modify by Click Solution Enterprise, by Daniel Diaz",
    'category': 'Payroll',
    'version': '10.0.1',

    'depends': ['base', 'hr', 'hr_payroll'],

    # always loaded
    'data': [
        'views/hr_payslip.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        ],
}