from odoo import models, fields, api
from odoo.exceptions import UserError

# class StockLocation(models.Model):
#     _inherit = 'stock.location'

#     serial_prefix = fields.Char(string="Serial Prefix")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_tolling = fields.Boolean(string="Is Tolling")
