# -*- coding: utf-8 -*-
import werkzeug
import logging
import json

from odoo import http
from odoo.http import request
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class PagueloFacilController(http.Controller):


	@http.route(['/payment/pagadito/return'], type='http', auth='none', csrf=False, methods=['GET'])
	def pagadito_form_feedback(self, **kwargs):
		if not kwargs.get('token'):
			raise werkzeug.exceptions.NotFound()
		
		TX = request.env['payment.transaction']
		tx = TX.sudo().search([('pagadito_token', '=', kwargs.get('token'))])

		kwargs['amount'] = tx[0].amount
		kwargs['reference'] = tx[0].reference

		request.env['payment.transaction'].sudo().form_feedback(kwargs, 'pagadito')
		return werkzeug.utils.redirect('/payment/process')



	@http.route(['/payment/pagadito/create_charge'], type='json', auth='public')
	def pagadito_create_charge(self, **kwargs):
		logging.info("El valor de pagadito_create_charge es:")
		logging.info(kwargs)
		TX = request.env['payment.transaction']
		tx = None
		if kwargs.get('reference'):
			tx = TX.sudo().search([('reference', '=', kwargs.get('reference'))])
		if not tx:
			tx_id = (request.session.get('sale_transaction_id') or
					request.session.get('website_payment_tx_id'))
			tx = TX.sudo().browse(int(tx_id))
		if not tx:
			raise werkzeug.exceptions.NotFound()

		logging.info("El valor de tx es")
		logging.info(tx)
		response = tx._create_pagadito_charge({
			'amount' : kwargs.get('amount'),
			'reference' : kwargs.get('reference'),
			'currency' : tx.currency_id.id
		})
		if response:
			return {
				"event": response.get('event'),
				"result": response.get('state'),
				"msg": response.get('msg')
			}
