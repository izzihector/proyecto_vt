# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, ValidationError


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    product_detail_ids = fields.One2many(
        comodel_name='stock.product.detail',
        inverse_name='landed_cost_id',
        string='Detalle por producto',
        copy=False)

    @api.multi
    def compute_landed_cost(self):
        result = super(StockLandedCost, self).compute_landed_cost()

        detail_lines = self.env['stock.product.detail']
        detail_lines.search([('landed_cost_id', 'in', self.ids)]).unlink()

        products = {}
        for line in self.valuation_adjustment_lines:
            if line.product_id.type != 'product':
                continue
            additional_cost = line.additional_landed_cost / line.quantity
            value = line.former_cost/line.quantity
            if line.product_id.id not in products.keys():
                products[line.product_id.id] = {
                    'name': self.name,
                    'landed_cost_id': self.id,
                    'product_id': line.product_id.id,
                    'quantity': line.quantity,
                    'actual_cost': value,
                    'additional_cost': additional_cost,
                    'new_cost': value + additional_cost,

                }
            else:
                products[line.product_id.id]['additional_cost'] += additional_cost
                products[line.product_id.id]['new_cost'] += additional_cost

        for key, value in products.items():
            self.env['stock.product.detail'].create(value)

        return result


class StockProductDetail(models.Model):
    _name = 'stock.product.detail'
    _description = 'Stock Landed Cost Product Details'

    name = fields.Char(u'Descripción', required=True)
    landed_cost_id = fields.Many2one(
        comodel_name='stock.landed.cost',
        string=u'Liquidación',
        ondelete='cascade',
        required=True)
    product_id = fields.Many2one('product.product', 'Producto', required=True)
    quantity = fields.Float(
        string='Cantidad',
        default=1.0,
        digits=dp.get_precision('Product Unit of Measure'),
        required=True)
    actual_cost = fields.Float(
        'Costo actual unitario',
        digits=dp.get_precision('Product Price'),
        readonly=True)
    additional_cost = fields.Float(
        string=u'Costo de Importación',
        digits=dp.get_precision('Product Price'),
        readonly=True)
    new_cost = fields.Float(
        string=u'Nuevo Costo',
        digits=dp.get_precision('Product Price'),
        readonly=True)
