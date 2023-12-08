from odoo import models, fields , api , _
import datetime

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
    user_branch = fields.Integer(string = 'Current Branch')
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
            vals['user_branch']=self.env.user.property_warehouse_id
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



class Taller_ot_line(models.Model):
    _name = 'taller.ot.line'
    _description = 'lineas OT'

    ot_line_id = fields.Many2one(comodel_name='taller.ot', string='lineas ot id', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char('OT', compute="_compute_ot")
    item = fields.Many2one('product.template', string="Nombre Item")
    obs = fields.Char('Observaciones')
    serie = fields.Integer('Serie')
    cant = fields.Integer(string='Cantidad', default=1)
    fecha = fields.Date(related='ot_line_id.fecha_entr', store=True)
    fecha_recep = fields.Date(related='ot_line_id.fecha_recep')
    nave = fields.Char('Nave', compute="_compute_nave")
    depto = fields.Many2one('taller.depto.rel', string='Departamento', related='item.depto', store=True)
    armador = fields.Many2one('res.partner', string='Armador', related='ot_line_id.armador')
    state = fields.Selection([
        ('tall','En Taller'),
        ('fina','Terminado'),
        ('cert','Certificado'),
        ('coti','Cotizado'),
        ('fact','Facturado')],string='Status',default='tall')
    color = fields.Integer('color', compute ="_compute_dias")
    hoy = fields.Date(string="From Date", compute = "_compute_hoy")
    dias = fields.Integer(compute = "_compute_dias")
    branch = fields.Integer(compute = "_compute_branch")

    def _compute_branch(self):
        for line in self:
            line.branch = line.ot_line_id.user_branch

    def _compute_nave(self):
        for line in self:
            line.nave = line.ot_line_id.nave

    def _compute_ot(self):
        for line in self:
            line.name = line.ot_line_id.name

    def _compute_hoy(self):
        for record in self:
            record ['hoy'] = datetime.datetime.now ()

    def _compute_dias(self):
        for record in self:
            record.dias = abs((record.hoy - record.fecha).days)
            if (record.dias > 7):
                record.color = 10
            elif (record.dias < 8 and record.dias > 1):
                record.color = 3
            else:
                record.color = 1
            if (record.hoy > record.fecha):
                record.color = 1


    viewer = fields.Integer('Current User', compute="_compute_viewer")

    def _compute_viewer(self):
        for record in self:
            record['viewer']=self.env.user.property_warehouse_id
            return
        
    @api.model
    def get_viewer_records(self):
        return self.search([('branch', '=', 'viewer')])