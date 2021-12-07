# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class ResConfigSettings(models.Model):
    _inherit = 'res.company'

    sh_event_reg_qr_generator_random_number = fields.Boolean(string="Generate QR code randomly, large and unhackable?")

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    sh_event_reg_qr_generator_random_number = fields.Boolean(string="Generate QR code randomly, large and unhackable?",related="company_id.sh_event_reg_qr_generator_random_number",readonly=False)