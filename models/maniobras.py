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
    obs = fields.Text('Observaciones')
    sucursal = fields.Char('Sucursal', compute="_compute_sucursal")
    estado = fields.Selection([
        ("pen","Pendiente"),
        ("rea","Realizado"),
        ("can","Cancelado")], default='pen'
    )
    lugar = fields.Many2one('taller.lugar.rel', string='Lugar')
    equipo = fields.Many2many('res.partner',string='Equipo' , domain="[('partner_share', '=', False)]")
    user = fields.Char(string = 'Recepciona', default='Sala de Ventas')
    sucursel = fields.Selection([('2','Ñuble'),('3','Par Vial')],string='Sucursal',default='2')

    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']=self.env['ir.sequence'].next_by_code('abr.ot') or 'New' 
            vals['user']=self.env.user.partner_id.name
            vals['user_branch'] = self.env.user.property_warehouse_id
            warehouse_id = str(self.env.user.property_warehouse_id.id)  # Convertimos a string para comparar
            if warehouse_id in ['2', '3']:                
                vals['sucursel'] = warehouse_id   
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

            observaciones_html = self.obs.replace('\n', '<br/>')  # Convertir saltos de línea en <br/>                      

            # Crear el evento primero
            event_vals = {
                'user_id': self.create_uid.id,
                'allday': False,
                'name': nombre,
                'location': self.lugar.name,
                'privacy': 'public',
                'show_as': 'busy',
                'description': observaciones_html,
                'active': True,
                'start': datet,
                'stop': dafin,
            }
            event = self.env['calendar.event'].create(event_vals)
            
            if event:
                # Crear asistentes y asegurarse de que se asocien correctamente al evento
                attendees = []
                for partner in self.equipo:
                    attendee = self.env['calendar.attendee'].create({
                        'partner_id': partner.id,
                        'event_id': event.id,
                        'state': 'needsAction',
                    })
                    attendees.append(attendee.partner_id.id)
                
                # Actualizar la relación Many2many manualmente
                event.write({'partner_ids': [(6, 0, attendees)]})
            ot_vals = {
                'armador': self.armador,
                'user_branch': self.user_branch,
                'name': self.name,
                'location': self.lugar,
                'nave': self.nave,
                'user': self.user,
                'obs': observaciones_html,
                'sucursel': self.sucursel,
                'fecha_recep': self.fecha,
                'stop': dafin,
            }
            
        return