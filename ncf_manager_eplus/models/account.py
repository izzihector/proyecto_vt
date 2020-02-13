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

from odoo import models, fields, api
from odoo.exceptions import ValidationError

class AccountJournal(models.Model):
    _inherit = "account.journal"

    payment_form = fields.Selection([("cash", u"Efectivo"),
                                     ("bank", u"Cheques/Transferencias/ Depósitos"),
                                     ("card", u"Tarjeta Crédito/Débido"),
                                     ("swap", u"Permuta"), 
                                     ("bond", u"Bono o Certificado de Regalo"),
                                     ("other", u"Otras Forma de Venta"),
                                     ("ritbis", u"Itbis Retenido por Tercero"),
                                     ("isr", u"Retención de Renta por Tercero")],
                                    string=u"Forma de Pago")


class AccountTaxPlus(models.Model):
    _inherit = 'account.tax'

    sale_tax_type = fields.Selection([("itbis", u"ITBIS Pagado"),
                                      ("selectivo", u"Selectivo al consumo"),
                                      ("otros", u"Otros impuestos/Tasa"),
                                      ("propina", u"Monto propina legal")],
                                      default="itbis", string="Tipo de impuesto ventas")

    #MERPLUS nuevo NCF
    servicios = fields.Boolean(string="ITBIS para servicios") 