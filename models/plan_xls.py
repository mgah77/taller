from odoo import api, fields, models, _ 
import time
from datetime import date, datetime
import pytz
import datetime
import io
from odoo.tools import date_utils

try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter


class taller_plan2xls(models.TransientModel):
    _name = "taller.wiz.plan2xls"
    _description = "Export plan to xls"

    fecha = fields.Date()

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'fecha': self.fecha,

        }
        return {
            'type': 'ir.actions.report',
            'data': {'model': 'taller.wiz.plan2xls',
                     'options': json.dumps(data, default=date_utils.json_default),
                     'output_format': 'xlsx',
                     'report_name': 'Current Stock History',
                     },
            'report_type': 'stock_xlsx'
        }

    def get_lines(self, data):
        lines = []
        categ_id = data.mapped('id')
        if categ_id:
            categ_products = self.env['taller.ot.line'].search([('tall', 'in', state)])
        for obj in categ_products:
            sale_value = 0
            purchase_value = 0
            vals = {
                'name': obj.name,
                'armador': obj.armador,
                'depto': obj.depto,
                'fecha': obj.fecha,
                'nave': obj.nave,
                'detalle': obj.alias,
                'status': obj.state,
                'color': obj.color,
            }
            lines.append(vals)
        return lines