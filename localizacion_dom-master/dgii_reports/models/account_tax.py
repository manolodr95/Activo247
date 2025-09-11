# © 2024 ISJO TECHNOLOGY, SRL (Daniel Diaz <daniel.diaz@isjo-technology.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class AccountTax(models.Model):
    _inherit = 'account.tax'

    @api.model
    def _get_isr_retention_type(self):
        return [('01', 'Alquileres'),
                ('02', 'Honorarios por Servicios'),
                ('03', 'Otras Rentas'),
                ('04', 'Rentas Presuntas'),
                ('05', u'Intereses Pagados a Personas Jurídicas'),
                ('06', u'Intereses Pagados a Personas Físicas'),
                ('07', u'Retención por Proveedores del Estado'),
                ('08', u'Juegos Telefónicos')]

    l10n_do_tax_type = fields.Selection(
        selection=[('itbis', 'ITBIS Pagado'),
                   ('ritbis', 'ITBIS Retenido'),
                   ('prop', 'Subjeto a Proporcionalidad'),
                   ('isr', 'ISR Retenido'),
                   ('itbis_cost', 'ITBIS llevado al Costo'),
                   ('isc', 'Selectivo al Consumo (ISC)'),
                   ('other', 'Otros Impuestos'),
                   ('tip', 'Propina Legal'),
                   ('rext', 'Pagos al Exterior (Ley 253-12)'),
                   ('none', 'No Deducible')],
        default="none",
        string="Tax DGII Type",
    )
    isr_retention_type = fields.Selection(
        selection=_get_isr_retention_type,
        string="Tipo de Retención en ISR")
    
    
    
    @api.model
    def _update_tax_configuration(self):
        # Lógica para actualizar la configuración de impuestos
        tax_template_ids = self.env['ir.model.data'].sudo().search([
            ('model', '=', 'account.tax.template'),
            ('module', '=', 'l10n_do'),
        ])

        for tax_template_id in tax_template_ids:
            tax_ids = self.env['ir.model.data'].sudo().search([
                ('model', '=', 'account.tax'),
                ('module', '=', 'l10n_do'),
                ('name', 'like', '%_' + tax_template_id.name),
            ])

            taxes = self.env['account.tax'].sudo().browse(
                tax_ids.mapped('res_id')) if tax_ids else False

            if taxes:
                tax_template_obj = self.env['account.tax.template'].sudo().browse(
                    tax_template_id.res_id)
                taxes.write({
                    'purchase_tax_type': tax_template_obj.purchase_tax_type,
                    'isr_retention_type': tax_template_obj.isr_retention_type,
                    'tax_group_id': tax_template_obj.tax_group_id.id
                })
