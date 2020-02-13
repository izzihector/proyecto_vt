# -*- coding: utf-8 -*-
{
  "name"                 :  "HR Payroll Batch Journal Entry",
  'summary'              :  """Allow to create one journal entry for payslip batch""",
  "category"             :  "HR",
  "version"              :  "12.0.1.0.0",
  "author"               :  "Abdallah Mohamed",
  "license"              :  "OPL-1",
  "maintainer"           :  "Abdallah Mohammed",
  "website"              :  "https://www.abdalla.work/r/Qsm",
  "support"              :  "https://www.abdalla.work/r/Qsm",
  "description"          :  """ODOO HR Payroll Accounting Batch""",
  "depends"              :  [
                             'hr_payroll_account',
                            ],
  "data"                 :  [
                             'views/hr_payslip_run.xml',
                            ],
  "images"               :  [
                             'static/description/main_screenshot.png',
                             'static/description/payslip_batch_date.png',
                             'static/description/payslip_batch_close.png',
                             'static/description/payslip_confirm_with_batch.png',
                             'static/description/payslip_batch_journal_entry.png',
                             ],
  "application"          :  False,
  "installable"          :  True,
  "price"                :  30,
  "currency"             :  "EUR",
  'sequence'             : 1
}