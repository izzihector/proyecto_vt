# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields

class payroll_statement_lines(models.Model):
    _name = 'payroll.statement.lines'
    
    employee_id = fields.Many2one('hr.employee',string='Employee')
    department_id = fields.Many2one('hr.department', string='Department')
    month = fields.Char('Month')

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: