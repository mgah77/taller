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
