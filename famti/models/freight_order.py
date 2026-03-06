from werkzeug import urls
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class FreightOrder(models.Model):
    _inherit = 'freight.order'
    _description = 'Freight Order'

    purchase_id = fields.Many2one(
        'purchase.order',
        string="Purchase Order"
    )
