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
    plan = fields.many2many('taller.ot.line', 'plan_wiz_rel', 'plan', 'wiz', string="plan")

    def export_xls(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'fecha': self.fecha,
            'plan': self.plan,

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

    def get_lines(self, data, plan):
        lines = []
        plan_id = data.mapped('id')
        if plan_id:
            categ_plan = self.env['taller.ot.line'].search([('state',=, 'tall')])        
        for obj in categ_plan:
            vals = {               
                'ot': obj.name,
                'partner': obj.armador,
                'depto': obj.depto,
                'detalle': obj.alias,
                'fecha': obj.fecha,
                'nave': obj.nava,
                'status': obj.state,
                'color': obj.color,
            }
            lines.append(vals)
        return lines