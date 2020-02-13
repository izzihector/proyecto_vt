# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

{
    'name': 'Customer/Vendor by Category',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Sales Management',
    'description':
        """
        This Module add below functionality into odoo

        1.Separate menu for creating category for customers\n
        2.Separate menu for creating category for vendors\n
        3.Assign Category to the Customer/Vendor\n
        4.You can group by Customers/Vendors by its Category\n
        5.Select customer in sale order by its category\n
        6.Select vendor in purchase order by  its category\n
        
        
        odoo category 
        odoo partner category 
        odoo customer category 
        odoo vendor category 
        Partner By Category
        Partners Hierarchy
        odoo Partners Hierarchy
        odoo Partner By Category
        partner group by Category
        customer group by Category
        vendor group by Category
        odoo customer group by Category
        odoo vendor group by Category
 Customer by category 
Odoo customer by category 
Manage customer category 
Odoo manage customer category 
Vendor by category 
Odoo vendor by category 
Manage vendor category 
Odoo manage vendor category 
Odoo app allows you to configure and assign partner category for customer
Odoo app allows you to configure and assign partner category for partner 
Afterward you can group by customer and vendor its category
Separate menus for creating partner category for customer and vendor
Assign Category to the Customer/Vendor
Odoo Assign Category to the Customer/Vendor
Group Customers/Vendors by its Category in Kanban View
Odoo Group Customers/Vendors by its Category in Kanban View
Group Customers/Vendors by its Category in Tree View
Odoo Group Customers/Vendors by its Category in Tree View
Select customer in sale order by code of customer's category
Odoo Select customer in sale order by code of customer's category
Assign category to customer 
Odoo assign category to customer 
       
        

    """,
    'summary': 'odoo app will add category of Customer/Vendor & partner filter by category',
    'depends': ['sale_management',
                'purchase'],
    'data': [
        'security/ir.model.access.csv',
        'views/customer_category_view.xml',
        'views/vendor_category_view.xml',
        'views/res_partner_view.xml',
        ],
    'demo': [],
    'test': [],
    'css': [],
    'qweb': [],
    'js': [],
    'images': ['images/main_screenshot.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
    
    # author and support Details =============#
    'author': 'DevIntelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',    
    'maintainer': 'DevIntelle Consulting Service Pvt.Ltd', 
    'support': 'devintelle@gmail.com',
    'price':10.0,
    'currency':'EUR',
    #'live_test_url':'https://youtu.be/A5kEBboAh_k',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
