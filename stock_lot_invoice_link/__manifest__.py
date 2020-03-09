{
    'name': "Stock Lot Invoice Link",
    'summary': """This module add lot/serial number in invoice line.""",
    'description': """  """,
    'author': "Yasmany Castillo",
    'website': "",
    'category': 'Category Hidden',
    'version': '12.0.1.0',
    'depends': ['account', 'sale_stock'],
    'data': [
        # 'security/ir.model.access.csv',
        'views/account_invoice_views.xml',
        'views/stock_production_lot_views.xml',
    ],
}
