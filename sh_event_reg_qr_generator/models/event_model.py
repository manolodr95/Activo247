# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
import uuid
from odoo import models, fields
from io import BytesIO

try:
    import qrcode
except ImportError:
    qrcode = None
try:
    import base64
except ImportError:
    base64 = None


class EventRegistration(models.Model):
    _inherit = 'event.registration'

    sh_er_qr_code = fields.Char(string="QR Code", readonly=True)
    sh_er_qr_code_img = fields.Binary(string="QR Code Image", readonly=True)

    def _check_auto_confirmation(self):

        for registration in self:

            prefix = 'ER_'
            seq = prefix + str(registration.id)
            if self.env.company.sh_event_reg_qr_generator_random_number:
                seq=str(uuid.uuid4())
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(seq)
            qr.make(fit=True)

            img = qr.make_image()
            temp = BytesIO()
            img.save(temp, format="PNG")
            qr_image = base64.b64encode(temp.getvalue())

            registration.sh_er_qr_code = seq
            registration.sh_er_qr_code_img = qr_image

        return super(EventRegistration, self)._check_auto_confirmation()
