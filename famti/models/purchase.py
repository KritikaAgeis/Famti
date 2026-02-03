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
    ], string='Status', readonly=True, index=True, copy=False, default='draft')

    
    def action_rfq_send(self):
        for order in self:
            if not order.order_line:
                raise UserError(
                    "You cannot send the email without adding at least one order line."
                )
        return super().action_rfq_send()

    def action_send_for_cfo_approval(self):
        for order in self:
            if not order.order_line:
                raise UserError(
                    "Purchase Order must have at least one order line.")
            
            if order.partner_id.state == 'certificate_expired':
                raise UserError(
                    f"Cannot send for CFO approval. Vendor '{order.partner_id.name}' certificate has expired. Please renew it."
                )
                
        self.state='to approve'

    def action_reject_coa(self):
        self.state = 'cancel'


    def button_confirm(self):
        if not self.env.user.has_group('purchase.group_purchase_manager'):
            raise  UserError("You are not allowed to process this purchase. Please send to 'CFO' for approval")
        return super().button_confirm()

    # def _prepare_picking(self):
    #     res = super()._prepare_picking()
    #
    #     qc_location = self.company_id.stock_location_id
    #     print("--------qc_location------", qc_location)
    #     default_dest_location = res.get('location_dest_id')
    #     print("--------default_dest_location------", default_dest_location)
    #
    #     if qc_location and default_dest_location != qc_location.id:
    #         print("false")
    #         res['location_dest_id'] = qc_location.id
    #
    #     return res




class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line"]

    weight_val = fields.Float(string="Weight",help="This helps to categorise specific product.")
    weight_uom = fields.Selection(selection=[
                                        ('kg', 'Kg'),
                                        ('lbs', 'Lbs'),
                                        ('gm', 'Gm'),
                                        ],required=True,default='kg',string=" ")
    thickness_val = fields.Float(string="Thickness",help="This helps to categorise specific product.")
    thickness_uom = fields.Selection(selection=[('guage','Guage'),('micron','Micron')],default='micron',string=" ")


    width_val = fields.Float(string="Width",help="This helps to categorise specific product.")
    width_uom = fields.Selection(selection=[('mm','MM'),('inch','Inch')],default='mm',string=" ")
    core_id = fields.Selection(selection=[('3','3 Inch'),('6','6 Inch')],string="Core")
    category = fields.Char(string="Film Category",  help="This helps to categorise specific product.")
    film = fields.Char(string="Film", help="Product Film.")
    film_type = fields.Char(string="Film Type", help="Film Type")
    length_val = fields.Float(string="Length", help="Product Length")
    length_uom = fields.Selection(selection=[('m','M'),('feet','Feet')],default='feet',string=" ")








