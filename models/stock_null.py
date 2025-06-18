# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductZeroStockWarehouse(models.Model):
    """Vista (read-only) con los productos sin stock en cada bodega."""
    _name = 'product.zero.stock.warehouse'
    _description = 'Productos sin Stock por Bodega'
    _auto = False  # SQL view
    _rec_name = 'display_name'
    _order = 'default_code'

    # Datos del producto
    product_id = fields.Many2one('product.product', string='Producto', readonly=True)
    default_code = fields.Char(related='product_id.default_code', string='Referencia', readonly=True)
    name = fields.Char(related='product_id.name', string='Nombre', readonly=True)
    categ_id = fields.Many2one(related='product_id.categ_id', string='Categoría', readonly=True)

    # Datos de bodega y stock
    warehouse_id = fields.Many2one('stock.warehouse', string='Bodega', readonly=True)
    qty_available = fields.Float(string='Stock', readonly=True)

    # Nombre combinando código + nombre
    display_name = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('default_code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.default_code}] {rec.name}" if rec.default_code else rec.name

    @property
    def _query(self):
        """Productos stock-able, vendibles, con stock = 0 por bodega."""
        return """
            SELECT
                pp.id || '-' || sw.id AS id,  -- ID único combinando producto y bodega
                pp.id AS product_id,
                sw.id AS warehouse_id,
                0 AS qty_available  -- Siempre será 0 por definición
            FROM product_product pp
            CROSS JOIN stock_warehouse sw
            WHERE pp.sale_ok IS TRUE
              AND pp.type = 'product'
              AND NOT EXISTS (
                  SELECT 1 FROM stock_quant sq
                  WHERE sq.product_id = pp.id
                    AND sq.warehouse_id = sw.id
                    AND sq.quantity > 0
              )
        """

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS ({self._query})
        """)