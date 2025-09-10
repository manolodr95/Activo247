# © 2024 ISJO TECHNOLOGY, SRL (Daniel Diaz <daniel.diaz@isjo-technology.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime as dt


class AccountInvoice(models.Model):
    _inherit = "account.move"

    def _get_invoice_payment_widget(self):
        return self.invoice_payments_widget.get('content', []) if self.invoice_payments_widget else []

    @api.depends('payment_state', 'invoice_date', 'invoice_payments_widget')
    def _compute_invoice_payment_date(self):
        for inv in self:
            payment_date = False
            if (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):
                dates = [
                    payment['date'] for payment in inv._get_invoice_payment_widget()
                ]

                if dates:
                    max_date = max(dates)
                    invoice_date = inv.invoice_date
                    payment_date = max_date if max_date >= invoice_date \
                        else invoice_date
            inv.payment_date = payment_date

    @api.depends('line_ids.tax_ids')
    def _check_isr_tax(self):
        """Restrict one ISR tax per invoice"""
        for inv in self:
            line = [
                tax_line.tax_line_id.l10n_do_tax_type
                for tax_line in inv._get_tax_line_ids()
                if tax_line.tax_line_id.l10n_do_tax_type in ['isr', 'ritbis']
            ]
            if len(line) != len(set(line)):
                raise ValidationError(
                    _('An invoice cannot have multiple' 'withholding taxes.')
                )

    def _convert_to_local_currency(self, amount):
        sign = -1 if self.move_type in ['in_refund', 'out_refund'] else 1
        if self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date)
            round_curr = currency_id.round
            amount = round_curr(currency_id._convert(
                amount, self.company_id.currency_id, self.company_id, self.date))

        return amount * sign

    def _get_tax_line_ids(self):
        return self.line_ids.filtered(lambda l: l.tax_line_id)

    @api.depends("invoice_line_ids", "date", "invoice_line_ids.product_id", "state", "invoice_line_ids.price_subtotal")
    def _compute_amount_fields(self):
        """Compute Purchase amount by product type"""
        for inv in self:
            service_amount = 0
            good_amount = 0

            if inv.date:
                for line in inv.invoice_line_ids:
                    if not line.product_id:
                        service_amount += line.price_subtotal

                    elif line.product_id.type in ['product', 'consu']:
                        good_amount += line.price_subtotal

                    else:
                        service_amount += line.price_subtotal

                service_amount = inv._convert_to_local_currency(service_amount)
                good_amount = inv._convert_to_local_currency(good_amount)

            inv.service_total_amount = abs(service_amount)
            inv.good_total_amount = abs(good_amount)

    @api.depends('payment_state', 'invoice_line_ids', 'invoice_line_ids.product_id')
    def _compute_isr_withholding_type(self):
        """Compute ISR Withholding Type

        Keyword / Values:
        01 -- Alquileres
        02 -- Honorarios por Servicios
        03 -- Otras Rentas
        04 -- Rentas Presuntas
        05 -- Intereses Pagados a Personas Jurídicas
        06 -- Intereses Pagados a Personas Físicas
        07 -- Retención por Proveedores del Estado
        08 -- Juegos Telefónicos
        """
        for inv in self:
            if (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):
                isr = [
                    tax_line.tax_line_id
                    for tax_line in inv._get_tax_line_ids()
                    if tax_line.tax_line_id.l10n_do_tax_type == 'isr'
                ]
                if isr:
                    inv.isr_withholding_type = isr.pop(0).isr_retention_type

    def _get_payment_string(self):
        """Compute Vendor Bills payment method string

        Keyword / Values:
        cash        -- Efectivo
        bank        -- Cheques / Transferencias / Depósitos
        card        -- Tarjeta Crédito / Débito
        credit      -- Compra a Crédito
        swap        -- Permuta
        credit_note -- Notas de Crédito
        mixed       -- Mixto
        """
        payments = []
        p_string = ""

        for payment in self._get_invoice_payment_widget():
            payment_id = self.env["account.payment"].browse(
                payment.get("account_payment_id")
            )
            move_id = False
            if payment_id:
                if payment_id.journal_id.type in ["cash", "bank"]:
                    p_string = payment_id.journal_id.payment_form

            if not payment_id:
                move_id = self.env["account.move"].browse(payment.get("move_id"))
                if move_id:
                    p_string = "swap"

            # If invoice is paid, but the payment doesn't come from
            # a journal, assume it is a credit note
            payment = p_string if payment_id or move_id else "credit_note"
            payments.append(payment)

        methods = {p for p in payments}
        if len(methods) == 1:
            return list(methods)[0]
        elif len(methods) > 1:
            return "mixed"

    @api.depends("payment_state")
    def _compute_in_invoice_payment_form(self):
        for inv in self:
            if (
                inv.move_type == "in_invoice"
                and inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual == 0
            ):
                payment_dict = {
                    "cash": "01",
                    "bank": "02",
                    "card": "03",
                    "credit": "04",
                    "swap": "05",
                    "credit_note": "06",
                    "mixed": "07",
                }

                inv.payment_form = payment_dict.get(inv._get_payment_string())

            elif (
                inv.payment_state not in ["reversed", "invoicing_legacy"]
                and inv.amount_residual != 0
                and inv.payment_state != "not_paid"
            ):
                inv.payment_form = "07"

            else:
                inv.payment_form = "04"

    def _get_payment_move_iterator(self, inv, witheld_type):
        if inv.move_type == "out_invoice":

            for payment in inv._get_invoice_payment_widget():
                pay = self.env["account.move"].browse(payment.get("move_id"))

            return [
                move_line.debit
                for move_line in pay.line_ids
                if move_line.account_id.account_fiscal_type in witheld_type
            ]
        else:
            return [
                move_line.credit
                for move_line in inv.line_ids
                if move_line.account_id.account_fiscal_type in witheld_type
            ]

    @api.depends('state',
                 'payment_state',
                 'line_ids',
                 'line_ids.balance',
                 'line_ids.tax_line_id')
    def _compute_withheld_taxes(self):

        for inv in self:
            tax_line_ids = inv._get_tax_line_ids()

            inv.withholded_itbis = 0
            inv.income_withholding = 0
            inv.third_withheld_itbis = 0
            inv.third_income_withholding = 0
            witheld_itbis_types = ["A34", "A36"]
            witheld_isr_types = ["ISR", "A38"]

            if inv.payment_state not in ('reversed', 'invoicing_legacy') and tax_line_ids and inv.amount_residual == 0:

                inv.withholded_itbis = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'ritbis').mapped('balance')
                ))

                inv.income_withholding = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'isr').mapped('balance')
                ))

                inv.third_withheld_itbis = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'ritbis').mapped('balance')
                ))

                inv.third_income_withholding = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'isr').mapped('balance')
                ))

                if inv.move_type == "out_invoice":
                    # ITBIS Retenido por Terceros
                    inv.third_withheld_itbis += sum(
                        self._get_payment_move_iterator(inv, witheld_itbis_types)
                    )

                    # Retención de Renta pr Terceros
                    inv.third_income_withholding += sum(
                        self._get_payment_move_iterator(inv, witheld_isr_types)
                    )
                elif inv.move_type == "in_invoice":
                    # ITBIS Retenido a Terceros
                    inv.withholded_itbis += sum(
                        self._get_payment_move_iterator(inv, witheld_itbis_types)
                    )

                    # Retención de Renta a Terceros
                    inv.income_withholding += sum(
                        self._get_payment_move_iterator(inv, witheld_isr_types)
                    )

    @api.depends("invoiced_itbis", "cost_itbis", "state")
    def _compute_advance_itbis(self):
        for inv in self:
            inv.advance_itbis = inv.invoiced_itbis - inv.cost_itbis

    payment_date = fields.Date(compute="_compute_invoice_payment_date", store=True)
    service_total_amount = fields.Monetary(
        compute="_compute_amount_fields",
        store=True,
        currency_field="company_currency_id",
    )
    good_total_amount = fields.Monetary(
        compute="_compute_amount_fields",
        store=True,
        currency_field="company_currency_id",
    )
    invoiced_itbis = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    withholded_itbis = fields.Monetary(
        compute="_compute_withheld_taxes",
        store=True,
        currency_field="company_currency_id",
    )
    proportionality_tax = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    cost_itbis = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    advance_itbis = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    isr_withholding_type = fields.Char(
        compute="_compute_isr_withholding_type", store=True, size=2
    )
    income_withholding = fields.Monetary(
        compute="_compute_withheld_taxes",
        store=True,
        currency_field="company_currency_id",
    )
    selective_tax = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    other_taxes = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    legal_tip = fields.Monetary(
        compute="_compute_taxes_fields",
        store=True,
        currency_field="company_currency_id",
    )
    l10n_do_payment_form = fields.Selection(
        selection=[
            ("01", "Cash"),
            ("02", "Check / Transfer / Deposit"),
            ("03", "Credit Card / Debit Card"),
            ("04", "Credit"),
            ("05", "Swap"),
            ("06", "Credit Note"),
            ("07", "Mixed"),
            ("08", "Other")
        ],
        compute_sudo=True,
        compute="_compute_in_invoice_payment_form",
        store=True,
    )
    third_withheld_itbis = fields.Monetary(
        compute="_compute_withheld_taxes",
        store=True,
        currency_field="company_currency_id",
    )
    third_income_withholding = fields.Monetary(
        compute="_compute_withheld_taxes",
        store=True,
        currency_field="company_currency_id",
    )

    fiscal_status = fields.Selection(
        selection=[("normal", "Partial"), ("done", "Reported"),
                   ("blocked", "Not Sent")],
        copy=False,
        help="* The 'Grey' status means ...\n"
        "* The 'Green' status means ...\n"
        "* The 'Red' status means ...\n"
        "* The blank status means that the invoice have"
        "not been included in a report.",
    )

    @api.model
    def norma_recompute(self):
        """
        This method add all compute fields into []env
        add_todo and then recompute
        all compute fields in case dgii config change and need to recompute.
        :return:
        """

        active_ids = self._context.get("active_ids")
        invoice_ids = self.browse(active_ids)
        for k, v in self.fields_get().items():
            if v.get("store") and v.get("depends"):
                out_fields = ['attachment_ids',
                              'invoice_line_ids', 'date', 'invoice_user_id']
                if k in out_fields:
                    continue
                self.env.add_to_compute(self._fields[k], invoice_ids)

        self.env._recompute_all()
        self._recompute_model(None)

    @api.depends("line_ids.tax_ids", "payment_state", "state", "line_ids")
    def _compute_taxes_fields(self):
        """Compute invoice common taxes fields"""

        for inv in self:

            inv.invoiced_itbis = 0
            inv.selective_tax = 0
            inv.other_taxes = 0
            inv.legal_tip = 0
            inv.advance_itbis = 0

            inv.cost_itbis = 0
            inv.proportionality_tax = 0

            tax_line_ids = inv._get_tax_line_ids()

            if tax_line_ids:

                # Taxes
                inv.invoiced_itbis = abs(sum(tax_line_ids.filtered(
                    lambda tax: tax.tax_line_id.l10n_do_tax_type in ['itbis', 'itbis_cost', 'prop']).mapped('balance')
                ))
                inv.selective_tax = abs(sum(tax_line_ids.filtered(
                    lambda tax: tax.tax_line_id.l10n_do_tax_type == 'isc').mapped('balance')
                ))
                inv.other_taxes = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'other').mapped('balance')
                ))
                inv.legal_tip = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'tip').mapped('balance')
                ))
                inv.cost_itbis = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'itbis_cost').mapped('balance')
                ))
                inv.proportionality_tax = abs(sum(
                    tax_line_ids.filtered(
                        lambda tax: tax.tax_line_id.l10n_do_tax_type == 'prop').mapped('balance')
                ))
                inv.advance_itbis = inv.invoiced_itbis - inv.cost_itbis
