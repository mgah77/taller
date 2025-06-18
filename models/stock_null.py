# product_zero_stock/models/product_zero_stock.py
"""
Extiende product.product y añade un campo virtual 'zero_stock_user'
para filtrar productos con stock exactamente 0 en la bodega asignada
al usuario.  Se usa únicamente en dominios (compute + search).
"""
from odoo import api, fields, models
from odoo.tools.float_utils import float_is_zero


class ProductZeroStock(models.Model):
    _inherit = "product.product"

    zero_stock_user = fields.Boolean(
        string="Stock 0 en mi bodega",
        compute="_compute_zero_stock_user",
        search="_search_zero_stock_user",
        store=False,
    )

    # ------------------------------------------------------------------
    # Cómputo “dummy”: basta para que Odoo reconozca el campo como calculado
    # ------------------------------------------------------------------
    def _compute_zero_stock_user(self):
        for rec in self:
            rec.zero_stock_user = False

    # ------------------------------------------------------------------
    # Búsqueda personalizada para usar en dominios
    # ------------------------------------------------------------------
    @api.model
    def _search_zero_stock_user(self, operator, value):
        """
        Permite ('zero_stock_user', '=', True) y '!=' en dominios.
        Devuelve los productos con stock EXACTAMENTE 0 en la bodega
        del usuario actual, siempre que sean almacenables y vendibles.
        """
        assert operator in ('=', '!=')  # otros operadores no previstos

        warehouse = self.env.user.property_warehouse_id
        if not warehouse:
            # Sin bodega → no mostrar nada (o todo si se usa '!=' pero
            # el menú ya restringe al '=')
            return [('id', '=', 0)]

        # Ubicaciones internas de la bodega
        loc_ids = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('warehouse_id', '=', warehouse.id),
        ]).ids

        # Universo base: almacenables + vendibles
        base_products = self.search([
            ('type', '=', 'product'),
            ('sale_ok', '=', True),
        ])
        base_ids = base_products.ids
        if not base_ids:
            return [('id', '=', 0)]

        # Cantidades por producto en las ubicaciones de la bodega del usuario
        quants = self.env['stock.quant'].read_group(
            [('product_id', 'in', base_ids), ('location_id', 'in', loc_ids)],
            ['product_id', 'quantity:sum'],
            ['product_id'],
        )

        non_zero_ids = {
            q['product_id'][0]
            for q in quants
            if not float_is_zero(q['quantity'], precision_digits=6)
        }

        zero_ids = list(set(base_ids) - non_zero_ids)

        if operator == '=' and value:
            return [('id', 'in', zero_ids)]
        elif operator == '!=' and value:
            return [('id', 'not in', zero_ids)]
        else:
            # Cualquier otra combinación devuelve vacío
            return [('id', '=', 0)]
