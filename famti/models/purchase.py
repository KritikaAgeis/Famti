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

    def _prepare_picking(self):
        # res = super()._prepare_picking()

        # qc_location = self.company_id.stock_location_id
        # print("===qc_location====",qc_location)
        # if qc_location:
        #     res['location_dest_id'] = qc_location.id

        # return res

        res = super()._prepare_picking()

        qc_location = self.company_id.stock_location_id
        print("--------qc_location------", qc_location)
        default_dest_location = res.get('location_dest_id')
        print("--------default_dest_location------", default_dest_location)

        if qc_location and default_dest_location != qc_location.id:
            print("false")
            res['location_dest_id'] = qc_location.id

        return res





