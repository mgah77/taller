from odoo import models, fields , api


class Taller_ingreso(models.Model):

    _name = 'taller.ot'
    _description = 'Ingreso Taller'

    name = fields.Char(string="Nro ", readonly=True, default='New', copy=False)

    fecha_recep = fields.Date('Fecha de Recepcion')
    fecha_entr = fields.Date('Fecha de Entrega')
    armador = fields.Many2one('res.partner',string='Armador')
    nave = fields.Char('Nave')
    obs = fields.Char('Observaciones')
    ot_line = fields.One2many('taller.ot.line','ot_line_id', string = 'Lineas OT')
    user = fields.Integer(string = 'Current User', compute="_compute_user")
    user_branch = fields.Integer(string = 'Current Branch', compute="_compute_sucursal")
    contacto = fields.Many2one('res.partner', string='Contacto')
    maniobra = fields.Boolean(string='Maniobra')
    lugar = fields.Many2one('res.city', string='Lugar')
    replace = fields.Boolean(string='Reemplazo')

    def _compute_sucursal(self):
        for record in self:
            record['user_branch']=self.env.user.property_warehouse_id
            return

    def _compute_user(self):
        for record in self:
            record['user']=self.env.user.partner_id
            return

    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.ot') or 'New'
        result = super(Taller_ingreso,self).create(vals)
        return result


class Taller_ot_line(models.Model):
    _name = 'taller.ot.line'
    _description = 'lineas OT'

    ot_line_id = fields.Many2one('taller.ot', string='lineas ot id')
    item = fields.Many2one('product.product', string="Nombre Item")
    obs = fields.Char('Observaciones')
    serie = fields.Integer('Serie')
    cant = fields.Integer(string = 'Cantidad', default = 1)
