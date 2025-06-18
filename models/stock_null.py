# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductZeroStockWarehouse(models.Model):
    """Vista (solo lectura) que muestra los productos sin stock por bodega."""
    _name = 'product.zero.stock.warehouse'
    _description = 'Productos sin Stock por Bodega'
    _auto = False  # se crea como vista SQL
    _rec_name = 'display_name'
    _order = 'default_code'

    # Campos
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    default_code = fields.Char(related='product_id.default_code', string='Referencia', readonly=True)
    name = fields.Char(related='product_id.name', string='Nombre', readonly=True)
    categ_id = fields.Many2one(related='product_id.categ_id', string='Categoría', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Bodega', readonly=True)
    qty_available = fields.Float(string='Stock', readonly=True)
    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('default_code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.default_code}] {rec.name}" if rec.default_code else rec.name

    def _query(self):
        """Productos 'product', vendibles, con stock = 0, por bodega interna."""
        return """
            SELECT
                MIN(sq.id) AS id,
                sq.product_id AS product_id,
                sl.warehouse_id AS warehouse_id,
                SUM(sq.quantity) AS qty_available
            FROM stock_quant sq
            JOIN stock_location sl ON sl.id = sq.location_id
            JOIN product_product pp ON pp.id = sq.product_id
            JOIN product_template pt ON pt.id = pp.product_tmpl_id
            WHERE pt.sale_ok = TRUE
              AND pt.type = 'product'
              AND pt.active = TRUE
              AND sl.usage = 'internal'
              AND sl.active = TRUE
            GROUP BY sq.product_id, sl.warehouse_id
            HAVING COALESCE(SUM(sq.quantity), 0) = 0
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS ({self._query()})
        """)

    @api.model
    def _search(self, args, offset=0, limit=None, order=None, count=False):
        ctx = self.env.context
        if ctx.get('warehouse_filter_by_user') and self.env.user.warehouse_id:
            args = [('warehouse_id', '=', self.env.user.warehouse_id.id)] + (args or [])
        return super()._search(args, offset=offset, limit=limit, order=order, count=count)