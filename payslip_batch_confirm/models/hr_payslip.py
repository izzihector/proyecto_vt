# -*- coding: utf-8 -*-
from odoo import models, fields, api

class hr_payslip_run(models.Model):
    """
    Confirm all payslips in batch
    """
    _inherit = "hr.payslip.run"

    @api.multi
    def confirm_payslips_in_batch(self):

        payslip_records = self.browse(self.slip_ids)
        
        for item in payslip_records:
            if item.ids[0].state == 'draft':
                item.ids[0].compute_sheet()
                item.ids[0].action_payslip_done()
        return True