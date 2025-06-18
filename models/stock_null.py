# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools


class ProductZeroStockWarehouse(models.Model):
    """Vista (read‑only) con los productos sin stock en cada bodega."""
    _name = 'product.zero.stock.warehouse'
    _description = 'Productos sin Stock por Bodega'
    _auto = False            # SQL view
    _rec_name = 'display_name'
    _order = 'default_code'

    # Datos del producto
    product_id     = fields.Many2one('product.product',   string='Producto', readonly=True)
    default_code   = fields.Char(   related='product_id.default_code', string='Referencia', readonly=True)
    name           = fields.Char(   related='product_id.name',         string='Nombre',     readonly=True)
    categ_id       = fields.Many2one(related='product_id.categ_id',    string='Categoría',  readonly=True)

    # Datos de bodega y stock
    warehouse_id   = fields.Many2one('stock.warehouse', string='Bodega', readonly=True)
    qty_available  = fields.Float(   string='Stock',    readonly=True)

    # Nombre combinando código + nombre
    display_name   = fields.Char(compute='_compute_display_name', store=False)

    @api.depends('default_code', 'name')
    def _compute_display_name(self):
        for rec in self:
            rec.display_name = f"[{rec.default_code}] {rec.name}" if rec.default_code else rec.name

    # --- SQL view ----------------------------------------------------------
    def _query(self):
        """Productos stock‑able, vendibles, con stock = 0 por bodega."""
        return """
            SELECT
                MIN(sq.id)                         AS id,
                sq.product_id                      AS product_id,
                sq.warehouse_id                    AS warehouse_id,
                SUM(sq.quantity)                   AS qty_available
            FROM stock_quant sq
            JOIN product_product pp ON pp.id = sq.product_id
            WHERE pp.sale_ok IS TRUE                      -- vendibles
              AND pp.type = 'product'                     -- almacenables
            GROUP BY sq.product_id, sq.warehouse_id
            HAVING SUM(sq.quantity) = 0                   -- stock = 0
        """

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS ({self._query()})
        """)
