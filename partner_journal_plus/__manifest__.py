{
    'name': 'Partner Journal default',
    'images': ['images/main_screenshot.png'],
    'version': '1.0.1',
    'category': 'Partner',
    'summary': 'Set alternative journal accounts on partners to use as default Journal when creating a new Invoice',
    'author': 'Inovacijos',
    'website': 'http://www.innovations.lt',
    'depends': [
               'account',
    ],
    'installable': True,
    'license': 'AGPL-3',
    'data': [
        'views/partner_views.xml',
    ],
}
