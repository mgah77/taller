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
    ot_check = fields.Boolean(string="Usar OT existente")
    old_ot = fields.Many2one('taller.ot', string="N° OT", domain="[('armador', '=', armador)]")
    user_branch = fields.Integer(string='Current Branch', default=2)
    sucursel = fields.Selection([('2', 'Ñuble'), ('3', 'Par Vial')], string='Sucursal', default='2')

    @api.model
    def default_get(self, fields):
        res = super(WizardManiobras, self).default_get(fields)
        user = self.env.user
        warehouse_id = user.property_warehouse_id.id
        if warehouse_id:
            res['sucursel'] = str(warehouse_id)
        return res

    @api.onchange('old_ot')
    def _onchange_old_ot(self):
        if self.ot_check and self.old_ot:
            self.nave = self.old_ot.nave
            self.sucursel = self.old_ot.sucursel

    @api.onchange('armador')
    def _onchange_armador(self):
        self.old_ot = False

    def confirmar_maniobra(self):
        """Crea el evento en el calendario y genera una OT en taller.ot o usa una existente."""
        self.ensure_one()
        nombre = (self.old_ot.name if self.ot_check and self.old_ot else self.env['ir.sequence'].next_by_code('abr.ot') or 'Nuevo') + ' ' + self.nave
        
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
        
        if self.ot_check and self.old_ot:
            ot = self.old_ot
        else:
            ot_vals = {
                'armador': self.armador.id,
                'name': nombre.split(' ')[0],
                'lugar': self.lugar.id,
                'nave': self.nave,
                'user': self.env.user.partner_id.name,
                'obs': (self.obs or '').replace('\n', '<br/>'),
                'fecha_recep': self.fecha,
                'state': 'borr',
                'maniobra': True,
                'user_branch': self.user_branch,
                'sucursel': self.sucursel,
            }
            ot = self.env['taller.ot'].create(ot_vals)
        
        ot.write({'event_ids': [(4, event.id)]})
        return {'type': 'ir.actions.act_window_close'}