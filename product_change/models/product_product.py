# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.template'

    codigo_suplidor = fields.Char(string="Codigo Suplidor")
