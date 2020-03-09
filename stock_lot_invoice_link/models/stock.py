from odoo import api, fields, models


class AccountInvoiceLine(models.Model):
    _inherit = 'stock.production.lot'

    invoice_line_ids = fields.Many2many(
        comodel_name='account.invoice.line',
        string="Invoice Lines",
        relation="stock_production_lot_invoice_rel",
        column1="lot_id",
        column2="invoice_line_id",
    )
    invoice_ids = fields.Many2many(
        comodel_name='account.invoice',
        string="Invoices",
        compute='_compute_invoice_ids',
    )
    invoice_count = fields.Integer(
        string='Invoice count',
        compute='_compute_invoice_ids',
    )

    @api.depends('invoice_line_ids')
    def _compute_invoice_ids(self):
        for lot in self:
            invoice_id = self.env['account.invoice.line'].search([
                ('production_lot_id', 'in', lot.ids),
                ('invoice_id.state', '!=', 'cancel')
            ]).mapped('invoice_id')
            lot.invoice_ids = [(4, invoice_id.id)]
            lot.invoice_count = len(lot.invoice_ids)

    def action_invoice_view(self):
        self.ensure_one()
        action = self.env.ref('account.action_invoice_tree').read()[0]
        action['domain'] = [('id', 'in', self.mapped('invoice_ids.id'))]
        return action
