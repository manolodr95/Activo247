odoo.define('tsl_payment_pagadito.pagadito', function (require) {
	"use strict";

	var ajax = require('web.ajax');
	var core = require('web.core');
	var Widget = require('web.Widget');
	
	var _t = core._t;
	var QWeb = core.qweb;
	ajax.loadXML("/tsl_payment_pagadito/static/src/xml/pagadito.xml", QWeb);

	function get_form_event(){
		ajax.jsonRpc("/payment/pagadito/create_charge", 'call', {
			'reference' : $("input[name='reference']").val(),
			'amount' : $("input[name='amount']").val(),
			'return_url': $("input[name='return_url']").val()
		}).then(function(data){
			if ($.blockUI) { $.unblockUI(); }
			if(data.result == true){
				window.location.href = data.msg;
			}else if(data.result == false){
				errorDialog(data.msg);
			}
		}).guardedCatch(function(){
			if ($.blockUI) { $.unblockUI(); }
			errorDialog('An error occured. Please try again later or contact us.');
		});
	}


	function errorDialog(message){
		$('.modal').modal('hide');
		var wizard = $(QWeb.render('pagadito.error', {
			'msg': _t(message)
		}));
		var button = $(wizard.find("button"));
		button.on('click', function(){
			window.location.href = $("input[name='odoo_base_url']").val();
		});
		wizard.appendTo($('body')).modal({'keyboard': false, 'backdrop':'static'});
	}


	$.blockUI({
		'message': '<h2 class="text-white"><img src="/web/static/src/img/spin.png" class="fa-pulse"/>' +
			'    <br />' + "Porfavor espere..." +
			'</h2>'
	});
	get_form_event();
});
