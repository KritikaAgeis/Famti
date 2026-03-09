from odoo import models, fields, api
from odoo.exceptions import UserError

# class StockLocation(models.Model):
#     _inherit = 'stock.location'

#     serial_prefix = fields.Char(string="Serial Prefix")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    is_tolling = fields.Boolean(string="Is Tolling")
    logo = fields.Image("Logo", max_width=1920, max_height=1920, default=lambda self: self.env.company.logo)

    so_type = fields.Selection(
        related='sale_id.so_type',
        string="SO Type",
        store=True
    )
