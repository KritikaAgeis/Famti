from odoo import api, fields, models
from odoo.exceptions import UserError


class Purchase(models.Model):
    _inherit = "purchase.order"

    state = fields.Selection([
        ('draft', 'RFQ'),
        ('sent', 'RFQ Sent'),
        ('to approve', 'To Approve'),
        ('cfo_rejected', 'CFO Rejected'),
        ('purchase', 'Purchase Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def action_send_for_cfo_approval(self):
        self.state='to approve'

    def action_reject_coa(self):
        self.state = 'cancel'


    def button_confirm(self):
        print("Self-----------",self.env.user.has_group('purchase.group_purchase_manager'))
        if not self.env.user.has_group('purchase.group_purchase_manager'):
            raise  UserError("You are not allowed to process this purchase. Please send to 'CFO' for approval")
        return super().button_confirm()





