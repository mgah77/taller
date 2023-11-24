from odoo import models, fields , api , _

class Maestro_depto(models.Model):
    _name = 'taller.depto.rel'
    _description = 'taller deptos'

    depto = fields.Char('depto', default='New', index=True)
