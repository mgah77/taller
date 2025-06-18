# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{ 'name': 'Insumar_taller',
'summary': "OT y certificaciones",
'author': "Mauricio Gah",
'license': "AGPL-3",
'application': "True",
'version': "2.0",
'data': ['security/groups.xml',
         'security/ir.model.access.csv',

         'views/product_template.xml',
         'views/menu.xml',
         'views/orden_trabajo.xml',
         'views/planificacion.xml',
         'views/maniobras.xml',
         'views/maestro.xml',
         'views/partner.xml',
         'views/reemplazos.xml',
         'views/stock_taller.xml',
         'views/stock_move.xml',
         'views/stock_null',
         'report/entrega_reemplazo.xml',
         'wizard/taller_excel.xml',
         'wizard/maniobras.xml',
],
'assets': {
    "web.assets_backend": [
        'taller/static/src/js/action_manager.js',
    ],
     'web.report_assets_common': [
        'taller/static/src/img/logo.png',
    ],
},

'depends': ['base' , 'contacts' , 'stock' , 'product', 'parches_insumar','calendar']
}
