  # -*- coding: utf-8 -*-
########################################################################################################################
#  Adaptacion de MERPLUS para nos nuevos formato NCF con la guia de:
#  Copyright (c) 2015 - Marcos Organizador de Negocios SRL. (<https://marcos.do/>) 
#  Write by Eneldo Serrata (eneldo@marcos.do)
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

class DgiiSaleReportPlus(models.Model):
    _name = "dgii.sale.report.plus"

    @api.one
    @api.depends("ITBIS_TOTAL","TOTAL_MONTO_FACTURADO")
    def _calc_total(self):

        self.TOTAL_MONTO_FACTURAS = sum([line.MONTO_FACTURADO for line in self.report_lines if not line.NUMERO_COMPROBANTE_MODIFICADO.strip()])
        self.TOTAL_MONTO_NC = sum([line.MONTO_FACTURADO for line in self.report_lines if line.NUMERO_COMPROBANTE_MODIFICADO.strip()])
        self.ITBIS_TOTAL_FACTURAS = sum([line.ITBIS_FACTURADO for line in self.report_lines if not line.NUMERO_COMPROBANTE_MODIFICADO.strip()])
        self.ITBIS_TOTAL_NC = sum([line.ITBIS_FACTURADO for line in self.report_lines if line.NUMERO_COMPROBANTE_MODIFICADO.strip()])
        self.TOTAL_VENTA = self.TOTAL_MONTO_FACTURAS-self.TOTAL_MONTO_NC
        self.TOTAL_VENTA_ITBIS = self.ITBIS_TOTAL_FACTURAS-self.ITBIS_TOTAL_NC

    def get_default_period(self):
        self.year = int(time.strftime("%Y"))


    company_id = fields.Many2one('res.company', string='Company', required=True,
        default=lambda self: self.env['res.company']._company_default_get('dgii.sale.report'))
    name = fields.Char("Nombre")
    year = fields.Integer(u"Año", size=4, default=lambda s: int(time.strftime("%Y")))
    month = fields.Integer(u"Mes", size=2, default=lambda s: int(time.strftime("%m")))
    CANTIDAD_REGISTRO = fields.Integer(u"Cantidad de registros")
    ITBIS_TOTAL = fields.Float(u"OFV ITBIS")
    TOTAL_MONTO_FACTURADO = fields.Float(u"OFV FACTURADO", help=u"Suma de las facturas y las notas de crédito como se digitan en el formulario de la DGII")

    TOTAL_MONTO_FACTURAS = fields.Float(u"FACTURADO", compute=_calc_total)
    TOTAL_MONTO_NC = fields.Float(u"NOTAS CRÉDITO", compute=_calc_total)
    ITBIS_TOTAL_FACTURAS = fields.Float(u"ITBIS FACTURADO", compute=_calc_total)
    ITBIS_TOTAL_NC = fields.Float(u"ITBIS NOTAS CRÉDITO", compute=_calc_total)
    TOTAL_VENTA = fields.Float(u"VENTA", compute=_calc_total)
    TOTAL_VENTA_ITBIS = fields.Float(u"ITBIS", compute=_calc_total)

    report_lines = fields.One2many("dgii.sale.report.line.plus", "sale_report_id")
    txt = fields.Binary(u"Reporte TXT", readonly=True)
    txt_name = fields.Char("Nombre del archivo", readonly=True)
    state = fields.Selection([('draft','Nuevo'),('done','Generado')], default="draft")

    @api.model
    def create(self, vals):
        vals.update({"name": "{}/{}".format(vals["month"],vals["year"])})
        self = super(DgiiSaleReportPlus, self).create(vals)
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
            
        lines = []
        line_number = 0
        for inv in invoices:
            #SI ES DE CONSUMO Y MONTO FACTURADO ES MENOR A $250,000 NO SERA PRESENTADO
            if inv.sale_fiscal_type == "final" and inv.amount_untaxed < 250000:
                continue

            line_number += 1
            LINE = line_number

            RNC_CEDULA = ""
            TIPO_IDENTIFICACION = ""
            NUMERO_COMPROBANTE_FISCAL = ""
            NUMERO_COMPROBANTE_MODIFICADO = ""
            TIPO_INGRESO = "01"
            FECHA_RETENCION = False
            MONTO_FACTURADO = 0
            ITBIS_FACTURADO = 0
            ITBIS_RETENIDO = 0
            ITBIS_PERCIBIDO = 0
            ISR_RETENIDO = 0
            ISR_PERCIBIDO = 0
            IMPUESTO_SELECTIVO = 0
            OTROS_IMPUESTOS = 0
            PROPINA_LEGAL = 0
            EFECTIVO = 0
            CK_TRAN_DEP = 0
            TARJETA = 0
            VENTA_CREDITO = 0
            BONOS = 0
            PERMUTA = 0
            OTRAS_VENTAS = 0

            if inv.partner_id.vat:
            	RNC_CEDULA = re.sub("[^0-9]", "", inv.partner_id.vat.strip())
            else:
                raise exceptions.UserError(u"El RNC / Cédula de la factura {}! no es valido!".format(inv.number))
            	
            TIPO_IDENTIFICACION = "1" if len(str(RNC_CEDULA).strip()) == 9 else "2"

            if len(inv.reference) != 11:
                raise exceptions.UserError(u"El número de NCF {}! no es valido!".format(inv.reference))

            # if not self.env['marcos.api.tools'].is_ncf(inv.number, inv.type):
            #     raise exceptions.ValidationError(u"El número de NCF o el RNC/Cédula del clienten para el comprobante {} no es valido!".format(inv.number))

            NUMERO_COMPROBANTE_FISCAL = inv.reference.strip()
            if inv.type == "out_refund":
                NUMERO_COMPROBANTE_MODIFICADO = inv.origin_out.strip()

            #FECHA = inv.date_invoice.split('-')
            #FECHA_COMPROBANTE = FECHA[2] + FECHA[1] + FECHA[0]
            FECHA_COMPROBANTE = inv.date_invoice
            MONTO_FACTURADO = inv.amount_untaxed
            VENTA_CREDITO = inv.residual
            TIPO_INGRESO = inv.income_type
 
            #TIPOS DE IMPUESTOS
            for impuesto in inv.tax_line_ids:
                if impuesto.tax_id.sale_tax_type == "itbis":
                    ITBIS_FACTURADO += impuesto.amount
                if impuesto.tax_id.sale_tax_type == "selectivo":
                    IMPUESTO_SELECTIVO += impuesto.amount
                if impuesto.tax_id.sale_tax_type == "otros":
                    OTROS_IMPUESTOS += impuesto.amount
                if impuesto.tax_id.sale_tax_type == "propina":
                    PROPINA_LEGAL += impuesto.amount

            # PAGOS RECIBIDOS via contabilidad
            for pagos_cont in inv.payment_move_line_ids:
                if inv.account_id == pagos_cont.account_id:
                    pagos_monto = pagos_cont.credit
                    pagos_monto -= pagos_cont.debit
                    PAGADO = inv.amount_total - inv.residual
                    if pagos_monto > PAGADO:
                    	pagos_monto = PAGADO
                    if pagos_cont.journal_id.payment_form == 'cash':
                        EFECTIVO += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'bank':
                        CK_TRAN_DEP += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'card':
                        TARJETA += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'swap':
                        PERMUTA += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'bond':
                        BONOS += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'other':
                        OTRAS_VENTAS += pagos_monto
                    if pagos_cont.journal_id.payment_form == 'ritbis':
                        ITBIS_RETENIDO += pagos_monto
                        FECHA_RETENCION = pagos_cont.date
                    if pagos_cont.journal_id.payment_form == 'isr':
                        ISR_RETENIDO += pagos_monto
                        FECHA_RETENCION = pagos_cont.date

            #CUANDO HAY UN PAGO PARA VARIAS FACTURAS RECALCULAMOS
            PAGADO = inv.amount_total - inv.residual
            PAGOS_INDIVIDUALES = EFECTIVO + PERMUTA + BONOS + OTRAS_VENTAS + ITBIS_RETENIDO + ISR_RETENIDO
            PAGO_CALCULADO = CK_TRAN_DEP + TARJETA + PAGOS_INDIVIDUALES

            if PAGO_CALCULADO > PAGADO:
                if CK_TRAN_DEP > TARJETA:
                    CK_TRAN_DEP = PAGADO - PAGOS_INDIVIDUALES - TARJETA
                else:
                    TARJETA = PAGADO - PAGOS_INDIVIDUALES - CK_TRAN_DEP

            lines.append((0,False,{"LINE":LINE,
                                   "RNC_CEDULA":RNC_CEDULA,
                                   "TIPO_IDENTIFICACION":TIPO_IDENTIFICACION,
                                   "NUMERO_COMPROBANTE_FISCAL":NUMERO_COMPROBANTE_FISCAL,
                                   "NUMERO_COMPROBANTE_MODIFICADO":NUMERO_COMPROBANTE_MODIFICADO,
                                   "TIPO_INGRESO":TIPO_INGRESO,
                                   "FECHA_COMPROBANTE":FECHA_COMPROBANTE,
                                   "FECHA_RETENCION":FECHA_RETENCION,
                                   "MONTO_FACTURADO":MONTO_FACTURADO,
                                   "ITBIS_FACTURADO":ITBIS_FACTURADO,
                                   "ITBIS_RETENIDO":ITBIS_RETENIDO,
                                   "ITBIS_PERCIBIDO":ITBIS_PERCIBIDO,
                                   "ISR_RETENIDO":ISR_RETENIDO,
                                   "ISR_PERCIBIDO":ISR_PERCIBIDO,
                                   "IMPUESTO_SELECTIVO":IMPUESTO_SELECTIVO,
                                   "OTROS_IMPUESTOS":OTROS_IMPUESTOS,
                                   "PROPINA_LEGAL":PROPINA_LEGAL,
                                   "EFECTIVO":EFECTIVO,
                                   "CK_TRAN_DEP":CK_TRAN_DEP,
                                   "TARJETA":TARJETA,
                                   "VENTA_CREDITO":VENTA_CREDITO,
                                   "BONOS":BONOS,
                                   "PERMUTA":PERMUTA,
                                   "OTRAS_VENTAS":OTRAS_VENTAS
                                   }))


        CANTIDAD_REGISTRO = len(lines)
        ITBIS_TOTAL = sum([line[2]["ITBIS_FACTURADO"] for line in lines])
        TOTAL_MONTO_FACTURADO = sum([line[2]["MONTO_FACTURADO"] for line in lines])

        res = self.write({"report_lines": lines,
                           "CANTIDAD_REGISTRO": CANTIDAD_REGISTRO,
                           "ITBIS_TOTAL": ITBIS_TOTAL,
                           "TOTAL_MONTO_FACTURADO": TOTAL_MONTO_FACTURADO,
                           "state": "done"})
        return res

    def generate_txt(self):

        company_fiscal_identificacion = re.sub("[^0-9]", "", self.company_id.vat)

        # if not company_fiscal_identificacion or not self.env['marcos.api.tools'].is_identification(company_fiscal_identificacion):
        #     raise exceptions.ValidationError("Debe de configurar el RNC de su empresa!")

        path = '/tmp/607{}.txt'.format(company_fiscal_identificacion)
        file = open(path,'w')
        lines = []

        header = "607" + "|"
        header += company_fiscal_identificacion + "|"
        header += str(self.year)
        header += str(self.month).zfill(2) + "|"
        header += str(self.CANTIDAD_REGISTRO)
        lines.append(header)

        for line in self.report_lines:
            fecha_comprobante_str = datetime.strftime(line.FECHA_COMPROBANTE, '%Y%m%d')
            if line.FECHA_RETENCION:
                fecha_retencion_str = datetime.strftime(line.FECHA_RETENCION, '%Y%m%d')
            else:
                fecha_retencion_str = ""

            ln = ""
            ln += line.RNC_CEDULA + "|"
            ln += line.TIPO_IDENTIFICACION + "|"
            ln += line.NUMERO_COMPROBANTE_FISCAL + "|"
            ln += line.NUMERO_COMPROBANTE_MODIFICADO + "|"
            ln += line.TIPO_INGRESO + "|"
            ln += fecha_comprobante_str + "|"
            ln += fecha_retencion_str + "|"
            ln += "{:.2f}".format(line.MONTO_FACTURADO) + "|"
            ln += "{:.2f}".format(line.ITBIS_FACTURADO) + "|"
            ln += "{:.2f}".format(line.ITBIS_RETENIDO) + "|"
            ln += "{:.2f}".format(line.ITBIS_PERCIBIDO) + "|"
            ln += "{:.2f}".format(line.ISR_RETENIDO) + "|"
            ln += "{:.2f}".format(line.ISR_PERCIBIDO) + "|"
            ln += "{:.2f}".format(line.IMPUESTO_SELECTIVO) + "|"
            ln += "{:.2f}".format(line.OTROS_IMPUESTOS) + "|"
            ln += "{:.2f}".format(line.PROPINA_LEGAL) + "|"
            ln += "{:.2f}".format(line.EFECTIVO) + "|"
            ln += "{:.2f}".format(line.CK_TRAN_DEP) + "|"
            ln += "{:.2f}".format(line.TARJETA) + "|"
            ln += "{:.2f}".format(line.VENTA_CREDITO) + "|"
            ln += "{:.2f}".format(line.BONOS) + "|"
            ln += "{:.2f}".format(line.PERMUTA) + "|"
            ln += "{:.2f}".format(line.OTRAS_VENTAS)
            ln = ln.replace("|0.00","|")
            lines.append(ln)

        for line in lines:
            file.write(line+"\n")

        file.close()
        file = open(path,'rb')
        report = base64.b64encode(file.read())
        # report_name = 'DGII_607_{}_{}{}.TXT'.format(company_fiscal_identificacion, str(self.year), str(self.month).zfill(2))
        report_name = 'DGII_607_{}.TXT'.format(company_fiscal_identificacion)
        self.write({'txt': report, 'txt_name': report_name})

    @api.multi
    def create_report(self):
        start_date, end_date = self.get_date_range()
        invoices = self.env["account.invoice"].search([('date_invoice','>=',start_date),
                                                       ('date_invoice','<=',end_date),
                                                       ('state','in',('open','paid')),
                                                       ('journal_id.ncf_control','=',True),
                                                       ('type','in',('out_invoice','out_refund'))])
        self.create_report_lines(invoices)
        self.generate_txt()
        return True


class DgiiSaleReportlinePlus(models.Model):
    _name = "dgii.sale.report.line.plus"

    TIPO_INGRESO = fields.Char("Tipo de ingreso", size=2)
    FECHA_RETENCION = fields.Date(u"Fecha de Retención")
    ITBIS_RETENIDO = fields.Float("ITBIS Retenido por terceros")
    ITBIS_PERCIBIDO = fields.Float("ITBIS Percibido")
    ISR_RETENIDO = fields.Float("Retención de Renta por Terceros")
    ISR_PERCIBIDO = fields.Float("ISR Percibido")
    IMPUESTO_SELECTIVO = fields.Float("Impuesto Selectivo al Consumo")
    OTROS_IMPUESTOS =fields.Float("Otros Impuestos o Tasas")
    PROPINA_LEGAL = fields.Float("Monto Propina Legal")
    EFECTIVO =fields.Float("Efectivo")
    CK_TRAN_DEP = fields.Float(u"Cheque/ Transferencia/ Depósito")
    TARJETA = fields.Float(u"Tarjeta Débito/ Crédito")
    VENTA_CREDITO = fields.Float(u"Venta a Crédito")
    BONOS = fields.Float(u"Bonos o Certificados de Regalo")
    PERMUTA = fields.Float("Permuta")
    OTRAS_VENTAS = fields.Float(u"Otras Formas de Ventas")
    sale_report_id = fields.Many2one("dgii.sale.report.plus")
    LINE = fields.Integer("Linea")
    RNC_CEDULA = fields.Char(u"RNC", size=11)
    TIPO_IDENTIFICACION= fields.Char("Tipo ID", size=1)
    NUMERO_COMPROBANTE_FISCAL = fields.Char("NCF", size=19)
    NUMERO_COMPROBANTE_MODIFICADO = fields.Char("Afecta", size=19)
    FECHA_COMPROBANTE = fields.Date("Fecha")
    FECHA_PAGO = fields.Date("Pagado")
    ITBIS_FACTURADO = fields.Float("ITBIS Facturado")
    MONTO_FACTURADO = fields.Float("Monto Facturado")




