from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    product_categ_id = fields.Many2one(
        related='product_id.product_tmpl_id.categ_id',
        string='Categoría del Producto',
        store=True,
        readonly=True
    )