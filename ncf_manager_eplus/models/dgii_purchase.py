# -*- coding: utf-8 -*-
########################################################################################################################
#  Copyright (c) 2018 - MERPLUS SRL. (<http://mer.plus/>) 
#  See LICENSE file for full copyright and licensing details.
#
# Odoo Proprietary License v1.0
#
# This software and associated files (the "Software") may only be used
# (nobody can redistribute (or sell) your module once they have bought it, unless you gave them your consent)
# if you have purchased a valid license
# from the authors, typically via Odoo Apps, or if you have received a written
# agreement from the authors of the Software (see the COPYRIGHT file).
#
# You may develop Odoo modules that use the Software as a library (typically
# by depending on it, importing it and using its resources), but without copying
# any source code or material from the Software. You may distribute those
# modules under the license of your choice, provided that this license is
# compatible with the terms of the Odoo Proprietary License (For example:
# LGPL, MIT, or proprietary licenses similar to this one).
#
# It is forbidden to publish, distribute, sublicense, or sell copies of the Software
# or modified copies of the Software.
#
# The above copyright notice and this permission notice must be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE,
# ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
########################################################################################################################
from odoo import models, fields, api, exceptions
import calendar
import base64
import time
import re
from datetime import datetime

class DgiiPurchaseReportPlus(models.Model):
    _name = "dgii.purchase.report.plus"

    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('dgii.purchase.report.plus'))
    name = fields.Char()
    year = fields.Integer(u"Año", size=4, default=lambda s: int(time.strftime("%Y")))
    month = fields.Integer("Mes", size=2, default=lambda s: int(time.strftime("%m")))
    CANTIDAD_REGISTRO = fields.Integer("Cantidad de registros")
    ITBIS_RETENIDO = fields.Float("TOTAL ITBIS RETENIDO")
    ITBIS_TOTAL = fields.Float("TOTAL ITBIS PAGADO")
    TOTAL_MONTO_FACTURADO = fields.Float("TOTAL FACTURADO")
    RETENCION_RENTA = fields.Float("TOTAL RETENCION RENTA")
    txt = fields.Binary("Reporte TXT", readonly=True)
    txt_filename = fields.Char("Nombre del archivo",readonly=True)
    state = fields.Selection([('draft','Nuevo'),('done','Generado')], default="draft")
    report_lines = fields.One2many("dgii.purchase.report.line.plus", "purchase_report_id")

    @api.model
    def create(self, vals):
        vals.update({"name": "{}/{}".format(vals["month"],vals["year"])})
        self = super(DgiiPurchaseReportPlus, self).create(vals)
        self.create_report()
        return self

    def get_date_range(self):
        if self.month > 12 or self.month < 1:
            self.month = False
            raise exceptions.ValidationError("El mes es invalido!")
        last_day = calendar.monthrange(self.year, self.month)[1]
        return ("{}-{}-{}".format(str(self.year), str(self.month).zfill(2), "01"),
                "{}-{}-{}".format(str(self.year), str(self.month).zfill(2), str(last_day).zfill(2)))

    def create_report_lines(self, invoices):
        if self._context.get("recreate", False):
            self.report_lines.unlink()
            self.txt = False

        CANTIDAD_REGISTRO = len(invoices)
        ITBIS_RETENIDO = 0
        ITBIS_TOTAL = 0
        TOTAL_MONTO_FACTURADO = 0
        RETENCION_RENTA = 0
        
        lines = []
        line_number = 0
        for inv in invoices:
            line_number += 1
            LINE = line_number
            
            LINE_TAX_COST = 0
            CURRENCY_RATE = 1

            RNC_CEDULA = ""
            TIPO_IDENTIFICACION = ""
            TIPO_BIENES_SERVICIOS_COMPRADOS = ""
            NUMERO_COMPROBANTE_FISCAL = ""
            NUMERO_COMPROBANTE_MODIFICADO = ""
            FECHA_COMPROBANTE = ""
            FECHA_PAGO = ""
            MONTO_SERVICIO = 0
            MONTO_BIENES = 0
            MONTO_FACTURADO = 0
            LINE_ITBIS_TOTAL = 0
            LINE_ITBIS_RETENIDO = 0
            ITBIS_PROPORCIONALIDAD = 0
            ITBIS_COSTO = 0
            ITBIS_ADELANTAR = 0
            ITBIS_PERCIBIDO = 0
            TIPO_RETENCION = ""
            LINE_RETENCION_RENTA = 0
            ISR_PERCIBIDO = 0
            IMPUESTO_SELECTIVO = 0
            OTROS_IMPUESTOS = 0
            PROPINA_LEGAL = ""
            MONTO_PAGO = 0

            if len(inv.reference.strip()) != 11:
                raise exceptions.UserError(u"El número de NCF {}! no es valido!".format(inv.reference))

            if not inv.partner_id.vat:
                raise exceptions.UserError(u"El número de RNC/Cédula del proveedor {} no es valido para el NCF {}".format(inv.partner_id.name, inv.number))

            if not inv.expense_type:
                raise exceptions.UserError(u"Debe de definir el tipo de gasto para la posición fiscal {}! en la factura {}".format(inv.fiscal_position_id.name, inv.number))

            cxp_move = [move_line for move_line in inv.move_id.line_ids if move_line.account_id.id == inv.account_id.id]
            impuestos = [impuestos for impuestos in inv.tax_line_ids]

            if cxp_move:
                if cxp_move[0].amount_currency:
                    CURRENCY_RATE = abs(cxp_move[0].credit+cxp_move[0].debit) / abs(cxp_move[0].amount_currency)

            for impuesto in impuestos:
                if impuesto.tax_id.purchase_tax_type == "itbis":
                    ITBIS_TOTAL += impuesto.amount * CURRENCY_RATE
                    LINE_ITBIS_TOTAL += impuesto.amount * CURRENCY_RATE
                    if impuesto.tax_id.servicios:
                        MONTO_SERVICIO += impuesto.base * CURRENCY_RATE
                    else:
                        MONTO_BIENES += impuesto.base * CURRENCY_RATE
                elif impuesto.tax_id.purchase_tax_type == "ritbis":
                    ITBIS_RETENIDO += abs(impuesto.amount) * CURRENCY_RATE
                    LINE_ITBIS_RETENIDO += abs(impuesto.amount) * CURRENCY_RATE
                elif impuesto.tax_id.purchase_tax_type == "isr":
                    RETENCION_RENTA += abs(impuesto.amount) * CURRENCY_RATE
                    LINE_RETENCION_RENTA += abs(impuesto.amount) * CURRENCY_RATE
                    TIPO_RETENCION = impuesto.tax_id.isr_retention_type
                elif impuesto.tax_id.purchase_tax_type == "cost":
                    ITBIS_COSTO += impuesto.amount * CURRENCY_RATE
                elif impuesto.tax_id.purchase_tax_type == "selectivo":
                    IMPUESTO_SELECTIVO += impuesto.amount * CURRENCY_RATE
                elif impuesto.tax_id.purchase_tax_type == "otros":
                    OTROS_IMPUESTOS += impuesto.amount * CURRENCY_RATE
                elif impuesto.tax_id.purchase_tax_type == "propina":
                    PROPINA_LEGAL += impuesto.amount * CURRENCY_RATE

            ITBIS_ADELANTAR = LINE_ITBIS_TOTAL-ITBIS_COSTO
            TOTAL_MONTO_FACTURADO += inv.amount_untaxed*CURRENCY_RATE
            MONTO_FACTURADO += inv.amount_untaxed*CURRENCY_RATE
            RNC_CEDULA = re.sub("[^0-9]", "", inv.partner_id.vat.strip())
            TIPO_BIENES_SERVICIOS_COMPRADOS = inv.expense_type
            NUMERO_COMPROBANTE_FISCAL = inv.reference.strip()
            FECHA_COMPROBANTE = inv.date_invoice
            TIPO_IDENTIFICACION = "1" if len(RNC_CEDULA.strip()) == 9 else "2"

            if MONTO_FACTURADO > (MONTO_BIENES + MONTO_SERVICIO):
                MONTO_BIENES += MONTO_FACTURADO - MONTO_BIENES - MONTO_SERVICIO

            if inv.type == "in_refund":
                NUMERO_COMPROBANTE_MODIFICADO = inv.origin_out

            if inv.payment_move_line_ids:
                FECHA_PAGO = max(inv.payment_move_line_ids).date  
            else:
                FECHA_PAGO = False

            #####COMO ENVIAR A LA DGII######
            #FORMA_PAGO = '01' (EFECTIVO)
            #FORMA_PAGO = '02' (CHEQUES/TRANSFERENCIAS/DEPÓSITO)
            #FORMA_PAGO = '03' (TARJETA CRÉDITO/DÉBITO)
            #FORMA_PAGO = '04' (COMPRA A CRÉDITO)
            #FORMA_PAGO = '05' (PERMUTA)
            #FORMA_PAGO = '06' (NOTAS DE CRÉDITO)
            #FORMA_PAGO = '07' (MIXTO)

            #####CREADO EN ODOO#####
            #inv.payment_ids.journal_id.payment_form
            #cash = (EFECTIVO)
            #bank = (CHEQUES/TRANSFERENCIAS/DEPÓSITO)
            #card = (TARJETA CRÉDITO/DÉBITO)
            #swap = (PERMUTA)
            #bond = (BONO)
            #other = (OTRA FORMA DE PAGO)

            FORMA_PAGO = "04"
            FORMA_PAGO_ODOO = "04"
            if inv.amount_total != inv.residual:
                if inv.residual == 0:
                    for pagos in inv.payment_ids:
                        if pagos.journal_id.payment_form == 'cash':
                            FORMA_PAGO_ODOO = '01'
                        elif pagos.journal_id.payment_form == 'bank':
                            FORMA_PAGO_ODOO = '02'
                        elif pagos.journal_id.payment_form == 'card':
                            FORMA_PAGO_ODOO = '03'
                        elif pagos.journal_id.payment_form == 'swap':
                            FORMA_PAGO_ODOO = '05'
                        else:
                            FORMA_PAGO_ODOO = '07'
                        MONTO_PAGO += pagos.amount
                        if FORMA_PAGO != FORMA_PAGO_ODOO and FORMA_PAGO != '04':
                            FORMA_PAGO = '07'
                        else:
                            FORMA_PAGO = FORMA_PAGO_ODOO
                else:
                    FORMA_PAGO = '07'

            if not FORMA_PAGO:
                raise exceptions.UserError(u"Falta la forma de pago en los diarios")            

            if MONTO_PAGO == 0 and inv.residual == 0:
                FORMA_PAGO = '06'

            lines.append((0,False,{"LINE":LINE,
                                   "RNC_CEDULA":RNC_CEDULA,
                                   "TIPO_IDENTIFICACION":TIPO_IDENTIFICACION,
                                   "TIPO_BIENES_SERVICIOS_COMPRADOS":TIPO_BIENES_SERVICIOS_COMPRADOS,
                                   "NUMERO_COMPROBANTE_FISCAL":NUMERO_COMPROBANTE_FISCAL,
                                   "NUMERO_COMPROBANTE_MODIFICADO":NUMERO_COMPROBANTE_MODIFICADO,
                                   "FECHA_COMPROBANTE":FECHA_COMPROBANTE,
                                   "FECHA_PAGO":FECHA_PAGO,
                                   "MONTO_SERVICIO":MONTO_SERVICIO,
                                   "MONTO_BIENES":MONTO_BIENES,
                                   "MONTO_FACTURADO":MONTO_FACTURADO,
                                   "ITBIS_FACTURADO":LINE_ITBIS_TOTAL,
                                   "ITBIS_RETENIDO":LINE_ITBIS_RETENIDO,
                                   "ITBIS_PROPORCIONALIDAD":ITBIS_PROPORCIONALIDAD,
                                   "ITBIS_COSTO":ITBIS_COSTO,
                                   "ITBIS_ADELANTAR":ITBIS_ADELANTAR,
                                   "ITBIS_PERCIBIDO":ITBIS_PERCIBIDO,
                                   "TIPO_RETENCION":TIPO_RETENCION,
                                   "RETENCION_RENTA":LINE_RETENCION_RENTA,
                                   "ISR_PERCIBIDO":ISR_PERCIBIDO,
                                   "IMPUESTO_SELECTIVO":IMPUESTO_SELECTIVO,
                                   "OTROS_IMPUESTOS":OTROS_IMPUESTOS,
                                   "PROPINA_LEGAL":PROPINA_LEGAL,
                                   "FORMA_PAGO":FORMA_PAGO,
                                   }))


        self.write({"report_lines":lines,
                    "CANTIDAD_REGISTRO":CANTIDAD_REGISTRO,
                    "ITBIS_RETENIDO":ITBIS_RETENIDO,
                    "ITBIS_TOTAL":ITBIS_TOTAL,
                    "TOTAL_MONTO_FACTURADO":TOTAL_MONTO_FACTURADO,
                    "RETENCION_RENTA":RETENCION_RENTA,
                    "state":"done"})

    def generate_txt(self):

        if not self.company_id.vat:
            raise exceptions.ValidationError(u"Para poder generar el 606 primero debe especificar el RNC/Cédula de la compañia.")

        company_fiscal_identificacion = re.sub("[^0-9]", "", self.company_id.vat)

        # if not company_fiscal_identificacion or not self.env['marcos.api.tools'].is_identification(company_fiscal_identificacion):
        #     raise exceptions.ValidationError("Debe de configurar el RNC de su empresa!")

        path = '/tmp/606{}.txt'.format(company_fiscal_identificacion)
        file = open(path,'w')
        lines = []

        header = "606" + "|"
        header += company_fiscal_identificacion + "|"
        header += str(self.year)
        header += str(self.month).zfill(2) + "|"
        header += "{}".format(self.CANTIDAD_REGISTRO)
        lines.append(header)

        for line in self.report_lines:
            fecha_comprobante_str = datetime.strftime(line.FECHA_COMPROBANTE, '%Y%m%d')
            if line.FECHA_PAGO:
                fecha_pago_str = datetime.strftime(line.FECHA_PAGO, '%Y%m%d')
            else:
                fecha_pago_str = ""

            ln = ""
            ln += line.RNC_CEDULA + "|" 
            ln += line.TIPO_IDENTIFICACION + "|"
            ln += line.TIPO_BIENES_SERVICIOS_COMPRADOS + "|"
            ln += line.NUMERO_COMPROBANTE_FISCAL + "|"
            ln += line.NUMERO_COMPROBANTE_MODIFICADO + "|"
            ln += fecha_comprobante_str + "|"
            ln += fecha_pago_str + "|"
            ln += "{:.2f}".format(line.MONTO_SERVICIO) + "|"
            ln += "{:.2f}".format(line.MONTO_BIENES) + "|"
            ln += "{:.2f}".format(line.MONTO_FACTURADO) + "|"
            ln += "{:.2f}".format(line.ITBIS_FACTURADO) + "|"
            ln += "{:.2f}".format(line.ITBIS_RETENIDO) + "|"
            ln += "{:.2f}".format(line.ITBIS_PROPORCIONALIDAD) + "|"
            ln += "{:.2f}".format(line.ITBIS_COSTO) + "|"
            ln += "{:.2f}".format(line.ITBIS_ADELANTAR) + "|"
            ln += "{:.2f}".format(line.ITBIS_PERCIBIDO) + "|"
            ln += line.TIPO_RETENCION + "|"
            ln += "{:.2f}".format(line.RETENCION_RENTA) + "|"
            ln += "{:.2f}".format(line.ISR_PERCIBIDO) + "|"
            ln += "{:.2f}".format(line.IMPUESTO_SELECTIVO) + "|"
            ln += "{:.2f}".format(line.OTROS_IMPUESTOS) + "|"
            ln += "{:.2f}".format(line.PROPINA_LEGAL) + "|"
            ln += line.FORMA_PAGO
            ln = ln.replace("|0.00", "|")
            lines.append(ln)

        for line in lines:
            file.write(line+"\n")

        file.close()
        file = open(path,'rb')
        report = base64.b64encode(file.read())
        report_name = 'DGII_606_{}_{}{}.TXT'.format(company_fiscal_identificacion, str(self.year), str(self.month).zfill(2))
        self.write({'txt': report, 'txt_filename': report_name})

    @api.multi
    def create_report(self):
        start_date, end_date = self.get_date_range()

        invoices = self.env["account.invoice"].search([('date_invoice','>=',start_date),
                                                       ('date_invoice','<=',end_date),
                                                       ('state','in',('open','paid')),
                                                       ('journal_id.purchase_type','in',('normal','minor','informal')),
                                                       ('type','in',('in_invoice','in_refund'))])

        invoice_ids = [rec.id for rec in invoices]
        invoice_ids = list(set(invoice_ids))
        invoices = self.env["account.invoice"].browse(invoice_ids)
        self.create_report_lines(invoices)
        self.generate_txt()
        return True

class DgiiPurchaseReportlinePlus(models.Model):
    _name = "dgii.purchase.report.line.plus"

    LINE = fields.Integer("Linea")
    RNC_CEDULA = fields.Char(u"RNC", size=11)
    TIPO_IDENTIFICACION= fields.Char("Tipo ID", size=1)
    TIPO_BIENES_SERVICIOS_COMPRADOS = fields.Char("Tipo", size=2)
    NUMERO_COMPROBANTE_FISCAL = fields.Char("NCF", size=19)
    NUMERO_COMPROBANTE_MODIFICADO = fields.Char("Afecta", size=19)
    FECHA_COMPROBANTE = fields.Date("Fecha")
    FECHA_PAGO = fields.Date("Fecha Pago")
    MONTO_SERVICIO = fields.Float(u"Monto Servicios")
    MONTO_BIENES = fields.Float(u"Monto Bienes")
    MONTO_FACTURADO = fields.Float("Monto Facturado")
    ITBIS_FACTURADO = fields.Float("ITBIS Facturado")
    ITBIS_RETENIDO = fields.Float("ITBIS Retenido")
    ITBIS_PROPORCIONALIDAD = fields.Float(u"ITBIS Sujeto a Proporcionalidad")
    ITBIS_COSTO = fields.Float(u"ITBIS llevado al costo")
    ITBIS_ADELANTAR = fields.Float(u"ITBIS por adelantar")
    ITBIS_PERCIBIDO = fields.Float(u"ITBIS percibido en compras")
    TIPO_RETENCION = fields.Char(u"Tipo retención en ISR", size=2)
    RETENCION_RENTA = fields.Float(u"Retención Renta")
    ISR_PERCIBIDO = fields.Float(u"ISR percibido en compras")
    IMPUESTO_SELECTIVO = fields.Float(u"Impuesto Selectivo al consumo")
    OTROS_IMPUESTOS = fields.Float(u"Otros Impuestos")
    PROPINA_LEGAL = fields.Float(u"Monto Propina Legal")
    FORMA_PAGO = fields.Char(u"Forma de pago", size=2)
    purchase_report_id = fields.Many2one("dgii.purchase.report.plus")
