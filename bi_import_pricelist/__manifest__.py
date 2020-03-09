# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Import Pricelist from Excel or CSV File',
    'version': '12.0.0.3',
    'sequence': 4,
    'summary': 'Easy to Import multiple pricelist with multiple pricelist lines on Odoo by Using CSV/XLS file.',
    'category': 'purchase,sales',
    "price": 55,
    "currency": 'EUR',
    'description': """
    Import vendor and sale pricelist from Excel and CSV File.
    import sale pricelist
    import pricelist from excel
    import pricelist from csv
    import vendor pricelist from excel
    import vendor pricelist from csv
    import supplier pricelist from excel
    import supplier pricelist from csv
    import purchase pricleist from excel
    import purchase pricelist from csv
    import sales pricelist from excel
    import customer pricelist from excel
    import sales pricelist from csv
    import customer pricelist from csv
    """,
    'author': 'BrowseInfo',
    'website': 'http://www.browseinfo.in',
    'depends': ['base','sale','purchase','sale_management'],
    'data': ['views/sale.xml'],
    'installable': True,
    'auto_install': False,
    "images":['static/description/Banner.png'],
}
