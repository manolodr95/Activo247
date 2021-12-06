# -*- coding: utf-8 -*-

import requests
import uuid 
import json
from datetime import datetime
import xml.etree.ElementTree as ET


class Pagadito:
	ENV_TEST = 'https://sandbox.pagadito.com/comercios/wspg/charges.php?wsdl'
	ENV_PROD = 'https://comercios.pagadito.com/wspg/charges.php?wsdl'


	__PAGADITO_HEADERS = {"Content-Type": "text/xml; charset=UTF-8",}


	PAGADITO_CURRENCY = ['USD', 'GTQ', 'HNL', 'NIO', 'CRC', 'PAB', 'DOP']

	PAGADITO_CODE_ERROR = [
		{'code':'PG1001', 	'title':'Connection successful', 			'text':'Conexión exitosa del Pagadito Comercio con el WSPG'},
		{'code':'PG1002', 	'title':'Transaction register successful',	'text':'La transacción enviada por el Pagadito Comercio fue registrada correctamente por el WSPG'},
		{'code':'PG1003', 	'title':'Transaction status', 				'text':'Ha sido procesada correctamente la petición de estado de transacción'},
		{'code':'PG1004', 	'title':'Exchange Rate', 					'text':'Ha sido procesada correctamente la petición de tasa de cambio'},
		{'code':'PG1005', 	'title':'Transfer', 						'text':'Ha sido procesada correctamente la petición de transferencia'},
		{'code':'PG1006', 	'title':'Authorization',					'text':'Ha sido procesada correctamente la petición de autorizacion'},
		{'code':'PG1007', 	'title':'Get Authorization token' ,			'text':'Ha sido procesada correctamente la petición de obtener token autorizacion'},
		{'code':'PG1008', 	'title':'Authorization for Recurring Payments', 'text':'Ha sido procesada correctamente la petición de autorizacion de pagos recurrentes'},
		{'code':'PG1009', 	'title':'Get Authorization token for Recurring payments','text':'Ha sido procesada correctamente la petición de obtener token autorizacion para pagos recurrentes'},
		{'code':'PG1010', 	'title':'Pending transaction status', 		'text':'Ha sido procesada correctamente la petición de obtener el estado de una transaccion pendiente'},
		{'code':'PG1012', 	'title':'Recurring Payments', 				'text':'Ha sido procesada correctamente la petición de pagos recurrentes'},
		{'code':'PG1014', 	'title':'Valid authorization token', 		'text':'Ha sido procesada correctamente la petición de validar token de autorizacion'},
		{'code':'PG1017', 	'title':'Multiple transactions', 			'text':'Ha sido procesada correctamente la petición de transacciones multiples'},
		{'code':'PG1018', 	'title':'Multiple transactions status', 	'text':'Ha sido procesada correctamente la petición de obtener estado de transacciones multiples'},
		{'code':'PG2001', 	'title':'Incomplete data', 					'text':'El Pagadito Comercio no envió todos los parámetros necesarios'},
		{'code':'PG2002', 	'title':'Incorrect format data', 			'text':'El formato de los datos enviados por el Pagadito Comercio no es el correcto'},
		{'code':'PG3001', 	'title':'Connection couldn´t be established','text':'Las credenciales de conexión no están registradas'},
		{'code':'PG3002', 	'title':'We´re sorry. An error has occurred','text':'Un error no controlado por el WSPG ocurrió y no se ha podido procesar la petición'},
		{'code':'PG3003', 	'title':'Unregistered transaction', 		'text':'La transacción solicitada no ha sido registrada'},
		{'code':'PG3004', 	'title':'Transaction amount doesn´t match with calculated amount','text':'La suma de los productos de la cantidad y el precio de los detalles no es igual al monto de la trasacción'},
		{'code':'PG3005', 	'title':'Connection is disabled', 			'text':'El Pagadito Comercio ha sido validado, pero la conexión se encuentra deshabilitada'},
		{'code':'PG3006', 	'title':'Amount has exceeded the maximum', 	'text':'La transacción ha sido denegada debido a que excede el monto máximo por transacción'},
		{'code':'PG3007', 	'title':'Denied access', 					'text':'El acceso ha sido denegado, debido a que el token no es válido'},
		{'code':'PG3008', 	'title':'Currency not supported', 			'text':'La moneda solicitada no es soportada por Pagadito'},
		{'code':'PG3009', 	'title':'Amount is lower than the minimum allowed','text':'La transacción ha sido denegada debido a que el monto es menor al mínimo permitido'},
		{'code':'PG3015', 	'title':'Incorrect authorization token', 	'text':'La transacción ha sido denegada debido a que el token de autorizacion es incorrecto'},
		{'code':'PG3018', 	'title':'You have already sent this ERN', 	'text':'La transacción ha sido denegada debido a que el ern ya fue enviado'},
		{'code':'PG3022', 	'title':'Amount of recurrent payments is higher than the maximum allowed','text':'La transacción ha sido denegada debido a que el monto de los pagos recurrentes es mayor al máximo permitido'},
		{'code':'PG3024', 	'title':'Permissions not allowed',			'text':'La transacción ha sido denegada debido a que los permisos proporcionados no son permitidos'},
		{'code':'PG3025', 	'title':'Cross-site scripting found on parameter','text':'La transacción ha sido denegada debido a que se detecto código malicioso'},
	]

	PAGADITO_PAYMENT_STATUS = [
		{'state':'REGISTERED',	'description':'La transacción ha sido registrada correctamente en Pagadito, pero aún se encuentra en proceso. En este punto, el cobro aún no ha sido realizado'},
		{'state':'COMPLETED',	'description':'La transacción ha sido procesada correctamente en Pagadito. En este punto el cobro ya ha sido realizado'},
		{'state':'VERIFYING',	'description':'La transacción ha sido procesada en Pagadito, pero ha quedado en verificación. En este punto el cobro ha quedado en validación administrativa. Posteriormente, la transacción puede marcarse como válida o denegada; por lo que se debe monitorear mediante esta función hasta que su estado cambie a COMPLETED o REVOKED'},
		{'state':'REVOKED',		'description':'La transacción en estado VERIFYING ha sido denegada por Pagadito. En este punto el cobro ya ha sido cancelado'},
		{'state':'FAILED',		'description':'La transacción ha sido registrada correctamente en Pagadito, pero no pudo ser procesada. En este punto, el cobro aún no ha sido realizado'},
		{'state':'CANCELED',	'description':'La transacción ha sido cancelada por el usuario en Pagadito, la transacción tiene este estado cuando el usuario hace click en el enlace de "regresar al comercio" en la pantalla de pago de Pagadito'},
		{'state':'EXPIRED',		'description':'La transacción ha expirado en Pagadito, la transacción tiene este estado cuando se termina el tiempo para completar la transacción por parte del usuario en Pagadito, el tiempo para completar la transacción en Pagadito por parte del usuario es de 10 minutos. Pagadito también se encarga de poner estado EXPIRED a todas las transacciones que no fueron completas, debido a que el usuario salio de manera inesperada del proceso de pago, por ejemplo cerrando la ventana del navegador'}
	]

	PAGADITO_STATUS_REGISTERED = 'REGISTERED'
	PAGADITO_STATUS_COMPLETED = 'COMPLETED'
	PAGADITO_STATUS_VERIFYING = 'VERIFYING'
	PAGADITO_STATUS_REVOKED = 'REVOKED'
	PAGADITO_STATUS_FAILED = 'FAILED'
	PAGADITO_STATUS_CANCELED = 'CANCELED'
	PAGADITO_STATUS_EXPIRED = 'EXPIRED'
	


	def __init__(self, uid, wsk, enabled=False):
		self.uid = uid
		self.wsk = wsk
		self.wspg_url = self.ENV_PROD if enabled == True else self.ENV_TEST
		self.error = ''
		self.token = None
		self.details = []
		self.data_send = ""
		self.data_received = "" 
		self.custom_params = {
			'param1': 'N.A.',
			'param2': 'N.A.',
			'param3': 'N.A.',
			'param4': 'N.A.',
			'param5': 'N.A.'
		}


	def enviranment(self, env):
		if env == 'test':
			self.wspg_url = self.ENV_TEST 
		elif env == 'prod':
			self.wspg_url = self.ENV_PROD
		else:
			pass


	def get_last_error(self):
		return self.error


	def get_data_send(self):
		return self.data_send


	def get_data_received(self):
		return self.data_received


	def add_detail(self, description, quantity, price, url_product):
		"""
		"""
		self.details.append({
			'quantity':int(quantity),
			'description':description,
			'price':price,
			'url_product':url_product
		})


	def connect(self, url=None):
		""" Genera el token necesario para realizar las demas consultas.

		Args:
			url (str, optional): URL del servicio a consultar. Defaults to None.

		Returns:
			str: Token obtenido de la consulta. None si algo fallo.
		"""
		base_url = url if url != None else self.wspg_url
		if not base_url:
			self.error = 'No se encontro una URL valida'
			return None

		CONTENT = """<?xml version="1.0" encoding="utf-8"?>
		<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
						xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
						xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
						xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
						xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
			<SOAP-ENV:Body>
				<ns1:connect xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
					<uid xsi:type="xsd:string">%s</uid>
					<wsk xsi:type="xsd:string">%s</wsk>
					<format_return xsi:type="xsd:string">json</format_return>
				</ns1:connect>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>
		""" % (str(self.uid), str(self.wsk))
		self.data_send = CONTENT


		resp = requests.post(base_url, data=CONTENT, headers=self.__PAGADITO_HEADERS)
		self.data_received = resp.text
		if resp.status_code != 200:
			self.error = str(resp.status_code)
			return None
		else:
			root = ET.fromstring(resp.text)
			results = [elem.text for elem in root.iter() if elem.tag == 'return']
			content = json.loads(results[0])
			if content.get('code') != 'PG1001':
				error = [element for element in self.PAGADITO_CODE_ERROR if element['code'] == content['code']]
				if len(error) > 0:
					self.error = error[0].get('text')
				return None
			else:
				self.token = content.get('value')
				return content.get('value')


	def exec_trans(self, token, amount, currency, details=None, url=None):
		"""[summary]

		Args:
			token (str): Token obtenido del metodo connect()
			amount (float): Cantidad total a pagar.
			details (list): Lista de objetos con los movimientos a pagar.
			url (str, optional): URL del servicio a consultar. Defaults to None.

		Returns:
			str: URL donde sera redirigido el usuario para realizar el pago.
		"""
		if not currency in self.PAGADITO_CURRENCY:
			raise Exception('El tipo de moneda ingresado no esta permitido')

		base_url = url if url != None else self.wspg_url
		lines = details if details != None else self.details
		if lines == None:
			raise Exception('Se requiere detalles/movimientos para poder realizar la solicitud')
		elif len(lines) == 0:
			raise Exception('Se requiere detalles/movimientos para poder realizar la solicitud')

		# raw = uuid.uuid1()
		# uid = raw.int

		current_time = datetime.today()
		uid = current_time.strftime('%Y%m%d%H%M%S%f')

		CONTENT = """<?xml version="1.0" encoding="utf-8"?>
		<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
						xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
						xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
						xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
						xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
			<SOAP-ENV:Body>
				<ns1:exec_trans xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
					<token xsi:type="xsd:string">%s</token>
					<ern xsi:type="xsd:string">%s</ern>
					<amount xsi:type="xsd:string">%.2f</amount>
					<details xsi:type="xsd:string">%s</details>
					<format_return xsi:type="xsd:string">json</format_return>
					<currency>%s</currency>
				</ns1:exec_trans>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>
		""" % (token, uid, amount, json.dumps(lines), currency)
		self.data_send = CONTENT

		resp = requests.post(base_url, data=CONTENT, headers=self.__PAGADITO_HEADERS)
		self.data_received = resp.text
		if resp.status_code != 200:
			self.error = str(resp.status_code)
			return None
		else:
			root = ET.fromstring(resp.text)
			results = [elem.text for elem in root.iter() if elem.tag == 'return']
			content = json.loads(results[0])
			if content.get('code') != 'PG1002':
				error = [element for element in self.PAGADITO_CODE_ERROR if element['code'] == content['code']]
				if len(error) > 0:
					self.error = error[0].get('text')
				return None
			else:
				return content.get('value')


	def get_status(self, token, token_trans, url=None):
		"""[summary]

		Args:
			token (str): token de autorización
			token_trans (str): token de autorizacion de la transaccion a consultar.
			url (str, optional): URL a consultar. Defaults to None.

		Returns:
			[type]: [description]
		"""
		base_url = url if url != None else self.wspg_url

		CONTENT = """<?xml version="1.0" encoding="utf-8"?>
		<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
						xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
						xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
						xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
						xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
			<SOAP-ENV:Body>
				<ns1:get_status xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
					<token xsi:type="xsd:string">%s</token>
					<token_trans xsi:type="xsd:string">%s</token_trans>
					<format_return xsi:type="xsd:string">json</format_return>
				</ns1:get_status>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>
		""" % (token, token_trans)
		self.data_send = CONTENT

		resp = requests.post(base_url, data=CONTENT, headers=self.__PAGADITO_HEADERS)
		self.data_received = resp.text
		if resp.status_code != 200:
			self.error = str(resp.status_code)
			return None
		else:
			root = ET.fromstring(resp.text)
			results = [elem.text for elem in root.iter() if elem.tag == 'return']
			content = json.loads(results[0])
			if content.get('code') != 'PG1003':
				error = [element for element in self.PAGADITO_CODE_ERROR if element['code'] == content['code']]
				if len(error) > 0:
					self.error = error[0].get('text')
				return None
			else:
				return content.get('value')


	def get_exchange_rate(self, token, currency, url=None):
		"""[summary]

		Args:
			token (str): token de autorizacion
			currency (str): Nombre del tipo de moneda
			url (str, optional): URL a consultar. Defaults to None.

		Raises:
			Exception: [description]

		Returns:
			float: ratio del valor de la moneda convertida a USD
		"""
		if not currency in self.PAGADITO_CURRENCY:
			raise Exception('El tipo de moneda ingresado no esta permitido')

		base_url = url if url != None else self.wspg_url

		CONTENT = """<?xml version="1.0" encoding="utf-8"?>
		<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" 
						xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" 
						xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
						xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
						xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
			<SOAP-ENV:Body>
				<ns1:get_exchange_rate xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
					<token xsi:type="xsd:string">%s</token>
					<currency xsi:type="xsd:string">%s</currency>
					<format_return xsi:type="xsd:string">json</format_return>
				</ns1:get_exchange_rate>
			</SOAP-ENV:Body>
		</SOAP-ENV:Envelope>
		""" % (token, currency)
		self.data_send = CONTENT

		try:
			resp = requests.post(base_url, data=CONTENT, headers=self.__PAGADITO_HEADERS)
			self.data_received = resp.text
			if resp.status_code != 200:
				self.error = str(resp.status_code)
				return None
			else:
				root = ET.fromstring(resp.text)
				results = [elem.text for elem in root.iter() if elem.tag == 'return']
				content = json.loads(results[0])
				if content.get('code') != 'PG1004':
					error = [element for element in self.PAGADITO_CODE_ERROR if element['code'] == content['code']]
					if len(error) > 0:
						self.error = error[0].get('text')
					return None
				else:
					return float(content.get('value'))
		except Exception as __ERROR:
			self.error = __ERROR
			return None