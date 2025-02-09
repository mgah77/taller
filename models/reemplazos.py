from odoo import models, fields, api

class EntregaEquipos(models.Model):
    _name = 'entrega.equipos'
    _description = 'Entrega de Equipos de Reemplazo'

    name = fields.Char(string='Número de Entrega', required=True, copy=False, readonly=True, default='Nuevo')
    armador = fields.Many2one('res.partner', string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact'), ('is_customer','=',True)]",required=True)
    ot_id = fields.Many2one('taller.ot', string='Orden de Trabajo', domain="[('armador', '=', armador)]", required=True)
    fecha_entrega = fields.Date(string='Fecha de Entrega', required=True)
    fecha_devolucion = fields.Date(string='Fecha de Devolución')
    line_ids = fields.One2many('entrega.equipos.line', 'entrega_id', string='Equipos Entregados')
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('entregado', 'Entregado')
    ], string='Estado', default='borrador')
    sucursel = fields.Selection([('2','Ñuble'),('3','Par Vial')],string='Sucursal',default='2')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('entrega.equipos') or 'Nuevo'
        return super(EntregaEquipos, self).create(vals)

    @api.model
    def default_get(self, fields):
        res = super(EntregaEquipos, self).default_get(fields)
        user = self.env.user
        warehouse_id = user.property_warehouse_id.id
        if warehouse_id:
            res['sucursel'] = str(warehouse_id)
        return res    

    def action_print_entregas(self):
        return self.env.ref('taller.action_report_entrega_equipos').report_action(self)

class EntregaEquiposLine(models.Model):
    _name = 'entrega.equipos.line'
    _description = 'Línea de Entrega de Equipos'

    product_id = fields.Many2one(
        'product.product', 
        string='Producto', 
        domain="[('exchange_ok', '=', True), ('product_tmpl_id.sucursal', '=', parent.sucursel), ('qty_available', '>', 0)]",
        required=True
    )
    cantidad = fields.Float(string='Cantidad', required=True, default=1)
    entrega_id = fields.Many2one('entrega.equipos', string='Entrega')
    state = fields.Selection([
        ('na', ' '),
        ('no_devuelto', 'No Devuelto'),
        ('devuelto', 'Devuelto')
    ], string='Estado', default='na')
