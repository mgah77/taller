from odoo import models, fields, api
from odoo.exceptions import ValidationError


class EntregaEquipos(models.Model):
    _name = 'entrega.equipos'
    _description = 'Entrega de Equipos de Reemplazo'

    name = fields.Char(string='Número de Entrega', required=True, copy=False, readonly=True, default='Nuevo')
    armador = fields.Many2one('res.partner', string='Armador',domain="[('type', '!=', 'private'), ('is_company', '=', True), ('type','=','contact'), ('is_customer','=',True)]",required=True)
    ot_id = fields.Many2one('taller.ot', string='Orden de Trabajo', domain="[('armador', '=', armador), ('sucursel', '=', viewer)]", required=True)
    fecha_entrega = fields.Date(string='Fecha de Entrega', required=True)
    fecha_devolucion = fields.Date(string='Fecha de Devolución', required=True)
    line_ids = fields.One2many('entrega.equipos.line', 'entrega_id', string='Equipos Entregados')
    state = fields.Selection([
        ('borrador', 'Borrador'),
        ('entregado', 'Entregado'),
        ('devuelto', 'Devuelto')
    ], string='Estado', default='borrador')
    sucursel = fields.Selection([('2', 'Ñuble'), ('3', 'Par Vial')], string='Sucursal', default='2')
    sucursel_readonly = fields.Selection([('2', 'Ñuble'), ('3', 'Par Vial')], string='Sucursal (Readonly)', compute="_compute_sucursel_readonly", store=True)
    viewer = fields.Integer('Current User', compute="_compute_viewer")
    responsable = fields.Many2one('res.users', string='Responsable', default=lambda self: self.env.user, readonly=True)

    def _compute_viewer(self):
        for record in self:
            record['viewer']=self.env.user.property_warehouse_id
            return
        
    @api.depends('sucursel')
    def _compute_sucursel_readonly(self):
        for record in self:
            record.sucursel_readonly = record.sucursel

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
        
        self.state = 'entregado'
        # Verificar y asignar bodega si el usuario no tiene una
        user = self.env.user
        if not user.property_warehouse_id:
            warehouse = self.env['stock.warehouse'].search([('id', '=', int(self.sucursel))], limit=1)            
        else:
            warehouse = user.property_warehouse_id

        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'outgoing'),
            ('warehouse_id', '=', warehouse.id)
        ], limit=1)

        # Crear el albarán de salida en borrador
        picking_vals = {
            'partner_id': self.armador.id,
            'picking_type_id': picking_type.id,
            'location_id': warehouse.lot_stock_id.id,
            'location_dest_id': self.armador.property_stock_customer.id,
            'origin': self.name,
            'state': 'draft',  # Estado inicial
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

        # Confirmar los movimientos de stock
        picking.action_confirm()

        # Reservar el stock (pasar a estado 'assigned')
        picking.action_assign()

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
        domain="""[
            ('exchange_ok', '=', True),
            ('qty_available', '>', 0),
            ('stock_quant_ids.location_id', '=', warehouse_location_id),            
        ]""",
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
                record.warehouse_location_id = warehouse.lot_stock_id.id
            else:
                sucursel_value = record.entrega_id.sucursel
                if sucursel_value:
                    warehouse = self.env['stock.warehouse'].search([('id', '=', int(sucursel_value))], limit=1)
                    if warehouse:
                        record.warehouse_location_id = warehouse.lot_stock_id.id
                    else:
                        record.warehouse_location_id = False
                else:
                    record.warehouse_location_id = False

    @api.onchange('product_id', 'cantidad')
    def _onchange_cantidad_stock(self):
        for record in self:
            if record.product_id and record.warehouse_location_id and record.cantidad > 0:
                stock_quant = self.env['stock.quant'].search([
                    ('product_id', '=', record.product_id.id),
                    ('location_id', '=', record.warehouse_location_id.id),
                ], limit=1)

                if stock_quant and record.cantidad > stock_quant.quantity:
                    return {
                        'warning': {
                            'title': "Stock insuficiente",
                            'message': f"No hay suficiente stock para el producto {record.product_id.name}. "
                                       f"Cantidad disponible: {stock_quant.quantity}",
                        }
                    }
                elif not stock_quant:
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