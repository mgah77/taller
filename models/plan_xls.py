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

    def get_xlsx_report(self, data, response):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        comp = self.env.user.company_id.name
        sheet = workbook.add_worksheet('Stock Info')
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format11 = workbook.add_format({'font_size': 12, 'align': 'center', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True})
        format3 = workbook.add_format({'bottom': True, 'top': True, 'font_size': 12})
        format4 = workbook.add_format({'font_size': 12, 'align': 'left', 'bold': True})
        font_size_8 = workbook.add_format({'font_size': 8, 'align': 'center'})
        font_size_8_l = workbook.add_format({'font_size': 8, 'align': 'left'})
        font_size_8_r = workbook.add_format({'font_size': 8, 'align': 'right'})
        red_mark = workbook.add_format({'font_size': 8, 'bg_color': 'red'})
        justify = workbook.add_format({'font_size': 12})
        format3.set_align('center')
        justify.set_align('justify')
        format1.set_align('center')
        red_mark.set_align('center')
        sheet.merge_range(1, 7, 2, 10, 'Product Stock Info', format0)
        sheet.merge_range(3, 7, 3, 10, comp, format11)
        w_house = ', '
        sheet.merge_range(5, 0, 5, 1, 'Warehouse(s) : ', format4)
        user = self.env['res.users'].browse(self.env.uid)
        tz = pytz.timezone(user.tz if user.tz else 'UTC')
        times = pytz.utc.localize(datetime.datetime.now()).astimezone(tz)
        sheet.merge_range('A8:G8', 'Report Date: ' + str(times.strftime("%Y-%m-%d %H:%M %p")), format1)
        sheet.merge_range(7, 7, 7, count, 'Warehouses', format1)
        sheet.merge_range('A9:G9', 'Product Information', format11)
        prod_row = 10
        prod_col = 0
        get_line = self.get_lines()
        for line in get_line:
            sheet.write(prod_row, prod_col, line['name'], red_mark)
            sheet.write(prod_row, prod_col + 1, line['armador'], red_mark)
            prod_row = prod_row + 1
        workbook.close()
        output.seek(0)
        response.stream.write(output.read())
        output.close()