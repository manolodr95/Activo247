# -*- coding: utf-8 -*-
# Copyright (C) Softhealer Technologies.
{
    "name": "Event Registration QRCode Generator",

    "author": "Softhealer Technologies",

    "website": "https://www.softhealer.com",

    "support": "support@softhealer.com",

    "version": "14.0.2",

    "category": "Extra Tools",

    "summary": "Event Registration QR Generator, Event Badge QR Generator, QRCode Generator,Maintain Attendees Ticket  QR Module, Generate Attendee Event QR, Manage Event Ticket QR, Produce Attendees event QR App,  Event Badge QR  Generator Odoo",

    "description": """Nowadays in the event, there are many attendees attend with fake tickets. That's why we build this module specially for event management. Using this module you can easily generate tickets with a QR, we show the QR in form view. So it will reduce the number of fraud attendees in the event. Also, you can print that ticket in PDF format.
 Event Registration QR Generator Odoo, Event Badge QR Generator Odoo,Maintain Attendees QR With Ticket  Module, Generate Attendee QR In Event, Manage Event Ticket QR, Event Ticket QR Generator,  Event Badge QR Generator Odoo
 Maintain Attendees Ticket  QR Module, Generate Attendee Event QR, Manage Event Ticket QR, Produce Attendees event QR App,  Event Badge QR  Generator Odoo""",

    "depends": ["event"],

    "data": [
        "views/event_view.xml",
        "views/res_config_setting_view.xml",
        "reports/event_report_tmpls.xml",
        
    ],

    "external_dependencies": {
        "python": ["qrcode"],
    },

    "images": ["static/description/background.png", ],
    "live_test_url": "https://youtu.be/XCkqr29Wxw8",
    "installable": True,
    "application": True,
    "autoinstall": False,
    "price": 15,
    "currency": "EUR",
    "license": "OPL-1"
}
