from odoo import models, fields, api

class WizardDevolucion(models.TransientModel):
    _name = 'wizard.devolucion'
    _description = 'Wizard para devolución de productos'

    entrega_id = fields.Many2one('entrega.equipos', string='Entrega', readonly=True)
    line_ids = fields.One2many('wizard.devolucion.line', 'wizard_id', string='Productos a Devolver')

    def action_aceptar(self):
        # Procesar los productos con cantidad distinta a 0
        for line in self.line_ids:
            if line.cantidad_devuelta > 0:
                self.env['return.equipos.line'].create({
                    'entrega_id': self.entrega_id.id,
                    'product_id': line.product_id.id,
                    'cantidad_devuelta': line.cantidad_devuelta,
                })
        return {'type': 'ir.actions.act_window_close'}

class WizardDevolucionLine(models.TransientModel):
    _name = 'wizard.devolucion.line'
    _description = 'Línea de productos a devolver en el wizard'

    wizard_id = fields.Many2one('wizard.devolucion', string='Wizard')
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    cantidad_entregada = fields.Float(string='Cantidad Entregada', readonly=True)
    cantidad_devuelta = fields.Float(string='Cantidad a Devolver', default=0.0)

    @api.model
    def default_get(self, fields):
        print("Contexto:", self.env.context)  # Depuración
        res = super(WizardDevolucionLine, self).default_get(fields)
        if self.env.context.get('active_id'):
            print("Active ID:", self.env.context['active_id'])  # Depuración
            entrega = self.env['entrega.equipos'].browse(self.env.context['active_id'])
            res['wizard_id'] = entrega.id
            lines = []

            # Obtener las cantidades ya devueltas para cada producto
            devoluciones = self.env['return.equipos.line'].search([('entrega_id', '=', entrega.id)])
            devoluciones_por_producto = {d.product_id.id: d.cantidad_devuelta for d in devoluciones}

            for line in entrega.line_ids:
                cantidad_devuelta = devoluciones_por_producto.get(line.product_id.id, 0.0)
                if line.cantidad > cantidad_devuelta:
                    lines.append((0, 0, {
                        'product_id': line.product_id.id,
                        'cantidad_entregada': line.cantidad,
                        'cantidad_devuelta': 0.0,
                    }))
            res['line_ids'] = lines
        return res