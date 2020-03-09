# -*- coding: utf-8 -*-
{
    'name': "Product Changes",

    'summary': """Agregar campos a los productos""",

    'description': """  """,

    'author': "Pedro Nunez Araujo",
    'website': "",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/12.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Productos',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        #'templates.xml',
        'views/view_product_form_inherit.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        #'demo.xml',
    ],
}
