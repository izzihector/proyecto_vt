# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import math
from odoo import models
import time
from odoo import api, fields, models, _
from odoo.tools.translate import _
import odoo.addons.decimal_precision as dp
from datetime import datetime, timedelta, date
from odoo.exceptions import UserError, ValidationError, Warning
        

      
class AccountBankStatement(models.Model):
    _inherit = "account.bank.statement"
    
    move_line_ids = fields.One2many('account.move.line', 'statement_id', string='Entry lines')
    account_id = fields.Many2one('account.account', related='journal_id.default_debit_account_id', type='many2one', string='Account', readonly=True, help='used in statement reconciliation domain, but shouldn\'t be used elswhere.')
	
    @api.one
    @api.depends('line_ids', 'balance_start', 'line_ids.amount', 'balance_end_real','move_line_ids')
    def _end_balance(self):
        res_users_obj = self.env['res.users']
        company_currency_id = self.env.user.company_id.currency_id
        statement_balance_start = self.balance_start
        for line in self.move_line_ids:
            if line.debit > 0:
                if line.account_id.id == \
                        self.journal_id.default_debit_account_id.id:
                    statement_balance_start += line.amount_currency or line.debit
            else:
                if line.account_id.id == \
                        self.journal_id.default_credit_account_id.id:
                    statement_balance_start += line.amount_currency or (-line.credit)
        self.balance_end = statement_balance_start
        if self.state in ('open'):
            for line in self.line_ids:
                statement_balance_start += line.amount
                self.balance_end = statement_balance_start
        self.difference = self.balance_end_real - self.balance_end  # MERPLUS

    @api.model
    def create(self, vals):
        # Dont allow adding transaction and Journal Entries in same statement.
        if vals.get('move_line_ids') and vals.get('line_ids'):
            raise UserError('You can Either add Journal Entries or Transactions..!')
        res = super(AccountBankStatement, self).create(vals)
        return res
        
    @api.multi
    def write(self, vals):
        # Dont allow adding transaction or Journal Entries when other is added in same statement.
        for statement in self:
            if ('line_ids' in vals and statement.move_line_ids) or (statement.line_ids and 'move_line_ids' in vals) or ('move_line_ids' in vals and 'line_ids' in vals):
                raise UserError('You can Either add Journal Entries or Transactions..!')
        res = super(AccountBankStatement, self).write(vals)
        return res
        
        
