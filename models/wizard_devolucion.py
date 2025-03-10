from odoo import models, fields, api
from odoo.exceptions import ValidationError

class WizardDevolucion(models.TransientModel):
    _name = 'wizard.devolucion'
    _description = 'Wizard para devolución de productos'

    # Campos del wizard
    entrega_id = fields.Many2one('entrega.equipos', string='Entrega', readonly=True)
    line_ids = fields.One2many('wizard.devolucion.line', 'wizard_id', string='Productos a Devolver')

    def default_get(self, fields):
        res = super(WizardDevolucion, self).default_get(fields)
        if self.env.context.get('active_id'):
            entrega = self.env['entrega.equipos'].browse(self.env.context['active_id'])
            res['entrega_id'] = entrega.id
            # Obtener los productos entregados y comparar con los ya devueltos
            line_vals = []
            for line in entrega.line_ids:
                # Buscar si el producto ya ha sido devuelto
                devuelto = sum(self.env['return.equipos.line'].search([
                    ('return_id', '=', entrega.id),
                    ('product_id', '=', line.product_id.id)
                ]).mapped('cantidad'))
                if devuelto < line.cantidad:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'cantidad_devuelta': 0,  # Por defecto 0
                    }))
            res['line_ids'] = line_vals
        return res

    def action_confirm(self):
        for line in self.line_ids:
            if line.cantidad_devuelta > 0 and line.product_id:
                self.env['return.equipos.line'].create({
                    'return_id': self.entrega_id.id,  # Se usa return_id en vez de entrega_id
                    'product_id': line.product_id.id,  # Se asegura que product_id tenga valor
                    'cantidad': line.cantidad_devuelta,  # Se usa cantidad en vez de cantidad_devuelta
                })
        return {'type': 'ir.actions.act_window_close'}


class WizardDevolucionLine(models.TransientModel):
    _name = 'wizard.devolucion.line'
    _description = 'Línea de productos a devolver en el wizard'

    wizard_id = fields.Many2one('wizard.devolucion', string='Wizard')
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    cantidad_devuelta = fields.Float(string='Cantidad a Devolver', default=0)