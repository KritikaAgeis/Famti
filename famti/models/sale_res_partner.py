from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    credit_grace_days = fields.Integer(string="Credit Grace Period (Days)", default=0)
    lc_required = fields.Boolean(string="LC Required")
    lc_document = fields.Binary(string="LC Document")
