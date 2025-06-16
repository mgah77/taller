from odoo import models, fields, api

class ProductDepartment(models.Model):
    _inherit = 'product.template'  # Reemplaza 'your.model' por el nombre del modelo que deseas modificar

    # Modifica el campo partner_id para agregar un filtro adicional
    depto = fields.Many2one('taller.depto.rel', string='Depto')
    alias = fields.Char('Detalle')

    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        # Filtrar por la bodega del usuario si está definida
        user_warehouse = self.env.user.property_warehouse_id
        if user_warehouse:
            args += [('warehouse_id', '=', user_warehouse.id)]
        return super(ProductTemplate, self).search(args, offset=offset, limit=limit, order=order, count=count)