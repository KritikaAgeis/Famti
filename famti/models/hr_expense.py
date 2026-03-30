from odoo import api, fields,models, _

class HrExpense(models.Model):
    _inherit = "hr.expense"

    purchase_id = fields.Many2one('purchase.order',string="Purchase Order")
    purchase_ids = fields.Many2many('purchase.order','po_expense_rel','expense_id',
        'po_id',string="Purchase Orders")
