from odoo import api, fields, models

class ProductZeroStock(models.Model):
    """
    No creamos un modelo nuevo: extendemos product.product y le
    damos un campo booleano virtual que indica si, para el usuario
    actual, el producto está con stock = 0 en SU bodega.
    """
    _inherit = "product.product"

    zero_stock_user = fields.Boolean(
        string="Stock 0 (mi bodega)",
        compute="_compute_zero_stock_user",
        search="_search_zero_stock_user",
        store=False,
    )

    # ---------------------------------------------------------------------
    # CÓMPUTO: marca True si el stock en la bodega del usuario es 0
    # ---------------------------------------------------------------------
    def _compute_zero_stock_user(self):
        user_wh = self.env.user.property_warehouse_id
        if not user_wh:
            # Sin bodega asignada → nada se marca
            for prod in self:
                prod.zero_stock_user = False
            return

        # Ubicaciones internas de esa bodega
        loc_ids = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('warehouse_id', '=', user_wh.id)
        ]).ids

        # Sumar cantidades > 0 por producto en esas ubicaciones
        groups = self.env['stock.quant'].read_group(
            [
                ('product_id', 'in', self.ids),
                ('location_id', 'in', loc_ids),
            ],
            ['product_id', 'quantity:sum'],
            ['product_id'],
        )
        qty_map = {g['product_id'][0]: g['quantity'] for g in groups}

        for prod in self:
            prod.zero_stock_user = qty_map.get(prod.id, 0.0) == 0.0

    # ---------------------------------------------------------------------
    # BÚSQUEDA: devuelve el dominio equivalente a “stock 0 en mi bodega”
    # ---------------------------------------------------------------------
    @api.model
    def _search_zero_stock_user(self, operator, value):
        """
        Permite poner ('zero_stock_user', '=', True) en un dominio.
        Solo se aceptan operadores =  or  !=
        """
        assert operator in ('=', '!=', 'in', 'not in')
        user_wh = self.env.user.property_warehouse_id
        if not user_wh:
            # Sin bodega: no devolver nada (o todo, depende del operador)
            return [('id', '!=', 0)] if (operator, value) in [('=', True), ('!=', False)] else [('id', '=', 0)]

        # Paso 1: base = productos vendibles y almacenables
        base_domain = [
            ('type', '=', 'product'),
            ('sale_ok', '=', True),
        ]
        prods = self.search(base_domain).ids

        # Paso 2: productos con stock > 0 en la bodega del usuario
        loc_ids = self.env['stock.location'].search([
            ('usage', '=', 'internal'),
            ('warehouse_id', '=', user_wh.id)
        ]).ids
        groups = self.env['stock.quant'].read_group(
            [('product_id', 'in', prods), ('location_id', 'in', loc_ids)],
            ['product_id', 'quantity:sum'],
            ['product_id'],
        )
        with_stock = {g['product_id'][0] for g in groups if g['quantity']}

        # Paso 3: stock 0 = base - with_stock
        zero_stock_ids = list(set(prods) - with_stock)

        if operator in ('=', 'in'):
            return [('id', 'in', zero_stock_ids)]
        else:  # '!=' or 'not in'
            return [('id', 'not in', zero_stock_ids)]
