from odoo import models, fields , api , _

class Taller_ingreso(models.Model):

    _name = 'taller.ot'
    _description = 'Ingreso Taller'

    name = fields.Char(string="Nro ", readonly=True, default='New', copy=False)

    fecha_recep = fields.Date('Fecha de Recepcion')
    fecha_entr = fields.Date('Fecha de Entrega')
    armador = fields.Many2one('res.partner',string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact')]")
    nave = fields.Char('Nave')
    obs = fields.Char('Observaciones')
    ot_line = fields.One2many(comodel_name = 'taller.ot.line',inverse_name = 'ot_line_id', string = 'Lineas OT',copy=True, auto_join=True)
    user = fields.Char(string = 'Recepciona', compute="_compute_user")
    user_branch = fields.Integer(string = 'Current Branch', compute="_compute_sucursal")
    contacto = fields.Many2one('res.partner', string='Contacto')
    maniobra = fields.Boolean(string = 'Maniobra')
    lugar = fields.Many2one('res.city', string = 'Lugar')
    replace = fields.Boolean(string = 'Reemplazo')

    def _compute_sucursal(self):
        for record in self:
            record['user_branch']=self.env.user.property_warehouse_id
            return

    def _compute_user(self):
        for record in self:
            record['user']=self.env.user.partner_id.name
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
    _rec_names_search = ['ot_line_id.name']

    ot_line_id = fields.Many2one(comodel_name = 'taller.ot', string = 'lineas ot id', required=True, ondelete='cascade', index=True, copy=False)
    item = fields.Many2one('product.product', string = "Nombre Item")
    obs = fields.Char('Observaciones')
    serie = fields.Integer('Serie')
    cant = fields.Integer(string = 'Cantidad', default = 1)
    fecha_entr = fields.Date('Fecha de Entrega', compute="_compute_fecha_entrega")
    nave = fields.Char('Nave', compute="_compute_nave")


    def _compute_fecha_entrega(self):
        for line in self:
            line['fecha_entr'] = line.ot_line_id.fecha_entr
        return

    def _compute_nave(self):
        for line in self:
            line['nave'] = line.ot_line_id.nave
        return
