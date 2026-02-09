# -*- coding: utf-8 -*-
{
    'name': 'famti_management',
    'version': '1.0',
    'depends': [
                    'base',
                    'web',
                    'contacts',
                    'sale_management',
                    'purchase',
                    'stock',
                    'mrp',
                    'account',

],
    'data': [
        'security/rules.xml',
        'security/ir.model.access.csv',
        'data/ir_server_actions.xml',
        'data/mail_template.xml',
        'data/ir_cron.xml',
        'data/product_data.xml',
        # 'data/inventory_data.xml',
        'wizard/lot_import_wizard.xml',
        'wizard/stock_lot_wiz.xml',
        'wizard/mrp_batch_wizard.xml',
        'wizard/mrp_scrap_wizard.xml',
        'views/purchase.xml',
        'views/res_partner.xml',
        'views/product.xml',
        'views/purchase_order_line.xml',
        'views/stock_picking.xml',
        'views/stock_lot.xml',
        'views/menu.xml',
        'views/action.xml',
        'views/sale.xml',
        'views/res_company_view.xml',
        'views/manufacturing.xml',
        'views/costing_sheet.xml',
    ],
    'demo': [
        # 'demo/account_demo.xml',
    ],
'assets': {
        'web.assets_backend': [
            'famti/static/src/xml/import_lot_patch.xml',
        ],
        'web.assets_frontend': [
                    'famti/static/src/js/import_lot_patch.js',
                ],
    },
# 'assets': {
#     'web.assets_backend': [
#         'famti/static/src/js/import_lot_patch.js',
#         'famti/static/src/xml/import_lot_patch.xml',
#     ],
# },

    'installable': True,
    'application': False,

    'license': 'LGPL-3',
}
