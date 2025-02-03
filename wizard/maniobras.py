from odoo import models, fields, api, _
import datetime

class WizardManiobras(models.TransientModel):
    _name = 'taller.maniobras.wizard'
    _description = 'Wizard para Agendar Maniobras'

    armador = fields.Many2one('res.partner', string='Armador', domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact'), ('is_customer','=',True)]", required=True)
    fecha = fields.Date('Fecha', index=True, required=True)
    horario = fields.Selection([
        ("am", "AM"),
        ("pm", "PM"),
        ("ap", "AM/PM")
    ], required=True)
    nave = fields.Char('Nave', required=True)
    obs = fields.Text('Observaciones', default=' ')
    lugar = fields.Many2one('taller.lugar.rel', string='Lugar', required=True)
    equipo = fields.Many2many('res.partner', string='Equipo', domain="[('partner_share', '=', False)]", required=True)

    def confirmar_maniobra(self):
        """Crea el evento en el calendario sin almacenar un registro en la BD."""
        self.ensure_one()
        nombre = self.nave
        if self.horario == 'am':
            datet = datetime.datetime.combine(self.fecha, datetime.time(13, 0))   
            dafin = datetime.datetime.combine(self.fecha, datetime.time(17, 0))
        elif self.horario == 'pm':
            datet = datetime.datetime.combine(self.fecha, datetime.time(18, 0))   
            dafin = datetime.datetime.combine(self.fecha, datetime.time(22, 0))
        elif self.horario == 'ap':
            datet = datetime.datetime.combine(self.fecha, datetime.time(13, 0))   
            dafin = datetime.datetime.combine(self.fecha, datetime.time(22, 0))  

        event_vals = {
            'user_id': self.env.uid,
            'allday': False,
            'name': nombre,
            'location': self.lugar.name,
            'privacy': 'public',
            'show_as': 'busy',
            'description': (self.obs or '').replace('\n', '<br/>'),
            'active': True,
            'start': datet,
            'stop': dafin,
        }
        event = self.env['calendar.event'].create(event_vals)
        
        attendees = [(0, 0, {'partner_id': partner.id, 'state': 'needsAction'}) for partner in self.equipo]
        event.write({'partner_ids': [(6, 0, self.equipo.ids)]})
        
        return {'type': 'ir.actions.act_window_close'}