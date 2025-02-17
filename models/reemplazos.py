from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EntregaEquipos(models.Model):
    _name = 'entrega.equipos'
    _description = 'Entrega de Equipos de Reemplazo'

    name = fields.Char(string='Número de Entrega', required=True, copy=False, readonly=True, default='Nuevo')
    armador = fields.Many2one('res.partner', string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact'), ('is_customer','=',True)]",required=True)
    ot_id = fields.Many2one('taller.ot', string='Orden de Trabajo', domain="[('armador', '=', armador)]", required=True)
    fecha_entrega = fields.Date(string='Fecha de Entrega', required=True)
    fecha_devolucion = fields.Date(string='Fecha de Devolución', required=True)
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
        """Genera el reporte y crea una salida de inventario en borrador."""
        
        # Escribir el número de entrega en el campo reobs de la OT
        if self.ot_id:
            observaciones_actuales = self.ot_id.reobs or ""
            enlace_entrega = (
                f'<a href="/web#id={self.id}&model=entrega.equipos&view_type=form">'
                f'Número de entrega: {self.name}</a>'
            )
            nueva_observacion = f"{observaciones_actuales}{enlace_entrega}<br>"
            self.ot_id.write({'reobs': nueva_observacion, 'replace': True})

        # Obtener la ubicación de stock del usuario
        warehouse = self.env.user.property_warehouse_id
        if not warehouse:
            raise ValidationError("No tienes una bodega asignada.")

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', '=', warehouse.id)
        ], limit=1)

        if not picking_type:
            raise ValidationError("No se encontró un tipo de operación de salida para tu bodega.")

        # Crear el albarán de salida en borrador
        picking_vals = {
            'partner_id': self.armador.id,
            'picking_type_id': picking_type.id,
            'location_id': warehouse.lot_stock_id.id,  # Ubicación de salida
            'location_dest_id': self.armador.property_stock_customer.id,  # Ubicación del cliente
            'origin': self.name,
        }

        picking = self.env['stock.picking'].create(picking_vals)

        # Crear movimientos de stock en el albarán
        move_lines = []
        for line in self.line_ids:
            move_vals = {
                'name': line.product_id.display_name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.cantidad,
                'product_uom': line.product_id.uom_id.id,
                'location_id': warehouse.lot_stock_id.id,
                'location_dest_id': self.armador.property_stock_customer.id,
                'picking_id': picking.id,
            }
            move_lines.append((0, 0, move_vals))

        picking.write({'move_ids_without_package': move_lines})

        # Generar el reporte
        return self.env.ref('taller.action_report_entrega_equipos').report_action(self)



    # Validación para la fecha de devolución
    @api.constrains('fecha_entrega', 'fecha_devolucion')
    def _check_fecha_devolucion(self):
        for record in self:
            if record.fecha_devolucion and record.fecha_entrega:
                if record.fecha_devolucion < record.fecha_entrega:
                    raise ValidationError(
                        "La fecha de devolución no puede ser menor que la fecha de entrega."
                    )

class EntregaEquiposLine(models.Model):
    _name = 'entrega.equipos.line'
    _description = 'Línea de Entrega de Equipos'

    product_id = fields.Many2one(
        'product.product',
        string='Producto',
        domain="[('exchange_ok', '=', True), ('qty_available', '>', 0), ('stock_quant_ids.location_id', '=', warehouse_location_id)]",
        required=True,
    )
    cantidad = fields.Float(string='Cantidad', required=True, default=1)
    warehouse_location_id = fields.Many2one(
        'stock.location',
        string='Ubicación del almacén',
        compute='_compute_warehouse_location_id',
        store=False,
    )
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

    @api.onchange('product_id', 'cantidad')
    def _onchange_cantidad_stock(self):
        for record in self:
            if record.product_id and record.warehouse_location_id and record.cantidad > 0:
                # Obtener la cantidad disponible en stock para el producto y la ubicación
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.warehouse_location_id.id),
                ], limit=1)

                if stock_quant and record.cantidad > stock_quant.quantity:
                    # Mostrar un mensaje de advertencia en la interfaz
                    return {
                        'warning': {
                            'title': "Stock insuficiente",
                            'message': f"No hay suficiente stock para el producto {record.product_id.name}. "
                                       f"Cantidad disponible: {stock_quant.quantity}",
                        }
                    }
                elif not stock_quant:
                    # Mostrar un mensaje de advertencia si no hay stock
                    return {
                        'warning': {
                            'title': "Stock no encontrado",
                            'message': f"No se encontró stock para el producto {record.product_id.name} en la ubicación seleccionada.",
                        }
                    }

    @api.constrains('cantidad', 'product_id', 'warehouse_location_id')
    def _check_cantidad_stock(self):
        for record in self:
            if record.product_id and record.warehouse_location_id and record.cantidad > 0:
                # Obtener la cantidad disponible en stock para el producto y la ubicación
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.warehouse_location_id.id),
                ], limit=1)

                if stock_quant and record.cantidad > stock_quant.quantity:
                    raise ValidationError(
                        f"No hay suficiente stock para el producto {record.product_id.name}. "
                        f"Cantidad disponible: {stock_quant.quantity}"
                    )
                elif not stock_quant:
                    raise ValidationError(
                        f"No se encontró stock para el producto {record.product_id.name} en la ubicación seleccionada."
                    )