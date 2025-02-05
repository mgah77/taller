class EntregaEquipos(models.Model):
    _name = 'entrega.equipos'
    _description = 'Entrega de Equipos de Reemplazo'

    name = fields.Char(string='Número de Entrega', required=True, copy=False, readonly=True, default='Nuevo')
    partner_id = fields.Many2one('res.partner', string='Cliente', required=True)
    ot_id = fields.Many2one(
        'taller.ot',
        string='Orden de Trabajo',
        domain="[('partner_id', '=', partner_id)]",  # Filtra las OT según el cliente seleccionado
        required=True
    )
    fecha_entrega = fields.Date(string='Fecha de Entrega', required=True)
    fecha_devolucion = fields.Date(string='Fecha de Devolución')
    line_ids = fields.One2many('entrega.equipos.line', 'entrega_id', string='Equipos Entregados')
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('entregado', 'Entregado')
    ], string='Estado', default='borrador')

    @api.model
    def create(self, vals):
        if vals.get('name', 'Nuevo') == 'Nuevo':
            vals['name'] = self.env['ir.sequence'].next_by_code('entrega.equipos') or 'Nuevo'
        return super(EntregaEquipos, self).create(vals)

class EntregaEquiposLine(models.Model):
    _name = 'entrega.equipos.line'
    _description = 'Línea de Entrega de Equipos'

    product_id = fields.Many2one(
        'product.product', 
        string='Producto', 
        domain=[('exchange_ok', '=', True)],
        required=True
    )
    cantidad = fields.Float(string='Cantidad', required=True, default=1)
    entrega_id = fields.Many2one('entrega.equipos', string='Entrega')
    state = fields.Selection([
        ('no_devuelto', 'No Devuelto'),
        ('devuelto', 'Devuelto')
    ], string='Estado', default='no_devuelto')
