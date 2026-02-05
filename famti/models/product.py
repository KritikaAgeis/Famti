from odoo import api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    mo_serial_no = fields.Boolean(string="MO Serial No")
    # core_id = fields.Char(string="Core Id", tracking=True)
    # film = fields.Char(string="Film", tracking=True, help="Product Film.")
    # film_type = fields.Char(string="Film Type", tracking=True, help="Film Type")
