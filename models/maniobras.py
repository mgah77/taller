from odoo import models, fields , api , _
import datetime

class Taller_ingreso(models.Model):

    _name = 'taller.maniobras'
    _description = 'Maniobras Taller'

    name = fields.Char(string="Nro ", readonly=True, default='New', copy=False)
    user_branch = fields.Integer(string = 'Current Branch')
    fecha = fields.Date('Fecha', index=True)
    horario = fields.Selection([
        ("am","AM"),
        ("pm","PM"),
        ("ap","AM/PM"),
        ("xc","X Confirmar")]
    )
    nave = fields.Char('Nave')
    obs = fields.Char('Observaciones')
    sucursal = fields.Char('Sucursal', compute="_compute_sucursal")
    estado = fields.Selection([
        ("pen","Pendiente"),
        ("rea","Realizado"),
        ("can","Cancelado")]
    )

    @api.model
    def create(self,vals):
        if vals.get('name','New')=='New':
            vals['name']='OK'
            vals['user_branch']=self.env.user.property_warehouse_id
        result = super(Taller_ingreso,self).create(vals)
        return result

    
    def _compute_sucursal(self):
        for line in self:
            if line.user_branch == 2:
                line.sucursal = 'Ñuble'
            elif line.user_branch == 3:
                line.sucursal = 'Par Vial'    