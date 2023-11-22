# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{ 'name': 'Insumar_taller',
'summary': "OT y certificaciones",
'author': "Mauricio Gah",
'license': "AGPL-3",
'application': "True",
'version': "2.0",
'data': ['security/groups.xml',
         'security/ir.model.access.cvs',
         'views/orden_trabajo.xml'
],
'depends': ['base' , 'contacts' , 'stock' , 'product']
}
