# -*- coding: utf-8 -*-

from . import pagadito
from odoo.http import request
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError 
from odoo.addons.payment.models.payment_acquirer import ValidationError
from odoo.tools.float_utils import float_compare, float_repr, float_round

import logging
_logger = logging.getLogger(__name__)


class PagaditoPaymentAcquirer(models.Model):
	_inherit = "payment.acquirer"

	provider = fields.Selection(selection_add=[
		('pagadito', 'Pagadito')
	], ondelete={'pagadito': 'set default'})

	pagadito_uid = fields.Char(required_if_provider='pagadito', string='UID')
	pagadito_wsk = fields.Char(required_if_provider='pagadito', string='WSK')


	def _get_pagadito_urls(self, environment):
		if environment == 'prod':
			return {
				'pagadito_form_url': 'https://comercios.pagadito.com/wspg/charges.php',
			}
		else:
			return {
				'pagadito_form_url':'https://sandbox.pagadito.com/comercios/wspg/charges.php',
			}


	def pagadito_get_form_action_url(self):
		return ''


	def _get_pagadito_form_url(self):
		environment = self.environment
		return self._get_pagadito_urls(environment)['pagadito_form_url']


	def pagadito_form_generate_values(self, tx_values):
		self.ensure_one()
		odoo_base_url = self.env['ir.config_parameter'].get_param('web.base.url')
		pagadito_tx_values = dict(tx_values)
		temp_pagadito_tx_values = {
			'odoo_base_url': odoo_base_url
		}
		pagadito_tx_values.update(temp_pagadito_tx_values)
		return pagadito_tx_values



class PagaditoPaymentTransaction(models.Model):
	_inherit = 'payment.transaction'

	pagadito_token = fields.Char('Pagadito token')


	def _pagadito_form_get_tx_from_data(self, data):
		reference = data.get('reference')

		if not reference:
			# error_msg = _('Pagadito: received data with missing reference (%s) or amount (%s)') % (reference, amount)
			error_msg = _('Pagadito: received data with missing reference (%s)') % (reference)
			_logger.info(error_msg)
			raise ValidationError(error_msg)

		tx = self.search([('reference', '=', reference)])
		if not tx or len(tx) > 1:
			error_msg = 'Pagadito: received data for reference %s' % (reference)
			if not tx:
				error_msg += '; no order found'
			else:
				error_msg += '; multiple order found'
			_logger.info(error_msg)
			raise ValidationError(error_msg)
		return tx[0]


	def _pagadito_form_get_invalid_parameters(self, data):
		"""
		invalid_parameters = []

		if float_compare(float(data.get('amount', '0.0')), self.amount, 2) != 0:
			invalid_parameters.append(('amount', data.get('TotalPagado'), '%.2f' % self.amount))

		return invalid_parameters
		"""
		return []


	def _pagadito_form_validate(self, data):
		acquirer = self.acquirer_id
		uid = acquirer.pagadito_uid
		wsk = acquirer.pagadito_wsk

		env = False if acquirer.state == 'test' else True
		_pagadito = pagadito.Pagadito(uid, wsk, env)
		token = _pagadito.connect()

		resp = _pagadito.get_status(token, self.pagadito_token)
		if not resp:
			ValidationError("Fallo al obtener el estado de la transaccion")
			self._set_transaction_pending()

		if self.state != 'draft':
			logging.info('Pagadito: trying to validate an already validated tx (ref %s)', self.reference)
			return True

		if resp.get('status') == 'REGISTERED':
			self._set_transaction_done()
			self.execute_callback()
			return True
		elif resp.get('status') == 'COMPLETED':
			self.write({
				'date': resp.get('date_trans'),
				'acquirer_reference': resp.get('reference'),
			})
			self._set_transaction_done()
			self.execute_callback()
			return True
		elif resp.get('status') == 'VERIFYING':
			self.write({
				'date': resp.get('date_trans'),
				'acquirer_reference': resp.get('reference'),
			})
			self._set_transaction_pending()
			self.execute_callback()
			return True
		else:
			self._set_transaction_cancel()
			return False


	def _create_pagadito_charge(self, data):
		acquirer = self.acquirer_id
		uid = acquirer.pagadito_uid
		wsk = acquirer.pagadito_wsk

		base_url = self.env['ir.config_parameter'].get_param('web.base.url')
		env = False if acquirer.state == 'test' else True
		_pagadito = pagadito.Pagadito(uid, wsk, env)

		token = _pagadito.connect()
		logging.info(_pagadito.get_data_send())
		logging.info(_pagadito.get_data_received())
		if not token:
			return {
				'event': 'token is null',
				'state': False,
				'msg' : _pagadito.get_last_error()
			}

		currency = self.env['res.currency'].browse(data.get('currency'))
		self.write({'pagadito_token' : token})
		if len(self.sale_order_ids) > 0:
			for sale in self.sale_order_ids:
				self._create_detail_pagadito(_pagadito, sale, base_url)
				break

		amount = float(data.get('amount'))
		redirect_url = _pagadito.exec_trans(token, amount, currency.name)
		logging.info(_pagadito.get_data_send())
		logging.info(_pagadito.get_data_received())
		if not redirect_url:
			return {
				'event': 'exec_trans failed',
				'state': False,
				'msg' : _pagadito.get_last_error()
			}
		else:
			return {
				'event' : '',
				'state': True,
				'msg' : redirect_url
			}


	def _create_detail_pagadito(self, _pagadito, order_id, base_url):
		for line in order_id.order_line:
			quantity = line.product_uom_qty
			description = line.product_id.name
			price = line.price_total / quantity
			url_product = '%s/shop/product/%s' % (base_url, str(line.product_id.id))

			_pagadito.add_detail(description, quantity, price, url_product)