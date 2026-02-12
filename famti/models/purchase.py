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



class PurchaseOrderLine(models.Model):
    _inherit = ["purchase.order.line"]

    weight_val = fields.Float(string="Weight",help="This helps to categorise specific product.")
    weight_uom = fields.Selection(selection=[
                                        ('kg', 'Kg'),
                                        ('lbs', 'Lbs'),
                                        ('gm', 'Gm'),
                                        ],required=True,default='kg',string=" ")
    thickness_val = fields.Float(string="Thickness",help="This helps to categorise specific product.")
    thickness_uom = fields.Selection(selection=[('guage','Guage'),('micron','Micron'),('mm','MM'),('mil','Mil')],default='micron',string=" ")


    width_val = fields.Float(string="Width",help="This helps to categorise specific product.")
    width_uom = fields.Selection(selection=[('mm','MM'),('inch','Inch'),('mil','Mil')],default='mm',string=" ")
    core_id = fields.Selection(selection=[('3','3 Inch'),('6','6 Inch')],string="Core")
    category = fields.Char(string="Film Category",  help="This helps to categorise specific product.")
    film = fields.Char(string="Film", help="Product Film.")
    film_type = fields.Char(string="Film Type", help="Film Type")
    length_val = fields.Float(string="Length", help="Product Length")
    length_uom = fields.Selection(selection=[('m','M'),('feet','Feet')],default='feet',string=" ")
    # uom_conv_id = fields.Many2one('uom.convert.wizard',string="UOM Conversion Wizard")

    def action_open_uom_conversion(self):
        print(f'-line 46--------{self}--{self.ids}')
        return {
            'name': 'Purchase Order Lines',
            'type': 'ir.actions.act_window',
            'res_model': 'uom.convert.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'active_id': self,
            }
        }








