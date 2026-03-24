from odoo import api, fields,models, _

class HrExpense(models.Model):
    _inherit = "hr.expense"

    purchase_id = fields.Many2one('purchase.order',string="Purchase Order")