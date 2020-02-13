# -*- coding: utf-8 -*-
""" HR Payroll Batch Journal Entry """

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    batch_date = fields.Date('Date Account', states={'draft': [('readonly',
                                                                False)]},
                             readonly=True,
                             help="Keep empty to use the period of the validation("
                                  "Batch) date To.")
    batch_move_id = fields.Many2one('account.move', 'Accounting Entry',
                                    readonly=True, copy=False)

    company_id = fields.Many2one('res.company', string='Company', required=True, index=True, default=lambda self: self.env.user.company_id,
        help="Company related to this journal")

    @api.constrains("journal_id", "slip_ids", "slip_ids.company_id")
    def _check_same_company(self):
        for slip in self.slip_ids:
            if slip.company_id != self.company_id:
                raise ValidationError(_(
                    'The payslip of employee (%s) must belong to the same '
                    'company(%s) in journal (%s).') %
                                      slip.employee_id.name,
                                      self.journal_id.company_id.name,
                                      self.journal_id.name)

    def _get_draft_payslips(self, payslips):
        """
        @param payslips: recordset of payslips
        @:return recordset of payslips not validated
        """
        self.ensure_one()
        return payslips.filtered(lambda x: x.state not in ["done", "cancel"])

    @api.multi
    def draft_payslip_run(self):
        moves = self.mapped('batch_move_id')
        moves.filtered(lambda x: x.state == 'posted').button_cancel()
        moves.unlink()
        for rec in self:
            rec._set_payslip_draft()
        return super(HrPayslipRun, self).draft_payslip_run()


    @api.multi
    def _set_payslip_draft(self):
        for rec in self:
            for slip in rec.slip_ids:
                if slip.state == "done":
                    slip.write({'state': 'draft'})
                    if slip.move_id:
                        slip.move_id.button_cancel()
                        slip.move_id.unlink()

    @api.multi
    def close_payslip_run(self):
        super(HrPayslipRun, self).close_payslip_run()
        for rec in self:
            if rec.batch_move_id:
                raise UserError(_("You cannot close a payslip batch that is "
                                  "not in "
                                  "draft."))
            payslips = self._get_draft_payslips(rec.slip_ids)
            if payslips:
                for payslip in payslips:
                    payslip.compute_sheet()
                rec._create_batch_move(payslips)

    def _create_batch_move(self, payslips):
        self.ensure_one()
        currency = self.journal_id.currency_id or \
                   self.journal_id.company_id.currency_id
        line_ids = []
        debit_sum = 0.0
        credit_sum = 0.0
        date = self.batch_date or self.date_end
        name = _("Payslip Batch of %s") % self.name
        move_dict = {
            'narration': name,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': date,
        }
        for slip in payslips:
            slip.write({'state': 'done'})
            for line in slip.details_by_salary_rule_category:
                amount = currency.round(
                    self.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue
                debit_account_id = line.salary_rule_id.account_debit.id
                credit_account_id = line.salary_rule_id.account_credit.id

                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': slip.employee_id.name + ' >> ' + line.name,
                        'partner_id': line._get_partner_id(
                            credit_account=False),
                        'account_id': debit_account_id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(debit_line)
                    debit_sum += debit_line[2]['debit'] - debit_line[2][
                        'credit']

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': slip.employee_id.name + ' >> ' + line.name,
                        'partner_id': line._get_partner_id(credit_account=True),
                        'account_id': credit_account_id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_account_id': line.salary_rule_id.analytic_account_id.id,
                        'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    })
                    line_ids.append(credit_line)
                    credit_sum += credit_line[2]['credit'] - credit_line[2][
                        'debit']
        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            acc_id = self.journal_id.default_credit_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Credit Account!') % (
                                    self.journal_id.name))
            adjust_credit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum - credit_sum),
            })
            line_ids.append(adjust_credit)
        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            acc_id = self.journal_id.default_debit_account_id.id
            if not acc_id:
                raise UserError(_(
                    'The Expense Journal "%s" has not properly configured the Debit Account!') % (
                                    self.journal_id.name))
            adjust_debit = (0, 0, {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': acc_id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum - debit_sum),
                'credit': 0.0,
            })
            line_ids.append(adjust_debit)
        move_dict['line_ids'] = line_ids
        move = self.env['account.move'].create(move_dict)
        self.write({'batch_move_id': move.id, 'batch_date': date})
        move.post()
