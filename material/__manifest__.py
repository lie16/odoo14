# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name' : 'Material Type',
    'version' : '1.0',
    'summary': 'Material Type',
    'sequence': 0,
    'description': """
    Material Type test
    """,
    'category': 'Sales/sales',
    'website': '',
    'images' : [],
    'depends' : ['base'],
    'data': [
        'views/material_type_views.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'post_init_hook': '',
    'license': 'LGPL-3',
}
