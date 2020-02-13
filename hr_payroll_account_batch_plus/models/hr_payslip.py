# -*- coding: utf-8 -*-
""" HR Payroll Batch Journal Entry """

from odoo import models, api, _
from odoo.exceptions import UserError, ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def action_payslip_done(self):
        super(HrPayslip, self).action_payslip_done()
        for rec in self:
            if rec.payslip_run_id:
                raise UserError(_(
                    'Payslip for employee "%s" related to batch "%s". To '
                    'confirm it, Please confirm payslip batch')
                                % (rec.employee_id.name,
                                   rec.payslip_run_id.name
                                   )
                                )

    @api.constrains("credit_note","payslip_run_id","payslip_run_id.credit_note")
    def _check_credit_note_batch(self):
        if self.payslip_run_id:
            if self.payslip_run_id.credit_note != self.credit_note:
                raise ValidationError(_(
                    'Please notes that "Credit Note" is not same as in '
                    'batch (%s).') %
                                      self.payslip_run_id.name)