# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, _


class CustomerVendorCategory(models.Model):
    _name = "customer.vendor.category"
    _description = "Categoria de Clientes/Suplidores"


    name = fields.Char(string="Categoria")
    code = fields.Char(string="Codigo")
    type = fields.Selection(string="Type",
                            selection=[('customer', 'Cliente'),
                                       ('vendor', 'Suplidor')])

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: