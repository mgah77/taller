from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero

class ProductZeroStock(models.Model):
    _inherit = "product.product"

    zero_stock_user = fields.Boolean(
        string="Stock 0 en mi bodega",
        compute=False,              # no hace falta calcularlo;
        search="_search_zero_stock_user",
        store=False,
    )

    # ------------------------------------------------------------------
    # Búsqueda: productos con stock EXACTAMENTE 0 en la bodega del usuario
    # ------------------------------------------------------------------
    @api.model
    def _search_zero_stock_user(self, operator, value):
        """
        Permite usar ('zero_stock_user', '=', True) o '!=' en dominios.
        Si el usuario no tiene bodega asignada → no devuelve nada.
        """
        assert operator in ('=', '!=')

        # 1) Bodega del usuario
        warehouse = self.env.user.property_warehouse_id
        if not warehouse:
            # Sin bodega → no mostrar registros (evita confusión)
            return [('id', '=', 0)]

        # 2) Ubicaciones internas de esa bodega
        loc_ids = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('warehouse_id', '=', warehouse.id),
        ]).ids

        # 3) Universo de productos elegibles (vendibles + almacenables)
        products = self.search([
            ('type', '=', 'product'),
            ('sale_ok', '=', True),
        ]).ids

        if not products:
            return [('id', '=', 0)]

        # 4) Sumar stock por producto en esas ubicaciones
        groups = self.env['stock.quant'].read_group(
            [('product_id', 'in', products), ('location_id', 'in', loc_ids)],
            ['product_id', 'quantity:sum'],
            ['product_id'],
        )

        # 5) Productos con cantidad distinta de 0 (positiva o negativa)
        non_zero_ids = {
            g['product_id'][0]
            for g in groups
            if not float_is_zero(g['quantity'], precision_rounding=self.env['decimal.precision'].precision_get('Product Unit of Measure'))
        }

        # 6) Stock 0 = universo - non_zero
        zero_ids = list(set(products) - non_zero_ids)

        if operator == '=' and value:
            return [('id', 'in', zero_ids)]
        elif operator == '!=' and value:
            return [('id', 'not in', zero_ids)]
        else:
            # Cualquier otra combinación (poco frecuente) → vacío
            return [('id', '=', 0)]
