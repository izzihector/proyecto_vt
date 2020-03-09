from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'

    production_lot_id = fields.Many2many(
        comodel_name="stock.production.lot",
        string="Lot/Serial number",
        relation="stock_production_lot_invoice_rel",
        column1="invoice_line_id",
        column2="lot_id",
        required=False,
    )

    # ----------------------------------------
    # ORM Overrides
    # ----------------------------------------

    @api.model
    def create(self, values):
        invoice_line_id = super(AccountInvoiceLine, self).create(values)

        for line in invoice_line_id.sale_line_ids:
            stock_move = self.env['stock.move'].search([
                ('origin', '=', line.order_id.name),
                ('product_id', '=', line.product_id.id),
                ('state', '=', 'done')
            ])
            stock_move_line = self.env['stock.move.line'].search([
                ('move_id', '=', stock_move.id)
            ])

            for move_line in stock_move_line:
                if move_line.lot_id.id:
                    invoice_line_id.production_lot_id = [(4, move_line.lot_id.id)]

        return invoice_line_id
