from odoo import models, fields , api , _

class Maestro_depto(models.Model):
    _name = 'taller.depto.rel'
    _description = 'taller deptos'

    name = fields.Char('depto', default='New', readonly=True)
