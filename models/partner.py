from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    taller = fields.Boolean(string='Taller', default=False)