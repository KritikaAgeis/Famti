# -*- coding: utf-8 -*-
{
    'name': 'famti_management',
    'version': '1.0',
    'depends': [
                    'base',
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
        'wizard/stock_lot_wiz.xml',
        'views/purchase.xml',
        'views/res_partner.xml',
        'views/stock_picking.xml',
        'views/stock_lot.xml',
        'views/menu.xml',
        'views/sale.xml',
        'views/sale_res_partner.xml',
        'views/res_company_view.xml',
    ],
    'demo': [
        # 'demo/account_demo.xml',
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}
