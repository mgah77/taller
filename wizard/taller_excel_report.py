import time
import datetime
from dateutil.relativedelta import relativedelta
from odoo import fields, models, api, _
from odoo.tools import float_is_zero
from odoo.tools import date_utils
import io
import json
try:
   from odoo.tools.misc import xlsxwriter
except ImportError:
   import xlsxwriter
class ExcelWizard(models.TransientModel):
   _name = "taller.xlsx.wizard"
   start_date = fields.Datetime(string="Start Date",
                                default=time.strftime('%Y-%m-01'),
                                required=True)
   end_date = fields.Datetime(string="End Date",
                              default=datetime.datetime.now(),
                              required=True)
   def print_xlsx(self):
       if self.start_date > self.end_date:
           raise ValidationError('Start Date must be less than End Date')
       data = {
           'start_date': self.start_date,
           'end_date': self.end_date,
       }
       current_date = datetime.datetime.now().date()
       current_date_string = current_date.strftime("%Y-%m-%d")
       report_name = "Taller Report  " + current_date_string
       return {
           'type': 'ir.actions.report',
           'data': {'model': 'taller.xlsx.wizard',
                    'options': json.dumps(data,
                                          default=date_utils.json_default),
                    'output_format': 'xlsx',
                    'report_name': report_name,
                    },
           'report_type': 'xlsx',
       }
   def get_xlsx_report(self, data, response):
        partners = self.env['taller.ot.line'].search([('state','=','tall')])
        balsas = self.env['taller.ot.line'].search([('depto.name','=','Inspeccion Balsas'),('branch','=','viewer')], order="fecha asc")

        # Create Excel workbook and worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Formatos
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})

        # Write headers
        worksheet.merge_range(1, 13, 2, 19, 'Planificación', format0)
        headers = ['Name', 'Item', 'Depto','Nave','Armador','Fecha','Dias ','Balsas']
        for col, header in enumerate(headers, start=7):
            worksheet.write(10, col, header)

        # Write data
        for row, partner in enumerate(partners, start=11):
            worksheet.write(row, 10, partner.name)
            worksheet.write(row, 11, partner.item.name)
            worksheet.write(row, 12, partner.depto.name)
            worksheet.write(row, 13, partner.nave)
            worksheet.write(row, 14, partner.armador.name)
            worksheet.write(row, 15, partner.fecha)
            worksheet.write(row, 16, partner.dias)

        for row, balsas in enumerate(balsas, start=12):
            worksheet.write(row, 17, balsas.name)
            worksheet.write(row, 18, balsas.fecha)
            worksheet.write(row, 19, balsas.nave)

        # Close workbook
        workbook.close()

        # Prepare HTTP response with Excel file
        #output.seek(0)
        output.seek(0)
        response.stream.write(output.read())
        output.close()
