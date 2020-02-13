# -*- coding: utf-8 -*-

from odoo import models, fields, api


class Partner(models.Model):
    _inherit = 'res.partner'

    sale_journal = fields.Many2one('account.journal', 'Default journal', domain=[('type', '=', 'sale')])
    purchase_journal = fields.Many2one('account.journal', 'Default journal', domain=[('type', '=', 'purchase')])

class Invoice(models.Model):
    _inherit = 'account.invoice'

    # @api.model
    # def create(self, vals):
    #   if self.partner_id.sale_journal and self.type == 'out_invoice':
    #     vals['journal_id'] = self.partner_id.sale_journal.id
    #   if self.partner_id.purchase_journal and self.type == 'in_invoice':
    #     vals['journal_id'] = self.partner_id.purchase_journal.id
    #   invoice = super(Invoice, self).create(vals)
    #   return invoice

    @api.model
    def create(self, vals):
        res = super(Invoice, self).create(vals)
        if res.partner_id.sale_journal and res.type == 'out_invoice':
            res.journal_id = res.partner_id.sale_journal.id
        if res.partner_id.purchase_journal and res.type == 'in_invoice':
            res.journal_id = res.partner_id.purchase_journal.id
        return res

    @api.onchange('partner_id')
    def partner_onchange(self):
      if self.partner_id.sale_journal and self.type == 'out_invoice':
        self.journal_id = self.partner_id.sale_journal.id
      if self.partner_id.purchase_journal and self.type == 'in_invoice':
        self.journal_id = self.partner_id.purchase_journal.id

