{
    'name': 'POS Custom',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 0,
    'summary': 'Customizations for the POS module',
    'depends': ['base', 'point_of_sale'],
    'data': [
        'views/template.xml',
    ],
    'qweb': [
    ],
    'license': 'LGPL-3',
    'installable': True,
    'application': True,
}