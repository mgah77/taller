from odoo import models, fields , api , _

class Maestro_depto(models.Model):
    _name = 'taller.depto.rel'
    _description = 'taller deptos'

    name = fields.Char('depto', default='New', readonly=True)

class Maestro_lugar(models.Model):
    _name = 'taller.lugar.rel'
    _description = 'taller lugar'

    name = fields.Char('Lugar', default='Puerto Montt')
       