from odoo import models, fields, api

class StockLocation(models.Model):
    _inherit = 'stock.location'

    serial_prefix = fields.Char(string="Serial Prefix")
