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
   user = fields.Integer()
   hoy = fields.Datetime(string="Hoy",
                              default=datetime.datetime.now(),
                              required=True)
   
   def print_xlsx(self):
       if self.start_date > self.end_date:
           raise ValidationError('Start Date must be less than End Date')
       data = {
           'start_date': self.start_date,
           'end_date': self.end_date,
           'user': self.env.user.partner_id.id,
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
        suc = self.env.user.property_warehouse_id.id
        
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
        green = workbook.add_format({'font_size': 11, 'bold': False})
        green.set_bg_color('#00EE00')
        green.set_border(1)
        red = workbook.add_format({'font_size': 11, 'bold': False})
        red.set_bg_color('#FF2222')
        red.set_border(1)
        yellow = workbook.add_format({'font_size': 11, 'bold': False})
        yellow.set_bg_color('#FFFF00')
        yellow.set_border(1)
        
        #fechas
        worksheet.set_column_pixels(2, 2, 62)
        worksheet.set_column_pixels(12, 12, 62)
        worksheet.set_column_pixels(16, 16, 62)
        worksheet.set_column_pixels(21, 21, 62)
        worksheet.set_column_pixels(26, 26, 62)
        #nombres
        worksheet.set_column_pixels(3, 3, 100)
        worksheet.set_column_pixels(6, 6, 100)
        worksheet.set_column_pixels(9, 9, 100)
        worksheet.set_column_pixels(13, 13, 100)
        worksheet.set_column_pixels(17, 18, 100)
        worksheet.set_column_pixels(22, 22, 100)
        worksheet.set_column_pixels(25, 25, 100)
        #espacio
        worksheet.set_column_pixels(4, 4, 18 )
        worksheet.set_column_pixels(7, 7, 18)
        worksheet.set_column_pixels(10, 10, 18)
        worksheet.set_column_pixels(14, 14, 18)
        worksheet.set_column_pixels(19, 19, 18)
        worksheet.set_column_pixels(23, 23, 18)

        worksheet.set_column_pixels(27, 27, 65)    

        # Write headers
        worksheet.merge_range(1, 13, 2, 19, 'PLANIFICACION DIARIA', format0)
        worksheet.merge_range(3, 1, 3, 3, 'Inspeccion de balsa', format1)
        worksheet.merge_range(3, 5, 3, 6, 'Contenedores', format1)
        worksheet.merge_range(3, 8, 3, 9, 'Válvulas', format1)
        worksheet.merge_range(3, 11, 3, 13, 'Extintores', format1)
        worksheet.merge_range(3, 15, 3, 18, 'Equipo Seguridad', format1)
        worksheet.merge_range(3, 20, 3, 22, 'Banco CO2', format1)
        worksheet.merge_range(3, 24, 3, 29, 'Textil', format1)

        headers = ['numero', 'fecha_ent', 'glosa','','numero','glosa','','numero','glosa','','numero','fecha_ent','glosa','','numero','fecha_ent','glosa','detalle','','numero','fecha_ent','glosa','','numero','glosa','fecha_ent','cantidad','detalle','local']
        for col, header in enumerate(headers, start=1):
            worksheet.write(4, col, header, formatmin)

        # Write data
        row = 5  # Inicializamos el índice del bucle
        for balsa in balsas:
            if balsa.branch_s == suc:
                if balsa.color == 10:
                    worksheet.write(row, 1, balsa.name, green)
                elif balsa.color == 1:
                    worksheet.write(row, 1, balsa.name, red)
                else:
                    worksheet.write(row, 1, balsa.name, yellow)                
                worksheet.write(row, 2, str(balsa.fecha.strftime("%d-%m-%y")), format2)
                worksheet.write(row, 3, balsa.nave, format2)
                worksheet.write(row, 4, " ")
                row += 1               
        row = 5
        for conte in conten:
            if conte.branch_s == suc:
                if conte.color == 10:
                    worksheet.write(row, 5, conte.name, green)
                elif conte.color == 1:
                    worksheet.write(row, 5, conte.name, red)
                else:
                    worksheet.write(row, 5, conte.name, yellow)
                worksheet.write(row, 6, conte.nave, format2)
                worksheet.write(row, 7, " ")
                row += 1
        row = 5        
        for valvu in valvul:
            if valvu.branch_s == suc:
                if valvu.color == 10:
                    worksheet.write(row, 8, valvu.name, green)
                elif valvu.color == 1:
                    worksheet.write(row, 8, valvu.name, red)
                else:
                    worksheet.write(row, 8, valvu.name, yellow)
                worksheet.write(row, 9, valvu.nave, format2)
                worksheet.write(row, 10, " ")
                row += 1
        row = 5
        for extin in extint:
            if extin.branch_s == suc:
                if extin.color == 10:
                    worksheet.write(row, 11, extin.name, green)
                elif extin.color == 1:
                    worksheet.write(row, 11, extin.name, red)
                else:
                    worksheet.write(row, 11, extin.name, yellow)
                worksheet.write(row, 12, str(extin.fecha.strftime("%d-%m-%y")), format2)
                worksheet.write(row, 13, extin.nave, format2)
                worksheet.write(row, 14, " ")
                row += 1
        row = 5        
        for segur in seguri:
            if segur.branch_s == suc:
                if segur.color == 10:
                    worksheet.write(row, 15, segur.name, green)
                elif segur.color == 1:
                    worksheet.write(row, 15, segur.name, red)
                else:
                    worksheet.write(row, 15, segur.name, yellow)
                worksheet.write(row, 16, str(segur.fecha.strftime("%d-%m-%y")), format2)
                worksheet.write(row, 17, segur.nave, format2)
                worksheet.write(row, 18, segur.item.alias, format2)
                worksheet.write(row, 19, " ")
                row += 1
        row = 5
        for bcoco in bcoco2:
            if bcoco.branch_s == suc:
                if bcoco.color == 10:
                    worksheet.write(row, 20, bcoco.name, green)
                elif bcoco.color == 1:
                    worksheet.write(row, 20, bcoco.name, red)
                else:
                    worksheet.write(row, 20, bcoco.name, yellow)
                worksheet.write(row, 21, str(bcoco.fecha.strftime("%d-%m-%y")), format2)
                worksheet.write(row, 22, bcoco.nave, format2)     
                worksheet.write(row, 23, " ") 
                row += 1  
        row = 5
        for texti in textil:
            if suc == 2:
                if texti.branch_s == suc:
                    if texti.color == 10:
                        worksheet.write(row, 24, texti.name, green)
                    elif texti.color == 1:
                        worksheet.write(row, 24, texti.name, red)
                    else:
                        worksheet.write(row, 24, texti.name, yellow)
                    worksheet.write(row, 25, texti.nave, format2)
                    worksheet.write(row, 26, str(texti.fecha.strftime("%d-%m-%y")), format2)
                    worksheet.write(row, 27, texti.cant, format2) 
                    worksheet.write(row, 28, texti.item.alias, format2)
                    if texti.branch_s == 3:
                        worksheet.write(row, 29, 'ParVial', format2)  
                    elif texti.branch_s == 2:
                        worksheet.write(row, 29, 'Ñuble', format2)    
                    row += 1
            else:
                if texti.color == 10:
                    worksheet.write(row, 24, texti.name, green)
                elif texti.color == 1:
                    worksheet.write(row, 24, texti.name, red)
                else:
                    worksheet.write(row, 24, texti.name, yellow)
                worksheet.write(row, 25, texti.nave, format2)
                worksheet.write(row, 26, str(texti.fecha.strftime("%d-%m-%y")), format2)
                worksheet.write(row, 27, texti.cant, format2) 
                worksheet.write(row, 28, texti.item.alias, format2)
                if texti.branch_s == 3:
                    worksheet.write(row, 29, 'ParVial', format2)  
                elif texti.branch_s == 2:
                    worksheet.write(row, 29, 'Ñuble', format2) 
                row += 1
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
