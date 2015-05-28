# -*- coding: utf-8 -*-

{
    'name': 'Saved CC Payment Acquirer',
    'category': 'Hidden',
    'summary': 'Payment Acquirer: Saved CC Implementation',
    'version': '1.0',
    'description': """Saved CC Payment Acquirer""",
    'author': 'xyenDev',
    'depends': ['payment', 'website_payment'],
    'data': [
        'views/savedcc.xml',
        'views/payment_acquirer.xml',
        'data/savedcc.xml',
    ],
    'installable': True,
    'auto_install': False,
}