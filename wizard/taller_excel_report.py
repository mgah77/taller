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
        formatmin = workbook.add_format({'font_size': 8, 'align': 'center', 'bold': False})
        format2 = workbook.add_format({'font_size': 11, 'bold': False})

        format2.set_border(1)

        #colores
               
        format1.set_bg_color('#B4C6E7')
        color_format0 = workbook.add_format()       
        color_format0.set_bg_color('#FFFFFF')


        #fechas
        worksheet.set_column_pixels(2, 2, 60)
        worksheet.set_column_pixels(12, 12, 60)
        worksheet.set_column_pixels(17, 17, 60)
        worksheet.set_column_pixels(22, 22, 60)
        #nombres
        worksheet.set_column_pixels(3, 3, 100)
        worksheet.set_column_pixels(6, 6, 100)
        worksheet.set_column_pixels(9, 9, 100)
        worksheet.set_column_pixels(13, 13, 100)
        worksheet.set_column_pixels(18, 19, 100)
        worksheet.set_column_pixels(23, 23, 100)
        worksheet.set_column_pixels(26, 26, 100)
        #espacio
        worksheet.set_column_pixels(4, 4, 20 )
        worksheet.set_column_pixels(7, 7, 20)
        worksheet.set_column_pixels(10, 10, 20)
        worksheet.set_column_pixels(15, 15, 20)
        worksheet.set_column_pixels(20, 20, 20)
        worksheet.set_column_pixels(24, 24, 20)



        # Write headers
        worksheet.merge_range(1, 13, 2, 19, 'PLANIFICACION DIARIA', format0)
        worksheet.merge_range(3, 1, 3, 3, 'Inspeccion de balsa', format1)
        worksheet.merge_range(3, 5, 3, 6, 'Contenedores', format1)
        worksheet.merge_range(3, 8, 3, 9, 'Válvulas', format1)
        worksheet.merge_range(3, 11, 3, 14, 'Extintores', format1)
        worksheet.merge_range(3, 16, 3, 19, 'Equipo Seguridad', format1)
        worksheet.merge_range(3, 21, 3, 23, 'Banco CO2', format1)
        worksheet.merge_range(3, 25, 3, 30, 'Textil', format1)

        headers = ['numero', 'fecha_ent', 'glosa','','numero','glosa','','numero','glosa','','numero','fecha_ent','glosa','obs','','numero','fecha_ent','glosa','detalle','','numero','fecha_ent','glosa','','numero','glosa','fecha_ent','cantidad','detalle','local']
        for col, header in enumerate(headers, start=1):
            worksheet.write(4, col, header, formatmin)

        # Write data
        for row, balsas in enumerate(balsas, start=5):
            if balsas['color'] = 10:
                worksheet.write(row, 1, balsas.name, formatmin)
            else:
                worksheet.write(row, 1, balsas.name, format2)
            worksheet.write(row, 2, str(balsas.fecha.strftime("%d-%m-%y")), format2)
            worksheet.write(row, 3, balsas.nave, format2)
            worksheet.write(row, 4, " ")

        for row, conten in enumerate(conten, start=5):
            worksheet.write(row, 5, conten.name, format2)
            worksheet.write(row, 6, conten.nave, format2)
            worksheet.write(row, 7, " ")
        
        for row, valvul in enumerate(valvul, start=5):
            worksheet.write(row, 8, valvul.name, format2)
            worksheet.write(row, 9, valvul.nave, format2)
            worksheet.write(row, 10, " ")

        for row, extint in enumerate(extint, start=5):
            worksheet.write(row, 11, extint.name, format2)
            worksheet.write(row, 12, str(extint.fecha.strftime("%d-%m-%y")), format2)
            worksheet.write(row, 13, extint.nave, format2)
            worksheet.write(row, 14, extint.obs, format2)
            worksheet.write(row, 15, " ")

        for row, seguri in enumerate(seguri, start=5):
            worksheet.write(row, 16, seguri.name, format2)
            worksheet.write(row, 17, str(seguri.fecha.strftime("%d-%m-%y")), format2)
            worksheet.write(row, 18, seguri.nave, format2)
            worksheet.write(row, 19, seguri.item.alias, format2)

        for row, bcoco2 in enumerate(bcoco2, start=5):
            worksheet.write(row, 21, bcoco2.name, format2)
            worksheet.write(row, 22, str(bcoco2.fecha.strftime("%d-%m-%y")), format2)
            worksheet.write(row, 23, bcoco2.nave, format2)     
            worksheet.write(row, 24, " ")   

        for row, textil in enumerate(textil, start=5):
            worksheet.write(row, 25, textil.name, format2)
            worksheet.write(row, 26, textil.nave, format2)
            worksheet.write(row, 27, str(textil.fecha.strftime("%d-%m-%y")), format2)
            worksheet.write(row, 28, textil.cant, format2) 
            worksheet.write(row, 29, textil.item.alias, format2)  
            worksheet.write(row, 30, textil.branch_s, format2)  


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
