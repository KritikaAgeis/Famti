from odoo import models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    lot_id = fields.Many2one('stock.lot',string='Serial Numbers')