from odoo import models, fields , api , _
import datetime

class Taller_ingreso(models.Model):

    _name = 'taller.maniobras'
    _description = 'Maniobras Taller'

    name = fields.Char(string="Nro ", readonly=True, default='New', copy=False)
    armador = fields.Many2one('res.partner',string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact')]")
    user_branch = fields.Integer(string = 'Current Branch',default='2')
    fecha = fields.Date('Fecha', index=True)
    horario = fields.Selection([
        ("am","AM"),
        ("pm","PM"),
        ("ap","AM/PM")
        ], default='xc'
    )
    nave = fields.Char('Nave')
    obs = fields.Char('Observaciones')
    sucursal = fields.Char('Sucursal', compute="_compute_sucursal")
    estado = fields.Selection([
        ("pen","Pendiente"),
        ("rea","Realizado"),
        ("can","Cancelado")], default='pen'
    )
    lugar = fields.Many2one('taller.lugar.rel', string='Lugar')
    equipo = fields.Many2many('res.partner',string='Equipo' , domain="[('partner_share', '=', False)]")

    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.ot') or 'New' 
            warehouse_id = str(self.env.user.property_warehouse_id.id)  # Convertimos a string para comparar
            if warehouse_id in ['2', '3']:
                vals['user_branch'] = warehouse_id   
        result = super(Taller_ingreso,self).create(vals)
        return result

    
    def _compute_sucursal(self):
        for line in self:
            if line.user_branch == 2:
                line.sucursal = 'Ñuble'
            elif line.user_branch == 3:
                line.sucursal = 'Par Vial'    

    def guardar(self):
        self.write({})

   
    def calendario(self):
        if self.armador:
            if self.horario == 'am':
                datet = datetime.datetime.combine(self.fecha, datetime.time(13, 0))   
                dafin = datetime.datetime.combine(self.fecha, datetime.time(17, 0))
            elif self.horario == 'pm':
                datet = datetime.datetime.combine(self.fecha, datetime.time(18, 0))   
                dafin = datetime.datetime.combine(self.fecha, datetime.time(22, 0))
            elif self.horario == 'ap':
                datet = datetime.datetime.combine(self.fecha, datetime.time(13, 0))   
                dafin = datetime.datetime.combine(self.fecha, datetime.time(22, 0))                            
            vals = {
                'user_id': self.create_uid.id,
                'allday': False,
                'name': self.name + ' ' + self.nave,
                'location': self.lugar.name,
                'privacy': 'public',
                'show_as': 'busy',
                'description': self.obs,
                'active': True, 
                'start': datet,
                'stop' : dafin               
                
            }
            self.env['calendar.event'].create(vals)    
        return  