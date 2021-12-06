# -*- coding: utf-8 -*-
{
	'name': "Pagadito Payment Acquirer",

	'summary': """
		Medio de pago: Implementación Pagadito""",

	'description': """
		Pagos online usando el sistema de Pagadito.
	""",

	'author': "Luis Dominguez",
	#'website': "http://www.techsantalibrada.com",
	'category': 'Accounting/Payment Acquirers',
	'maintainer':"Luis Dominguez",
	'support': 'luis.dominguez19@yahoo.es',
	'images': ['static/description/banner.jpg'],
	'version': '14.0.1.0.1',
	'license': 'OPL-1',
	'price': 65.00,
	'currency': 'USD',

	# any module necessary for this one to work correctly
	'depends': ['payment'],

	# any external dependence necessary for this one to work correctly
	'external_dependencies':{
		'python':[],
		'bin':[]
	},

	# always loaded
	'data': [
		# 'security/ir.model.access.csv',
		'views/payment_view.xml',
		'views/pagadito_template.xml',
		'data/payment_acquirer_data.xml',
	],

	'qweb': [
		'/tsl_payment_pagadito/static/src/xml/pagadito.xml'
	],

	# only loaded in demonstration mode
	'demo': [
		#'demo/demo.xml',
	],
	'post_init_hook': 'create_missing_journal_for_acquirers',
	'uninstall_hook': 'uninstall_hook',
}