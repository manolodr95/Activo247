# -*- coding: utf-8 -*-

import requests
import json
import urllib
import xml.etree.ElementTree as ET

uid = 'bf4f90d3aaa4972ba61935758c056d64'
wsk = '221cd7912f50bc9d6c4af5a4a20bbb4e'
url = 'https://sandbox.pagadito.com/comercios/wspg/charges.php'

HEADER = {"Content-Type": "text/xml; charset=UTF-8",}


CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
	<soap:Body>
		<connect xmlns="http://schemas.xmlsoap.org/soap/http">
			<uid>bf4f90d3aaa4972ba61935758c056d64</uid>
			<wsk>221cd7912f50bc9d6c4af5a4a20bbb4e</wsk>
			<format_return>json</format_return>
		</connect>
	</soap:Body>
</soap:Envelope>
"""

CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
	<soap:Body>
		<exec_trans xmlns="http://schemas.xmlsoap.org/soap/http">
			<token>85463821c1d9c009ffae978269fa5179</token>
			<ern>67904798480808490187756869905161032574</ern>
			<amount>12.50</amount>
			<details>[{"quantity": 1, "description": "Office Chair Black", "price": 12.5, "url_product": "https://tslodoo13b.eastus.cloudapp.azure.com/shop/product/25"}]</details>
			<currency>USD</currency>
			<format_return>json</format_return>
		</exec_trans>
	</soap:Body>
</soap:Envelope>
"""
CONTENT = """<?xml version="1.0" encoding="utf-8"?>
<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
	<SOAP-ENV:Body>
		<ns1:exec_trans xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
			<token xsi:type="xsd:string">85463821c1d9c009ffae978269fa5179</token>
			<ern xsi:type="xsd:string">67904798480808490187756869905161032574</ern>
			<amount xsi:type="xsd:string">12.50</amount>
			<details xsi:type="xsd:string">[{"quantity": 1, "description": "Office Chair Black", "price": 12.5, "url_product": "https://tslodoo13b.eastus.cloudapp.azure.com/shop/product/25"}]</details>
			<currency xsi:type="xsd:string">USD</currency>
			<format_return xsi:type="xsd:string">json</format_return>
		</ns1:exec_trans>
	</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"""


resp = requests.post(url, data=CONTENT, headers=HEADER)
print(resp.status_code)
print(resp.text)
"""
resp = "# ""<?xml version="1.0" encoding="ISO-8859-1"?>
<SOAP-ENV:Envelope SOAP-ENV:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/" xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:SOAP-ENC="http://schemas.xmlsoap.org/soap/encoding/">
	<SOAP-ENV:Body>
		<ns1:connectResponse xmlns:ns1="http://schemas.xmlsoap.org/soap/http">
			<return xsi:type="xsd:string">
				{&quot;code&quot;:&quot;PG1001&quot;,&quot;message&quot;:&quot;Connection successful.&quot;,&quot;value&quot;:&quot;66da109f823db90eee584762b109fa32&quot;,&quot;datetime&quot;:&quot;2020-07-13 21:33:49&quot;}
			</return>
		</ns1:connectResponse>
	</SOAP-ENV:Body>
</SOAP-ENV:Envelope>
"# ""

root = ET.fromstring(resp)
results = [elem.text for elem in root.iter() if elem.tag == 'return']
content = json.loads(results[0])
print(content)
"""