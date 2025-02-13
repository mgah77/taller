from odoo import models, fields, api


class EntregaEquiposLine(models.Model):
    _name = 'entrega.equipos.line'
    _description = 'Línea de Entrega de Equipos'

    warehouse_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación del almacén',
        compute='_compute_warehouse_location_id',
        store=False,  # No es necesario almacenarlo en la base de datos
    )

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        domain="[('exchange_ok', '=', True), ('qty_available', '>', 0), ('stock_quant_ids.location_id', '=', warehouse_location_id)]",
        required=True,
    )

    cantidad = fields.Float(string='Cantidad', required=True, default=1)
    entrega_id = fields.Many2one('entrega.equipos', string='Entrega')
    state = fields.Selection([
        ('no_devuelto', 'No Devuelto'),
        ('devuelto', 'Devuelto')
    ], string='Estado', default='no_devuelto')

    @api.depends('entrega_id.armador')
    def _compute_warehouse_location_id(self):
        for record in self:
            user = self.env.user
            warehouse = user.property_warehouse_id

            if warehouse:
                # Si el usuario tiene una bodega asignada, usamos su ubicación de stock
                record.warehouse_location_id = warehouse.lot_stock_id.id
            else:
                # Si el usuario no tiene bodega, usamos el valor de sucursel para encontrar la bodega correspondiente
                sucursel_value = record.entrega_id.sucursel  # Obtener el valor de sucursel
                if sucursel_value:
                    # Buscar la bodega correspondiente al valor de sucursel
                    warehouse = self.env['stock.warehouse'].search([('id', '=', int(sucursel_value))], limit=1)
                    if warehouse:
                        # Usar la ubicación de stock de la bodega encontrada
                        record.warehouse_location_id = warehouse.lot_stock_id.id
                    else:
                        # Si no se encuentra la bodega, dejar el campo vacío
                        record.warehouse_location_id = False
                else:
                    # Si no hay valor de sucursel, dejar el campo vacío
                    record.warehouse_location_id = False