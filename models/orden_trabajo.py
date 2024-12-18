from odoo import models, fields , api , _
from odoo.exceptions import ValidationError
import datetime

class Taller_ingreso(models.Model):

    _name = 'taller.ot'
    _description = 'Ingreso Taller'

    name = fields.Char(string="Nro ", readonly=True, default='Nuevo', copy=False)

    fecha_recep = fields.Date('Fecha de Recepción', default=fields.Date.context_today)
    fecha_entr = fields.Date('Fecha de Entrega', index=True)
    armador = fields.Many2one('res.partner',string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact'), ('is_customer','=',True)]")
    nave = fields.Char('Nave',default='MN ')
    obs = fields.Html('Observaciones')
    ot_line = fields.One2many(comodel_name = 'taller.ot.line',inverse_name = 'ot_line_id', string = 'Lineas OT',copy=True, auto_join=True)
    user = fields.Char(string = 'Recepciona', default='Sala de Ventas')
    user_branch = fields.Integer(string = 'Current Branch', default='3')
    contacto = fields.Many2one('res.partner', string='Contacto')
    contacto_fono = fields.Char('Fono')
    contacto_mail = fields.Char('e-mail')
    maniobra = fields.Boolean(string = 'Maniobra')
    event_ids = fields.Many2many('calendar.event',string="Maniobras", readonly= True)
    lugar = fields.Many2one('taller.lugar.rel', string = 'Lugar')
    replace = fields.Boolean(string = 'Reemplazo')
    reobs = fields.Html('Observaciones')
    viewer = fields.Integer('Current User', compute="_compute_viewer")
    sucursal = fields.Char('Sucursal', compute="_compute_sucursal")
    sucursel = fields.Selection([('2','Ñuble'),('3','Par Vial')],string='Sucursal',default='2')
    state = fields.Selection([
        ('borr','Borrador'),
        ('tall','En Taller'),        
        ('cert','Certificado'),
        ('entr','Entregado'),
        ('coti','Cotizado'),
        ('fact','Facturado')
        ],string='Status',default='borr')

    def _compute_sucursal(self):
        for line in self:            
            if line.sucursel == 2:
                line.sucursal = 'Ñuble'
            elif line.sucursel == 3:
                line.sucursal = 'Par Vial'
            

    def _compute_viewer(self):
        for record in self:
            record['viewer']=self.env.user.property_warehouse_id
            return

    @api.model
    def create(self,vals):
        if vals.get('name','Nuevo')=='Nuevo':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.ot') or 'Nuevo'
            vals['user']=self.env.user.partner_id.name
            vals['user_branch']=self.env.user.property_warehouse_id
            warehouse_id = str(self.env.user.property_warehouse_id.id)  # Convertimos a string para comparar
            if warehouse_id in ['2', '3']:
                vals['sucursel'] = warehouse_id
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

    def guardar(self):
    # Validar si los campos están llenos
        if not self.ot_line:
            raise ValidationError("Falta ingresar trabajos.")
        
        if not self.fecha_entr:
            raise ValidationError("Falta ingresar la fecha de entrega.")
        
        # Si ambos campos están presentes, cambiar el estado
        self.state = 'tall'
        self.write({})
        for rec in self.ot_line:
            if rec.state == 'borr':
                rec.state = 'tall'
                rec.state_old = 'tall'
        return True




class Taller_ot_line(models.Model):
    _name = 'taller.ot.line'
    _description = 'lineas OT'

    ot_line_id = fields.Many2one('taller.ot', string='lineas ot id', required=True, ondelete='cascade', index=True, copy=False)
    name = fields.Char('OT', compute="_compute_ot")
    item = fields.Many2one('product.template', string="Nombre Item", domain="[('sale_ok', '=', True)]" )
    obs = fields.Char('Observaciones')
    serie = fields.Char('Serie')
    cant = fields.Integer(string='Cantidad', default=1)
    fecha = fields.Date(related='ot_line_id.fecha_entr', store=True)
    fecha_recep = fields.Date(related='ot_line_id.fecha_recep')
    nave = fields.Char('Nave', compute="_compute_nave")
    depto = fields.Many2one('taller.depto.rel', string='Departamento', related='item.depto', store=True)
    armador = fields.Many2one('res.partner', string='Armador', related='ot_line_id.armador')
    state = fields.Selection([
        ('borr','Borrador'),
        ('tall','En Taller'),        
        ('cert','Certificado'),
        ('entr','Entregado'),
        ('coti','Cotizado'),
        ('fact','Facturado')], string='Estado', default='borr')
    state_old = fields.Selection([
        ('borr','Borrador'),
        ('tall','En Taller'),        
        ('cert','Certificado'),
        ('entr','Entregado'),
        ('coti','Cotizado')], string='Estado', default='borr')
    color = fields.Integer('color', compute ="_compute_dias")
    hoy = fields.Date(string="From Date", compute = "_compute_hoy")
    dias = fields.Integer(compute = "_compute_dias")
    branch = fields.Integer(compute = "_compute_branch")
    branch_s = fields.Integer(compute = "_compute_branch1", store=True)
    alias = fields.Char(compute = "_compute_alias")
    sucursal = fields.Selection([
        ('2','Ñuble'),
        ('3','Par Vial')],string='Sucursal')

    def _compute_branch1(self):
        for line in self:
            line.branch_s = line.ot_line_id.sucursel
        return

    def _compute_branch(self):
        for line in self:
            line.branch = line.ot_line_id.sucursel
            if line.branch == 2:
                line.sucursal = '2'
            elif line.branch == 3:
                line.sucursal = '3'

    def _compute_nave(self):
        for line in self:
            line.nave = line.ot_line_id.nave

    def _compute_ot(self):
        for line in self:
            line.name = line.ot_line_id.name

    def _compute_hoy(self):
        for record in self:
            record ['hoy'] = datetime.datetime.now ()

    def _compute_alias(self):
        for record in self:
            record ['alias'] = record.item.alias

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

    @api.depends('ot_line_id')
    def _compute_branch1(self):
        for line in self:
            line.branch_s = line.ot_line_id.sucursel
            if line.branch_s == 2:
                line.sucursal = '2'
            elif line.branch_s == 3:
                line.sucursal = '3'
        return

    @api.onchange('state')
    def onchange_state(self):
        if self.state == 'cert' and self.state_old not in ['tall', 'cert']:
            raise ValidationError("1No puede volver a ese estado.")
            return
        elif self.state == 'borr' and self.state_old != 'borr':
            raise ValidationError("2No puede volver a ese estado.")
            return
        elif self.state == 'tall' and self.state_old not in ['borr', 'tall']:
            raise ValidationError("3No puede volver a ese estado.")
            return        
    
    def write(self, vals):
        if 'state' in vals:
            vals['state_old'] = self.state  # Guarda el estado actual antes de cambiarlo
        return super(taller.ot.line, self).write(vals)
    
