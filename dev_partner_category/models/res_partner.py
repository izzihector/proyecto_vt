# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2015 DevIntelle Consulting Service Pvt.Ltd (<http://www.devintellecs.com>).
#
#    For Module Support : devintelle@gmail.com  or Skype : devintelle
#
##############################################################################

from odoo import models, fields, api
from odoo.osv import expression
from lxml import etree


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        res = super(ResPartner, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar,
            submenu=submenu)
        doc = etree.XML(res['arch'])
        for node in doc.xpath("//field[@name='customer_vendor_categ_id']"):
            ctx = self._context
            if 'search_default_customer' in ctx:
                node.set('domain', "[('type', '=', 'customer')]")
            if 'search_default_supplier' in ctx:
                node.set('domain', "[('type', '=', 'vendor')]")
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        if operator in ('ilike', 'like', '=', '=like', '=ilike'):
            domain = expression.AND(
                [args or [], ['|', ('name', operator, name),
                              ('customer_vendor_categ_id.code',
                               operator, name)]])
            return self.search(domain, limit=limit).name_get()
        return super(ResPartner, self).name_search(
            name, args, operator, limit)


    customer_vendor_categ_id = fields.Many2one("customer.vendor.category",
                                               string="Categoria")

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: