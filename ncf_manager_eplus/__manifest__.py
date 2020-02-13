# -*- coding: utf-8 -*-
{
    'name': "ncf_manager_plus",

    'summary': """
        Nuevos formato de declaracion para Numero de comprobantes fiscales en 
        Dominicana""",

    'description': """
        Mejora para el nuevo NCF Manager
    """,

    'author': "MERPLUS, SRL",
    'website': "http://www.mer.plus",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['ncf_manager'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/ncf_manager_security.xml',
        'views/account_view.xml',
        #'views/dgii_exterior_view.xml',
        'views/dgii_purchase_view.xml',
        'views/dgii_sale_view.xml',
        'views/dgii_cancel_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
