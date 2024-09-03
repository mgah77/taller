from odoo import models, fields , api , _
import datetime

class Taller_maniobras(models.Model):

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
    nave = fields.Char('Nave', default='MN ')
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
        result = super(Taller_maniobras,self).create(vals)
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
        nombre = self.name + ' ' + self.nave
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
            # Obtener los IDs de los usuarios del campo equipo
            attendees = []
            for user in self.equipo:
                attendee = self.env['calendar.attendee'].create({
                    'partner_id': user.partner_id.id,
                    'event_id': False,  # Se establece a False porque el evento aún no existe
                    'state': 'needs-action',
                })
                attendees.append(attendee.id)                           
            vals = {
                'user_id': self.create_uid.id,
                'allday': False,
                'name': nombre,
                'location': self.lugar.name,
                'privacy': 'public',
                'show_as': 'busy',
                'description': self.obs,
                'active': True, 
                'start': datet,
                'stop' : dafin,
                'attendee_ids': [(6, 0, attendees)],  # Asignar los asistentes al evento
            }
            event = self.env['calendar.event'].create(vals)
            # Actualizar los asistentes con el ID del evento recién creado
            for attendee in event.attendee_ids:
                attendee.write({'event_id': event.id})
                self.env['calendar.event'].create(vals)            
        return  