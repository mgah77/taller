from odoo import models, fields , api , _

class Taller_ingreso(models.Model):

    _name = 'taller.ot'
    _description = 'Ingreso Taller'

    name = fields.Char(string="Nro ", readonly=True, default='New', copy=False)

    fecha_recep = fields.Date('Fecha de Recepcion')
    fecha_entr = fields.Date('Fecha de Entrega', index=True)
    armador = fields.Many2one('res.partner',string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact')]")
    nave = fields.Char('Nave')
    obs = fields.Char('Observaciones')
    ot_line = fields.One2many(comodel_name = 'taller.ot.line',inverse_name = 'ot_line_id', string = 'Lineas OT',copy=True, auto_join=True)
    user = fields.Char(string = 'Recepciona')
    user_branch = fields.Integer(string = 'Current Branch', compute="_compute_sucursal")
    contacto = fields.Many2one('res.partner', string='Contacto')
    contacto_fono = fields.Char('Fono')
    contacto_mail = fields.Char('e-mail')
    maniobra = fields.Boolean(string = 'Maniobra')
    lugar = fields.Many2one('res.city', string = 'Lugar')
    replace = fields.Boolean(string = 'Reemplazo')

    def _compute_sucursal(self):
        for record in self:
            record['user_branch']=self.env.user.property_warehouse_id
            return

    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.ot') or 'New'
            vals['user']=self.env.user.partner_id.name
        result = super(Taller_ingreso,self).create(vals)
        return result

    @api.onchange('contacto')
    def onchange_partner_id(self):
        if self.contacto:
            if self.contacto.phone:
                self.contacto_fono = self.contacto.phone
            elif self.contacto.mobile:
                self.contacto_fono = self.contacto.mobile
            self.contacto_mail = self.contacto.email
        else:
            self.contacto_fono = False
            self.contacto_mail = False

    @api.onchange('ot_line')
    def _compute_fecha(self):
        """calcula cfu al cambiar linea"""
        if self.fecha_entr:
            for line in self.ot_line:
                line.fecha_entr = self.fecha_entr
                

class Taller_ot_line(models.Model):
    _name = 'taller.ot.line'
    _description = 'lineas OT'

    ot_line_id = fields.Many2one(comodel_name='taller.ot', string='lineas ot id', required=True, ondelete='cascade', index=True, copy=False)
    item = fields.Many2one('product.template', string="Nombre Item")
    obs = fields.Char('Observaciones')
    serie = fields.Integer('Serie')
    cant = fields.Integer(string='Cantidad', default=1)
    fecha_entr = fields.Date('Fecha de Entrega', related="ot_line_id.fecha_entr", store=True)
    nave = fields.Char('Nave', compute="_compute_nave")
    depto = fields.Many2one('taller.depto.rel', string='Departamento', related='item.depto', store=True)

    def _compute_fecha_entrega(self):
        for line in self:
            line.fecha_entr = line.ot_line_id.fecha_entr

    def _compute_nave(self):
        for line in self:
            line.nave = line.ot_line_id.nave
