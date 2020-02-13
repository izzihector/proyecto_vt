# -*- coding: utf-8 -*-
#################################################################################
# Author      : Acespritech Solutions Pvt. Ltd. (<www.acespritech.com>)
# Copyright(c): 2012-Present Acespritech Solutions Pvt. Ltd.
# All Rights Reserved.
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#################################################################################

from openerp import fields, models, api, _
from datetime import datetime, date, timedelta
from openerp.exceptions import Warning


class mass_payment(models.Model):
    _name = 'mass.payment'
    _description = 'Mass Payment'

    @api.multi
    def unlink(self):
        if self.filtered(lambda payment:payment.state == 'posted'):
            raise Warning(_("No puedes borrar si ya esta contabilizado."))
        return super(mass_payment, self).unlink()

    @api.one
    @api.depends('account_payment_ids')
    def _get_amount_total(self):
        total = 0.0
        total_cobrado = 0.0
        total_no_cobrado = 0.0
        for each_payment in self.account_payment_ids:
            total += each_payment.amount
            if each_payment.payment_form in ('cash','bank','trans','card') and each_payment.state != 'cancelled':
                total_cobrado += each_payment.amount
            else:
                total_no_cobrado += each_payment.amount
        self.total = total
        self.total_cobrado = total_cobrado
        self.total_no_cobrado = total_no_cobrado

    name = fields.Char(string="Name")
    company_id = fields.Many2one('res.company', string=u"Compañía", default=1)
    partner_ids = fields.Many2many('res.partner', string="Contacto")
    journal_id = fields.Many2one('account.journal', string="Diario")
    partner_type = fields.Selection([('customer', 'Customer'), ('supplier', 'Supplier')], string="Tipo contacto")
    no_of_day = fields.Integer(string=u"Días de antigüedad")
    state = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('sent', 'Sent'),('cancelled','Cancelled')],
                                readonly=True, default='draft', copy=False, string="Estado")
    account_payment_ids = fields.One2many('account.payment', 'mass_payment_id', string="Pagos")
    total = fields.Float(string="Total", compute='_get_amount_total')
    invoice_ids = fields.Many2many('account.invoice', 'mass_payment_id', 'invoice_id', 'mass_invoice_tabel_rel', string="Facturas")
    total_cobrado = fields.Float(string="Total cobrado", compute='_get_amount_total')
    total_no_cobrado = fields.Float(string="Total no cobrado", compute='_get_amount_total')
    partner_id = fields.Many2one('res.partner', string='Cobrado por', domain=[('is_payment','=', True)])
    payment_date = fields.Date(string='Fecha Cobro', default=fields.Date.context_today, required=True)

    @api.onchange('company_id')
    def onchange_company_id(self):
        if self.company_id:
            if self.partner_type == 'customer':
                return {'domain': {'partner_ids': [('customer', '=', True), '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)]}}
            else:
                return {'domain': {'partner_ids': [('supplier', '=', True), '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)]}}

    @api.model
    def create(self, vals):
        if vals.get('partner_type'):
            if vals.get('partner_type') == 'customer':
                vals['name'] = self.env['ir.sequence'].next_by_code('customer.mass.payment') or '/'
            elif vals.get('partner_type') == 'supplier':
                vals['name'] = self.env['ir.sequence'].next_by_code('supplier.mass.payment') or '/'
        return super(mass_payment, self).create(vals)

    @api.multi
    def post(self):
        acc_obj = self.pool['account.invoice']
        if not self.account_payment_ids:
            self.create_draft_payment()
        for each_payment_id in self.account_payment_ids:
            ctx = dict(self._context)
            ctx.update({'force_company': each_payment_id.company_id.id})
            if each_payment_id.state == 'draft':
                if each_payment_id.payment_form in ('cash','bank','card','trans'):
                    each_payment_id.with_context(ctx).post()
                else:
                    each_payment_id.with_context(ctx).cancel()
            if each_payment_id.state == 'posted':
                for each_move_line in each_payment_id.move_line_ids:
                    if each_payment_id.invoice_id:
                        if self.partner_type == 'customer':
                            if each_move_line.credit > 0 and each_move_line.debit == 0:
                                each_payment_id.invoice_id.assign_outstanding_credit(each_move_line.id)
                        else:
                            if each_move_line.credit == 0 and each_move_line.debit > 0:
                                each_payment_id.invoice_id.assign_outstanding_credit(each_move_line.id)
        if all([x.state in ('posted','cancelled') for x in self.account_payment_ids]):
            self.write({'state': 'posted'})

    @api.multi
    def cancel(self):
        ctx = dict(self._context)
        for each_payment_id in self.account_payment_ids:
            if each_payment_id.state in ('draft','posted'):
                each_payment_id.with_context(ctx).cancel()
        if all([x.state == 'cancelled' for x in self.account_payment_ids]):
            self.write({'state': 'cancelled'})

    @api.multi
    def create_draft_payment(self):
        account_invoice_obj = self.env['account.invoice']
        cust_mass_payment_type = self.env.ref('account.account_payment_method_manual_in')
        supp_mass_payment_type = self.env.ref('account.account_payment_method_manual_out')
        for each_id in self.account_payment_ids:
            each_id.unlink()
        if self and self.partner_type:
            company_id = self.company_id.id
            if not self.partner_ids:
                if self.partner_type == 'customer':
                    partner_ids = [each_partner.id for each_partner in self.env['res.partner'].search([('customer', '=', True), '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)])]
                else:
                    partner_ids = [each_partner.id for each_partner in self.env['res.partner'].search([('supplier', '=', True), '|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)])]
            else:
                partner_ids = [each_partner.id for each_partner in self.partner_ids]
            if not self.no_of_day:
                to_date = date.today()
            else:
                if self.no_of_day < 0:
                    raise Warning(_("No of day must be in positive."))
                to_date = date.today() - timedelta(days=int(self.no_of_day))
            payment_list = []
            if not self.invoice_ids:
                invoice_ids = account_invoice_obj.search([('company_id', '=', company_id),
                                                          ('partner_id', 'in', partner_ids),
                                                          ('type', '=', 'out_invoice' if self.partner_type == 'customer' else 'in_invoice'),
                                                          ('date_invoice', '<=', to_date),
                                                          ('residual', '>', 0), ('state', '=', 'open')])
            else:
                invoice_ids = self.invoice_ids
            payments_default_data = self.env['account.payment'].default_get(['currency_id', 'payment_date', 'state', 'name'])
            if not invoice_ids:
                raise Warning(_('No open invoice found for mass payment.'))
            for each_invoice in invoice_ids:
                if not self.journal_id:
                    journal_id = self.env['account.journal'].search([('company_id', '=', each_invoice.company_id.id), ('type', '=', 'bank')], limit=1)
                else:
                    journal_id = self.journal_id
                if journal_id:
                    payment_list.append((0, 0, {'currency_id': payments_default_data.get('currency_id'),
                                                'payment_date': self.payment_date,
                                                'state': payments_default_data.get('state'),
                                                'name': payments_default_data.get('name'),
                                                'payment_type': self._context.get('default_payment_type'),
                                                'partner_type': self._context.get('default_partner_type'),
                                                'partner_id': each_invoice.partner_id.id,
                                                'invoice_id': each_invoice.id,
                                                'journal_id': journal_id.id,
                                                'amount': each_invoice.residual,
                                                'payment_method_id': cust_mass_payment_type.id if self.partner_type == 'customer' else supp_mass_payment_type.id,
                                                'company_id': each_invoice.company_id.id
                                                }))
            self.account_payment_ids = payment_list
        return True

    @api.multi
    def action_view_journal_entries(self):
        journal_entries_id = []
        for each_payment_id in self.account_payment_ids:
            if each_payment_id.move_line_ids:
                journal_entries_id.append(each_payment_id.move_line_ids[0].move_id.id)
        if journal_entries_id:
            action = self.env.ref('account.action_move_journal_line').read()[0]
            action['domain'] = [('id', 'in', journal_entries_id)]
            action['context'] = {'search_default_misc_filter':0, 'view_no_maturity': True}
            return action


class account_payment(models.Model):
    _inherit = "account.payment"

    mass_payment_id = fields.Many2one('mass.payment', string="Pagos masivos")
    invoice_id = fields.Many2one('account.invoice', string="Factura")
    payment_form = fields.Selection(
        [("cash", "Efectivo"),
         ("bank", u"Cheque"),
         ("card", u"Tarjeta"),
         ("credit", u"Crédito"),
         ("trans", "Transferencia"),
         ("credit_note", u"Nota Crédito"),
         ("no", u"No Cobrada"),
         ("cancel", "Anular")],
        string="Forma de Pago",
        default="no")

    @api.onchange('invoice_id')
    def onchange_invoice_id(self):
        if not self.mass_payment_id:
            return
        if self.invoice_id:
            self.amount = self.invoice_id.residual
            self.currency_id = self.invoice_id.currency_id.id


class account_journal(models.Model):
    _inherit = 'account.journal'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('mass_payment_journal_id'):
            args = args or []
            args.append(('id', '=', self._context.get('mass_payment_journal_id')))
        return super(account_journal, self).name_search(name, args, operator, limit)


class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_mass_payment'):
            args = args or []
            args.append(('state', '=', 'open'))
            if self._context.get('partner_type'):
                if self._context.get('partner_type') == 'customer':
                    args.append(('type', '=', 'out_invoice'))
                else:
                    args.append(('type', '=', 'in_invoice'))
            if self._context.get('partner_id'):
                args.append(('partner_id', '=', self._context.get('partner_id')))
            if self._context.get('partner_ids') and self._context.get('partner_ids')[0][2]:
                args.append(('partner_id', 'in', self._context.get('partner_ids')[0][2]))
            if self._context.get('company_id'):
                args.append(('company_id', '=', self._context.get('company_id')))
            if self._context.get('no_of_day'):
                to_date = date.today() - timedelta(days=int(self._context.get('no_of_day')))
                args.append(('date_invoice', '<=', to_date))
        return super(AccountInvoice, self).name_search(name, args, operator, limit)


class res_partner(models.Model):
    _inherit = 'res.partner'

    is_payment = fields.Boolean (string="Cobra Factura")

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if self._context.get('from_mass_payment'):
            args = args or []
            if self._context.get('invoice_id'):
                partner_id = self.env['account.invoice'].browse(self._context.get('invoice_id')).partner_id
                args.append(('id', '=', partner_id.id))
            elif self._context.get('partner_id'):
                args.append(('id', '=', self._context.get('partner_id')))
        return super(res_partner, self).name_search(name, args, operator=operator, limit=limit)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: