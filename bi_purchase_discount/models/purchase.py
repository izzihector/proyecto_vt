# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'

    @api.one
    @api.depends('order_line.discount')
    def _compute_discount(self):
        discount = 0.0
        for line in self.order_line:
            if line.discount:
                discount += (line.price_unit * line.product_qty) - (
                    (line.price_unit * line.product_qty) * (1 - (
                        line.discount or 0.0) / 100.0))
        self.discount_total = discount

    discount_total = fields.Float(
        string="Descuento", store=True, readonly=True,
        compute='_compute_discount', track_visibility='always')


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    discount = fields.Float(
        string='Discount %',
        digits=dp.get_precision('Discount'),
    )

    @api.depends('product_qty', 'price_unit', 'taxes_id', 'discount')
    def _compute_amount(self):
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.taxes_id.compute_all(
                price,
                line.order_id.currency_id,
                line.product_qty,
                product=line.product_id,
                partner=line.order_id.partner_id,
            )
            line.update({
                'price_tax': sum(
                    t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
