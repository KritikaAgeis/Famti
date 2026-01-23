from odoo import api, fields, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = "res.partner"

    is_supplier = fields.Boolean(string="Supplier")
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company', required=True, readonly=True,
        default=lambda self: self.env.company)

    credit_grace_days = fields.Integer(string="Credit Grace Period (Days)", default=0)
    lc_required = fields.Boolean(string="LC Required")
    lc_document = fields.Binary(string="LC Document")