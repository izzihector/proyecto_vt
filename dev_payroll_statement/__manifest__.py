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
    'name': 'Employee Payroll Statement',
    'version': '12.0.1.0',
    'sequence': 1,
    'category': 'Generic Modules/Human Resources',
    'description':
        """
        This Module add below functionality into odoo

        1.Prints Employee Payroll Statement Report according date range and with filters\n
        2.Print Report as PDF Document\n
        3.Print Report in Excel Sheet\n
        4.or View Report on Screen\n
 odoo App will print employee payroll monthly statement with salary rules

Employee payslip statement, payroll statement, hr payslip statement, hr payroll , hr employee payroll, payroll summary report, emploee payslip by monthly, payslip ragistar, employee payslip generator, payslip salary rule , employee salary rule
Employee payroll statement
HR payroll
HR employee payroll
HR employee payroll statement
Print payroll statement
Print employee payroll statement
Print detailed employee payroll statement
Payroll monthly statement
Export payroll statement
Export employee payroll
Export employee payroll statement
Monthly payroll statement
Monthly employee payroll statement
Payroll report
HR payroll report
Payroll report for HR
Payroll statement odoo
HR payroll statement odoo
Employee payroll statement odoo
Payroll summary report
payroll summary by salary rule
payroll salary rule statement
employee payroll statement
odoo payroll summary 
export payroll summary in odoo
payroll department wise statement
payroll department wise statement in odoo
payroll job wise statement
payroll job wise statement in odoo
monthly payroll statement 
odoo monthly payroll statement         
        
        
    """,
    'summary': 'odoo App will print employee payroll monthly statement with salary rules',
    'author': 'Devintelle Consulting Service Pvt.Ltd',
    'website': 'http://www.devintellecs.com',
    'depends': ['base', 'hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'wizard/emp_payroll_statement_view.xml',
        'views/payroll_statement_tempate.xml',
        'views/payroll_statement_report_menu.xml',
        'views/payroll_statement_lines.xml',
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
    'price':39.0,
    'currency':'EUR',
    'live_test_url':'https://youtu.be/TpBgCFsyOsc',
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
