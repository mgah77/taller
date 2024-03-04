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
        balsas = partners.search([('depto.name','=','Inspeccion Balsas'),('branch','=','viewer')], order="fecha asc")
        conten = partners.search([('depto.name','=','Contenedores'),('branch','=','viewer')], order="fecha asc")
        valvul = partners.search([('depto.name','=','Valvulas'),('branch','=','viewer')], order="fecha asc")
        extint = partners.search([('depto.name','=','Extintores'),('branch','=','viewer')], order="fecha asc")
        seguri = partners.search([('depto.name','=','Equipo Seguridad'),('branch','=','viewer')], order="fecha asc")
        bcoco2 = partners.search([('depto.name','=','Banco CO2'),('branch','=','viewer')], order="fecha asc")
        textil = partners.search([('depto.name','=','Textil'),('branch','=','viewer')], order="fecha asc")

        # Create Excel workbook and worksheet
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output)
        worksheet = workbook.add_worksheet()

        # Formatos
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format1 = workbook.add_format({'font_size': 11, 'align': 'center', 'bold': True})

        # Write headers
        worksheet.merge_range(1, 13, 2, 19, 'PLANIFICACION DIARIA', format0)
        worksheet.merge_range(3, 1, 3, 3, 'Inspeccion de balsa', format1)
        worksheet.merge_range(3, 5, 3, 6, 'Contenedores', format1)
        worksheet.merge_range(3, 8, 3, 9, 'Válvulas', format1)
        worksheet.merge_range(3, 11, 3, 14, 'Extintores', format1)
        worksheet.merge_range(3, 16, 3, 19, 'Equipo Seguridad', format1)
        worksheet.merge_range(3, 21, 3, 23, 'Banco CO2', format1)
        worksheet.merge_range(3, 25, 3, 30, 'Textil', format1)

        #headers = ['Name', 'Item', 'Depto','Nave','Armador','Fecha','Dias ','Balsas']
        #for col, header in enumerate(headers, start=7):
         #   worksheet.write(10, col, header)

        # Write data
        for row, balsas in enumerate(balsas, start=4):
            worksheet.write(row, 1, balsas.name)
            worksheet.write(row, 2, str(balsas.fecha.strftime("%Y-%m-%d")))
            worksheet.write(row, 3, balsas.nave)

        for row, conten in enumerate(conten, start=4):
            worksheet.write(row, 5, conten.name)
            worksheet.write(row, 6, conten.nave)
        
        for row, valvul in enumerate(valvul, start=4):
            worksheet.write(row, 8, valvul.name)
            worksheet.write(row, 9, valvul.nave)

        for row, extint in enumerate(extint, start=4):
            worksheet.write(row, 11, extint.name)
            worksheet.write(row, 12, extint.fecha)
            worksheet.write(row, 13, extint.nave)
            worksheet.write(row, 14, extint.obs)

        for row, seguri in enumerate(seguri, start=4):
            worksheet.write(row, 16, seguri.name)
            worksheet.write(row, 17, seguri.fecha)
            worksheet.write(row, 18, seguri.nave)
            worksheet.write(row, 19, seguri.item.alias)

        for row, bcoco2 in enumerate(bcoco2, start=4):
            worksheet.write(row, 21, bcoco2.name)
            worksheet.write(row, 22, bcoco2.fecha)
            worksheet.write(row, 23, bcoco2.nave)        

        for row, textil in enumerate(textil, start=4):
            worksheet.write(row, 25, textil.name)
            worksheet.write(row, 26, textil.nave)
            worksheet.write(row, 27, textil.fecha)
            worksheet.write(row, 28, textil.cant) 
            worksheet.write(row, 29, textil.item.alias)  
            worksheet.write(row, 30, textil.branch_s)  


        #for row, partner in enumerate(partners, start=11):
         #   worksheet.write(row, 10, partner.name)
          #  worksheet.write(row, 11, partner.item.name)
           # worksheet.write(row, 12, partner.depto.name)
            #worksheet.write(row, 13, partner.nave)
         #   worksheet.write(row, 14, partner.armador.name)
          #  worksheet.write(row, 15, partner.fecha)
           # worksheet.write(row, 16, partner.dias)

        

        # Close workbook
        workbook.close()

        # Prepare HTTP response with Excel file
        #output.seek(0)
        output.seek(0)
        response.stream.write(output.read())
        output.close()
